#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json, re, urllib.error, urllib.parse, urllib.request
from pathlib import Path
from typing import Any

DOI="10.5061/dryad.p5dq84v"
README="README_for_Larter et al 2019 Dvdy Iochrominae development evolution DATA.txt"
ARCHIVE="Larter et al 2019 Dvdy Iochrominae development evolution DATA.rar"
API="https://datadryad.org/api/v2"
UA="CHUN-iochrominae-dryad-recheck/0.3"


def req(url:str, accept:str="*/*")->dict:
    q=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":accept})
    try:
        with urllib.request.urlopen(q,timeout=120) as r:
            return {"ok":True,"status":r.status,"url":url,"final_url":r.geturl(),
                    "headers":dict(r.headers),"body":r.read()}
    except urllib.error.HTTPError as e:
        try: body=e.read()
        except Exception: body=b""
        return {"ok":False,"status":e.code,"url":url,"final_url":e.geturl(),
                "headers":dict(e.headers or {}),"body":body,"reason":str(e.reason)}
    except Exception as e:
        return {"ok":False,"status":None,"url":url,"final_url":url,"headers":{},
                "body":b"","reason":repr(e)}


def jget(url:str)->Any:
    r=req(url,"application/json")
    if not r["ok"]:
        raise RuntimeError(f"JSON request failed {url}: {r['status']} {r.get('reason')}")
    return json.loads(r["body"])


def collect_candidate_urls(x:Any)->list[str]:
    found=[]
    def walk(v:Any):
        if isinstance(v,dict):
            for k,z in v.items():
                if k=="href" and isinstance(z,str):
                    if z.startswith(("http://","https://")):
                        found.append(z)
                    elif z.startswith("/"):
                        found.append("https://datadryad.org"+z)
                walk(z)
        elif isinstance(v,list):
            for z in v: walk(z)
    walk(x)
    return list(dict.fromkeys(found))


def exact_match(meta:dict,body:bytes)->bool:
    size=int(meta.get("size") or 0)
    if size and len(body)!=size:
        return False
    typ=str(meta.get("digestType") or "").lower().replace("_","-")
    expected=str(meta.get("digest") or "").lower()
    if expected:
        if typ in {"md5"}:
            return hashlib.md5(body).hexdigest()==expected
        if typ in {"sha-256","sha256"}:
            return hashlib.sha256(body).hexdigest()==expected
        return False
    return bool(body)


def file_id(meta:dict)->int:
    candidates=[]
    def walk(v:Any):
        if isinstance(v,str):
            candidates.append(v)
        elif isinstance(v,dict):
            for z in v.values(): walk(z)
        elif isinstance(v,list):
            for z in v: walk(z)
    walk(meta)
    for u in candidates:
        m=re.search(r"/files/(\d+)(?:$|[/?#])",u)
        if m: return int(m.group(1))
    raise ValueError("cannot infer file id")


def html_payload(r:dict)->bool:
    ctype=str(r.get("headers",{}).get("Content-Type","")).lower()
    b=r.get("body",b"").lstrip().lower()
    return "html" in ctype or b.startswith(b"<!doctype html") or b.startswith(b"<html")


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    a.out.parent.mkdir(parents=True,exist_ok=True)

    ds=jget(API+"/datasets/"+urllib.parse.quote("doi:"+DOI,safe=""))
    vh=ds["_links"]["stash:version"]["href"]
    vurl=vh if vh.startswith("http") else API+vh.removeprefix("/api/v2")
    listing=jget(vurl.rstrip("/")+"/files?per_page=100")
    files=listing.get("_embedded",{}).get("stash:files",[])
    by={f.get("path"):f for f in files}
    missing=[n for n in (README,ARCHIVE) if n not in by]
    if missing:
        raise RuntimeError(f"missing expected metadata objects {missing}")

    receipts={}
    recovered={}
    for name in (README,ARCHIVE):
        list_meta=by[name]
        fid=file_id(list_meta)
        detail=None
        detail_diag=None
        try:
            detail=jget(f"{API}/files/{fid}")
        except Exception as e:
            detail_diag=repr(e)

        urls=[]
        for src in (list_meta,detail or {}):
            urls.extend(collect_candidate_urls(src))
        urls += [
            f"{API}/files/{fid}/download",
            f"https://datadryad.org/stash/downloads/file_stream/{fid}",
        ]
        urls=list(dict.fromkeys(urls))

        attempts=[]
        body_ok=None
        via=None
        meta=detail if isinstance(detail,dict) and detail.get("size") else list_meta
        for url in urls:
            r=req(url)
            match=bool(r["ok"] and not html_payload(r) and exact_match(meta,r["body"]))
            attempts.append({
                "url":url,"status":r["status"],"final_url":r["final_url"],
                "content_type":str(r.get("headers",{}).get("Content-Type","")),
                "bytes":len(r["body"]),"html_payload":html_payload(r),
                "md5":hashlib.md5(r["body"]).hexdigest() if r["body"] else None,
                "exact_match":match,"reason":r.get("reason"),
            })
            if match:
                body_ok=r["body"]; via=url; break

        receipts[name]={
            "file_id":fid,
            "size":meta.get("size"),
            "digest_type":meta.get("digestType"),
            "digest":meta.get("digest"),
            "detail_metadata_available":detail is not None,
            "detail_metadata_error":detail_diag,
            "metadata_candidate_urls":urls,
            "recovered":body_ok is not None,
            "recovered_via":via,
            "attempts":attempts,
        }
        if body_ok is not None:
            recovered[name]=body_ok
            target=(a.out.parent/("iochrominae_README.txt" if name==README else "iochrominae_DATA.rar"))
            target.write_bytes(body_ok)

    all_ok=len(recovered)==2
    status=("SOURCE_BYTES_ACQUIRED_SCHEMA_INSPECTION_ALLOWED_PROFILE_UNCOMPUTED"
            if all_ok else "HOLD_DRYAD_SOURCE_BYTES_STILL_UNAVAILABLE_PROFILE_UNCOMPUTED")
    out={
        "version":"v0.3","source_doi":DOI,"status":status,
        "dataset_version_number":ds.get("versionNumber"),
        "objects":receipts,
        "all_exact_objects_recovered":all_ok,
        "archive_data_rows_opened":False,
        "archive_member_names_inspected":False,
        "profile_state_mapping_frozen":False,
        "profile_states_computed":False,
        "patristic_distances_computed":False,
        "profile_auc_computed":False,
        "winner_computed":False,
        "next_gate":("READ_README_AND_LIST_ARCHIVE_MEMBER_NAMES_ONLY"
                     if all_ok else "KEEP_SOURCE_HOLD"),
        "paper1_science_changed":False,
        "el_v0_3_science_changed":False,
    }
    a.out.write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({
        "status":status,
        "all_exact_objects_recovered":all_ok,
        "objects":{k:{"file_id":v["file_id"],"recovered":v["recovered"],
                      "candidate_urls":len(v["metadata_candidate_urls"])}
                   for k,v in receipts.items()}
    },indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
