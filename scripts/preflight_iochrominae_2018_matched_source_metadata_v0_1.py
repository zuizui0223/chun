#!/usr/bin/env python3
"""Metadata-only preflight for independent 2018 Iochrominae expression-memory replication.

Sources are deliberately separated:
 - 2018 Larter qPCR/pigment article, doi:10.1093/molbev/msy117
 - 2015 Smith/Goldberg article and cited tree dataset, doi:10.5061/dryad.0732g
 - distinct 2018 floral-shape tree, doi:10.5061/dryad.5jn7b
 - separate 2019 Dvdy package, doi:10.5061/dryad.p5dq84v

NEVER read expression rows, chemistry measurements or phylogenetic tree bytes here.
"""
from __future__ import annotations
import argparse
import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

UA="CHUN-independent-nested-memory-source-preflight/0.1"
DRYAD_API="https://datadryad.org/api/v2"
DOIS=("10.5061/dryad.0732g","10.5061/dryad.5jn7b")

def get_json(url: str, timeout: int=20) -> dict:
    r=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/json"})
    with urllib.request.urlopen(r,timeout=timeout) as response:
        data=response.read(2_000_000)
    out=json.loads(data)
    if not isinstance(out,dict):raise ValueError("expected JSON object")
    return out

def get_href(obj:dict,key:str)->str|None:
    links=obj.get("_links",{})
    link=links.get(key) if isinstance(links,dict) else None
    if isinstance(link,dict):return link.get("href")
    if isinstance(link,str):return link
    return None

def metadata_one(doi:str,timeout:int=20)->dict:
    url=f"{DRYAD_API}/datasets/"+urllib.parse.quote("doi:"+doi,safe="")
    out={"doi":doi,"url":url,"resolved":False,"versions":[],"files":[]}
    try:
        ds=get_json(url,timeout)
        out["resolved"]=True
        out["dataset_id"]=ds.get("id")
        out["title"]=ds.get("title")
        href=get_href(ds,"stash:versions") or f"{url}/versions"
        if href.startswith("/"):href="https://datadryad.org"+href
        ver=get_json(href,timeout)
        versions=ver.get("_embedded",{}).get("stash:versions",[])
        # Stop on schema mismatches; no guessing of file IDs or source versions.
        if not isinstance(versions,list):
            raise ValueError("versions schema missing")
        for v in versions:
            version_url=get_href(v,"self")
            out["versions"].append({"version_url":version_url,"versionNumber":v.get("versionNumber")})
        if versions:
            # Dryad /versions entries advertise their IDs via their self href,
            # not necessarily an integer "id" field.
            version_href=get_href(ds,"stash:version")
            if not version_href:
                latest=sorted(versions,key=lambda v:v.get("versionNumber",0))[-1]
                version_href=get_href(latest,"self")
            if not version_href or "/versions/" not in version_href:
                raise ValueError("latest version href missing")
            if version_href.startswith("/"):
                version_href="https://datadryad.org"+version_href
            if not version_href.startswith(f"{DRYAD_API}/versions/"):
                raise ValueError("unexpected source version hostname or path")
            out["latest_version_url"]=version_href
            files=get_json(version_href+"/files",timeout)
            # Dryad file metadata only; do not follow any data/download URLs.
            embeds=files.get("_embedded",{}).get("stash:files",[])
            if not isinstance(embeds,list):raise ValueError("file metadata schema missing")
            for item in embeds:
                out["files"].append({
                    "name":item.get("path") or item.get("filename"),
                    "id":item.get("id"),
                    "size":item.get("size"),
                    "digest":item.get("digest")
                })
    except (urllib.error.HTTPError, urllib.error.URLError,TimeoutError,ValueError,KeyError) as e:
        out["error_type"]=type(e).__name__
        out["error"]=str(e)[:240]
    return out

def preflight(timeout:int=20)->dict:
    entries=[metadata_one(doi,timeout) for doi in DOIS]
    return {
      "version":"v0.1",
      "status":"HOLD_NUMERIC_2018_QPCR_AND_MATCHED_TREE_BYTES_NOT_VERIFIED",
      "analysis":"IOCHROMINAE_2018_INDEPENDENT_MATCHED_SOURCE_METADATA_ONLY",
      "reported_comparative_qpcr_species":28,
      "reported_expression_genes":7,
      "required_numeric_2018_qpcr_species_matrix_verified":False,
      "required_exact_source_tree_payload_verified":False,
      "no_trait_or_expression_rows_opened":True,
      "dryad_sources":entries,
      "source_identity_caveat":"2018 Larter qPCR uses 2015 Smith Goldberg published tree; 2018 Smith Kriebel later shape tree is separate and 2019 Dvdy Dryad is separate. No tree substitution is authorized.",
      "source_paper_doi":"10.1093/molbev/msy117",
      "tree_paper_doi":"10.3732/ajb.1500163",
      "direct_replication_completed":False,
      "petunieae_design_and_outcomes_changed":False,
      "freeze_boundary":"Do not acquire, parse, map or analyze numeric phenotype/expression/tree content in this metadata-only preflight."
    }

def main()->None:
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--timeout",type=int,default=20)
    args=p.parse_args()
    r=preflight(args.timeout)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":r["status"],"datasets":[{"doi":x["doi"],"resolved":x["resolved"],"n_files":len(x["files"]),"error_type":x.get("error_type")} for x in r["dryad_sources"]]},indent=2))

if __name__=="__main__":main()
