#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

EXPECTED_NAME="R codes and data from Evolution #15-0052.zip"
EXPECTED_BYTES=1689978
EXPECTED_MD5="56003177c0bf87981e1afd0b24138461"
DRYAD_DOI="10.5061/dryad.rv08g"
FILE_ID=89978
UA="CHUN-Erysimum-exact-recovery/0.1"

DRYAD_ROUTES=[
    f"https://datadryad.org/api/v2/files/{FILE_ID}/download",
    f"https://datadryad.org/stash/downloads/file_stream/{FILE_ID}",
    f"https://datadryad.org/downloads/file_stream/{FILE_ID}",
]

def fetch(url:str,accept:str="*/*")->dict:
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":accept})
    try:
        with urllib.request.urlopen(req,timeout=120) as r:
            body=r.read()
            return {
                "ok":True,"status":getattr(r,"status",200),"final_url":r.geturl(),
                "headers":dict(r.headers),"body":body
            }
    except Exception as e:
        code=getattr(e,"code",None)
        return {"ok":False,"status":code,"final_url":url,"headers":{},"body":b"","error":f"{type(e).__name__}: {e}"}

def md5(b:bytes)->str:
    return hashlib.md5(b).hexdigest()

def exact(b:bytes)->bool:
    return len(b)==EXPECTED_BYTES and md5(b)==EXPECTED_MD5

def json_fetch(url:str)->tuple[object,dict]:
    r=fetch(url,"application/json,*/*")
    if not r["ok"]:
        return None,{k:v for k,v in r.items() if k!="body"}
    try:
        return json.loads(r["body"].decode("utf-8")),{k:v for k,v in r.items() if k!="body"}
    except Exception as e:
        d={k:v for k,v in r.items() if k!="body"}
        d["json_error"]=f"{type(e).__name__}: {e}"
        return None,d

def wayback_urls()->tuple[list[str],list[dict]]:
    targets=[
        f"datadryad.org/api/v2/files/{FILE_ID}/download",
        f"datadryad.org/stash/downloads/file_stream/{FILE_ID}",
        f"datadryad.org/downloads/file_stream/{FILE_ID}",
        f"datadryad.org/*{FILE_ID}*",
    ]
    snapshots=[]
    diags=[]
    for target in targets:
        q=urllib.parse.urlencode({
            "url":target,
            "output":"json",
            "filter":"statuscode:200",
            "collapse":"digest",
            "fl":"timestamp,original,statuscode,mimetype,digest,length",
        })
        url="https://web.archive.org/cdx/search/cdx?"+q
        x,d=json_fetch(url); d["target"]=target; diags.append(d)
        if not isinstance(x,list) or len(x)<2:
            continue
        head=x[0]
        for row in x[1:]:
            if not isinstance(row,list) or len(row)!=len(head):
                continue
            rec=dict(zip(head,row))
            ts=rec.get("timestamp"); orig=rec.get("original")
            if ts and orig:
                snapshots.append(f"https://web.archive.org/web/{ts}id_/{orig}")
    return list(dict.fromkeys(snapshots)),diags

def zenodo_urls()->tuple[list[str],list[dict]]:
    queries=[
        f'"{EXPECTED_NAME}"',
        f'"{DRYAD_DOI}"',
        f'"{EXPECTED_MD5}"',
        "Erysimum pollinators floral diversification Gomez Perfectti Lorite 2015",
    ]
    urls=[]
    diags=[]
    for q0 in queries:
        q=urllib.parse.urlencode({"q":q0,"size":100})
        api="https://zenodo.org/api/records?"+q
        x,d=json_fetch(api); d["query"]=q0; diags.append(d)
        if not isinstance(x,dict):
            continue
        hits=((x.get("hits") or {}).get("hits") or [])
        for hit in hits:
            for f in hit.get("files",[]) or []:
                key=str(f.get("key") or "")
                checksum=str(f.get("checksum") or "").lower()
                size=f.get("size")
                if (
                    key==EXPECTED_NAME
                    or EXPECTED_MD5 in checksum
                    or (size==EXPECTED_BYTES and key.lower().endswith(".zip"))
                ):
                    links=f.get("links") or {}
                    for k in ("content","self"):
                        u=links.get(k)
                        if u: urls.append(u)
    return list(dict.fromkeys(urls)),diags

def try_urls(urls:list[str],source:str)->tuple[bytes|None,str|None,list[dict]]:
    attempts=[]
    for u in urls:
        r=fetch(u)
        body=r["body"]
        row={k:v for k,v in r.items() if k!="body"}
        row.update({
            "source":source,
            "bytes":len(body),
            "md5":md5(body) if body else None,
            "exact_size_and_md5":exact(body) if body else False,
        })
        attempts.append(row)
        if body and exact(body):
            return body,r["final_url"],attempts
    return None,None,attempts

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--exact-out",type=Path,required=True)
    a=ap.parse_args()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.exact_out.parent.mkdir(parents=True,exist_ok=True)

    all_attempts=[]
    body,url,att=try_urls(DRYAD_ROUTES,"dryad_current")
    all_attempts.extend(att)

    wb_diags=[]; zen_diags=[]
    if body is None:
        wb_urls,wb_diags=wayback_urls()
        body,url,att=try_urls(wb_urls,"wayback")
        all_attempts.extend(att)
    else:
        wb_urls=[]

    if body is None:
        zen_urls,zen_diags=zenodo_urls()
        body,url,att=try_urls(zen_urls,"zenodo")
        all_attempts.extend(att)
    else:
        zen_urls=[]

    if body is not None:
        a.exact_out.write_bytes(body)
        status="ERYSIMUM_EXACT_PACKAGE_RECOVERED"
        next_gate="RUN_SOURCE_ARCHIVE_SCHEMA_INVENTORY"
    else:
        status="HOLD_ERYSIMUM_EXACT_PACKAGE_NO_IDENTITY_VERIFIED_MIRROR"
        next_gate="STOP_HOLD"

    out={
      "version":"v0.1",
      "status":status,
      "frozen_identity":{
        "dataset_doi":DRYAD_DOI,
        "file_id":FILE_ID,
        "filename":EXPECTED_NAME,
        "bytes":EXPECTED_BYTES,
        "md5":EXPECTED_MD5,
      },
      "recovered_url":url,
      "recovered_path":str(a.exact_out) if body is not None else None,
      "dryad_routes":DRYAD_ROUTES,
      "wayback_candidate_urls":wb_urls,
      "zenodo_candidate_urls":zen_urls,
      "attempts":all_attempts,
      "wayback_diagnostics":wb_diags,
      "zenodo_diagnostics":zen_diags,
      "outcome_firewall":{
        "archive_member_names_opened":False,
        "author_code_opened":False,
        "trait_rows_opened":False,
        "species_level_colour_values_opened":False,
        "tree_tip_labels_opened":False,
        "hidden_memory_auc_computed":False,
      },
      "next_gate":next_gate,
      "paper1_science_changed":False,
      "el_v0_3_science_changed":False,
    }
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
      "status":status,
      "recovered_url":url,
      "attempt_count":len(all_attempts),
      "wayback_candidates":len(wb_urls),
      "zenodo_candidates":len(zen_urls),
      "attempts":all_attempts,
    },indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
