#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path

from Bio import Phylo


def norm_id(x:str)->str:
    s=str(x or "").strip().replace("_"," ")
    return re.sub(r"\s+"," ",s).lower()


def load_identifier_rows(path:Path)->list[dict]:
    out=[]
    with path.open(newline="",encoding="utf-8-sig") as f:
        reader=csv.DictReader(f)
        if "x" not in (reader.fieldnames or []) or "species" not in (reader.fieldnames or []):
            raise ValueError("required identifier columns x/species missing")
        for i,row in enumerate(reader,start=2):
            raw_x=str(row.get("x") or "").strip()
            species=str(row.get("species") or "").strip()
            if not raw_x:
                continue
            out.append({"source_row":i,"x":raw_x,"species":species,"key":norm_id(raw_x)})
    return out


def build_crosswalk(trait_path:Path,tree_path:Path)->tuple[dict,object]:
    rows=load_identifier_rows(trait_path)
    tree=Phylo.read(str(tree_path),"newick")
    tips=[str(t.name or "").strip() for t in tree.get_terminals()]
    tip_keys=[norm_id(t) for t in tips]

    row_counts=Counter(r["key"] for r in rows)
    tip_counts=Counter(tip_keys)
    duplicate_source=sorted(k for k,v in row_counts.items() if v>1)
    duplicate_tree=sorted(k for k,v in tip_counts.items() if v>1)

    by_tip={norm_id(t):t for t in tips if tip_counts[norm_id(t)]==1}
    matches=[]
    unmatched=[]
    for r in rows:
        k=r["key"]
        if row_counts[k]!=1:
            continue
        if k in by_tip:
            matches.append({
              "source_row":r["source_row"],
              "source_x":r["x"],
              "species":r["species"],
              "tree_tip":by_tip[k],
              "key":k,
            })
        else:
            unmatched.append({"source_row":r["source_row"],"source_x":r["x"],"species":r["species"],"key":k})

    matched_tips={m["tree_tip"] for m in matches}
    for t in list(tree.get_terminals()):
        if str(t.name or "").strip() not in matched_tips:
            tree.prune(t)

    return {
      "source_identifier_rows":len(rows),
      "source_unique_identifier_keys":len(row_counts),
      "tree_tip_count":len(tips),
      "matched_count":len(matches),
      "unmatched_source_count":len(unmatched),
      "duplicate_source_keys":duplicate_source,
      "duplicate_tree_keys":duplicate_tree,
      "matches":matches,
      "unmatched_source_rows":unmatched,
      "pruned_tree_tip_count":len(tree.get_terminals()),
    },tree


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--trait",type=Path,required=True)
    ap.add_argument("--tree",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--out-tree",type=Path,required=True)
    a=ap.parse_args()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out_tree.parent.mkdir(parents=True,exist_ok=True)

    cw,tree=build_crosswalk(a.trait,a.tree)
    if cw["duplicate_source_keys"] or cw["duplicate_tree_keys"]:
        status="HOLD_MERIANIEAE_DUPLICATE_IDENTIFIER_CROSSWALK"
    elif cw["matched_count"]<20:
        status="HOLD_MERIANIEAE_MATCHED_FRAME_LT_20"
    else:
        status="MERIANIEAE_IDENTIFIER_CROSSWALK_FROZEN_COROLLA_COLOUR_UNOPENED"

    Phylo.write(tree,str(a.out_tree),"newick")
    out={
      "version":"v0.1",
      "status":status,
      **cw,
      "crosswalk_rule":"exact normalized x/tree-tip intersection only; trim + underscore-to-space + whitespace collapse + lowercase; no alias or fuzzy repair",
      "trait_identifier_columns_accessed":["x","species"],
      "corolla_colour_column_accessed":False,
      "state_frequencies_computed":False,
      "hidden_memory_auc_computed":False,
      "pruned_tree_path":str(a.out_tree),
      "next_gate":(
        "OPEN_COROLLA_COLOUR_FOR_STATE_SUPPORT_ONLY"
        if status=="MERIANIEAE_IDENTIFIER_CROSSWALK_FROZEN_COROLLA_COLOUR_UNOPENED"
        else "STOP_HOLD"
      ),
      "paper1_science_changed":False,
      "el_v0_3_science_changed":False
    }
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
      "status":status,
      "source_identifier_rows":cw["source_identifier_rows"],
      "tree_tip_count":cw["tree_tip_count"],
      "matched_count":cw["matched_count"],
      "unmatched_source_count":cw["unmatched_source_count"],
      "duplicate_source_keys":cw["duplicate_source_keys"],
      "duplicate_tree_keys":cw["duplicate_tree_keys"],
    },indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
