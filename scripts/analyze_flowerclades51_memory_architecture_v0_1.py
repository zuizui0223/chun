#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr, wilcoxon

HOLD_CLASS="HOLD_INSUFFICIENT_COMMON_FRAME_OR_STATE_VARIATION"


def memory_coordinates(c:float,i:float,f:float)->dict:
    return {
        "amplitude":(c+i+f)/3.0-0.5,
        "scale_tilt":f-c,
        "intermediate_curvature":i-(c+f)/2.0,
    }


def orthogonal_coordinates(x:np.ndarray)->np.ndarray:
    x=np.asarray(x,dtype=float)
    if x.ndim!=2 or x.shape[1]!=3:
        raise ValueError("x must be n x 3 in coarse/intermediate/fine order")
    c,i,f=x[:,0],x[:,1],x[:,2]
    return np.column_stack([
        (c+i+f)/np.sqrt(3.0),
        (f-c)/np.sqrt(2.0),
        (2.0*i-c-f)/np.sqrt(6.0),
    ])


def _completed(d:pd.DataFrame)->pd.DataFrame:
    req=["clade","terminal_class","AUC_coarse","AUC_intermediate","AUC_fine"]
    missing=[x for x in req if x not in d.columns]
    if missing:
        raise ValueError(f"missing profile columns: {missing}")
    x=d[d["terminal_class"]!=HOLD_CLASS].copy()
    x=x.dropna(subset=["AUC_coarse","AUC_intermediate","AUC_fine"])
    return x


def _variance_share_from_matrix(x:np.ndarray)->np.ndarray:
    z=orthogonal_coordinates(x)
    centered=z-z.mean(axis=0)
    ss=(centered**2).sum(axis=0)
    total=float(ss.sum())
    if total<=0:
        return np.array([np.nan,np.nan,np.nan])
    return ss/total


def profile_architecture(d:pd.DataFrame,bootstrap_replicates:int=10000,seed:int=20260919)->dict:
    x=_completed(d)
    mat=x[["AUC_coarse","AUC_intermediate","AUC_fine"]].to_numpy(dtype=float)
    share=_variance_share_from_matrix(mat)

    coords=[]
    for row in x.itertuples(index=False):
        q=memory_coordinates(float(row.AUC_coarse),float(row.AUC_intermediate),float(row.AUC_fine))
        coords.append({"clade":row.clade,**q})
    cdf=pd.DataFrame(coords)

    rng=np.random.default_rng(seed)
    boots=np.empty((bootstrap_replicates,3),dtype=float)
    n=len(x)
    for b in range(bootstrap_replicates):
        idx=rng.integers(0,n,n)
        boots[b]=_variance_share_from_matrix(mat[idx])

    ci={}
    names=["amplitude","scale_tilt","intermediate_curvature"]
    for j,name in enumerate(names):
        ci[name]={
            "q025":float(np.nanquantile(boots[:,j],0.025)),
            "median":float(np.nanquantile(boots[:,j],0.5)),
            "q975":float(np.nanquantile(boots[:,j],0.975)),
        }

    abs_tilt=np.abs(cdf["scale_tilt"].to_numpy())
    abs_curv=np.abs(cdf["intermediate_curvature"].to_numpy())
    w=wilcoxon(abs_tilt,abs_curv,alternative="greater",zero_method="wilcox")
    curv_zero=wilcoxon(cdf["intermediate_curvature"],alternative="two-sided",zero_method="wilcox")
    tilt_zero=wilcoxon(cdf["scale_tilt"],alternative="two-sided",zero_method="wilcox")

    return {
        "n_clades":int(len(x)),
        "clades":cdf["clade"].tolist(),
        "coordinates":coords,
        "variance_share":{
            "amplitude":float(share[0]),
            "scale_tilt":float(share[1]),
            "intermediate_curvature":float(share[2]),
        },
        "variance_share_bootstrap95":ci,
        "geometry":{
            "median_absolute_scale_tilt":float(np.median(abs_tilt)),
            "median_absolute_intermediate_curvature":float(np.median(abs_curv)),
            "wilcoxon_abs_tilt_greater_than_abs_curvature_p":float(w.pvalue),
            "median_scale_tilt":float(np.median(cdf["scale_tilt"])),
            "wilcoxon_scale_tilt_vs_zero_p_two_sided":float(tilt_zero.pvalue),
            "median_intermediate_curvature":float(np.median(cdf["intermediate_curvature"])),
            "wilcoxon_curvature_vs_zero_p_two_sided":float(curv_zero.pvalue),
            "positive_tilt_clades":int((cdf["scale_tilt"]>1e-12).sum()),
            "negative_tilt_clades":int((cdf["scale_tilt"]<-1e-12).sum()),
            "zero_tilt_clades":int((np.abs(cdf["scale_tilt"])<=1e-12).sum()),
        }
    }


def _rho(x,y)->dict:
    r=spearmanr(np.asarray(x,float),np.asarray(y,float))
    return {"rho":float(r.statistic),"p_two_sided":float(r.pvalue)}


def temporal_bridge(profiles:pd.DataFrame,persistence:pd.DataFrame)->dict:
    x=_completed(profiles)
    coords=[]
    for row in x.itertuples(index=False):
        q=memory_coordinates(float(row.AUC_coarse),float(row.AUC_intermediate),float(row.AUC_fine))
        coords.append({"clade":row.clade,**q})
    cdf=pd.DataFrame(coords)
    p=persistence[["clade","slope","area","near_far"]].copy()
    j=cdf.merge(p,on="clade",how="inner",validate="one_to_one")
    if len(j)<3:
        raise ValueError("too few joined clades")
    return {
        "n_clades":int(len(j)),
        "amplitude_vs_slope":_rho(j["amplitude"],j["slope"]),
        "amplitude_vs_area":_rho(j["amplitude"],j["area"]),
        "amplitude_vs_near_far":_rho(j["amplitude"],j["near_far"]),
        "scale_tilt_vs_slope":_rho(j["scale_tilt"],j["slope"]),
        "scale_tilt_vs_area":_rho(j["scale_tilt"],j["area"]),
        "scale_tilt_vs_near_far":_rho(j["scale_tilt"],j["near_far"]),
        "curvature_vs_slope":_rho(j["intermediate_curvature"],j["slope"]),
        "curvature_vs_area":_rho(j["intermediate_curvature"],j["area"]),
        "amplitude_vs_scale_tilt":_rho(j["amplitude"],j["scale_tilt"]),
    }


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--profiles",type=Path,required=True)
    ap.add_argument("--persistence",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--bootstrap",type=int,default=10000)
    ap.add_argument("--seed",type=int,default=20260919)
    args=ap.parse_args()

    profiles=pd.read_csv(args.profiles)
    persistence=pd.read_csv(args.persistence)
    arch=profile_architecture(profiles,args.bootstrap,args.seed)
    bridge=temporal_bridge(profiles,persistence)

    headline={
        "status":"FLOWERCLADES51_MEMORY_ARCHITECTURE_EXPLORATORY_RESULT",
        "n_clades":arch["n_clades"],
        "variance_share":arch["variance_share"],
        "amplitude_temporal_bridge":{
            "slope_rho":bridge["amplitude_vs_slope"]["rho"],
            "slope_p":bridge["amplitude_vs_slope"]["p_two_sided"],
            "area_rho":bridge["amplitude_vs_area"]["rho"],
            "area_p":bridge["amplitude_vs_area"]["p_two_sided"],
        },
        "scale_tilt_temporal_bridge":{
            "slope_rho":bridge["scale_tilt_vs_slope"]["rho"],
            "slope_p":bridge["scale_tilt_vs_slope"]["p_two_sided"],
            "area_rho":bridge["scale_tilt_vs_area"]["rho"],
            "area_p":bridge["scale_tilt_vs_area"]["p_two_sided"],
        },
        "amplitude_vs_scale_tilt":bridge["amplitude_vs_scale_tilt"],
        "abs_tilt_gt_curvature_p":arch["geometry"]["wilcoxon_abs_tilt_greater_than_abs_curvature_p"],
        "interpretation":"Between-clade profile heterogeneity is dominated by overall memory amplitude, with a smaller coarse-fine scale-tilt axis and little intermediate-specific curvature. Overall amplitude tracks temporal persistence, whereas scale tilt is largely decoupled from memory strength.",
        "claim_boundary":"post-outcome exploratory reparameterization; not prospective and not independent replication"
    }

    out={
        "version":"v0.1",
        "status":"FLOWERCLADES51_MEMORY_ARCHITECTURE_EXPLORATORY_RESULT",
        "analysis_role":"EL_V0_4_EXTENSION_NOT_EL_V0_3_MODIFICATION",
        "headline":headline,
        "profile_architecture":arch,
        "temporal_bridge":bridge,
        "el_v0_3_science_changed":False,
        "paper1_science_changed":False,
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(headline,indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
