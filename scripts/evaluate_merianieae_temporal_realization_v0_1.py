#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def evaluate(pred_path:Path,result_path:Path)->dict:
    pred=json.loads(pred_path.read_text())
    result=json.loads(result_path.read_text())
    if pred["status"]!="MERIANIEAE_TEMPORAL_REALIZATION_PREDICTION_FROZEN_PRE_AUC":
        raise ValueError("temporal prediction unavailable")
    effect=float(result["centered_auc_effect"])
    threshold=float(pred["training_hidden_effect_median"])
    observed_class="ABOVE_TRAINING_MEDIAN" if effect>threshold else "AT_OR_BELOW_TRAINING_MEDIAN"
    match=observed_class==pred["predicted_hidden_effect_class"]
    return {
      "version":"v0.1",
      "status":"MERIANIEAE_TEMPORAL_REALIZATION_DIRECTION_MATCH" if match else "MERIANIEAE_TEMPORAL_REALIZATION_DIRECTION_MISMATCH",
      "analysis_role":"SECONDARY_PRE_AUC_OUT_OF_SAMPLE_DIRECTIONAL_PREDICTION",
      "fine_persistence_area":pred["fine_persistence_area"],
      "training_predictor_median":pred["training_predictor_median"],
      "predicted_hidden_effect_class":pred["predicted_hidden_effect_class"],
      "observed_centered_hidden_effect":effect,
      "training_hidden_effect_median":threshold,
      "observed_hidden_effect_class":observed_class,
      "direction_match":match,
      "no_significance_claim":True,
      "cannot_rescue_primary":True,
      "shared_colour_tree_information":True,
      "causal_claim_allowed":False,
      "paper1_science_changed":False,
      "el_v0_3_science_changed":False
    }


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--prediction",type=Path,required=True)
    ap.add_argument("--primary",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    out=evaluate(a.prediction,a.primary)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
