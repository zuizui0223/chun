#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import io
import json
import hashlib
from collections import Counter
from pathlib import Path

from Bio import Phylo


def project_tip_labels(body:bytes)->list[str]:
    text=body.decode("utf-8-sig")
    rows=csv.reader(io.StringIO(text))
    header=next(rows,None)
    if not header or header[0].strip()!="Tip_Label":
        raise ValueError(f"first column must be Tip_Label, got {header}")
    out=[]
    for row in rows:
        if not row:
            continue
        x=row[0].strip()
        if x:
            out.append(x)
    return out


def tree_tip_labels(body:bytes)->list[str]:
    t=Phylo.read(io.StringIO(body.decode("utf-8-sig")),"newick")
    return [str(x.name).strip() for x in t.get_terminals()]


def crosswalk_summary(trait:list[str],tree:list[str])->dict:
    tc=Counter(trait); rc=Counter(tree)
    ts=set(trait); rs=set(tree)
    return {
        "trait_labels":len(trait),
        "tree_labels":len(tree),
        "unique_trait_labels":len(ts),
        "unique_tree_labels":len(rs),
        "duplicate_trait_labels":sum(v-1 for v in tc.values() if v>1),
        "duplicate_tree_labels":sum(v-1 for v in rc.values() if v>1),
        "exact_matches":len(ts & rs),
        "matched":sorted(ts & rs),
        "trait_only":sorted(ts-rs),
        "tree_only":sorted(rs-ts),
        "automatic_synonym_substitution":False,
    }


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--color",type=Path,required=True)
    ap.add_argument("--tree",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()

    trait=project_tip_labels(a.color.read_bytes())
    tree=tree_tip_labels(a.tree.read_bytes())
    cw=crosswalk_summary(trait,tree)

    if cw["duplicate_trait_labels"] or cw["duplicate_tree_labels"]:
        status="HOLD_DUPLICATE_IDENTIFIER"
    elif cw["exact_matches"]<20:
        status="HOLD_CROSSWALK_LT_20"
    else:
        status=("IDENTIFIER_CROSSWALK_FROZEN_EXACT_INTERSECTION_COLOR_STATE_SUPPORT_PENDING"
                if cw["trait_only"] else
                "IDENTIFIER_CROSSWALK_FROZEN_COLOR_STATE_SUPPORT_PENDING")

    retained=sorted(set(trait)&set(tree))
    retained_sha=hashlib.sha256(("\n".join(retained)+"\n").encode()).hexdigest()
    out={
        "version":"v0.1",
        "status":status,
        "candidate":"RHODODENDRON_SECT_SCHISTANTHE",
        "identifier_column":"Tip_Label",
        "crosswalk":cw,
        "crosswalk_rule":"retain exact Tip_Label intersection after outer whitespace trim only; unmatched trait rows are excluded before phenotype opening; no synonym or fuzzy repair",
        "retained_exact_match_count":len(retained),
        "retained_exact_match_sha256":retained_sha,
        "excluded_trait_identifiers":cw["trait_only"],
        "flower_color_values_opened":False,
        "state_frequencies_computed":False,
        "hidden_memory_auc_computed":False,
        "next_gate":("OPEN_FROZEN_FLOWER_COLOR_COLUMN_FOR_SCHEMA_AND_STATE_SUPPORT_ONLY"
                     if status.startswith("IDENTIFIER_CROSSWALK_FROZEN") else "STOP_HOLD"),
        "el_v0_3_science_changed":False,
        "v0_7_promotion_state_changed":False,
        "paper1_science_changed":False,
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "status":status,
        "trait_labels":cw["trait_labels"],
        "tree_labels":cw["tree_labels"],
        "exact_matches":cw["exact_matches"],
        "trait_only":cw["trait_only"],
        "duplicate_trait_labels":cw["duplicate_trait_labels"],
        "duplicate_tree_labels":cw["duplicate_tree_labels"],
    },indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
