#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from Bio import Phylo
from scipy.stats import rankdata

PERMUTATIONS=9999
SEED=20260920
READY_STATUS="GESNERIOIDEAE_BIOCHEMICAL_HIDDEN_MEMORY_OPPORTUNITY_CONFIRMED"


def same_coarse_pair_indices(coarse:np.ndarray)->tuple[np.ndarray,np.ndarray]:
    coarse=np.asarray(coarse)
    ii,jj=np.triu_indices(len(coarse),1)
    keep=coarse[ii]==coarse[jj]
    return ii[keep],jj[keep]


def auc_from_y_ranks(y:np.ndarray,ranks:np.ndarray)->float:
    y=np.asarray(y,dtype=bool)
    ranks=np.asarray(ranks,dtype=float)
    n1=int(y.sum()); n0=len(y)-n1
    if n1==0 or n0==0:
        raise ValueError("conditional AUC response has one class")
    return float((ranks[y].sum()-n1*(n1+1)/2)/(n1*n0))


def permute_fine_within_coarse(
    fine:np.ndarray,coarse:np.ndarray,rng:np.random.Generator
)->np.ndarray:
    fine=np.asarray(fine).copy()
    coarse=np.asarray(coarse)
    out=fine.copy()
    for g in np.unique(coarse):
        idx=np.where(coarse==g)[0]
        out[idx]=rng.permutation(fine[idx])
    return out


def centered_effect(observed:float,null:np.ndarray)->float:
    return float(observed-np.mean(np.asarray(null,dtype=float)))


def analyze(
    gate_path:Path,
    frame_path:Path,
    tree_path:Path,
    permutations:int=PERMUTATIONS,
    seed:int=SEED,
)->dict:
    gate=json.loads(gate_path.read_text())
    if gate["status"]!=READY_STATUS:
        raise RuntimeError(f"state-support gate not open: {gate['status']}")
    if gate.get("hidden_memory_auc_computed") is not False:
        raise RuntimeError("pre-AUC gate firewall drift")
    if not gate.get("compression_opportunity"):
        raise RuntimeError("compression opportunity false")

    frame=json.loads(frame_path.read_text())
    rows=frame["rows"]
    if frame.get("hidden_memory_auc_computed") is not False:
        raise RuntimeError("state frame AUC firewall drift")
    if len(rows)!=gate["common_frame_tips"]:
        raise ValueError("state-frame size drift")
    tips=[r["tree_tip"] for r in rows]
    if len(tips)!=len(set(tips)):
        raise ValueError("duplicate retained tree tips")

    tree=Phylo.read(str(tree_path),"newick")
    original={t.name for t in tree.get_terminals()}
    if not set(tips)<=original:
        raise ValueError("retained state-frame tips missing from pruned tree")
    for terminal in list(tree.get_terminals()):
        if terminal.name not in set(tips):
            tree.prune(terminal)
    if {t.name for t in tree.get_terminals()}!=set(tips):
        raise ValueError("final tree/frame mismatch")

    coarse_labels=[r["coarse_state"] for r in rows]
    fine_labels=[r["fine_state"] for r in rows]
    cmap={x:i for i,x in enumerate(sorted(set(coarse_labels)))}
    fmap={x:i for i,x in enumerate(sorted(set(fine_labels)))}
    coarse=np.array([cmap[x] for x in coarse_labels],dtype=np.int8)
    fine=np.array([fmap[x] for x in fine_labels],dtype=np.int16)

    if len(fmap)<=len(cmap):
        raise RuntimeError("opportunity disappeared before estimator")
    if len(cmap)<2 or len(fmap)<2:
        raise RuntimeError("state support disappeared before estimator")

    terminals={t.name:t for t in tree.get_terminals()}
    ii,jj=same_coarse_pair_indices(coarse)
    dist=np.array([
        tree.distance(terminals[tips[int(a)]],terminals[tips[int(b)]])
        for a,b in zip(ii,jj)
    ],dtype=float)
    if not np.isfinite(dist).all():
        raise ValueError("non-finite patristic distance")
    ranks=rankdata(-dist,method="average").astype(float)
    y=fine[ii]==fine[jj]
    observed=auc_from_y_ranks(y,ranks)

    rng=np.random.default_rng(seed)
    null=np.empty(permutations,dtype=float)
    for b in range(permutations):
        p=permute_fine_within_coarse(fine,coarse,rng)
        null[b]=auc_from_y_ranks(p[ii]==p[jj],ranks)

    null_mean=float(null.mean())
    effect=centered_effect(observed,null)
    p_one=(1+int(np.count_nonzero(null>=observed)))/(permutations+1)
    passed=bool(effect>0 and p_one<=0.05)
    status=("PROSPECTIVE_GESNERIOIDEAE_BIOCHEMICAL_HIDDEN_MEMORY_PASS"
            if passed else
            "PROSPECTIVE_GESNERIOIDEAE_BIOCHEMICAL_HIDDEN_MEMORY_FAIL")

    return {
      "version":"v0.1",
      "status":status,
      "analysis_role":"TARGET_ESTIMAND_PROSPECTIVE_NOT_LITERATURE_BLINDED",
      "eligible_tips":len(rows),
      "coarse_state_counts":gate["retained_coarse_frequencies"],
      "fine_state_counts":gate["retained_fine_frequencies"],
      "fine_state_count":len(fmap),
      "coarse_state_count":len(cmap),
      "same_coarse_pairs":int(len(ii)),
      "same_fine_positive_pairs":int(y.sum()),
      "different_fine_negative_pairs":int(len(y)-y.sum()),
      "conditional_auc":float(observed),
      "null_mean_auc":null_mean,
      "centered_auc_effect":effect,
      "null_q025":float(np.quantile(null,0.025)),
      "null_q975":float(np.quantile(null,0.975)),
      "p_one_sided":float(p_one),
      "permutations":permutations,
      "seed":seed,
      "pass_rule":"centered_auc_effect > 0 and one-sided permutation P <= 0.05, conditional on frozen compression opportunity",
      "promotion_gate_pass":passed,
      "chemistry_values_opened":True,
      "state_frequencies_computed":True,
      "hidden_memory_auc_computed":True,
      "ruellia_specific_v0_7_v0_8_gate_changed":False,
      "el_v0_3_science_changed":False,
      "paper1_science_changed":False,
    }


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--gate",type=Path,required=True)
    ap.add_argument("--frame",type=Path,required=True)
    ap.add_argument("--tree",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--permutations",type=int,default=PERMUTATIONS)
    ap.add_argument("--seed",type=int,default=SEED)
    a=ap.parse_args()
    out=analyze(a.gate,a.frame,a.tree,a.permutations,a.seed)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
