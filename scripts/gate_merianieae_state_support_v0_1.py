#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path

MISSING={"","na","n/a","nan"}
NUMERIC_CODE_RE=re.compile(r"^[+-]?(?:\\d+(?:\\.\\d*)?|\\.\\d+)$")
MIN_FINE=5
MIN_TIPS=20


def norm_state(x:str)->str:
    return re.sub(r"\s+"," ",str(x or "").strip()).lower()


def is_numeric_code_token(x:str)->bool:
    return bool(NUMERIC_CODE_RE.fullmatch(norm_state(x)))


def read_rows(path:Path)->dict[int,dict]:
    out={}
    with path.open(newline="",encoding="utf-8-sig") as f:
        reader=csv.DictReader(f)
        fields=reader.fieldnames or []
        for req in ("x","species","corolla.colour"):
            if req not in fields:
                raise ValueError(f"required column missing: {req}")
        for i,row in enumerate(reader,start=2):
            out[i]=row
    return out


def build_state_frame(trait_path:Path,crosswalk_path:Path)->dict:
    cw=json.loads(crosswalk_path.read_text())
    if cw["status"]!="MERIANIEAE_IDENTIFIER_CROSSWALK_FROZEN_COROLLA_COLOUR_UNOPENED":
        raise ValueError("crosswalk not in ready state")
    rows=read_rows(trait_path)

    opened=[]
    for m in cw["matches"]:
        r=rows[int(m["source_row"])]
        if norm_state(r.get("x","")).replace("_"," ") != norm_state(m["source_x"]).replace("_"," "):
            raise ValueError(f"identifier drift at source row {m['source_row']}")
        fine=norm_state(r.get("corolla.colour",""))
        if fine in MISSING:
            continue
        opened.append({
          "source_row":int(m["source_row"]),
          "species":str(r.get("species") or "").strip(),
          "source_x":str(r.get("x") or "").strip(),
          "tree_tip":m["tree_tip"],
          "fine_state":fine,
        })

    raw_counts=Counter(r["fine_state"] for r in opened)
    retained_states=sorted(s for s,n in raw_counts.items() if n>=MIN_FINE)
    retained_set=set(retained_states)
    retained=[dict(r) for r in opened if r["fine_state"] in retained_set]

    fine_counts=Counter(r["fine_state"] for r in retained)
    numeric_code_schema=bool(retained and all(is_numeric_code_token(r["fine_state"]) for r in retained))

    # The admission contract allows WHITE/NONWHITE only for literal source
    # colour strings. A purely numeric coded field is a schema HOLD; do not
    # decode codes or reinterpret every code as NONWHITE after exposure.
    if numeric_code_schema:
        coarse_counts=Counter()
        opportunity=False
    else:
        for r in retained:
            r["coarse_state"]="WHITE" if r["fine_state"]=="white" else "NONWHITE"
        coarse_counts=Counter(r["coarse_state"] for r in retained)
        opportunity=bool(
            len(retained)>=MIN_TIPS
            and len(fine_counts)>=2
            and len(coarse_counts)>=2
            and len(fine_counts)>len(coarse_counts)
        )
    return {
      "matched_rows_before_colour_missingness":cw["matched_count"],
      "nonmissing_colour_rows":len(opened),
      "raw_fine_state_counts":dict(sorted(raw_counts.items())),
      "rare_fine_states_excluded":dict(sorted((s,n) for s,n in raw_counts.items() if n<MIN_FINE)),
      "retained_tips":len(retained),
      "fine_state_counts":dict(sorted(fine_counts.items())),
      "coarse_state_counts":dict(sorted(coarse_counts.items())),
      "fine_state_count":len(fine_counts),
      "coarse_state_count":len(coarse_counts),
      "numeric_code_schema":numeric_code_schema,
      "compression_opportunity":opportunity,
      "rows":retained,
    }


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--trait",type=Path,required=True)
    ap.add_argument("--crosswalk",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--frame-out",type=Path,required=True)
    a=ap.parse_args()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.frame_out.parent.mkdir(parents=True,exist_ok=True)

    x=build_state_frame(a.trait,a.crosswalk)
    if x["numeric_code_schema"]:
        status="HOLD_MERIANIEAE_COROLLA_COLOUR_NUMERIC_CODE_SCHEMA"
    elif x["retained_tips"]<MIN_TIPS:
        status="HOLD_MERIANIEAE_RETAINED_FRAME_LT_20"
    elif x["fine_state_count"]<2:
        status="HOLD_MERIANIEAE_FINE_STATES_LT_2"
    elif x["coarse_state_count"]<2:
        status="STRUCTURAL_NO_OPPORTUNITY_MERIANIEAE_COARSE_STATES_LT_2"
    elif not x["compression_opportunity"]:
        status="STRUCTURAL_NO_OPPORTUNITY_MERIANIEAE_FINE_NOT_GREATER_THAN_COARSE"
    else:
        status="MERIANIEAE_STATE_SUPPORT_COMPRESSION_READY_PRE_INFORMATION_GATE"

    frame={
      "version":"v0.1",
      "status":status,
      "rows":x["rows"],
      "retained_tips":x["retained_tips"],
      "fine_state_counts":x["fine_state_counts"],
      "coarse_state_counts":x["coarse_state_counts"],
      "fine_state_count":x["fine_state_count"],
      "coarse_state_count":x["coarse_state_count"],
      "numeric_code_schema":x["numeric_code_schema"],
    }
    a.frame_out.write_text(json.dumps(frame,indent=2,sort_keys=True)+"\n")

    out={
      "version":"v0.1",
      "status":status,
      **{k:v for k,v in x.items() if k!="rows"},
      "fine_state_rule":"exact corolla.colour after trim/lowercase/whitespace collapse; no semantic merging",
      "coarse_state_rule":"WHITE iff literal fine_state == 'white'; otherwise NONWHITE only for literal categorical colour strings",
      "schema_rule":"If the retained corolla.colour field is purely numeric-coded, stop at HOLD_SCHEMA and do not decode or coarsen it post-outcome.",
      "missing_tokens":sorted(MISSING),
      "minimum_fine_state_support":MIN_FINE,
      "minimum_retained_tips":MIN_TIPS,
      "corolla_colour_values_opened":True,
      "state_frequencies_computed":True,
      "hidden_memory_auc_computed":False,
      "next_gate":(
        "RUN_PRE_AUC_INFORMATION_GATE"
        if status=="MERIANIEAE_STATE_SUPPORT_COMPRESSION_READY_PRE_INFORMATION_GATE"
        else "STOP_TERMINAL"
      ),
      "paper1_science_changed":False,
      "el_v0_3_science_changed":False
    }
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
      "status":status,
      "matched_rows":x["matched_rows_before_colour_missingness"],
      "nonmissing_colour_rows":x["nonmissing_colour_rows"],
      "retained_tips":x["retained_tips"],
      "fine_state_counts":x["fine_state_counts"],
      "coarse_state_counts":x["coarse_state_counts"],
      "compression_opportunity":x["compression_opportunity"],
      "numeric_code_schema":x["numeric_code_schema"],
    },indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
