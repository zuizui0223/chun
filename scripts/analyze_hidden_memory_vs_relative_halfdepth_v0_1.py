#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
from pathlib import Path

import numpy as np
from scipy.stats import rankdata, spearmanr

ROOT=Path(__file__).resolve().parents[1]
DESIGN=ROOT/"data"/"hidden_memory_vs_relative_halfdepth_design_v0_1.json"
HIDDEN=ROOT/"data"/"flowerclades51_hidden_fine_memory_clades_v0_1.csv"

def load_module(name:str,path:Path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

DIST=load_module("distance_persistence",ROOT/"scripts"/"run_flowerclades51_distance_persistence_v0_1.py")
HALF=load_module("halfdepth",ROOT/"scripts"/"run_flowerclades51_relative_time_halfdepth_v0_1.py")

PERMUTATIONS=99999
BOOTSTRAPS=20000
SEED=20260927

def rho(x,y)->float:
    r=float(spearmanr(np.asarray(x,float),np.asarray(y,float)).statistic)
    if not math.isfinite(r):
        raise ValueError("non-finite rho")
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
        keys=rng.random((b,len(yr)))
        order=np.argsort(keys,axis=1)
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
    return {
      "requested":n,"usable":int(len(a)),
      "q025":float(np.quantile(a,.025)),
      "median":float(np.quantile(a,.5)),
      "q975":float(np.quantile(a,.975)),
      "positive_fraction":float(np.mean(a>0)),
    }

def read_hidden()->dict[str,dict]:
    with HIDDEN.open(newline="",encoding="utf-8") as f:
        return {r["clade"]:r for r in csv.DictReader(f)}

def build(work:Path)->dict:
    design=json.loads(DESIGN.read_text())
    csv_path,trees_path,diagnostics=DIST.recover_exact_sources(work/"source")
    if csv_path is None or trees_path is None:
        return {
          "version":"v0.1",
          "status":"HOLD_EXACT_FLOWERCLADES51_SOURCE_BYTES_UNAVAILABLE_HALFDEPTH_RELATION_UNCOMPUTED",
          "download_diagnostics":diagnostics,
          "halfdepth_relation_computed":False,
          "paper1_science_changed":False,
          "el_v0_3_science_changed":False,
        }

    half=HALF.analyse(csv_path,trees_path)
    hidden=read_hidden()
    rows=[]
    for clade,h in hidden.items():
        d=half["results"].get(clade)
        if not d or d.get("status")!="RELATIVE_TIME_HALFDEPTH_COMPLETE":
            continue
        f=d["resolutions"]["fine"]
        c=d["resolutions"]["coarse"]
        rows.append({
          "clade":clade,
          "hidden_centered_auc_effect":float(h["centered_auc_effect"]),
          "fine_half_depth_ln2_over_lambda":float(f["half_depth_ln2_over_lambda"]),
          "fine_lambda":float(f["lambda"]),
          "fine_lambda_boundary":f["boundary"],
          "fine_pseudo_loglik_gain_over_q":float(f["pseudo_loglik_gain_over_q"]),
          "coarse_half_depth_ln2_over_lambda":float(c["half_depth_ln2_over_lambda"]),
          "fine_minus_coarse_half_depth":float(f["half_depth_ln2_over_lambda"]-c["half_depth_ln2_over_lambda"]),
        })
    if len(rows)!=21:
        raise ValueError(f"expected all 21 hidden-memory opportunity clades to have half-depth estimates, got {len(rows)}")

    y=[r["hidden_centered_auc_effect"] for r in rows]
    x=[r["fine_half_depth_ln2_over_lambda"] for r in rows]
    primary_rho=rho(x,y)
    primary_p=perm_p_two_sided(x,y,primary_rho)
    boot=bootstrap_rho(x,y)

    loo=[]
    for i,r in enumerate(rows):
        xx=[x[j] for j in range(len(x)) if j!=i]
        yy=[y[j] for j in range(len(y)) if j!=i]
        loo.append({"excluded":r["clade"],"rho":rho(xx,yy)})
    lr=[r["rho"] for r in loo]

    interior=[r for r in rows if r["fine_lambda_boundary"]=="INTERIOR"]
    interior_rel=None
    if len(interior)>=5:
        sr=spearmanr(
          [r["fine_half_depth_ln2_over_lambda"] for r in interior],
          [r["hidden_centered_auc_effect"] for r in interior],
        )
        interior_rel={"n":len(interior),"rho":float(sr.statistic),"p_two_sided_asymptotic":float(sr.pvalue)}

    secondary={}
    for name in ("fine_lambda","fine_pseudo_loglik_gain_over_q","fine_minus_coarse_half_depth"):
        sr=spearmanr([r[name] for r in rows],y)
        secondary[name]={"rho":float(sr.statistic),"p_two_sided_asymptotic":float(sr.pvalue)}

    supported=bool(primary_rho>0 and primary_p<=0.05)
    return {
      "version":"v0.1",
      "status":"HIDDEN_MEMORY_VS_RELATIVE_HALFDEPTH_EXPLORATORY_RESULT",
      "analysis_role":design["analysis_role"],
      "source_sha256":{"final_dataset.csv":HALF.CSV_SHA,"trees.zip":HALF.TREES_SHA},
      "n_clades":len(rows),
      "primary":{
        "predictor":"fine_half_depth_ln2_over_lambda",
        "outcome":"hidden_centered_auc_effect",
        "expected_direction":"positive",
        "rho":primary_rho,
        "permutation_p_two_sided":primary_p,
        "permutations":PERMUTATIONS,
        "seed":SEED,
        "supported":supported,
        "bootstrap":boot,
        "leave_one_clade_out":{
          "min_rho":float(min(lr)),"max_rho":float(max(lr)),
          "positive_count":int(sum(v>0 for v in lr)),
          "negative_count":int(sum(v<0 for v in lr)),
        }
      },
      "interior_fine_lambda_sensitivity":interior_rel,
      "secondary_descriptive":secondary,
      "rows":rows,
      "interpretation":(
        "Longer relative persistence of exact fine flower-colour states predicts stronger hierarchical hidden memory."
        if supported else
        "Hierarchical hidden memory is not positively explained by longer relative persistence of exact fine flower-colour states under the frozen primary test. Temporal persistence and within-coarse organization therefore remain separable evolutionary axes in this exploratory comparison."
      ),
      "claim_boundary":[
        "post-outcome exploratory relation between two estimands derived from shared source trees and colour states",
        "not independent replication",
        "relative divergence depth only; no absolute-time claim",
        "secondary and interior-only relations cannot rescue a failed primary test",
        "no ecological or molecular cause inferred",
        "frozen EL v0.3 remains unchanged"
      ],
      "download_diagnostics":diagnostics,
      "paper1_science_changed":False,
      "el_v0_3_science_changed":False,
    }

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--work",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    a.work.mkdir(parents=True,exist_ok=True)
    out=build(a.work)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
      "status":out["status"],
      "n_clades":out.get("n_clades"),
      "primary":out.get("primary"),
      "interior_fine_lambda_sensitivity":out.get("interior_fine_lambda_sensitivity"),
      "secondary_descriptive":out.get("secondary_descriptive"),
      "interpretation":out.get("interpretation"),
    },indent=2,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
