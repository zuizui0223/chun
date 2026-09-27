#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np
from Bio import Phylo

TRAIN_PRED_MEDIAN=0.022164300864659012
TRAIN_EFFECT_MEDIAN=0.02700779596581926
CV_MAX=1e-8
N_BINS=10


def pair_baseline(states:np.ndarray)->float:
    n=len(states)
    counts=Counter(states.tolist())
    return sum(v*(v-1)//2 for v in counts.values())/(n*(n-1)//2)


def root_to_tip_cv(tree)->float:
    x=np.array([tree.distance(tree.root,t) for t in tree.get_terminals()],float)
    return float(x.std(ddof=0)/x.mean())


def signed_area(tree,tips:list[str],states:np.ndarray)->dict:
    by={str(t.name or "").strip():t for t in tree.get_terminals()}
    keep=set(tips)
    if set(by)!=keep:
        raise ValueError("tree/frame tip mismatch")
    cv=root_to_tip_cv(tree)
    if not np.isfinite(cv) or cv>CV_MAX:
        return {
          "status":"HOLD_MERIANIEAE_TEMPORAL_PREDICTION_TREE_NOT_ULTRAMETRIC",
          "root_to_tip_cv":cv,
          "fine_persistence_area":None,
        }
    h=float(np.mean([tree.distance(tree.root,t) for t in tree.get_terminals()]))
    ii,jj=np.triu_indices(len(tips),1)
    d=np.array([tree.distance(by[tips[int(a)]],by[tips[int(b)]])/(2*h) for a,b in zip(ii,jj)],float)
    same=states[ii]==states[jj]
    q=pair_baseline(states)
    denom=1-q
    order=np.argsort(d,kind="stable")
    groups=np.array_split(order,min(N_BINS,len(order)))
    bins=[]
    for bi,idx in enumerate(groups,1):
        ps=float(np.mean(same[idx]))
        ex=float((ps-q)/denom)
        bins.append({
          "bin":bi,
          "n_pairs":int(len(idx)),
          "mean_relative_depth":float(np.mean(d[idx])),
          "p_same":ps,
          "excess_retention":ex,
        })
    xx=np.array([b["mean_relative_depth"] for b in bins],float)
    yy=np.array([b["excess_retention"] for b in bins],float)
    area=float(np.trapezoid(yy,xx))
    return {
      "status":"MERIANIEAE_TEMPORAL_REALIZATION_PREDICTION_FROZEN_PRE_AUC",
      "root_to_tip_cv":cv,
      "fine_persistence_area":area,
      "bins":bins,
    }


def build(frame_path:Path,tree_path:Path)->dict:
    frame=json.loads(frame_path.read_text())
    if frame["status"]!="MERIANIEAE_STATE_SUPPORT_COMPRESSION_READY_PRE_INFORMATION_GATE":
        raise ValueError("state support not ready")
    rows=frame["rows"]
    tips=[r["tree_tip"] for r in rows]
    states=np.array([r["fine_state"] for r in rows],object)
    tree=Phylo.read(str(tree_path),"newick")
    x=signed_area(tree,tips,states)
    if x["status"].startswith("HOLD_"):
        return {
          "version":"v0.1",
          **x,
          "prediction_opened":False,
          "hidden_memory_auc_computed":False,
          "cannot_rescue_primary":True,
          "paper1_science_changed":False,
          "el_v0_3_science_changed":False
        }
    area=float(x["fine_persistence_area"])
    predicted_high=bool(area>TRAIN_PRED_MEDIAN)
    return {
      "version":"v0.1",
      **x,
      "training_predictor_median":TRAIN_PRED_MEDIAN,
      "training_hidden_effect_median":TRAIN_EFFECT_MEDIAN,
      "predicted_hidden_effect_class":"ABOVE_TRAINING_MEDIAN" if predicted_high else "AT_OR_BELOW_TRAINING_MEDIAN",
      "prediction_rule":"fine persistence area > training median predicts centered hidden-memory effect > training hidden-effect median; otherwise predicts at-or-below",
      "prediction_opened":True,
      "hidden_memory_auc_computed":False,
      "cannot_rescue_primary":True,
      "paper1_science_changed":False,
      "el_v0_3_science_changed":False
    }


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--frame",type=Path,required=True)
    ap.add_argument("--tree",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    out=build(a.frame,a.tree)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
      "status":out["status"],
      "root_to_tip_cv":out.get("root_to_tip_cv"),
      "fine_persistence_area":out.get("fine_persistence_area"),
      "predicted_hidden_effect_class":out.get("predicted_hidden_effect_class"),
      "hidden_memory_auc_computed":out["hidden_memory_auc_computed"]
    },indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
