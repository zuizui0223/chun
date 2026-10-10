#!/usr/bin/env python3
"""Bounded 2016 Pirie Erica publisher-supplement machine-tree source preflight.

Official Springer URLs, source only. A PDF figure ZIP never becomes a Newick
tree or patristic-distance estimator. Separate from TreeBASE S18291.
"""
from __future__ import annotations
import argparse, hashlib, io, json, pathlib, urllib.request, zipfile

SOURCE_DOI="10.1186/s12862-016-0764-3"
BASE="https://media.springernature.com/original/springer-static/esm/art%3A10.1186%2Fs12862-016-0764-3/MediaObjects/"
FILES={
 "MOESM2_Figure_S1":BASE+"12862_2016_764_MOESM2_ESM.zip",
 "MOESM3_Figure_S2":BASE+"12862_2016_764_MOESM3_ESM.zip",
}
MAX_DOWNLOAD=16_000_000
PARSABLE_TREE_EXT={".nex",".nexus",".tre",".tree",".nwk",".newick"}

def list_members(raw):
    if not raw.startswith(b"PK"): raise ValueError("downloaded content not ZIP")
    with zipfile.ZipFile(io.BytesIO(raw)) as f:
        if f.testzip() is not None: raise ValueError("invalid ZIP member CRC")
        entries=[]
        for z in f.infolist():
            if z.is_dir():continue
            if z.file_size>40_000_000:raise ValueError("unsafe extracted archive member")
            entries.append({"name":z.filename,"size":z.file_size,
                "explicit_tree_filename":pathlib.PurePosixPath(z.filename).suffix.lower() in PARSABLE_TREE_EXT})
    return entries

def run(timeout=25,urlopen=None):
    urlopen=urlopen or urllib.request.urlopen
    r={"version":"v0.1","original_publication_doi":SOURCE_DOI,
       "original_2016_treebase_S18291_unchanged_HOLD":True,
       "status":"HOLD_ORIGINAL_SUPPLEMENT_MACHINE_TREE_UNVERIFIED",
       "source_archives":{},"new_phylogenetic_tree_admitted":False,
       "no_species_tip_or_branch_distance_computed":True,
       "new_regulatory_memory_replicate":False,
       "AJB_and_EL_frozen_science_unchanged":True}
    recovered={}
    for key,url in FILES.items():
        row={"url":url,"status":"HOLD"}
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"CHUN-Pirie2016-supplement-inventory/0.1",
                 "Accept":"application/zip,application/octet-stream,*/*"})
            with urlopen(req,timeout=timeout) as response:
                code=getattr(response,"status",200)
                if code!=200:raise ValueError(f"HTTP {code}")
                payload=response.read(MAX_DOWNLOAD+1)
            if len(payload)>MAX_DOWNLOAD:raise ValueError("exceeds exact transport byte ceiling")
            entries=list_members(payload)
            row.update({"status":"SOURCE_ZIP_INVENTORIED","source_bytes":len(payload),
                        "sha256":hashlib.sha256(payload).hexdigest(),
                        "members":entries,
                        "explicit_tree_file_candidates":[x["name"] for x in entries if x["explicit_tree_filename"]]})
            recovered[key]=payload
        except (OSError,ValueError,zipfile.BadZipFile) as exc:
            row["reason"]=type(exc).__name__+": "+str(exc)[:300]
        r["source_archives"][key]=row
    if recovered:
        r["status"]="SUPPLEMENT_ARCHIVES_INVENTORIED_BUT_NOT_ADMITTED_AS_TREE"
    return r,recovered

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=pathlib.Path,required=True)
    p.add_argument("--archive-dir",type=pathlib.Path)
    p.add_argument("--timeout",type=int,default=25)
    args=p.parse_args()
    if not 1<=args.timeout<=40:raise ValueError("invalid transport timeout")
    result,zips=run(args.timeout)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    for label,source in result["source_archives"].items():
        print("ERICA_2016_PUBLISHER_SUPPLEMENT",label,source)
    if args.archive_dir:
        args.archive_dir.mkdir(parents=True,exist_ok=True)
        for label,data in zips.items():
            (args.archive_dir/(label+".zip")).write_bytes(data)
    print("ERICA_ORIGINAL_SUPPLEMENT_DECISION",result["status"])
    print("NO_MACHINE_TREE_CHOSEN_NO_MEMORY_INFERENCE")

if __name__=="__main__":
    main()
