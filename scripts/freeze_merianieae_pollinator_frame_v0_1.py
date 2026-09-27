#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path

MISSING={"","na","n/a","nan"}


def norm(x:str)->str:
    return re.sub(r"\s+"," ",str(x or "").strip()).lower()


def freeze_pollinator_frame(trait_path:Path,crosswalk_path:Path)->dict:
    cw=json.loads(crosswalk_path.read_text())
    if cw["status"]!="MERIANIEAE_IDENTIFIER_CROSSWALK_FROZEN_COROLLA_COLOUR_UNOPENED":
        raise ValueError("crosswalk not ready")
    wanted={int(m["source_row"]):m for m in cw["matches"]}
    rows=[]
    with trait_path.open(newline="",encoding="utf-8-sig") as f:
        reader=csv.DictReader(f)
        if "estimated_pollinator" not in (reader.fieldnames or []):
            raise ValueError("estimated_pollinator header missing")
        for i,row in enumerate(reader,start=2):
            if i not in wanted:
                continue
            p=norm(row.get("estimated_pollinator",""))
            if p in MISSING:
                continue
            m=wanted[i]
            rows.append({
              "source_row":i,
              "tree_tip":m["tree_tip"],
              "species":m["species"],
              "pollinator_state":p,
            })
    counts=Counter(r["pollinator_state"] for r in rows)
    ready=len(rows)>=20 and len(counts)>=2
    return {
      "version":"v0.1",
      "status":(
        "MERIANIEAE_POLLINATOR_FRAME_FROZEN_COROLLA_COLOUR_UNOPENED"
        if ready else
        "HOLD_MERIANIEAE_POLLINATOR_FRAME_INSUFFICIENT"
      ),
      "nonmissing_pollinator_tips":len(rows),
      "pollinator_state_count":len(counts),
      "pollinator_state_counts":dict(sorted(counts.items())),
      "rows":rows,
      "pollinator_column_accessed":True,
      "corolla_colour_column_accessed":False,
      "state_frequencies_computed":False,
      "hidden_memory_auc_computed":False,
      "secondary_ready":ready,
      "paper1_science_changed":False,
      "el_v0_3_science_changed":False
    }


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--trait",type=Path,required=True)
    ap.add_argument("--crosswalk",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    out=freeze_pollinator_frame(a.trait,a.crosswalk)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
      "status":out["status"],
      "nonmissing_pollinator_tips":out["nonmissing_pollinator_tips"],
      "pollinator_state_counts":out["pollinator_state_counts"],
    },indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
