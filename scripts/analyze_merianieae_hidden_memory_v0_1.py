#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
INFO_SCRIPT=ROOT/"scripts"/"gate_merianieae_informativeness_v0_1.py"
spec=importlib.util.spec_from_file_location("info_gate",INFO_SCRIPT)
info_gate=importlib.util.module_from_spec(spec)
spec.loader.exec_module(info_gate)

B=9999
SEED=20260927


def analyse(frame_path:Path,tree_path:Path,info_path:Path)->dict:
    frame=json.loads(frame_path.read_text())
    info=json.loads(info_path.read_text())
    if info["status"]!="PRE_AUC_INFORMATION_GATE_PASS_OPEN_OBSERVED_AUC":
        raise ValueError("informativeness gate did not pass")
    fine,coarse,ii,jj,score=info_gate.build_pair_frame(frame,tree_path)
    observed=info_gate.auc_from_score_labels(score,fine[ii]==fine[jj])

    rng=np.random.default_rng(SEED)
    null=np.empty(B,float)
    for b in range(B):
        p=info_gate.permute_within_coarse(fine,coarse,rng)
        null[b]=info_gate.auc_from_score_labels(score,p[ii]==p[jj])
    mean=float(null.mean())
    centered=float(observed-mean)
    p=float((1+np.count_nonzero(null>=observed-1e-15))/(B+1))
    passed=bool(centered>0 and p<=.05)
    return {
      "version":"v0.1",
      "status":(
        "PROSPECTIVE_MERIANIEAE_VISIBLE_HIDDEN_MEMORY_PASS"
        if passed else
        "PROSPECTIVE_MERIANIEAE_VISIBLE_HIDDEN_MEMORY_FAIL"
      ),
      "candidate":"MERIANIEAE_MELASTOMATACEAE",
      "analysis_role":"INDEPENDENT_PROSPECTIVE_VISIBLE_HIDDEN_MEMORY_REPLICATION",
      "retained_tips":len(fine),
      "fine_state_counts":frame["fine_state_counts"],
      "coarse_state_counts":frame["coarse_state_counts"],
      "same_coarse_pairs":int(len(ii)),
      "same_fine_pairs_within_coarse":int(np.count_nonzero(fine[ii]==fine[jj])),
      "different_fine_pairs_within_coarse":int(np.count_nonzero(fine[ii]!=fine[jj])),
      "conditional_auc":float(observed),
      "null_mean_auc":mean,
      "centered_auc_effect":centered,
      "null_q025":float(np.quantile(null,.025)),
      "null_q975":float(np.quantile(null,.975)),
      "p_one_sided":p,
      "permutations":B,
      "seed":SEED,
      "pass_rule":"centered conditional AUC > 0 and one-sided permutation P <= 0.05 after the pre-AUC informativeness gate passes",
      "prospective_pass":passed,
      "no_posthoc_rescue":True,
      "ruellia_specific_promotion_rule_changed":False,
      "paper1_science_changed":False,
      "el_v0_3_science_changed":False
    }


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--frame",type=Path,required=True)
    ap.add_argument("--tree",type=Path,required=True)
    ap.add_argument("--info",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    out=analyse(a.frame,a.tree,a.info)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
