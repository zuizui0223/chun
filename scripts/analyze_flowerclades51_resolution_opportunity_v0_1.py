#!/usr/bin/env python3
from __future__ import annotations

import argparse
import collections
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import binomtest, spearmanr, wilcoxon


def pair_same_q(states)->float:
    vals=list(states)
    n=len(vals)
    if n<2:
        raise ValueError("need at least two states")
    counts=collections.Counter(vals)
    return sum(v*(v-1) for v in counts.values())/(n*(n-1))


def shannon_entropy(states)->float:
    vals=list(states)
    if not vals:
        raise ValueError("empty states")
    counts=np.array(list(collections.Counter(vals).values()),dtype=float)
    p=counts/counts.sum()
    return float(-(p*np.log(p)).sum())


def compression_metrics(fine_states, fine_to_coarse:dict)->dict:
    fine=list(fine_states)
    missing=sorted(set(fine)-set(fine_to_coarse))
    if missing:
        raise ValueError(f"missing coarse mapping for {missing}")
    coarse=[fine_to_coarse[x] for x in fine]
    kf=len(set(fine)); kc=len(set(coarse))
    hf=shannon_entropy(fine); hc=shannon_entropy(coarse)
    qf=pair_same_q(fine); qc=pair_same_q(coarse)
    return {
        "fine_states":kf,
        "coarse_states":kc,
        "compression_opportunity":bool(kf>kc),
        "state_collapse_count":kf-kc,
        "entropy_loss":hf-hc,
        "pair_collision_gain":qc-qf,
    }


def _rho(x,y)->dict:
    r=spearmanr(np.asarray(x,dtype=float),np.asarray(y,dtype=float))
    return {"rho":float(r.statistic),"p_two_sided":float(r.pvalue)}


def analyze_metrics(d:pd.DataFrame)->dict:
    required={
        "clade","fine_states","coarse_states","state_collapse_fine_to_coarse",
        "entropy_loss_fine_to_coarse","collision_gain_fine_to_coarse",
        "amplitude","scale_tilt"
    }
    missing=sorted(required-set(d.columns))
    if missing:
        raise ValueError(f"missing columns: {missing}")
    if d["clade"].duplicated().any():
        raise ValueError("duplicate clade")

    x=d.copy()
    zero=x[x["state_collapse_fine_to_coarse"]==0].copy()
    opp=x[x["state_collapse_fine_to_coarse"]>0].copy()

    if len(opp)<3:
        raise ValueError("too few opportunity clades")

    tilt=opp["scale_tilt"].to_numpy(dtype=float)
    positive=int(np.sum(tilt>1e-12))
    negative=int(np.sum(tilt<-1e-12))
    zeros=int(len(tilt)-positive-negative)
    w=wilcoxon(tilt,alternative="greater",zero_method="wilcox")
    sign=binomtest(positive,positive+negative,0.5,alternative="greater") if positive+negative else None

    compression={}
    for col in (
        "state_collapse_fine_to_coarse",
        "entropy_loss_fine_to_coarse",
        "collision_gain_fine_to_coarse",
    ):
        compression[col]={
            "vs_signed_tilt":_rho(opp[col],opp["scale_tilt"]),
            "vs_absolute_tilt":_rho(opp[col],np.abs(opp["scale_tilt"])),
        }

    return {
        "n_clades":int(len(x)),
        "zero_opportunity":{
            "n_clades":int(len(zero)),
            "clades":zero["clade"].tolist(),
            "all_scale_tilt_zero":bool(np.allclose(zero["scale_tilt"].to_numpy(dtype=float),0.0,atol=1e-12)),
        },
        "opportunity":{
            "n_clades":int(len(opp)),
            "clades":opp["clade"].tolist(),
            "positive_tilt_clades":positive,
            "negative_tilt_clades":negative,
            "zero_tilt_clades":zeros,
            "median_scale_tilt":float(np.median(tilt)),
            "wilcoxon_tilt_gt_zero_p":float(w.pvalue),
            "sign_tilt_gt_zero_p":float(sign.pvalue) if sign is not None else None,
        },
        "compression_magnitude":compression,
        "specificity":{
            "fine_state_count_vs_scale_tilt_all":_rho(x["fine_states"],x["scale_tilt"]),
            "fine_state_count_vs_amplitude_all":_rho(x["fine_states"],x["amplitude"]),
        },
    }


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--metrics",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()

    d=pd.read_csv(args.metrics)
    a=analyze_metrics(d)
    headline={
        "status":"FLOWERCLADES51_RESOLUTION_OPPORTUNITY_EXPLORATORY_RESULT",
        "n_clades":a["n_clades"],
        "zero_opportunity_clades":a["zero_opportunity"]["n_clades"],
        "zero_opportunity_all_tilt_zero":a["zero_opportunity"]["all_scale_tilt_zero"],
        "opportunity_clades":a["opportunity"]["n_clades"],
        "opportunity_positive_tilt":a["opportunity"]["positive_tilt_clades"],
        "opportunity_negative_tilt":a["opportunity"]["negative_tilt_clades"],
        "median_tilt_opportunity":a["opportunity"]["median_scale_tilt"],
        "wilcoxon_tilt_gt_zero_p":a["opportunity"]["wilcoxon_tilt_gt_zero_p"],
        "fine_state_count_vs_tilt_rho":a["specificity"]["fine_state_count_vs_scale_tilt_all"]["rho"],
        "fine_state_count_vs_tilt_p":a["specificity"]["fine_state_count_vs_scale_tilt_all"]["p_two_sided"],
        "fine_state_count_vs_amplitude_rho":a["specificity"]["fine_state_count_vs_amplitude_all"]["rho"],
        "fine_state_count_vs_amplitude_p":a["specificity"]["fine_state_count_vs_amplitude_all"]["p_two_sided"],
        "interpretation":"Representation compression creates the opportunity for coarse-fine tilt, but compression magnitude does not determine realized tilt. Fine-state richness is associated with scale tilt but not with overall memory amplitude.",
        "claim_boundary":"post-outcome pilot-exposed exploratory analysis; frozen EL v0.3 unchanged",
    }
    out={
        "version":"v0.1",
        "status":"FLOWERCLADES51_RESOLUTION_OPPORTUNITY_EXPLORATORY_RESULT",
        "analysis_role":"EL_V0_5_EXTENSION_NOT_EL_V0_3_MODIFICATION",
        "n_clades":a["n_clades"],
        "zero_opportunity":a["zero_opportunity"],
        "opportunity":a["opportunity"],
        "source_provenance":{
            "final_dataset_sha256":"a253308785e4cbd0e361b3ca04cdfdae29c523eefa843375cebf8030ee0874af",
            "memory_architecture_merge_commit":"b54758a958542647d828d77e28327723d4d08287",
        },
        "headline":headline,
        "analysis":a,
        "el_v0_3_science_changed":False,
        "paper1_science_changed":False,
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(headline,indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
