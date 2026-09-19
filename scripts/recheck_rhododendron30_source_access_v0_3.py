#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import http.cookiejar
import io
import json
import re
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from Bio import Phylo

TRAIT_DOI="10.1111/plb.12649"
TABLE_S3="plb12649-sup-0002-TableS3.docx"
ARTICLE_URL="https://onlinelibrary.wiley.com/doi/10.1111/plb.12649"
TREE_DOI="10.5061/dryad.8cz8w9grq"
TREE_FILE="1_WP_RAxML.tre"
TREE_FILE_ID=1853438
TREE_SHA256="784011d0e2e17df9ea21eb22d31197bad29219a37ac213fda013766e29b51362"
UA="Mozilla/5.0 CHUN-Rhododendron30-source-recheck/0.3"
W="{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def norm(x:str)->str:
    return re.sub(r"\s+"," ",str(x).strip().replace("_"," ")).lower()


def opener():
    jar=http.cookiejar.CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))


def request(op,url,accept="*/*",referer=None,timeout=90):
    headers={"User-Agent":UA,"Accept":accept,"Accept-Language":"en-US,en;q=0.9"}
    if referer:
        headers["Referer"]=referer
    req=urllib.request.Request(url,headers=headers)
    try:
        with op.open(req,timeout=timeout) as r:
            return {
                "ok":True,"status":getattr(r,"status",200),"final_url":r.geturl(),
                "headers":dict(r.headers),"body":r.read()
            }
    except urllib.error.HTTPError as e:
        try:
            body=e.read()
        except Exception:
            body=b""
        return {
            "ok":False,"status":e.code,"final_url":e.geturl(),
            "headers":dict(e.headers or {}),"body":body,"reason":str(e.reason)
        }
    except Exception as e:
        return {"ok":False,"status":None,"final_url":url,"headers":{},"body":b"","reason":repr(e)}


def valid_docx_bytes(body:bytes)->bool:
    if len(body)<4 or body[:2]!=b"PK":
        return False
    try:
        with zipfile.ZipFile(io.BytesIO(body)) as z:
            names=set(z.namelist())
            return "[Content_Types].xml" in names and "word/document.xml" in names
    except Exception:
        return False


def first_column_species(body:bytes):
    if not valid_docx_bytes(body):
        raise ValueError("not a DOCX")
    with zipfile.ZipFile(io.BytesIO(body)) as z:
        root=ET.fromstring(z.read("word/document.xml"))
    species=[]
    preview=[]
    for tr in root.iter(W+"tr"):
        cells=list(tr.findall(W+"tc"))
        if not cells:
            continue
        txt="".join((t.text or "") for t in cells[0].iter(W+"t")).strip()
        if len(preview)<10:
            preview.append(txt)
        if re.match(r"^Rhododendron\b",txt,re.I):
            species.append(txt)
    return species,preview


def validate_tree_payload(body:bytes,content_type:str|None,expected_sha256:str)->dict:
    got=hashlib.sha256(body).hexdigest()
    ctype=(content_type or "").lower()
    treeish=(
        len(body)>10 and
        b"(" in body and b")" in body and b";" in body and
        "html" not in ctype and not body.lstrip().lower().startswith(b"<!doctype html")
    )
    return {
        "downloaded_bytes":len(body),
        "sha256":got,
        "digest_match":got.lower()==expected_sha256.lower(),
        "treeish_payload":bool(treeish),
        "content_type":content_type,
    }


def _collect_urls(x):
    out=[]
    if isinstance(x,str):
        if x.startswith("http://") or x.startswith("https://"):
            out.append(x)
    elif isinstance(x,dict):
        for v in x.values():
            out.extend(_collect_urls(v))
    elif isinstance(x,list):
        for v in x:
            out.extend(_collect_urls(v))
    return out


def dryad_candidate_urls(file_id:int,metadata:dict)->list[str]:
    urls=[
        f"https://datadryad.org/api/v2/files/{file_id}/download",
        f"https://datadryad.org/stash/downloads/file_stream/{file_id}",
    ]
    for u in _collect_urls(metadata):
        lu=u.lower()
        if str(file_id) in u and ("download" in lu or "file_stream" in lu):
            urls.append(u)
    return list(dict.fromkeys(urls))


def decide_status(trait_ready:bool,tree_ready:bool,crosswalk_matches:int)->str:
    if not trait_ready or not tree_ready:
        return "HOLD_SOURCE_ACCESS_STILL_BLOCKED_OUTCOMES_UNOPENED"
    if crosswalk_matches<20:
        return "HOLD_CROSSWALK_OR_TREE_COVERAGE_OUTCOMES_UNOPENED"
    return "SOURCE_ACCESS_AND_CROSSWALK_PASS_CHEMISTRY_STILL_UNOPENED"


def wiley_urls():
    qdoi=urllib.parse.quote(TRAIT_DOI,safe="")
    qfile=urllib.parse.quote(TABLE_S3,safe="")
    return [
        f"https://onlinelibrary.wiley.com/action/downloadSupplement?doi={qdoi}&file={qfile}",
        f"https://onlinelibrary.wiley.com/action/downloadSupplement?doi={TRAIT_DOI}&file={TABLE_S3}",
        f"https://onlinelibrary.wiley.com/doi/suppl/{TRAIT_DOI}/supinfo/{TABLE_S3}",
        f"https://onlinelibrary.wiley.com/doi/supinfo/{TRAIT_DOI}/supinfo/{TABLE_S3}",
        f"https://onlinelibrary.wiley.com/doi/suppl/{TRAIT_DOI}/suppinfo/{TABLE_S3}",
    ]


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    op=opener()

    outcome_firewall={
        "table_s1_chemistry_downloaded":False,
        "row_level_anthocyanin_values_accessed":False,
        "flower_colour_values_accessed":False,
        "CIELAB_values_accessed":False,
        "compound_presence_states_computed":False,
        "state_frequencies_computed":False,
        "AUC_computed":False,
        "winner_computed":False,
    }

    # Species identity only: exact Table S3, first column only.
    landing=request(op,ARTICLE_URL,"text/html")
    discovered=[]
    if landing["body"]:
        text=landing["body"].decode("utf-8","replace")
        for m in re.finditer(r'href=["\']([^"\']*'+re.escape(TABLE_S3)+r'[^"\']*)["\']',text,re.I):
            discovered.append(urllib.parse.urljoin(landing.get("final_url") or ARTICLE_URL,m.group(1)))
    trait_attempts=[]
    trait_body=None
    trait_species=[]
    first_preview=[]
    for url in list(dict.fromkeys(discovered+wiley_urls())):
        r=request(op,url,"application/vnd.openxmlformats-officedocument.wordprocessingml.document,*/*",ARTICLE_URL)
        is_docx=bool(r["ok"] and valid_docx_bytes(r["body"]))
        rec={
            "url":url,"http_status":r.get("status"),"final_url":r.get("final_url"),
            "content_type":r.get("headers",{}).get("Content-Type"),
            "downloaded_bytes":len(r["body"]),
            "sha256":hashlib.sha256(r["body"]).hexdigest() if r["body"] else None,
            "is_docx_payload":is_docx,"reason":r.get("reason")
        }
        trait_attempts.append(rec)
        if is_docx:
            trait_body=r["body"]
            trait_species,first_preview=first_column_species(trait_body)
            break
    trait_ready=trait_body is not None and len({norm(x) for x in trait_species})==30

    # Dryad exact tree metadata.
    meta_resp=request(op,f"https://datadryad.org/api/v2/files/{TREE_FILE_ID}","application/json")
    metadata={}
    if meta_resp["ok"]:
        try:
            metadata=json.loads(meta_resp["body"].decode("utf-8"))
        except Exception:
            metadata={}

    tree_attempts=[]
    tree_body=None
    for url in dryad_candidate_urls(TREE_FILE_ID,metadata):
        r=request(op,url,"*/*",f"https://datadryad.org/dataset/doi%3A10.5061%2Fdryad.8cz8w9grq")
        valid=validate_tree_payload(r["body"],r.get("headers",{}).get("Content-Type"),TREE_SHA256)
        rec={
            "url":url,"http_status":r.get("status"),"final_url":r.get("final_url"),
            "reason":r.get("reason"),**valid
        }
        tree_attempts.append(rec)
        if valid["digest_match"] and valid["treeish_payload"]:
            tree_body=r["body"]
            break

    tree_ready=tree_body is not None
    tips=[]
    all_bl=False
    duplicate_tips=None
    if tree_ready:
        tree=Phylo.read(io.StringIO(tree_body.decode("utf-8-sig")),"newick")
        tips=[str(t.name) for t in tree.get_terminals()]
        normalized=[norm(x) for x in tips]
        duplicate_tips=len(normalized)-len(set(normalized))
        branches=[c.branch_length for c in tree.find_clades() if c is not tree.root]
        all_bl=bool(branches) and all(v is not None for v in branches)
        if duplicate_tips!=0 or not all_bl:
            tree_ready=False

    ts={norm(x):x for x in trait_species}
    tt={norm(x):x for x in tips}
    matched=sorted(set(ts)&set(tt))
    status=decide_status(trait_ready,tree_ready,len(matched))
    decision=(
        "OPEN_NEXT_GATE_FREEZE_EXACT_SOURCE_HASHES_AND_CROSSWALK_BEFORE_TABLE_S1_CHEMISTRY"
        if status=="SOURCE_ACCESS_AND_CROSSWALK_PASS_CHEMISTRY_STILL_UNOPENED"
        else "STOP_HOLD_DO_NOT_OPEN_TABLE_S1_CHEMISTRY"
    )

    out={
        "version":"v0.3",
        "status":status,
        "trait_source":{
            "doi":TRAIT_DOI,"file":TABLE_S3,
            "article_landing_http_status":landing.get("status"),
            "attempts":trait_attempts,
            "genuine_docx_recovered":trait_body is not None,
            "species_identifiers_recovered":len(ts),
            "first_column_preview_only":first_preview,
            "sha256":hashlib.sha256(trait_body).hexdigest() if trait_body else None,
        },
        "primary_tree":{
            "doi":TREE_DOI,"file":TREE_FILE,"file_id":TREE_FILE_ID,
            "expected_sha256":TREE_SHA256,
            "metadata_http_status":meta_resp.get("status"),
            "metadata":metadata,
            "attempts":tree_attempts,
            "recovered":tree_body is not None,
            "tip_count":len(tips),
            "duplicate_normalized_tips":duplicate_tips,
            "all_nonroot_branch_lengths_present":all_bl,
        },
        "crosswalk":{
            "automatic_synonym_substitution":False,
            "trait_species_count":len(ts),
            "tree_tip_count":len(tt),
            "exact_normalized_matches":len(matched),
            "matched_normalized":matched,
            "trait_only_normalized":sorted(set(ts)-set(tt)) if tips else sorted(set(ts)),
            "tree_only_normalized_restricted_report":sorted(set(tt)-set(ts))[:200] if trait_species else [],
        },
        "outcome_firewall":outcome_firewall,
        "chemistry_opened":False,
        "profile_auc_computed":False,
        "decision":decision,
        "paper1_science_changed":False,
        "el_v0_3_science_changed":False,
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
    if trait_body:
        (args.out.parent/TABLE_S3).write_bytes(trait_body)
    if tree_body:
        (args.out.parent/TREE_FILE).write_bytes(tree_body)
    print(json.dumps({
        "status":status,
        "trait_ready":trait_ready,
        "trait_species_count":len(ts),
        "trait_http":[x["http_status"] for x in trait_attempts],
        "tree_ready":tree_ready,
        "tree_attempts":[{"http":x["http_status"],"digest_match":x["digest_match"],"treeish":x["treeish_payload"],"url":x["url"]} for x in tree_attempts],
        "tree_tips":len(tips),
        "crosswalk_matches":len(matched),
        "decision":decision,
        "outcome_firewall":outcome_firewall,
    },indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
