#!/usr/bin/env python3
"""Fetch only exact source archive bytes for Smith & Goldberg (2015) tree.

Source identity is fixed by the prior gate. This script is a transport
preflight, *not* a phylogenetic or biochemical analysis. Never inspect
tree members or biological outcome rows here.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

UA="CHUN-SmithGoldberg2015-tree-exact-source-preflight/0.1"
BASE="https://datadryad.org"
API=BASE+"/api/v2"


def get_json(url:str, timeout:int=25)->dict:
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=timeout) as res:
        out=json.loads(res.read(2_000_000))
    if not isinstance(out,dict):raise ValueError("unexpected metadata type")
    return out


def downloaded(url:str, max_bytes:int=3_000_000, timeout:int=25)->bytes:
    if not url.startswith(BASE+"/api/v2/"):
        raise ValueError("unexpected source download host/path")
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/zip,application/octet-stream,*/*"})
    with urllib.request.urlopen(req,timeout=timeout) as res:
        result=res.read(max_bytes+1)
    if len(result)>max_bytes:raise ValueError("source transport size limit exceeded")
    return result


def href(item:dict,key:str)->str|None:
    lk=(item.get("_links") or {}).get(key)
    if isinstance(lk,dict):return lk.get("href")
    if isinstance(lk,str):return lk
    return None


def normalized_link(path:str)->str:
    if path.startswith("/"):path=BASE+path
    if not path.startswith(API+"/"):raise ValueError("not a Dryad API link")
    return path


def inspect_transport(gate:dict, out_dir:Path, timeout:int=25)->dict:
    doi=gate["source_doi"]
    endpoint=gate["public_api_source"]
    response=get_json(endpoint,timeout)
    files=(response.get("_embedded") or {}).get("stash:files") or []
    if not isinstance(files,list):raise ValueError("Dryad file metadata schema changed")
    items=[x for x in files if (x.get("path") or x.get("filename"))==gate["filename"]]
    if len(items)!=1:raise ValueError("frozen archive filename not uniquely represented in version metadata")
    item=items[0]
    if int(item.get("size") or 0)!=gate["expected_size_bytes"]:
        raise ValueError("source archive size metadata drift")
    if str(item.get("digest") or "").lower()!=gate["expected_md5"]:
        raise ValueError("source archive MD5 metadata drift")
    self_href=href(item,"self")
    attempts=[]
    possibilities=[]
    if self_href:
        h=normalized_link(self_href)
        # Conventional public file downloads only, no token or signed URL fabrication.
        possibilities.append(("file_api_download",h.rstrip("/")+"/download"))
    possibilities.append(("dataset_api_download",API+"/datasets/"+urllib.parse.quote("doi:"+doi,safe="")+"/download"))
    out_dir.mkdir(parents=True,exist_ok=True)
    admitted=None
    for label,url in possibilities:
        attempt={"route":label,"url":url,"status":"HOLD"}
        try:
            raw=downloaded(url,timeout=timeout)
            if label=="dataset_api_download":
                # Dataset download is a transport wrapper. Read only member names,
                # then exact original ZIP bytes; do not open that inner ZIP.
                with zipfile.ZipFile(io.BytesIO(raw)) as wrapper:
                    matches=[name for name in wrapper.namelist() if Path(name).name==gate["filename"]]
                    if len(matches)!=1:raise ValueError("frozen archive absent or ambiguous in dataset ZIP")
                    raw=wrapper.read(matches[0])
            checksum=hashlib.md5(raw).hexdigest()
            if len(raw)!=gate["expected_size_bytes"] or checksum!=gate["expected_md5"]:
                raise ValueError("downloaded archive size/MD5 mismatch")
            outpath=out_dir/gate["filename"]
            outpath.write_bytes(raw)
            admitted={"path":str(outpath),"bytes":len(raw),"md5":checksum,"route":label}
            attempt["status"]="EXACT_BYTES_VERIFIED"
            attempts.append(attempt)
            break
        except (urllib.error.URLError,urllib.error.HTTPError,ValueError,zipfile.BadZipFile,OSError) as err:
            attempt["error_type"]=type(err).__name__
            attempt["error"]=str(err)[:200]
            attempts.append(attempt)
    return {
      "version":"v0.1",
      "status":"ORIGINAL_TREE_ARCHIVE_EXACT_BYTES_VERIFIED_SOURCE_PREFLIGHT_ONLY" if admitted else "HOLD_ORIGINAL_TREE_ARCHIVE_DOWNLOAD_NOT_VERIFIED",
      "source_doi":doi,
      "filename":gate["filename"],
      "expected_size_bytes":gate["expected_size_bytes"],
      "expected_md5":gate["expected_md5"],
      "attempts":attempts,
      "exact_file":admitted,
      "tree_members_opened":False,
      "tree_tips_read":False,
      "qpcr_outcomes_opened":False,
      "pigment_outcomes_opened":False,
      "gene_expression_phylogenetic_result_computed":False,
      "independent_replication_pass":False
    }


def main()->None:
    p=argparse.ArgumentParser()
    p.add_argument("--gate",type=Path,required=True)
    p.add_argument("--out-dir",type=Path,required=True)
    p.add_argument("--summary",type=Path,required=True)
    p.add_argument("--timeout",type=int,default=25)
    a=p.parse_args()
    gate=json.loads(a.gate.read_text(encoding="utf-8"))
    out=inspect_transport(gate,a.out_dir,a.timeout)
    a.summary.parent.mkdir(parents=True,exist_ok=True)
    a.summary.write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":out["status"],"attempts":out["attempts"],"exact_file":out["exact_file"]},indent=2))


if __name__=="__main__":main()
