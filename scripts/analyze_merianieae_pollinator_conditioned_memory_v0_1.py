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
SEED=20260928


def permute_within_groups(fine:np.ndarray,groups:list[tuple],rng)->np.ndarray:
    out=fine.copy()
    by={}
    for i,g in enumerate(groups):
        by.setdefault(g,[]).append(i)
    for g,idxs in sorted(by.items(),key=lambda z:str(z[0])):
        idx=np.array(idxs,int)
        out[idx]=rng.permutation(out[idx])
    return out


def analyse(frame_path:Path,poll_path:Path,tree_path:Path,primary_path:Path)->dict:
    frame=json.loads(frame_path.read_text())
    poll=json.loads(poll_path.read_text())
    primary=json.loads(primary_path.read_text())
    if primary["status"]!="PROSPECTIVE_MERIANIEAE_VISIBLE_HIDDEN_MEMORY_PASS":
        raise ValueError("ecological diagnostic only opens after primary PASS")
    if poll["status"]!="MERIANIEAE_POLLINATOR_FRAME_FROZEN_COROLLA_COLOUR_UNOPENED":
        raise ValueError("pollinator frame not ready")

    pmap={r["tree_tip"]:r["pollinator_state"] for r in poll["rows"]}
    rows=[r for r in frame["rows"] if r["tree_tip"] in pmap]
    if len(rows)<20:
        raise ValueError("pollinator-complete retained frame <20")
    compact={
      "rows":rows,
      "status":"MERIANIEAE_STATE_SUPPORT_COMPRESSION_READY_PRE_INFORMATION_GATE"
    }
    fine,coarse,ii,jj,score=info_gate.build_pair_frame(compact,tree_path)
    pollstates=np.array([pmap[r["tree_tip"]] for r in rows],object)
    if len(set(pollstates.tolist()))<2:
        raise ValueError("pollinator states <2")

    observed=info_gate.auc_from_score_labels(score,fine[ii]==fine[jj])
    rngA=np.random.default_rng(SEED)
    rngB=np.random.default_rng(SEED)
    nullA=np.empty(B,float)
    nullB=np.empty(B,float)
    groupsA=[(str(c),) for c in coarse.tolist()]
    groupsB=[(str(c),str(p)) for c,p in zip(coarse.tolist(),pollstates.tolist())]
    for b in range(B):
        pa=permute_within_groups(fine,groupsA,rngA)
        pb=permute_within_groups(fine,groupsB,rngB)
        nullA[b]=info_gate.auc_from_score_labels(score,pa[ii]==pa[jj])
        nullB[b]=info_gate.auc_from_score_labels(score,pb[ii]==pb[jj])

    meanA=float(nullA.mean()); meanB=float(nullB.mean())
    centeredA=float(observed-meanA); centeredB=float(observed-meanB)
    pA=float((1+np.count_nonzero(nullA>=observed-1e-15))/(B+1))
    pB=float((1+np.count_nonzero(nullB>=observed-1e-15))/(B+1))
    attenuation=float(centeredA-centeredB)
    fraction=float(attenuation/centeredA) if centeredA>0 else None
    residual=bool(centeredB>0 and pB<=.05)
    return {
      "version":"v0.1",
      "status":(
        "MERIANIEAE_HIDDEN_MEMORY_PERSISTS_BEYOND_POLLINATOR_GROUPING"
        if residual else
        "MERIANIEAE_POLLINATOR_GROUPING_COMPATIBLE_WITH_HIDDEN_MEMORY_ATTENUATION"
      ),
      "analysis_role":"SECONDARY_ECOLOGICAL_BOUNDARY_AFTER_PRIMARY_PROSPECTIVE_PASS",
      "pollinator_complete_tips":len(rows),
      "pollinator_state_counts":{p:int(np.count_nonzero(pollstates==p)) for p in sorted(set(pollstates.tolist()))},
      "observed_conditional_auc":float(observed),
      "coarse_only_null_mean_auc":meanA,
      "coarse_only_centered_effect":centeredA,
      "coarse_only_p_one_sided":pA,
      "coarse_x_pollinator_null_mean_auc":meanB,
      "pollinator_conditioned_centered_effect":centeredB,
      "pollinator_conditioned_p_one_sided":pB,
      "centered_effect_attenuation":attenuation,
      "attenuation_fraction_of_coarse_only_effect":fraction,
      "residual_hidden_memory_beyond_pollinator_grouping":residual,
      "permutations_each_null":B,
      "seed":SEED,
      "causal_claim_allowed":False,
      "cannot_rescue_primary":True,
      "paper1_science_changed":False,
      "el_v0_3_science_changed":False
    }


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--frame",type=Path,required=True)
    ap.add_argument("--pollinator",type=Path,required=True)
    ap.add_argument("--tree",type=Path,required=True)
    ap.add_argument("--primary",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    out=analyse(a.frame,a.pollinator,a.tree,a.primary)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
