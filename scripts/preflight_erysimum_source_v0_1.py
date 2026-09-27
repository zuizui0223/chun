#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

from Bio import Phylo

DOI="10.5061/dryad.rv08g"
DOI_ENC=urllib.parse.quote("doi:"+DOI,safe="")
PACKAGE="R codes and data from Evolution #15-0052.zip"
UA="CHUN-Erysimum-source-inventory/0.1"

DATASET_API_CANDIDATES=[
    f"https://datadryad.org/api/v2/datasets/{DOI_ENC}",
    f"https://datadryad.org/api/v2/datasets/doi%3A10.5061%2Fdryad.rv08g",
]
LANDING=f"https://datadryad.org/dataset/doi:{DOI}"

TREE_EXT={".tre",".tree",".nex",".nexus",".nwk",".newick"}
CODE_EXT={".r",".rmd",".txt"}

def fetch(url:str,accept:str="*/*")->tuple[bytes,str,dict]:
    last=None
    for attempt in range(5):
        req=urllib.request.Request(url,headers={
            "User-Agent":UA,
            "Accept":accept,
            "Referer":LANDING,
        })
        try:
            with urllib.request.urlopen(req,timeout=120) as r:
                return r.read(),r.geturl(),dict(r.headers)
        except urllib.error.HTTPError as e:
            last=e
            if e.code not in {429,500,502,503,504} or attempt==4:
                raise
        except Exception as e:
            last=e
            if attempt==4:
                raise
        time.sleep(min(2**attempt,8))
    raise RuntimeError(str(last))

def get_json(url:str)->tuple[dict,str]:
    b,u,_=fetch(url,"application/json,*/*")
    return json.loads(b.decode("utf-8")),u

def sha256(b:bytes)->str:
    return hashlib.sha256(b).hexdigest()

def md5(b:bytes)->str:
    return hashlib.md5(b).hexdigest()

def collect_urls(obj)->list[str]:
    out=[]
    if isinstance(obj,dict):
        for v in obj.values():
            out.extend(collect_urls(v))
    elif isinstance(obj,list):
        for v in obj:
            out.extend(collect_urls(v))
    elif isinstance(obj,str) and obj.startswith(("http://","https://","/")):
        out.append(obj)
    return out

def absolute_dryad(url:str)->str:
    return urllib.parse.urljoin("https://datadryad.org",url)

def resolve_file_inventory()->tuple[list[dict],dict]:
    diagnostics={"dataset_attempts":[],"file_list_attempts":[]}
    dataset=None
    dataset_url=None
    for u in DATASET_API_CANDIDATES:
        try:
            x,final=get_json(u)
            diagnostics["dataset_attempts"].append({"url":u,"ok":True,"final_url":final})
            dataset=x; dataset_url=final
            break
        except Exception as e:
            diagnostics["dataset_attempts"].append({"url":u,"ok":False,"error":f"{type(e).__name__}: {e}"})
    if dataset is None:
        raise RuntimeError("Dryad dataset metadata unavailable")

    urls=[absolute_dryad(u) for u in collect_urls(dataset)]
    # Prefer explicit version/file links exposed by the API.
    candidates=[]
    for u in urls:
        low=u.lower()
        if "/files" in low or "/versions/" in low:
            candidates.append(u)
    # Known API shapes recovered from dataset/version metadata.
    version_ids=[]
    for u in urls:
        m=re.search(r"/versions/(\d+)",u)
        if m:
            version_ids.append(m.group(1))
    for vid in sorted(set(version_ids)):
        candidates += [
            f"https://datadryad.org/api/v2/versions/{vid}/files",
            f"https://datadryad.org/api/v2/versions/{vid}",
        ]

    seen=set()
    queue=[]
    for u in candidates:
        if u not in seen:
            queue.append(u); seen.add(u)
    inventories=[]
    visited=0
    while queue and visited<20:
        u=queue.pop(0); visited+=1
        try:
            x,final=get_json(u)
            diagnostics["file_list_attempts"].append({"url":u,"ok":True,"final_url":final})
        except Exception as e:
            diagnostics["file_list_attempts"].append({"url":u,"ok":False,"error":f"{type(e).__name__}: {e}"})
            continue
        objs=[]
        if isinstance(x,list):
            objs=x
        elif isinstance(x,dict):
            for key in ("_embedded","files","stash:files"):
                v=x.get(key)
                if isinstance(v,list): objs.extend(v)
                elif isinstance(v,dict):
                    for vv in v.values():
                        if isinstance(vv,list): objs.extend(vv)
            # Some endpoints return one file object directly.
            if any(k in x for k in ("path","filename","file_name")):
                objs.append(x)
        for o in objs:
            if not isinstance(o,dict):
                continue
            name=o.get("path") or o.get("filename") or o.get("file_name") or o.get("name")
            if name:
                inventories.append(o)
        for nxt in collect_urls(x):
            au=absolute_dryad(nxt)
            if ("/files" in au.lower() or "/versions/" in au.lower()) and au not in seen:
                queue.append(au); seen.add(au)
    diagnostics["dataset_url"]=dataset_url
    return inventories,diagnostics

def file_name(o:dict)->str:
    return str(o.get("path") or o.get("filename") or o.get("file_name") or o.get("name") or "")

def file_download_url(o:dict)->str|None:
    # Search nested metadata for URLs that look like a file content/download endpoint.
    urls=[absolute_dryad(u) for u in collect_urls(o)]
    ranked=[]
    for u in urls:
        low=u.lower()
        score=0
        if "download" in low or "file_stream" in low: score+=3
        if "/files/" in low: score+=2
        if "api/v2/files/" in low: score+=2
        ranked.append((score,u))
    ranked.sort(reverse=True)
    if ranked and ranked[0][0]>0:
        return ranked[0][1]
    # Fall back to file id if exposed.
    fid=o.get("id") or o.get("file_id")
    if fid:
        return f"https://datadryad.org/api/v2/files/{fid}/download"
    return None

def metadata_digest(o:dict)->dict:
    vals={}
    for k,v in o.items():
        lk=str(k).lower()
        if "digest" in lk or lk in {"md5","sha256","checksum"}:
            vals[str(k)]=v
    return vals

def verify_against_metadata(body:bytes,o:dict)->dict:
    size=o.get("size") or o.get("file_size") or o.get("bytes")
    dig=metadata_digest(o)
    checks=[]
    for k,v in dig.items():
        s=str(v).strip().lower()
        if ":" in s:
            algo,hexv=s.split(":",1)
        else:
            algo,hexv="",s
        if algo in {"md5",""} and re.fullmatch(r"[0-9a-f]{32}",hexv):
            checks.append({"field":k,"expected":s,"observed":"md5:"+md5(body),"match":md5(body)==hexv})
        elif algo in {"sha-256","sha256",""} and re.fullmatch(r"[0-9a-f]{64}",hexv):
            checks.append({"field":k,"expected":s,"observed":"sha256:"+sha256(body),"match":sha256(body)==hexv})
    size_match=None if size is None else int(size)==len(body)
    digest_match=True if not checks else all(x["match"] for x in checks)
    return {"metadata_size":size,"size_match":size_match,"digest_checks":checks,"digest_match":digest_match}

def archive_inventory(body:bytes)->list[dict]:
    with zipfile.ZipFile(io.BytesIO(body)) as z:
        return [
            {"path":n,"bytes":z.getinfo(n).file_size,"ext":Path(n).suffix.lower()}
            for n in z.namelist() if not n.endswith("/")
        ]

def code_evidence(body:bytes)->list[dict]:
    evidence=[]
    with zipfile.ZipFile(io.BytesIO(body)) as z:
        for n in z.namelist():
            if n.endswith("/") or Path(n).suffix.lower() not in CODE_EXT:
                continue
            try:
                raw=z.read(n)
                txt=raw.decode("utf-8",errors="replace")
            except Exception:
                continue
            hits=[]
            for i,line in enumerate(txt.splitlines(),1):
                low=line.lower()
                if (
                    "corolla" in low and ("color" in low or "colour" in low)
                    or "yellow" in low or "lilac" in low or "white" in low
                    or "read.tree" in low or "read.nexus" in low
                    or "ape::read" in low
                    or "read.csv" in low or "read.table" in low
                ):
                    hits.append({"line":i,"text":line[:500]})
            if hits:
                evidence.append({"path":n,"hits":hits[:100]})
    return evidence

def tree_candidates(body:bytes)->list[dict]:
    out=[]
    with zipfile.ZipFile(io.BytesIO(body)) as z:
        for n in z.namelist():
            if n.endswith("/") or Path(n).suffix.lower() not in TREE_EXT:
                continue
            b=z.read(n)
            meta={"path":n,"bytes":len(b),"sha256":sha256(b),"parse_status":"UNPARSED"}
            for fmt in ("newick","nexus"):
                try:
                    tree=Phylo.read(io.StringIO(b.decode("utf-8-sig",errors="strict")),fmt)
                    tips=tree.get_terminals()
                    branches=[c.branch_length for c in tree.find_clades() if c is not tree.root]
                    meta.update({
                        "parse_status":"READY",
                        "format":fmt,
                        "tip_count":len(tips),
                        "duplicate_tip_labels":len(tips)-len({str(t.name or "").strip() for t in tips}),
                        "missing_nonroot_branch_lengths":sum(x is None for x in branches),
                        "negative_nonroot_branch_lengths":sum(x is not None and x<0 for x in branches),
                    })
                    break
                except Exception:
                    pass
            out.append(meta)
    return out

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--stage",type=Path,required=True)
    a=ap.parse_args()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.stage.parent.mkdir(parents=True,exist_ok=True)

    try:
        inventory,diagnostics=resolve_file_inventory()
    except Exception as e:
        out={
          "version":"v0.1","status":"HOLD_ERYSIMUM_DRYAD_METADATA_UNAVAILABLE",
          "error":f"{type(e).__name__}: {e}",
          "outcome_firewall":{"archive_downloaded":False,"trait_rows_opened":False,"colour_values_opened":False,"tree_tip_labels_emitted":False},
          "next_gate":"STOP_HOLD","paper1_science_changed":False,"el_v0_3_science_changed":False
        }
        a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n"); print(json.dumps(out,indent=2)); return 0

    matches=[o for o in inventory if file_name(o)==PACKAGE]
    if len(matches)!=1:
        out={
          "version":"v0.1","status":"HOLD_ERYSIMUM_EXACT_PACKAGE_METADATA_NOT_UNIQUE",
          "package_matches":[{"name":file_name(o),"metadata":o} for o in matches],
          "diagnostics":diagnostics,
          "outcome_firewall":{"archive_downloaded":False,"trait_rows_opened":False,"colour_values_opened":False,"tree_tip_labels_emitted":False},
          "next_gate":"STOP_HOLD","paper1_science_changed":False,"el_v0_3_science_changed":False
        }
        a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n"); print(json.dumps({"status":out["status"],"n_matches":len(matches)},indent=2)); return 0

    obj=matches[0]
    url=file_download_url(obj)
    if not url:
        raise RuntimeError("no Dryad package download URL")
    body,final_url,headers=fetch(url)
    check=verify_against_metadata(body,obj)
    if check["size_match"] is False or not check["digest_match"] or not body.startswith(b"PK\x03\x04"):
        status="HOLD_ERYSIMUM_PACKAGE_IDENTITY_VERIFICATION_FAILED"
    else:
        status="ERYSIMUM_EXACT_PACKAGE_READY_PRE_SCHEMA_FREEZE"
        a.stage.write_bytes(body)

    members=archive_inventory(body) if body.startswith(b"PK\x03\x04") else []
    codes=code_evidence(body) if body.startswith(b"PK\x03\x04") else []
    trees=tree_candidates(body) if body.startswith(b"PK\x03\x04") else []
    out={
      "version":"v0.1",
      "status":status,
      "dataset_doi":DOI,
      "package":{
        "filename":PACKAGE,
        "metadata":obj,
        "download_url":final_url,
        "bytes":len(body),
        "sha256":sha256(body),
        "md5":md5(body),
        "identity_check":check,
      },
      "archive_members":members,
      "author_code_evidence":codes,
      "tree_candidates":trees,
      "outcome_firewall":{
        "archive_downloaded":True,
        "archive_member_names_opened":True,
        "author_code_opened":True,
        "trait_data_rows_opened":False,
        "species_level_colour_values_opened":False,
        "colour_state_frequencies_computed":False,
        "tree_tip_labels_emitted":False,
        "hidden_memory_auc_computed":False,
      },
      "next_gate":"FREEZE_AUTHOR_REFERENCED_TRAIT_TREE_AND_COLOUR_SCHEMA" if status=="ERYSIMUM_EXACT_PACKAGE_READY_PRE_SCHEMA_FREEZE" else "STOP_HOLD",
      "diagnostics":diagnostics,
      "paper1_science_changed":False,
      "el_v0_3_science_changed":False
    }
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
      "status":status,
      "package_bytes":len(body),
      "identity_check":check,
      "archive_member_count":len(members),
      "tree_candidates":trees,
      "code_evidence_files":[x["path"] for x in codes],
    },indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
