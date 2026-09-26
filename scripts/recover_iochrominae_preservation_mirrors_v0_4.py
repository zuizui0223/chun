#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

DOI="10.5061/dryad.p5dq84v"
UA="CHUN-Iochrominae-preservation-recovery/0.4"
TIMEOUT=25
OBJECTS={
  "readme":{
    "file_id":108458,
    "filename":"README_for_Larter et al 2019 Dvdy Iochrominae development evolution DATA.txt",
    "size":4072,
    "md5":"2e4a251725ad4c13975fc09481da302d",
    "out_name":"iochrominae_README.txt",
  },
  "archive":{
    "file_id":108456,
    "filename":"Larter et al 2019 Dvdy Iochrominae development evolution DATA.rar",
    "size":3054999,
    "md5":"76b46e384fb7c9bf1ef3fbd7d1e5d2f0",
    "out_name":"iochrominae_DATA.rar",
  },
}


def get(url:str,accept:str="*/*")->dict:
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":accept})
    try:
        with urllib.request.urlopen(req,timeout=TIMEOUT) as r:
            return {"ok":True,"status":getattr(r,"status",200),"final_url":r.geturl(),
                    "headers":dict(r.headers),"body":r.read()}
    except urllib.error.HTTPError as e:
        try: body=e.read()
        except Exception: body=b""
        return {"ok":False,"status":e.code,"final_url":e.geturl(),
                "headers":dict(e.headers or {}),"body":body,"reason":str(e.reason)}
    except Exception as e:
        return {"ok":False,"status":None,"final_url":url,"headers":{},
                "body":b"","reason":repr(e)}


def exact(body:bytes,spec:dict)->bool:
    return len(body)==spec["size"] and hashlib.md5(body).hexdigest().lower()==spec["md5"].lower()


def jget(url:str)->tuple[dict|list|None,dict]:
    r=get(url,"application/json,*/*")
    try:
        obj=json.loads(r["body"].decode("utf-8")) if r["ok"] else None
    except Exception:
        obj=None
    diag={"url":url,"status":r["status"],"bytes":len(r["body"]),"reason":r.get("reason")}
    return obj,diag


def zenodo_queries(spec:dict)->list[str]:
    return [
        DOI,
        f'"{spec["filename"]}"',
        spec["md5"],
    ]


def zenodo_candidates(spec:dict)->tuple[list[str],list[dict]]:
    urls=[]; diagnostics=[]
    for q in zenodo_queries(spec):
        api="https://zenodo.org/api/records?"+urllib.parse.urlencode({"q":q,"size":25})
        obj,diag=jget(api); diag["query"]=q
        hits=[]
        if isinstance(obj,dict):
            hits=obj.get("hits",{}).get("hits",[]) or []
        diag["hit_count"]=len(hits)
        diagnostics.append(diag)
        for rec in hits:
            if not isinstance(rec,dict):
                continue
            for f in rec.get("files",[]) or []:
                if not isinstance(f,dict):
                    continue
                key=str(f.get("key") or "")
                size=f.get("size")
                checksum=str(f.get("checksum") or "").lower()
                same_name=(key==spec["filename"])
                same_size=(size is not None and int(size)==spec["size"])
                same_md5=(checksum in {spec["md5"].lower(),"md5:"+spec["md5"].lower()})
                if not (same_name or (same_size and same_md5)):
                    continue
                links=f.get("links") or {}
                for k in ("self","download","content"):
                    u=links.get(k) if isinstance(links,dict) else None
                    if isinstance(u,str) and u.startswith("http"):
                        urls.append(u)
    return list(dict.fromkeys(urls)),diagnostics


def datacite_diagnostics()->dict:
    api="https://api.datacite.org/dois?"+urllib.parse.urlencode({
        "query":DOI,
        "page[size]":25,
    })
    obj,diag=jget(api)
    rows=obj.get("data",[]) if isinstance(obj,dict) else []
    diag["record_count"]=len(rows)
    diag["related_urls"]=[]
    for row in rows[:25]:
        att=row.get("attributes",{}) if isinstance(row,dict) else {}
        url=att.get("url")
        rid=att.get("doi")
        if url or rid:
            diag["related_urls"].append({"doi":rid,"url":url})
    return diag


def dryad_direct_urls(spec:dict)->list[str]:
    fid=spec["file_id"]
    return [
        f"https://datadryad.org/api/v2/files/{fid}/download",
        f"https://datadryad.org/stash/downloads/file_stream/{fid}",
        f"https://datadryad.org/stash/downloads/file_stream/{fid}?download=1",
    ]


def cdx_url(original:str)->str:
    return "https://web.archive.org/cdx/search/cdx?"+urllib.parse.urlencode({
        "url":original,
        "output":"json",
        "fl":"timestamp,original,statuscode,mimetype,digest,length",
        "filter":"statuscode:200",
        "collapse":"digest",
    })


def parse_cdx(body:bytes)->list[dict]:
    try: x=json.loads(body.decode("utf-8"))
    except Exception: return []
    if not isinstance(x,list) or len(x)<2 or not isinstance(x[0],list):
        return []
    h=x[0]
    return [dict(zip(h,row)) for row in x[1:] if isinstance(row,list) and len(row)==len(h)]


def archive_urls(rows:list[dict])->list[str]:
    if not rows: return []
    chosen=[rows[0]]
    if len(rows)>1: chosen.append(rows[-1])
    out=[]
    for x in chosen:
        ts=x.get("timestamp"); original=x.get("original")
        if ts and original:
            out.append(f"https://web.archive.org/web/{ts}id_/{original}")
    return list(dict.fromkeys(out))


def attempt_urls(urls:list[str],spec:dict)->tuple[bytes|None,str|None,list[dict]]:
    attempts=[]
    for u in urls:
        r=get(u)
        match=bool(r["ok"] and exact(r["body"],spec))
        attempts.append({
            "url":u,"status":r["status"],"final_url":r["final_url"],
            "content_type":r["headers"].get("Content-Type"),"bytes":len(r["body"]),
            "md5":hashlib.md5(r["body"]).hexdigest() if r["body"] else None,
            "exact_size_md5_match":match,"reason":r.get("reason"),
        })
        if match:
            return r["body"],r["final_url"],attempts
    return None,None,attempts


def recover_one(spec:dict)->dict:
    all_attempts=[]

    direct=dryad_direct_urls(spec)
    body,via,attempts=attempt_urls(direct,spec)
    all_attempts.extend(attempts)

    zdiag=[]; zurls=[]
    if body is None:
        zurls,zdiag=zenodo_candidates(spec)
        b,v,a=attempt_urls(zurls,spec)
        all_attempts.extend(a)
        body,via=b,v

    cdx_diags=[]; warc_urls=[]
    if body is None:
        for original in direct:
            c=get(cdx_url(original),"application/json,*/*")
            rows=parse_cdx(c["body"]) if c["ok"] else []
            cdx_diags.append({
                "original":original,"url":cdx_url(original),"status":c["status"],
                "bytes":len(c["body"]),"snapshot_rows":len(rows),"reason":c.get("reason"),
            })
            warc_urls.extend(archive_urls(rows))
        b,v,a=attempt_urls(list(dict.fromkeys(warc_urls)),spec)
        all_attempts.extend(a)
        body,via=b,v

    return {
        "file_id":spec["file_id"],"filename":spec["filename"],
        "expected_size":spec["size"],"expected_md5":spec["md5"],
        "dryad_direct_urls":direct,
        "zenodo_search_diagnostics":zdiag,
        "zenodo_candidate_urls":zurls,
        "wayback_cdx_diagnostics":cdx_diags,
        "wayback_candidate_urls":list(dict.fromkeys(warc_urls)),
        "attempts":all_attempts,
        "recovered":body is not None,
        "recovered_via":via,
        "recovered_size":len(body) if body is not None else None,
        "recovered_md5":hashlib.md5(body).hexdigest() if body is not None else None,
        "_body":body,
    }


def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("--out",type=Path,required=True); a=ap.parse_args()
    a.out.parent.mkdir(parents=True,exist_ok=True)

    dc=datacite_diagnostics()
    out_objects={}
    recovered_count=0
    for label,spec in OBJECTS.items():
        rec=recover_one(spec)
        body=rec.pop("_body")
        if body is not None:
            recovered_count+=1
            (a.out.parent/spec["out_name"]).write_bytes(body)
        out_objects[label]=rec

    all_ok=recovered_count==len(OBJECTS)
    status=("IOCHROMINAE_EXACT_SOURCE_BYTES_RECOVERED_CONTENTS_UNOPENED"
            if all_ok else "HOLD_IOCHROMINAE_PRESERVATION_MIRRORS_NO_EXACT_BYTES")
    firewall={
        "readme_text_opened":False,
        "archive_member_names_opened":False,
        "archive_data_rows_opened":False,
        "profile_state_mapping_computed":False,
        "profile_states_computed":False,
        "patristic_distances_computed":False,
        "profile_auc_computed":False,
        "hidden_memory_auc_computed":False,
    }
    out={
        "version":"v0.4","source_doi":DOI,"status":status,
        "objects":out_objects,"datacite_discovery":dc,
        "all_exact_objects_recovered":all_ok,
        "outcome_firewall":firewall,
        "analysis_role":"RETROSPECTIVE_SECOND_BIOCHEMICAL_ANCHOR_NOT_PROSPECTIVE_REPLICATION",
        "next_gate":("FREEZE_RECOVERED_HASHES_THEN_READ_README_AND_LIST_ARCHIVE_MEMBER_NAMES_ONLY"
                     if all_ok else "KEEP_SOURCE_HOLD"),
        "paper1_science_changed":False,
        "el_v0_3_science_changed":False,
        "v0_8_promotion_state_changed":False,
    }
    a.out.write_text(json.dumps(out,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "status":status,
        "all_exact_objects_recovered":all_ok,
        "readme_recovered":out_objects["readme"]["recovered"],
        "archive_recovered":out_objects["archive"]["recovered"],
        "readme_zenodo_hits":[x["hit_count"] for x in out_objects["readme"]["zenodo_search_diagnostics"]],
        "archive_zenodo_hits":[x["hit_count"] for x in out_objects["archive"]["zenodo_search_diagnostics"]],
        "readme_wayback_snapshots":[x["snapshot_rows"] for x in out_objects["readme"]["wayback_cdx_diagnostics"]],
        "archive_wayback_snapshots":[x["snapshot_rows"] for x in out_objects["archive"]["wayback_cdx_diagnostics"]],
        "next_gate":out["next_gate"],
        "outcome_firewall":firewall,
    },indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
