#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

from Bio import Phylo

DATA_RECORD=6757645
CODE_RECORD=6694682
UA="CHUN-Hedychium-source-first/0.1"

EXPECTED={
  "Discrete_13.csv":"eac3262d6bde7a2efc484088c17c199e",
  "C_tree.nwk":"606b73ac5118b4e080446fee75fcf216",
  "HEDYCHIUM_2022__DATA_README.txt":"b1816d7a71efacabb7c11a22f00f84da",
}
CODE_CANDIDATE="STOCHASTIC_MAPPING_ARD_labellum_09January2021.R"
CODE_EXPECTED_MD5="60360c9e41b3033adfa85433b84a1bef"

def fetch(url:str,accept:str="*/*")->bytes:
    last=None
    for attempt in range(4):
        req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":accept})
        try:
            with urllib.request.urlopen(req,timeout=30) as r:
                return r.read()
        except Exception as e:
            last=e
            if attempt==3:
                raise
            time.sleep(min(2**attempt,4))
    raise RuntimeError(str(last))

def md5(b:bytes)->str:
    return hashlib.md5(b).hexdigest()

def record(record_id:int)->dict:
    return json.loads(fetch(f"https://zenodo.org/api/records/{record_id}","application/json").decode("utf-8"))

def file_map(meta:dict)->dict[str,dict]:
    return {str(f.get("key")):f for f in meta.get("files",[])}

def content_url(f:dict)->str:
    links=f.get("links") or {}
    u=links.get("content") or links.get("self")
    if not u:
        raise RuntimeError(f"no content URL for {f.get('key')}")
    return u

def verify_download(f:dict,expected_md5:str)->tuple[bytes,dict]:
    b=fetch(content_url(f))
    observed=md5(b)
    checksum=str(f.get("checksum") or "").lower()
    repo_md5=checksum.split(":",1)[1] if checksum.startswith("md5:") else None
    return b,{
      "filename":f.get("key"),
      "bytes":len(b),
      "api_size":f.get("size"),
      "expected_md5":expected_md5,
      "repository_checksum":checksum,
      "observed_md5":observed,
      "expected_match":observed==expected_md5,
      "repository_match":repo_md5 is None or observed==repo_md5,
    }

def tree_metadata(b:bytes)->dict:
    text=b.decode("utf-8-sig")
    tree=Phylo.read(io.StringIO(text),"newick")
    tips=tree.get_terminals()
    branches=[x.branch_length for x in tree.find_clades() if x is not tree.root]
    return {
      "tip_count":len(tips),
      "duplicate_tip_labels":len(tips)-len({str(t.name or "").strip() for t in tips}),
      "nonroot_branch_count":len(branches),
      "missing_nonroot_branch_lengths":sum(x is None for x in branches),
      "negative_nonroot_branch_lengths":sum(x is not None and x<0 for x in branches),
      "rooted":bool(getattr(tree,"rooted",False)),
    }

def schema_lines(text:str)->list[dict]:
    terms=("labellum","color","colour","white","pale","bright","red","orange","pink","yellow","discrete_13","character 11","character11")
    out=[]
    for i,line in enumerate(text.splitlines(),1):
        low=line.lower()
        if any(t in low for t in terms):
            # Exclude obvious species-row-like long comma-delimited lines from emitted evidence.
            if line.count(",")>=5:
                continue
            out.append({"line":i,"text":line[:500]})
    return out[:200]

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    a.out.parent.mkdir(parents=True,exist_ok=True)

    data_meta=record(DATA_RECORD)
    fm=file_map(data_meta)
    missing=[name for name in EXPECTED if name not in fm]
    if missing:
        status="HOLD_HEDYCHIUM_REQUIRED_ZENODO_OBJECT_MISSING"
        out={"version":"v0.1","status":status,"missing":missing}
        a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n"); print(json.dumps(out,indent=2)); return 0

    downloads={}
    bodies={}
    for name,digest in EXPECTED.items():
        b,diag=verify_download(fm[name],digest)
        bodies[name]=b
        downloads[name]=diag

    exact_source=all(x["expected_match"] and x["repository_match"] for x in downloads.values())
    tmeta=tree_metadata(bodies["C_tree.nwk"])
    readme=bodies["HEDYCHIUM_2022__DATA_README.txt"].decode("utf-8",errors="replace")
    readme_schema=schema_lines(readme)

    code_meta=None
    code_diag=None
    code_schema=[]
    try:
        cm=record(CODE_RECORD)
        cfm=file_map(cm)
        if CODE_CANDIDATE in cfm:
            cb,code_diag=verify_download(cfm[CODE_CANDIDATE],CODE_EXPECTED_MD5)
            code_meta={"record":CODE_RECORD,"filename":CODE_CANDIDATE}
            code_schema=schema_lines(cb.decode("utf-8",errors="replace"))
    except Exception as e:
        code_diag={"error":f"{type(e).__name__}: {e}"}

    mapping_tokens=("white","pale","bright","red","orange","pink","yellow")
    evidence_text="\n".join(x["text"].lower() for x in readme_schema+code_schema)
    mapping_colour_tokens=sorted({t for t in mapping_tokens if t in evidence_text})
    pre_row_mapping_evidence=bool(
        ("labellum" in evidence_text or "character 11" in evidence_text or "character11" in evidence_text)
        and len(mapping_colour_tokens)>=2
    )

    if not exact_source:
        status="HOLD_HEDYCHIUM_EXACT_ZENODO_BYTES_MISMATCH"
    elif tmeta["tip_count"]<20:
        status="HOLD_HEDYCHIUM_TREE_LT20"
    elif tmeta["duplicate_tip_labels"]>0:
        status="HOLD_HEDYCHIUM_DUPLICATE_TREE_TIPS"
    elif tmeta["missing_nonroot_branch_lengths"]>0 or tmeta["negative_nonroot_branch_lengths"]>0:
        status="HOLD_HEDYCHIUM_BRANCH_LENGTHS_INVALID"
    elif not pre_row_mapping_evidence:
        status="HOLD_HEDYCHIUM_PRE_ROW_COLOUR_SCHEMA_MAPPING_NOT_ESTABLISHED"
    else:
        status="PASS_HEDYCHIUM_SOURCE_FIRST_ADMISSION"

    out={
      "version":"v0.1",
      "status":status,
      "candidate":"HEDYCHIUM",
      "reported_taxa":70,
      "zenodo_data_record":DATA_RECORD,
      "zenodo_code_record":CODE_RECORD,
      "downloads":downloads,
      "tree_metadata":tmeta,
      "readme_schema_evidence":readme_schema,
      "code_object":code_meta,
      "code_download":code_diag,
      "code_schema_evidence":code_schema,
      "pre_row_colour_mapping_evidence":pre_row_mapping_evidence,
      "mapping_colour_tokens_found":mapping_colour_tokens,
      "hard_checks":{
        "exact_trait_bytes_recoverable":downloads["Discrete_13.csv"]["expected_match"],
        "exact_tree_bytes_recoverable":downloads["C_tree.nwk"]["expected_match"],
        "exact_readme_bytes_recoverable":downloads["HEDYCHIUM_2022__DATA_README.txt"]["expected_match"],
        "tree_tip_count_ge20":tmeta["tip_count"]>=20,
        "tree_branch_lengths_valid":tmeta["missing_nonroot_branch_lengths"]==0 and tmeta["negative_nonroot_branch_lengths"]==0,
        "pre_row_colour_schema_mapping_established":pre_row_mapping_evidence,
      },
      "outcome_firewall":{
        "discrete_trait_bytes_downloaded_for_hash_only":True,
        "discrete_trait_rows_parsed":False,
        "species_level_colour_values_opened":False,
        "colour_state_frequencies_computed":False,
        "tree_tip_labels_emitted":False,
        "hidden_memory_auc_computed":False,
      },
      "next_gate":"STOP_SCREEN_AND_FREEZE_HEDYCHIUM_ADMISSION" if status=="PASS_HEDYCHIUM_SOURCE_FIRST_ADMISSION" else "CONTINUE_SOURCE_FIRST_SCREEN_IF_BUDGET_REMAINS",
      "paper1_science_changed":False,
      "el_v0_3_science_changed":False
    }
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
      "status":status,
      "downloads":downloads,
      "tree_metadata":tmeta,
      "mapping_colour_tokens_found":mapping_colour_tokens,
      "pre_row_colour_mapping_evidence":pre_row_mapping_evidence,
      "readme_schema_evidence":readme_schema,
      "code_schema_evidence":code_schema,
    },indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
