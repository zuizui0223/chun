#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import time
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

ARTICLE_DOI="10.1016/j.ympev.2018.06.035"
TITLE="Evolution of floral traits and impact of reproductive mode on diversification in the phlox family (Polemoniaceae)"
GITHUB_REPO="jblandis/Polemoniaceae_family"
GITHUB_COMMIT="a91401cb188f44ef58a0bb6f2874bde1f60a57e7"
REQUIRED_TRAIT="Color.csv"
REQUIRED_TREE="MCC.fixed.nex"
UA="CHUN-Polemoniaceae-source-first/0.1"

QUERIES=[
    f'"{TITLE}"',
    ARTICLE_DOI,
    '"Polemoniaceae" "flower color"',
    '"Polemoniaceae" "floral traits" diversification',
    '"Color.csv" "MCC.fixed.nex"',
]

def fetch(url:str,accept:str="*/*")->bytes:
    last=None
    for attempt in range(5):
        req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":accept})
        try:
            with urllib.request.urlopen(req,timeout=60) as r:
                return r.read()
        except Exception as e:
            last=e
            if attempt==4:
                raise
            time.sleep(min(2**attempt,8))
    raise RuntimeError(str(last))

def jget(url:str)->dict:
    return json.loads(fetch(url,"application/json").decode("utf-8"))

def sha256(b:bytes)->str:
    return hashlib.sha256(b).hexdigest()

def md5(b:bytes)->str:
    return hashlib.md5(b).hexdigest()

def zenodo_search(q:str)->list[dict]:
    url="https://zenodo.org/api/records?"+urllib.parse.urlencode({"q":q,"size":50})
    x=jget(url)
    hits=((x.get("hits") or {}).get("hits") or [])
    return hits if isinstance(hits,list) else []

def record_text(rec:dict)->str:
    m=rec.get("metadata") or {}
    rel=m.get("related_identifiers") or []
    bits=[
        str(rec.get("id") or ""),
        str(m.get("title") or ""),
        str(m.get("description") or ""),
        str(m.get("doi") or ""),
        str(m.get("publication_date") or ""),
        json.dumps(rel,ensure_ascii=False),
    ]
    return "\n".join(bits).lower()

def file_rows(rec:dict)->list[dict]:
    out=[]
    for f in rec.get("files") or []:
        key=str(f.get("key") or "")
        links=f.get("links") or {}
        out.append({
            "key":key,
            "size":f.get("size"),
            "checksum":f.get("checksum"),
            "content_url":links.get("content") or links.get("self"),
        })
    return out

def source_link_score(rec:dict)->dict:
    txt=record_text(rec)
    title_tokens=("evolution of floral traits","reproductive mode","polemoniaceae")
    title_match=all(x in txt for x in title_tokens)
    doi_match=ARTICLE_DOI.lower() in txt
    return {
      "title_match":title_match,
      "article_doi_match":doi_match,
      "source_linked":bool(title_match or doi_match),
    }

def safe_archive_member_inventory(body:bytes,name:str)->list[str]:
    low=name.lower()
    if not (low.endswith(".zip") or body.startswith(b"PK\x03\x04")):
        return []
    try:
        with zipfile.ZipFile(io.BytesIO(body)) as z:
            return sorted(n for n in z.namelist() if not n.endswith("/"))
    except Exception:
        return []

def exact_download(f:dict)->tuple[bytes,dict]:
    url=f.get("content_url")
    if not url:
        raise RuntimeError("missing Zenodo content URL")
    body=fetch(url)
    checksum=str(f.get("checksum") or "").lower()
    check=None
    if checksum.startswith("md5:"):
        check=md5(body)==checksum.split(":",1)[1]
    elif checksum.startswith("sha256:") or checksum.startswith("sha-256:"):
        check=sha256(body)==checksum.split(":",1)[1]
    size=f.get("size")
    size_ok=None if size is None else int(size)==len(body)
    return body,{
      "bytes":len(body),
      "sha256":sha256(body),
      "md5":md5(body),
      "repository_checksum":checksum,
      "checksum_match":check,
      "repository_size":size,
      "size_match":size_ok,
    }

def code_contract()->dict:
    urls={
      "SIMMAP_Phytools.R":f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_COMMIT}/SIMMAP_Phytools.R",
      "MuSSE.R":f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_COMMIT}/MuSSE.R",
      "README.md":f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_COMMIT}/README.md",
    }
    out={}
    for name,u in urls.items():
        b=fetch(u,"text/plain,*/*")
        txt=b.decode("utf-8",errors="replace")
        lines=[]
        for i,s in enumerate(txt.splitlines(),1):
            low=s.lower()
            if (
                REQUIRED_TRAIT.lower() in low
                or REQUIRED_TREE.lower() in low
                or "non pigmented" in low
                or "anthocyanin" in low
                or "carotenoid" in low
                or "chlorophyll" in low
                or "data is coded as 0-3" in low
            ):
                lines.append({"line":i,"text":s[:600]})
        out[name]={
          "sha256":sha256(b),
          "evidence":lines[:100],
        }
    return out

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    a.out.parent.mkdir(parents=True,exist_ok=True)

    code=code_contract()
    seen={}
    qdiag=[]
    for q in QUERIES:
        try:
            hits=zenodo_search(q)
            qdiag.append({"query":q,"ok":True,"hits":len(hits)})
            for rec in hits:
                rid=str(rec.get("id") or "")
                if rid:
                    seen[rid]=rec
        except Exception as e:
            qdiag.append({"query":q,"ok":False,"error":f"{type(e).__name__}: {e}"})

    candidates=[]
    admitted=None
    for rid,rec in sorted(seen.items(),key=lambda kv:int(kv[0])):
        link=source_link_score(rec)
        files=file_rows(rec)
        row={
          "record_id":int(rid),
          "title":str((rec.get("metadata") or {}).get("title") or ""),
          "doi":str((rec.get("metadata") or {}).get("doi") or ""),
          **link,
          "files":[{k:v for k,v in f.items() if k!="content_url"} for f in files],
          "downloaded_files":[],
          "direct_required_files":[],
          "archive_required_members":[],
        }
        if not link["source_linked"]:
            candidates.append(row)
            continue

        # Only source-linked records may have bytes downloaded.
        for f in files:
            key=f["key"]
            lower=key.casefold()
            direct=Path(key).name.casefold() in {REQUIRED_TRAIT.casefold(),REQUIRED_TREE.casefold()}
            archive=Path(key).suffix.lower() in {".zip"}
            if not (direct or archive):
                continue
            try:
                body,diag=exact_download(f)
            except Exception as e:
                row["downloaded_files"].append({"key":key,"error":f"{type(e).__name__}: {e}"})
                continue
            emitted={"key":key,**diag}
            row["downloaded_files"].append(emitted)
            if diag["checksum_match"] is False or diag["size_match"] is False:
                continue
            if direct:
                row["direct_required_files"].append(key)
            if archive:
                members=safe_archive_member_inventory(body,key)
                matched=[n for n in members if Path(n).name.casefold() in {REQUIRED_TRAIT.casefold(),REQUIRED_TREE.casefold()}]
                if matched:
                    row["archive_required_members"].append({"archive":key,"matches":matched})

        found=set(Path(x).name.casefold() for x in row["direct_required_files"])
        for z in row["archive_required_members"]:
            found.update(Path(x).name.casefold() for x in z["matches"])
        row["has_trait_bytes"]=REQUIRED_TRAIT.casefold() in found
        row["has_tree_bytes"]=REQUIRED_TREE.casefold() in found
        if row["has_trait_bytes"] and row["has_tree_bytes"] and admitted is None:
            admitted={"record_id":row["record_id"],"title":row["title"],"found_required":sorted(found)}
        candidates.append(row)

    if admitted is not None:
        status="PASS_POLEMONIACEAE_SOURCE_FIRST_EXACT_TRAIT_TREE_FOUND"
    else:
        status="HOLD_POLEMONIACEAE_REQUIRED_TRAIT_TREE_BYTES_NOT_RECOVERED"

    out={
      "version":"v0.1",
      "status":status,
      "candidate":"POLEMONIACEAE",
      "candidate_order":3,
      "article_doi":ARTICLE_DOI,
      "article_title":TITLE,
      "author_github_repo":GITHUB_REPO,
      "author_github_commit":GITHUB_COMMIT,
      "author_code_contract":code,
      "required_trait_filename":REQUIRED_TRAIT,
      "required_tree_filename":REQUIRED_TREE,
      "pre_row_colour_schema":{
        "raw_codes":"0-3 per author code",
        "author_defined_states":["Non pigmented","Anthocyanin","Carotenoid","Chlorophyll"],
        "nested_hierarchy":"NONPIGMENTED versus PIGMENTED, with anthocyanin/carotenoid/chlorophyll as fine pigmented states",
        "mapping_evidence_opened_from_author_code_only":True,
      },
      "zenodo_queries":qdiag,
      "zenodo_records_considered":len(seen),
      "candidate_records":candidates,
      "admitted_source_record":admitted,
      "outcome_firewall":{
        "species_level_Color_csv_rows_opened":False,
        "colour_state_frequencies_computed":False,
        "tree_tip_labels_emitted":False,
        "hidden_memory_auc_computed":False,
      },
      "next_gate":"STOP_SCREEN_AND_ADMIT_POLEMONIACEAE" if admitted else "CONTINUE_SOURCE_FIRST_SCREEN_IF_BUDGET_REMAINS",
      "paper1_science_changed":False,
      "el_v0_3_science_changed":False
    }
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
      "status":status,
      "zenodo_records_considered":len(seen),
      "queries":qdiag,
      "admitted_source_record":admitted,
      "source_linked_records":[
        {"id":x["record_id"],"title":x["title"],"trait":x.get("has_trait_bytes"),"tree":x.get("has_tree_bytes")}
        for x in candidates if x["source_linked"]
      ],
    },indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
