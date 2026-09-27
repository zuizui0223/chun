#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def maybe(path:Path):
    return json.loads(path.read_text()) if path.exists() else None


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--receipts",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    a.out.parent.mkdir(parents=True,exist_ok=True)

    source=maybe(a.receipts/"source.json")
    crosswalk=maybe(a.receipts/"crosswalk.json")
    support=maybe(a.receipts/"state_support.json")
    info=maybe(a.receipts/"informativeness.json")
    result=maybe(a.receipts/"hidden_memory_result.json")

    if result is not None:
        terminal=result["status"]
        biological_decision="PASS" if terminal.endswith("_PASS") else "FAIL"
        outcome_opened=True
    elif info is not None and info["status"]!="PRE_AUC_INFORMATION_GATE_PASS_OPEN_OBSERVED_AUC":
        terminal=info["status"]
        biological_decision="NONE_INFORMATION_HOLD"
        outcome_opened=False
    elif support is not None and support["status"]!="MERIANIEAE_STATE_SUPPORT_COMPRESSION_READY_PRE_INFORMATION_GATE":
        terminal=support["status"]
        biological_decision="NONE_STRUCTURAL_OR_SUPPORT_TERMINAL"
        outcome_opened=False
    elif crosswalk is not None and crosswalk["status"]!="MERIANIEAE_IDENTIFIER_CROSSWALK_FROZEN_COROLLA_COLOUR_UNOPENED":
        terminal=crosswalk["status"]
        biological_decision="NONE_CROSSWALK_HOLD"
        outcome_opened=False
    elif source is not None and source["status"]!="MERIANIEAE_EXACT_SOURCE_READY_COROLLA_COLOUR_UNOPENED":
        terminal=source["status"]
        biological_decision="NONE_SOURCE_HOLD"
        outcome_opened=False
    else:
        terminal="HOLD_MERIANIEAE_PIPELINE_INCOMPLETE"
        biological_decision="NONE_PIPELINE_INCOMPLETE"
        outcome_opened=False

    out={
      "version":"v0.1",
      "status":terminal,
      "candidate":"MERIANIEAE_MELASTOMATACEAE",
      "biological_decision":biological_decision,
      "observed_hidden_memory_auc_opened":outcome_opened,
      "source_status":source["status"] if source else None,
      "crosswalk_status":crosswalk["status"] if crosswalk else None,
      "state_support_status":support["status"] if support else None,
      "informativeness_status":info["status"] if info else None,
      "hidden_memory_status":result["status"] if result else None,
      "sequential_gate_order_preserved":True,
      "ruellia_specific_promotion_rule_changed":False,
      "paper1_science_changed":False,
      "el_v0_3_science_changed":False
    }
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
