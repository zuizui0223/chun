#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np
from scipy.stats import rankdata, spearmanr

ROOT=Path(__file__).resolve().parents[1]
DESIGN=ROOT/"data"/"hidden_memory_vs_relative_persistence_design_v0_1.json"
HIDDEN=ROOT/"data"/"flowerclades51_hidden_fine_memory_clades_v0_1.csv"
PERSIST=ROOT/"data"/"flowerclades51_relative_time_persistence_clade_metrics_historical_v0_1.csv"
RECOVERY=ROOT/"data"/"flowerclades51_relative_time_persistence_clade_metrics_recovery_v0_1.json"

PERMUTATIONS=99999
BOOTSTRAPS=20000
SEED=20260927


def read_csv(path:Path)->list[dict]:
    with path.open(newline="",encoding="utf-8") as f:
        return list(csv.DictReader(f))


def rho(x,y)->float:
    r=float(spearmanr(np.asarray(x,float),np.asarray(y,float)).statistic)
    if not math.isfinite(r):
        raise ValueError("non-finite Spearman rho")
    return r


def perm_p_two_sided(x,y,obs:float,n:int=PERMUTATIONS,seed:int=SEED)->float:
    rng=np.random.default_rng(seed)
    xr=rankdata(np.asarray(x,float),method="average")
    yr=rankdata(np.asarray(y,float),method="average")
    xc=xr-xr.mean()
    yc=yr-yr.mean()
    xden=np.sqrt(np.sum(xc*xc))
    yden=np.sqrt(np.sum(yc*yc))
    target=abs(obs)
    extreme=0
    done=0
    batch=2048
    while done<n:
        b=min(batch,n-done)
        order=np.argsort(rng.random((b,len(yr))),axis=1)
        yp=yr[order]
        ypc=yp-yp.mean(axis=1,keepdims=True)
        rr=(ypc @ xc)/(xden*yden)
        extreme+=int(np.count_nonzero(np.abs(rr)>=target-1e-15))
        done+=b
    return float((extreme+1)/(n+1))


def bootstrap_rho(x,y,n:int=BOOTSTRAPS,seed:int=SEED)->dict:
    rng=np.random.default_rng(seed)
    x=np.asarray(x,float); y=np.asarray(y,float)
    vals=[]
    for _ in range(n):
        idx=rng.integers(0,len(x),size=len(x))
        if len(np.unique(x[idx]))<2 or len(np.unique(y[idx]))<2:
            continue
        r=float(spearmanr(x[idx],y[idx]).statistic)
        if math.isfinite(r):
            vals.append(r)
    a=np.asarray(vals,float)
    if len(a)<int(n*.95):
        raise RuntimeError("too many degenerate bootstrap samples")
    return {
      "requested":n,
      "usable":int(len(a)),
      "q025":float(np.quantile(a,.025)),
      "median":float(np.quantile(a,.5)),
      "q975":float(np.quantile(a,.975)),
      "positive_fraction":float(np.mean(a>0)),
    }


def build()->dict:
    design=json.loads(DESIGN.read_text())
    recovery=json.loads(RECOVERY.read_text())
    if recovery["status"]!="HISTORICAL_EXACT_SOURCE_DERIVED_ARTIFACT_RECOVERED":
        raise RuntimeError("historical persistence provenance not frozen")

    hidden=read_csv(HIDDEN)
    pers=read_csv(PERSIST)
    by={r["clade"]:r for r in pers}

    rows=[]
    for h in hidden:
        clade=h["clade"]
        if clade not in by:
            raise ValueError(f"missing persistence metric for {clade}")
        p=by[clade]
        if int(h["tips"])!=int(p["eligible_tips"]):
            raise ValueError(f"retained-tip mismatch for {clade}")
        rows.append({
          "clade":clade,
          "eligible_tips":int(h["tips"]),
          "hidden_centered_auc_effect":float(h["centered_auc_effect"]),
          "fine_area":float(p["fine_area"]),
          "fine_slope":float(p["fine_slope"]),
          "fine_near_far":float(p["fine_near_far"]),
          "coarse_area":float(p["coarse_area"]),
          "fine_area_minus_coarse_area":float(p["fine_area"])-float(p["coarse_area"]),
        })
    if len(rows)!=21:
        raise ValueError(f"expected 21 opportunity clades, got {len(rows)}")

    x=[r["fine_area"] for r in rows]
    y=[r["hidden_centered_auc_effect"] for r in rows]
    prho=rho(x,y)
    pp=perm_p_two_sided(x,y,prho)
    boot=bootstrap_rho(x,y)

    loo=[]
    for i,r in enumerate(rows):
        xx=[x[j] for j in range(len(x)) if j!=i]
        yy=[y[j] for j in range(len(y)) if j!=i]
        loo.append({"excluded":r["clade"],"rho":rho(xx,yy)})
    lr=[r["rho"] for r in loo]

    secondary={}
    for name in ("fine_slope","fine_near_far","fine_area_minus_coarse_area"):
        sr=spearmanr([r[name] for r in rows],y)
        secondary[name]={
          "rho":float(sr.statistic),
          "p_two_sided_asymptotic":float(sr.pvalue),
        }

    supported=bool(prho>0 and pp<=.05)
    interpretation=(
      "Across the existing visible-colour opportunity clades, stronger integrated persistence of exact fine colour through relative evolutionary divergence covaries with stronger within-coarse hidden fine-state memory. This links two non-independent summaries of the same source histories and provides a temporal interpretation, not an independent replication or causal mechanism."
      if supported else
      "The frozen primary test does not show that clades with greater integrated persistence of exact fine colour through relative evolutionary divergence also have stronger within-coarse hidden fine-state memory. Global fine-state persistence and hierarchical within-coarse organization therefore remain separable evolutionary axes in this exploratory comparison."
    )

    return {
      "version":"v0.1",
      "status":"HIDDEN_MEMORY_VS_RELATIVE_PERSISTENCE_EXPLORATORY_RESULT",
      "analysis_role":design["analysis_role"],
      "historical_persistence_provenance":{
        "source_branch":recovery["source_branch"],
        "source_branch_head":recovery["source_branch_head"],
        "source_git_blob_sha":recovery["source_git_blob_sha"],
        "underlying_exact_source_sha256":recovery["underlying_exact_source_sha256"],
      },
      "n_clades":len(rows),
      "primary":{
        "predictor":"fine_area",
        "outcome":"hidden_centered_auc_effect",
        "expected_direction":"positive",
        "rho":prho,
        "permutation_p_two_sided":pp,
        "permutations":PERMUTATIONS,
        "seed":SEED,
        "supported":supported,
        "bootstrap":boot,
        "leave_one_clade_out":{
          "min_rho":float(min(lr)),
          "max_rho":float(max(lr)),
          "positive_count":int(sum(v>0 for v in lr)),
          "negative_count":int(sum(v<0 for v in lr)),
        },
      },
      "secondary_descriptive":secondary,
      "rows":rows,
      "interpretation":interpretation,
      "claim_boundary":design["boundaries"],
      "paper1_science_changed":False,
      "el_v0_3_science_changed":False,
    }


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    out=build()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
      "status":out["status"],
      "n_clades":out["n_clades"],
      "primary":out["primary"],
      "secondary_descriptive":out["secondary_descriptive"],
      "interpretation":out["interpretation"],
    },indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
