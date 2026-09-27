#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from Bio import Phylo
from scipy.stats import rankdata

B=9999
SEED=20260927


def auc_from_score_labels(score:np.ndarray,y:np.ndarray)->float:
    score=np.asarray(score,float)
    y=np.asarray(y,bool)
    n1=int(y.sum())
    n0=int(len(y)-n1)
    if n1==0 or n0==0:
        raise ValueError("AUC requires both positive and negative pairs")
    ranks=rankdata(score,method="average")
    return float((ranks[y].sum()-n1*(n1+1)/2)/(n1*n0))


def prune_tree(tree,tips:list[str]):
    keep=set(tips)
    for t in list(tree.get_terminals()):
        if str(t.name or "").strip() not in keep:
            tree.prune(t)
    got={str(t.name or "").strip() for t in tree.get_terminals()}
    if got!=keep:
        raise ValueError(f"retained tree mismatch missing={sorted(keep-got)} extra={sorted(got-keep)}")
    return tree


def build_pair_frame(frame:dict,tree_path:Path):
    rows=frame["rows"]
    tips=[r["tree_tip"] for r in rows]
    fine=np.array([r["fine_state"] for r in rows],object)
    coarse=np.array([r["coarse_state"] for r in rows],object)
    tree=Phylo.read(str(tree_path),"newick")
    tree=prune_tree(tree,tips)
    by={str(t.name or "").strip():t for t in tree.get_terminals()}
    ii,jj=np.triu_indices(len(rows),1)
    same_coarse=coarse[ii]==coarse[jj]
    ii=ii[same_coarse]; jj=jj[same_coarse]
    score=np.array([-tree.distance(by[tips[int(a)]],by[tips[int(b)]]) for a,b in zip(ii,jj)],float)
    return fine,coarse,ii,jj,score


def permute_within_coarse(fine:np.ndarray,coarse:np.ndarray,rng)->np.ndarray:
    out=fine.copy()
    for c in sorted(set(coarse.tolist())):
        idx=np.flatnonzero(coarse==c)
        out[idx]=rng.permutation(out[idx])
    return out


def audit(frame_path:Path,tree_path:Path,gate_path:Path)->dict:
    frame=json.loads(frame_path.read_text())
    gate=json.loads(gate_path.read_text())
    if frame["status"]!="MERIANIEAE_STATE_SUPPORT_COMPRESSION_READY_PRE_INFORMATION_GATE":
        raise ValueError("state-support frame not ready")
    benchmark=float(gate["informativeness_rule"]["benchmark_centered_effect"])
    fine,coarse,ii,jj,score=build_pair_frame(frame,tree_path)
    rng=np.random.default_rng(SEED)
    null=np.empty(B,float)
    for b in range(B):
        p=permute_within_coarse(fine,coarse,rng)
        null[b]=auc_from_score_labels(score,p[ii]==p[jj])
    mean=float(null.mean())
    critical=float(np.quantile(null,.95))
    centered=float(critical-mean)
    pass_gate=bool(centered<=benchmark)
    return {
      "version":"v0.1",
      "status":(
        "PRE_AUC_INFORMATION_GATE_PASS_OPEN_OBSERVED_AUC"
        if pass_gate else
        "STRUCTURAL_LOW_INFORMATION_HOLD_OBSERVED_AUC_UNOPENED"
      ),
      "candidate":"MERIANIEAE_MELASTOMATACEAE",
      "retained_tips":len(fine),
      "same_coarse_pairs":int(len(ii)),
      "null_mean_auc":mean,
      "one_sided_alpha_0_05_auc_critical":critical,
      "centered_critical_effect":centered,
      "benchmark_centered_effect":benchmark,
      "informativeness_pass":pass_gate,
      "permutations":B,
      "seed":SEED,
      "observed_auc_computed":False,
      "hidden_memory_decision":"UNOPENED",
      "next_gate":"OPEN_OBSERVED_AUC" if pass_gate else "STOP_HOLD",
      "paper1_science_changed":False,
      "el_v0_3_science_changed":False
    }


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--frame",type=Path,required=True)
    ap.add_argument("--tree",type=Path,required=True)
    ap.add_argument("--gate",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    out=audit(a.frame,a.tree,a.gate)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
