#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import urllib.request
import zipfile
from pathlib import Path

from Bio import Phylo

ZENODO_API="https://zenodo.org/api/records/7659158"
ZENODO_RECORD=7659158
BUNDLE="skripts.zip"
BUNDLE_MD5="aab3192fa22e8562f93551dc18f040b7"
TRAIT_BASENAME="floraltraits.csv"
TREE_BASENAME="marcelo_meris.tre"
UA="CHUN-Merianieae-source-gate/0.1"


def fetch(url:str,accept:str="*/*")->bytes:
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":accept})
    with urllib.request.urlopen(req,timeout=120) as r:
        return r.read()


def md5(b:bytes)->str:
    return hashlib.md5(b).hexdigest()


def sha256(b:bytes)->str:
    return hashlib.sha256(b).hexdigest()


def zenodo_bundle_url(meta:dict)->str:
    matches=[]
    for f in meta.get("files",[]):
        if str(f.get("key","")).casefold()==BUNDLE.casefold():
            links=f.get("links") or {}
            url=links.get("content") or links.get("self")
            if url:
                matches.append(url)
    if len(matches)!=1:
        raise RuntimeError(f"expected one Zenodo {BUNDLE}, got {len(matches)}")
    return matches[0]


def member_candidates(names:list[str],basename_casefold:str)->list[str]:
    return sorted(
        [n for n in names if not n.endswith("/") and Path(n).name.casefold()==basename_casefold.casefold()]
    )


def choose_identical_members(z:zipfile.ZipFile,candidates:list[str],label:str)->tuple[str,bytes,list[dict]]:
    if not candidates:
        raise RuntimeError(f"{label}: required archive member not found")
    payloads=[(n,z.read(n)) for n in candidates]
    digests={sha256(b) for _,b in payloads}
    if len(digests)!=1:
        raise RuntimeError(f"{label}: multiple non-identical archive members")
    chosen=payloads[0]
    return chosen[0],chosen[1],[{"path":n,"bytes":len(b),"sha256":sha256(b)} for n,b in payloads]


def header_only(csv_bytes:bytes)->list[str]:
    text=io.TextIOWrapper(io.BytesIO(csv_bytes),encoding="utf-8-sig",newline="")
    row=next(csv.reader(text))
    return [str(x).strip() for x in row]


def tree_metadata(tree_bytes:bytes)->dict:
    text=tree_bytes.decode("utf-8-sig")
    tree=Phylo.read(io.StringIO(text),"newick")
    tips=tree.get_terminals()
    branches=[c.branch_length for c in tree.find_clades() if c is not tree.root]
    missing=sum(x is None for x in branches)
    negative=sum((x is not None and x<0) for x in branches)
    dups=len(tips)-len({str(t.name).strip() for t in tips})
    return {
        "tip_count":len(tips),
        "duplicate_tip_labels":dups,
        "nonroot_branch_count":len(branches),
        "missing_nonroot_branch_lengths":missing,
        "negative_nonroot_branch_lengths":negative,
    }


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--stage-dir",type=Path,required=True)
    a=ap.parse_args()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.stage_dir.mkdir(parents=True,exist_ok=True)

    meta=json.loads(fetch(ZENODO_API,"application/json").decode("utf-8"))
    url=zenodo_bundle_url(meta)
    bundle=fetch(url)
    bundle_md5=md5(bundle)
    if bundle_md5!=BUNDLE_MD5:
        raise RuntimeError(f"Zenodo bundle MD5 drift: {bundle_md5}")

    with zipfile.ZipFile(io.BytesIO(bundle)) as z:
        names=z.namelist()
        trait_cands=member_candidates(names,TRAIT_BASENAME)
        tree_cands=member_candidates(names,TREE_BASENAME)
        trait_path,trait_bytes,trait_copies=choose_identical_members(z,trait_cands,"trait")
        tree_path,tree_bytes,tree_copies=choose_identical_members(z,tree_cands,"tree")

    header=header_only(trait_bytes)
    required=["species","x","corolla.colour"]
    header_ok=all(x in header for x in required)
    tmeta=tree_metadata(tree_bytes)

    # Stage exact required members for the next gates; trait rows remain unopened here.
    trait_stage=a.stage_dir/"floraltraits.csv"
    tree_stage=a.stage_dir/"Marcelo_Meris.tre"
    trait_stage.write_bytes(trait_bytes)
    tree_stage.write_bytes(tree_bytes)

    if not header_ok:
        status="HOLD_MERIANIEAE_REQUIRED_TRAIT_HEADER_MISSING"
    elif tmeta["tip_count"]<20:
        status="HOLD_MERIANIEAE_TREE_LT_20"
    elif tmeta["duplicate_tip_labels"]>0:
        status="HOLD_MERIANIEAE_DUPLICATE_TREE_TIPS"
    elif tmeta["missing_nonroot_branch_lengths"]>0 or tmeta["negative_nonroot_branch_lengths"]>0:
        status="HOLD_MERIANIEAE_BRANCH_LENGTHS_INVALID"
    else:
        status="MERIANIEAE_EXACT_SOURCE_READY_COROLLA_COLOUR_UNOPENED"

    out={
      "version":"v0.1",
      "status":status,
      "candidate":"MERIANIEAE_MELASTOMATACEAE",
      "zenodo_record_id":ZENODO_RECORD,
      "zenodo_bundle":{
        "filename":BUNDLE,
        "frozen_md5":BUNDLE_MD5,
        "observed_md5":bundle_md5,
        "bytes":len(bundle),
        "download_url":url,
      },
      "trait_member":{
        "chosen_path":trait_path,
        "bytes":len(trait_bytes),
        "sha256":sha256(trait_bytes),
        "all_matching_copies":trait_copies,
        "header":header,
        "required_header":required,
        "required_header_present":header_ok,
      },
      "tree_member":{
        "chosen_path":tree_path,
        "bytes":len(tree_bytes),
        "sha256":sha256(tree_bytes),
        "all_matching_copies":tree_copies,
        **tmeta,
      },
      "staged_trait_path":str(trait_stage),
      "staged_tree_path":str(tree_stage),
      "outcome_firewall":{
        "trait_header_opened":True,
        "trait_data_rows_opened":False,
        "identifier_values_opened":False,
        "corolla_colour_values_opened":False,
        "state_frequencies_computed":False,
        "tree_tip_labels_emitted":False,
        "hidden_memory_auc_computed":False,
      },
      "next_gate":(
        "FREEZE_IDENTIFIER_ONLY_CROSSWALK_WITH_COROLLA_COLOUR_UNOPENED"
        if status=="MERIANIEAE_EXACT_SOURCE_READY_COROLLA_COLOUR_UNOPENED"
        else "STOP_HOLD"
      ),
      "paper1_science_changed":False,
      "el_v0_3_science_changed":False
    }
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
      "status":status,
      "bundle_bytes":len(bundle),
      "trait_path":trait_path,
      "trait_sha256":out["trait_member"]["sha256"],
      "header":header,
      "tree_path":tree_path,
      "tree_sha256":out["tree_member"]["sha256"],
      "tree_metadata":tmeta,
    },indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
