#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

ROOT=Path(__file__).resolve().parents[1]
HIDDEN=ROOT/"data"/"flowerclades51_hidden_fine_memory_clades_v0_1.csv"
STRUCT=ROOT/"data"/"flowerclades51_resolution_opportunity_metrics_v0_1.csv"
DESIGN=ROOT/"data"/"hidden_memory_realization_structural_predictors_design_v0_1.json"

PERMUTATIONS=99999
BOOTSTRAPS=20000
SEED=20260927


def read_csv(path:Path)->list[dict]:
    with path.open(newline="",encoding="utf-8") as f:
        return list(csv.DictReader(f))


def rho(x,y)->float:
    r=float(spearmanr(np.asarray(x,dtype=float),np.asarray(y,dtype=float)).statistic)
    if not math.isfinite(r):
        raise ValueError("non-finite Spearman rho")
    return r


def perm_p_two_sided(x,y,observed:float,permutations:int=PERMUTATIONS,seed:int=SEED)->float:
    rng=np.random.default_rng(seed)
    x=np.asarray(x,dtype=float)
    y=np.asarray(y,dtype=float)
    extreme=0
    target=abs(observed)
    for _ in range(permutations):
        r=rho(x,rng.permutation(y))
        if abs(r)>=target-1e-15:
            extreme+=1
    return float((extreme+1)/(permutations+1))


def bootstrap_rho(x,y,n:int=BOOTSTRAPS,seed:int=SEED)->dict:
    rng=np.random.default_rng(seed)
    x=np.asarray(x,dtype=float)
    y=np.asarray(y,dtype=float)
    vals=[]
    for _ in range(n):
        idx=rng.integers(0,len(x),size=len(x))
        if len(np.unique(x[idx]))<2 or len(np.unique(y[idx]))<2:
            continue
        r=float(spearmanr(x[idx],y[idx]).statistic)
        if math.isfinite(r):
            vals.append(r)
    a=np.asarray(vals,dtype=float)
    if len(a)<int(n*0.95):
        raise RuntimeError("too many degenerate bootstrap replicates")
    return {
        "requested":n,
        "usable":int(len(a)),
        "q025":float(np.quantile(a,0.025)),
        "median":float(np.quantile(a,0.5)),
        "q975":float(np.quantile(a,0.975)),
        "positive_fraction":float(np.mean(a>0)),
    }


def build()->dict:
    design=json.loads(DESIGN.read_text())
    hidden=read_csv(HIDDEN)
    structural=read_csv(STRUCT)
    by={r["clade"]:r for r in structural}

    rows=[]
    for h in hidden:
        if h["clade"] not in by:
            raise ValueError(f"missing structural row {h['clade']}")
        s=by[h["clade"]]
        if int(s["state_collapse_fine_to_coarse"])<=0:
            raise ValueError(f"hidden-memory clade lacks opportunity: {h['clade']}")
        rows.append({
            "clade":h["clade"],
            "centered_auc_effect":float(h["centered_auc_effect"]),
            "collision_gain_fine_to_coarse":float(s["collision_gain_fine_to_coarse"]),
            "entropy_loss_fine_to_coarse":float(s["entropy_loss_fine_to_coarse"]),
            "state_collapse_fine_to_coarse":int(s["state_collapse_fine_to_coarse"]),
            "fine_states":int(s["fine_states"]),
            "eligible_tips":int(s["eligible_tips"]),
            "log10_eligible_tips":float(np.log10(int(s["eligible_tips"]))),
        })

    if len(rows)!=21:
        raise ValueError(f"expected 21 opportunity clades, got {len(rows)}")
    if [r["clade"] for r in rows] != [r["clade"] for r in hidden]:
        raise ValueError("clade order drift")

    y=[r["centered_auc_effect"] for r in rows]
    primary_name=design["primary_hypothesis"]["predictor"]
    x=[r[primary_name] for r in rows]
    primary_rho=rho(x,y)
    primary_p=perm_p_two_sided(x,y,primary_rho)
    boot=bootstrap_rho(x,y)

    loo=[]
    for i,row in enumerate(rows):
        xx=[x[j] for j in range(len(x)) if j!=i]
        yy=[y[j] for j in range(len(y)) if j!=i]
        loo.append({"excluded":row["clade"],"rho":rho(xx,yy)})
    loo_rhos=[r["rho"] for r in loo]

    secondary={}
    for name in design["secondary_descriptive_predictors"]:
        xx=[r[name] for r in rows]
        sr=spearmanr(xx,y)
        secondary[name]={
            "rho":float(sr.statistic),
            "p_two_sided_asymptotic":float(sr.pvalue),
        }

    supported=bool(primary_rho>0 and primary_p<=0.05)
    return {
        "version":"v0.1",
        "status":"HIDDEN_MEMORY_STRUCTURAL_REALIZATION_EXPLORATORY_RESULT",
        "analysis_role":design["analysis_role"],
        "n_clades":len(rows),
        "primary":{
            "predictor":primary_name,
            "predicted_direction":"positive",
            "rho":primary_rho,
            "permutation_p_two_sided":primary_p,
            "permutations":PERMUTATIONS,
            "seed":SEED,
            "bootstrap":boot,
            "leave_one_clade_out":{
                "min_rho":float(min(loo_rhos)),
                "max_rho":float(max(loo_rhos)),
                "positive_count":int(sum(r>0 for r in loo_rhos)),
                "negative_count":int(sum(r<0 for r in loo_rhos)),
                "details":loo,
            },
            "supported":supported,
        },
        "secondary_descriptive":secondary,
        "rows":rows,
        "interpretation":(
            "The preregistered pair-collision measure of fine-to-coarse representation opportunity does not positively predict the magnitude of hidden fine-state memory. "
            "Thus the recurrent hidden-memory signal is not explained by the trivial amount of pairwise state collision created by coarse coding. "
            "Secondary structural correlations are descriptive only and cannot replace the failed primary hypothesis."
        ),
        "biological_implication":(
            "Opportunity determines whether hidden fine structure can exist, but simple combinatorial opportunity does not determine how strongly lineage history is realized inside coarse phenotype classes. "
            "The remaining among-radiation variation therefore requires lineage history, transition dynamics, ecology, or other biological structure not captured by these state-space compression metrics."
        ),
        "claim_boundary":[
            "post-outcome exploratory analysis",
            "primary structural hypothesis failed unless rho > 0 and permutation P <= 0.05",
            "secondary predictors are descriptive and cannot rescue the primary test",
            "no ecological or molecular cause is inferred",
            "no new environmental predictor was searched",
            "frozen EL v0.3 remains unchanged"
        ],
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
