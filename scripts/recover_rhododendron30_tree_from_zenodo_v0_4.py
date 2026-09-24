#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, io, json, urllib.error, urllib.request
from pathlib import Path

from Bio import Phylo

DRYAD_FILE_ID=1853438
EXPECTED_SHA256="784011d0e2e17df9ea21eb22d31197bad29219a37ac213fda013766e29b51362"
DRYAD_META=f"https://datadryad.org/api/v2/files/{DRYAD_FILE_ID}"
ZENODO_URL="https://zenodo.org/records/7149402/files/1_WP_RAxML.tre?download=1"
UA="CHUN-Rhododendron30-tree-recovery/0.4"


def exact_match(body:bytes, expected_size:int, expected_sha256:str)->bool:
    return len(body)==int(expected_size) and hashlib.sha256(body).hexdigest()==expected_sha256.lower()


def treeish(body:bytes)->bool:
    s=body.lstrip()
    return bool(s.startswith(b"(") and b")" in s and s.rstrip().endswith(b";") and b"<html" not in s.lower())


def get(url:str,accept:str="*/*")->dict:
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":accept})
    try:
        with urllib.request.urlopen(req,timeout=120) as r:
            return {"ok":True,"status":getattr(r,"status",200),"final_url":r.geturl(),
                    "headers":dict(r.headers),"body":r.read()}
    except urllib.error.HTTPError as e:
        try: body=e.read()
        except Exception: body=b""
        return {"ok":False,"status":e.code,"final_url":e.geturl(),"headers":dict(e.headers or {}),
                "body":body,"reason":str(e.reason)}
    except Exception as e:
        return {"ok":False,"status":None,"final_url":url,"headers":{},"body":b"","reason":repr(e)}


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    a.out.parent.mkdir(parents=True,exist_ok=True)

    meta_req=get(DRYAD_META,"application/json")
    meta=None
    if meta_req["ok"]:
        try: meta=json.loads(meta_req["body"])
        except Exception: meta=None

    expected_size=int(meta.get("size")) if isinstance(meta,dict) and meta.get("size") is not None else None
    metadata_digest=(str(meta.get("digest")).lower() if isinstance(meta,dict) and meta.get("digest") else None)
    metadata_digest_type=(str(meta.get("digestType")).lower() if isinstance(meta,dict) and meta.get("digestType") else None)
    metadata_consistent=bool(
        meta is not None and expected_size is not None and
        metadata_digest_type in {"sha-256","sha256"} and
        metadata_digest==EXPECTED_SHA256
    )

    zr=get(ZENODO_URL)
    body=zr["body"]
    digest=hashlib.sha256(body).hexdigest() if body else None
    exact=bool(zr["ok"] and expected_size is not None and exact_match(body,expected_size,EXPECTED_SHA256))
    is_tree=bool(exact and treeish(body))

    tree_diag=None
    if is_tree:
        try:
            tree=Phylo.read(io.StringIO(body.decode("utf-8-sig")),"newick")
            tips=[str(t.name) for t in tree.get_terminals()]
            branches=[c.branch_length for c in tree.find_clades() if c is not tree.root]
            tree_diag={
              "tip_count":len(tips),
              "duplicate_tip_labels":len(tips)-len(set(tips)),
              "all_nonroot_branch_lengths_present":bool(branches) and all(x is not None for x in branches),
            }
        except Exception as e:
            tree_diag={"parse_error":f"{type(e).__name__}: {e}"}
            is_tree=False

    if is_tree:
        (a.out.parent/"1_WP_RAxML.tre").write_bytes(body)

    status=("RHODODENDRON30_PRIMARY_TREE_RECOVERED_EXACT_MIRROR"
            if metadata_consistent and is_tree
            else "HOLD_RHODODENDRON30_TREE_MIRROR_NOT_EXACT")

    out={
      "version":"v0.4",
      "status":status,
      "primary_tree":{
        "dryad_doi":"10.5061/dryad.8cz8w9grq",
        "dryad_file_id":DRYAD_FILE_ID,
        "file":"1_WP_RAxML.tre",
        "dryad_metadata_http_status":meta_req["status"],
        "dryad_metadata_size":expected_size,
        "dryad_metadata_digest_type":metadata_digest_type,
        "dryad_metadata_digest":metadata_digest,
        "frozen_expected_sha256":EXPECTED_SHA256,
        "dryad_metadata_consistent_with_frozen_sha":metadata_consistent,
        "mirror":"https://zenodo.org/records/7149402",
        "mirror_file_url":ZENODO_URL,
        "mirror_http_status":zr["status"],
        "mirror_downloaded_bytes":len(body),
        "mirror_sha256":digest,
        "exact_size_and_sha_match":exact,
        "treeish_payload":treeish(body) if body else False,
        "tree_diagnostics":tree_diag,
      },
      "table_s3_opened":False,
      "chemistry_opened":False,
      "row_level_anthocyanin_values_accessed":False,
      "profile_auc_computed":False,
      "next_gate":("TABLE_S3_OR_IDENTIFIER_SOURCE_RECOVERY_ONLY"
                   if status=="RHODODENDRON30_PRIMARY_TREE_RECOVERED_EXACT_MIRROR"
                   else "KEEP_TREE_HOLD"),
      "el_v0_3_science_changed":False,
      "v0_8_promotion_state_changed":False,
      "paper1_science_changed":False,
    }
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":status,"primary_tree":out["primary_tree"]},indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
