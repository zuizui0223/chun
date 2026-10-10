#!/usr/bin/env python3
"""Metadata-first phylogenomic-tree source audit for Erica (Musker et al. 2025).

Published source DOI 10.25375/uct.27134208. This 2025 phylogenomic
sample is independent of the 2016 and 2024 Erica phylogenetic sources.
A downloaded tree is *not* a species/taxon match or valid memory estimate.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import urllib.parse
import urllib.request
import zipfile

ARTICLE_ID=27134208
DOI="10.25375/uct.27134208"
API=f"https://api.figshare.com/v2/articles/{ARTICLE_ID}"
MAX_BYTES=15_000_000
TREE_SUFFIXES={".nwk",".newick",".nex",".nexus",".tre",".tree",".treefile"}
SOURCE_HINTS=("tree","phylo","astral","iqtree","source","data","supplement","archive")


def candidates(article:dict)->list[dict]:
    if article.get("id")!=ARTICLE_ID:
        raise ValueError("different Figshare article id")
    all_dois=json.dumps({"doi":article.get("doi"),
                         "related_material":article.get("related_material",[]),
                         "references":article.get("references",[])})
    if DOI.lower() not in all_dois.lower():
        raise ValueError("record DOI/source identity mismatch")
    found=[]
    for f in article.get("files",[]):
        name=str(f.get("name",""))
        if not name:
            raise ValueError("unnamed attached file")
        ext=Path(name).suffix.lower()
        hits=[s for s in SOURCE_HINTS if s in name.lower()]
        chosen=bool(ext in TREE_SUFFIXES or ext==".zip" or hits)
        url=f.get("download_url")
        host=urllib.parse.urlparse(url or "").hostname
        available=bool(chosen and f.get("size",0)<=MAX_BYTES and f.get("size",0)>0
                       and url and host
                       and (host.endswith(".figshare.com") or host=="figshare.com"))
        found.append({"name":name,"size":f.get("size"),"id":f.get("id"),
                      "advertised_md5":f.get("computed_md5"),
                      "extension":ext,"possible_tree_source":chosen,
                      "bounded_safe_download":available,
                      "download_url":url})
    return found


def zip_members(raw:bytes)->list[dict]:
    if not raw.startswith(b"PK"):
        raise ValueError("not ZIP data")
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        if z.testzip() is not None:
            raise ValueError("ZIP member CRC mismatch")
        out=[]
        for f in z.infolist():
            if f.is_dir():continue
            if f.file_size>25_000_000:
                raise ValueError("oversized archive member")
            name=f.filename
            out.append({"filename":name,"size":f.file_size,
                        "tree_file_candidate":Path(name).suffix.lower() in TREE_SUFFIXES})
        return out


def get(url,*,timeout,urlopen=None,maxsize=MAX_BYTES):
    urlopen=urlopen or urllib.request.urlopen
    req=urllib.request.Request(url,headers={
        "User-Agent":"CHUN-Erica-phylogenomics-source-only/0.1",
        "Accept":"application/json,application/zip,application/octet-stream,*/*"})
    with urlopen(req,timeout=timeout) as r:
        if getattr(r,"status",200)!=200:raise ValueError("HTTP non-200")
        raw=r.read(maxsize+1)
    if len(raw)>maxsize:raise ValueError("source exceeds size ceiling")
    return raw


def run(timeout:int=20,urlopen=None):
    receipt={"version":"v0.1","target_article_id":ARTICLE_ID,"expected_doi":DOI,
             "status":"HOLD_PHYLOGENOMIC_SOURCE_METADATA_UNAVAILABLE",
             "actual_file_bytes_verified":False,
             "selected_phylogeny":False,
             "same_taxa_expression_tree_join_verified":False,
             "original_2016_and_2024_tree_distinction_maintained":True,
             "observed_sequenced_tips_only_unverified":True,
             "independent_memory_test_performed":False,
             "frozen_AJB_EL_unchanged":True}
    payloads={}
    try:
        a=json.loads(get(API,timeout=timeout,urlopen=urlopen,maxsize=3_000_000))
        cc=candidates(a)
        receipt["title"]=a.get("title")
        receipt["files"]=cc
        receipt["candidate_files"]=sum(x["possible_tree_source"] for x in cc)
        receipt["safe_files"]=sum(x["bounded_safe_download"] for x in cc)
        receipt["status"]="PASS_2025_METADATA_FILE_INVENTORY_ONLY"
    except (OSError,ValueError,TypeError,KeyError,json.JSONDecodeError) as exc:
        receipt["metadata_error"]=type(exc).__name__+": "+str(exc)[:350]
        return receipt,payloads
    for f in cc:
        if not f["bounded_safe_download"] or not f["possible_tree_source"]:
            continue
        # Source exploration is bounded to 3 files and <=15MB/file. Never guess unseen filenames.
        if len(payloads)>=3:break
        try:
            raw=get(f["download_url"],timeout=timeout,urlopen=urlopen)
            if f["size"]!=len(raw):raise ValueError("advertised file size changed")
            digest=hashlib.md5(raw).hexdigest()
            if f["advertised_md5"] and digest!=f["advertised_md5"]:
                raise ValueError("original file checksum changed")
            obj={"filename":f["name"],"id":f["id"],"source_sha256":hashlib.sha256(raw).hexdigest(),
                 "size":len(raw),"file_kind":"ZIP" if raw.startswith(b"PK") else "UNKNOWN"}
            if Path(f["name"]).suffix.lower()==".zip":
                obj["zip_members"]=zip_members(raw)
            elif Path(f["name"]).suffix.lower() in TREE_SUFFIXES:
                obj["file_kind"]="POTENTIAL_TREE_TEXT_UNPARSED"
                obj["head_text"]=raw[:120].decode("utf-8","replace")
            else:continue
            receipt.setdefault("recovered_files",[]).append(obj)
            payloads[f["name"]]=raw
        except (OSError,ValueError,zipfile.BadZipFile) as exc:
            receipt.setdefault("download_holds",[]).append({
                "name":f["name"],"error":type(exc).__name__+": "+str(exc)[:300]})
    # Follow exact article README rather than guessing unseen tree filenames.
    readmes=[f for f in cc if f["name"].lower() in ("readme.txt","readme.md")]
    if len(readmes)==1 and 0<readmes[0]["size"]<=16_000:
        f=readmes[0]
        u=f["download_url"]
        host=urllib.parse.urlparse(u or "").hostname
        if u and host and (host.endswith(".figshare.com") or host=="figshare.com"):
            try:
                raw=get(u,timeout=timeout,urlopen=urlopen,maxsize=16_000)
                if len(raw)!=f["size"] or (f["advertised_md5"] and
                        hashlib.md5(raw).hexdigest()!=f["advertised_md5"]):
                    raise ValueError("original README byte identity mismatch")
                plain=raw.decode("utf-8")
                receipt["readme_source_sha256"]=hashlib.sha256(raw).hexdigest()
                receipt["readme_text"]=plain[:12000]
                receipt["readme_references"]=re.findall(r"https?://[^\\s<>\\\"]+",plain)
                receipt["readme_source_identity_verified"]=True
                payloads[f["name"]]=raw
            except (OSError,ValueError,UnicodeError) as exc:
                receipt["readme_hold"]=type(exc).__name__+": "+str(exc)[:300]
    if receipt.get("recovered_files"):
        receipt["actual_file_bytes_verified"]=True
        receipt["status"]="PASS_2025_SOURCE_BYTES_INVENTORY_NO_TREE_TIP_JOIN"
    return receipt,payloads


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--archive-dir",type=Path)
    p.add_argument("--timeout",type=int,default=20)
    a=p.parse_args()
    if not 1<=a.timeout<=40:raise ValueError("invalid timeout")
    r,payloads=run(timeout=a.timeout)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
    print("ERICA_2025_SOURCE_STATUS",r["status"])
    print("ERICA_2025_SOURCE_LIST",json.dumps(r.get("files",[]))[:12000])
    print("ERICA_2025_RECOVERED",json.dumps(r.get("recovered_files",[]))[:16000])
    print("ERICA_2025_HOLDS",json.dumps(r.get("download_holds",[]))[:3000])
    print("ERICA_2025_README_VERIFIED",r.get("readme_source_identity_verified",False))
    print("ERICA_2025_README_TEXT",r.get("readme_text","")[:7000])
    if a.archive_dir and payloads:
        a.archive_dir.mkdir(parents=True,exist_ok=True)
        for filename,content in payloads.items():
            if Path(filename).name!=filename:raise ValueError("unsafe name")
            (a.archive_dir/filename).write_bytes(content)
    print("NO_NEW_PHYLOGENETIC_REGULATORY_MEMORY_TEST")


if __name__=="__main__":
    main()
