#!/usr/bin/env python3
"""Petunieae regulatory phylogenetic memory after source pigment-abundance adjustment.

New statistic frozen in data/petunieae_pigment_abundance_adjusted_regulatory_memory_design_v0_1.json
BEFORE opening this result. Source itself already outcome-exposed: retrospective only.
"""
from __future__ import annotations
import argparse
import collections
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from run_petunieae_nested_regulatory_leaveoneout_prediction_v0_1 import load_source
from analyze_petunieae_nested_regulatory_memory_v0_1 import within_state_pairs


def standardized_log(x:np.ndarray,multiplier:float)->tuple[np.ndarray,list[int]]:
    x=np.asarray(x,dtype=float)
    if x.ndim!=2 or not np.isfinite(x).all() or (x<0).any():
        raise ValueError("invalid raw concentrations/expression")
    transformed=np.log1p(x*multiplier)
    sd=transformed.std(axis=0,ddof=0)
    z=np.zeros_like(transformed)
    use=sd>1e-12
    z[:,use]=(transformed[:,use]-transformed[:,use].mean(axis=0))/sd[use]
    return z,[int(v) for v in np.where(~use)[0]]


def residual_projector(fine:list[str],chem_z:np.ndarray)->tuple[np.ndarray,int]:
    n=len(fine)
    labels=sorted(set(fine))
    if chem_z.shape[0]!=n:raise ValueError("chemistry and state frames disagree")
    dummy=np.stack([np.asarray(fine)==code for code in labels],axis=1).astype(float)
    D=np.column_stack([dummy,chem_z])
    M=np.eye(n)-D@np.linalg.pinv(D,rcond=1e-12)
    M=(M+M.T)/2
    rank=int(np.linalg.matrix_rank(D,tol=1e-10))
    if not np.allclose(M@M,M,atol=1e-10):raise ValueError("residual projector not idempotent")
    if rank>=n:raise ValueError("nuisance overparameterized")
    return M,rank


def rankcorr(xr:np.ndarray, y:np.ndarray)->float:
    yr=rankdata(y,method="average").astype(float)
    xd=xr-xr.mean()
    yd=yr-yr.mean()
    denominator=np.sqrt(float(np.dot(xd,xd)*np.dot(yd,yd)))
    if denominator<=1e-15:raise ValueError("rank correlation not identifiable")
    return float(np.dot(xd,yd)/denominator)


def correlated_distance(dist:np.ndarray,expr:np.ndarray,fine:list[str],chem_z:np.ndarray,
                        *,permutations:int=9999,seed:int=20261010,loo:bool=True)->dict:
    n=len(fine)
    if dist.shape!=(n,n) or expr.shape[0]!=n or chem_z.shape[0]!=n:
        raise ValueError("input row mismatch")
    ii,jj=within_state_pairs(fine)
    if len(ii)<10:raise ValueError("not enough same-state pairs")
    M,nuisance_rank=residual_projector(fine,chem_z)
    residual=M@expr
    d_rank=rankdata(dist[ii,jj],method="average").astype(float)

    def calc(v:np.ndarray)->float:
        differences=v[ii]-v[jj]
        rms=np.sqrt(np.mean(differences*differences,axis=1))
        return rankcorr(d_rank,rms)

    observed=calc(residual)
    original=calc(expr)
    null=np.empty(permutations,dtype=float)
    rng=np.random.default_rng(seed)
    groups=[np.flatnonzero(np.asarray(fine)==k) for k in sorted(set(fine))]
    for b in range(permutations):
        order=np.arange(n)
        for g in groups:
            order[g]=rng.permutation(g)
        # Freedman-Lane residual shuffle with the source pigment/class effects
        # fixed and the outcome residualized again in each permutation:
        # M@(F + permute(R)) = M@permute(R), as M@F == 0.
        null[b]=calc(M@residual[order])
    if not np.isfinite(null).all():raise ValueError("nonfinite permutation null")
    mean=float(null.mean())
    p=float((1+np.count_nonzero(null>=observed))/(permutations+1))
    previous_overall=float(np.sum(expr*expr))
    retained_residual_fraction=float(np.sum(residual*residual)/previous_overall)
    result={
        "n_tips":n,"n_fine_states":len(set(fine)),"n_pairs":len(ii),
        "n_gene_axes":expr.shape[1],"n_pigment_axes":chem_z.shape[1],
        "nuisance_rank":nuisance_rank,
        "unadjusted_rho_on_this_frame":original,
        "abundance_adjusted_rho":observed,
        "permutation_null_mean":mean,
        "permutation_null_q025":float(np.quantile(null,.025)),
        "permutation_null_q975":float(np.quantile(null,.975)),
        "permutation_centered_rho":observed-mean,
        "p_one_sided":p,
        "decision":"RETROSPECTIVE_SUPPORT" if observed>mean and p<=.05 else "NOT_SUPPORTED",
        "permutations":permutations,
        "seed":seed,
        "residual_sum_of_squares_fraction":retained_residual_fraction,
    }
    if loo:
        lo=[]
        for excluded in range(n):
            indices=[v for v in range(n) if v!=excluded]
            fk=[fine[v] for v in indices]
            Mk,_=residual_projector(fk,chem_z[indices])
            ek=Mk@expr[indices]
            d_sub=dist[np.ix_(indices,indices)]
            aa,bb=within_state_pairs(fk)
            dr=rankdata(d_sub[aa,bb],method="average").astype(float)
            yr=np.sqrt(np.mean((ek[aa]-ek[bb])**2,axis=1))
            lo.append(rankcorr(dr,yr))
        result["leave_one_tip_out_descriptive"]={
            "n":n,"positive_count":sum(v>0 for v in lo),
            "min_rho":float(min(lo)),
            "median_rho":float(np.median(lo)),
            "max_rho":float(max(lo)),
        }
    return result


def run(source:Path,design:dict,original:dict, *,permutations_override:int|None=None)->dict:
    original_pred_design={
        "retained_taxa":design["frame"]["retained_tips"],
        "class_counts":{
          "000000":6,"000010":6,"000011":6,"000100":10,"000110":6,"000111":13
        }
    }
    dist,fine,names,gene_log=load_source(source,original_pred_design,original)
    table=source/original["source"]["processed_csv_path"]
    df=pd.read_csv(table).set_index("key_0").loc[names]
    chemistry=design["covariate_adjustment"]["columns"]
    if not set(chemistry)<=set(df.columns):raise ValueError("missing specified pigment columns")
    chem,zeros=standardized_log(df[chemistry].to_numpy(dtype=float),100.0)
    expr, gene_zero=standardized_log(np.expm1(gene_log),1.0)
    if gene_zero:raise ValueError("previous 21-gene expression panel gained zero-variance column")
    if len(zeros)!=3 or sorted(chemistry[i] for i in zeros)!=sorted(design["frame"]["absent_after_rare_filter"]):
        raise ValueError("the frozen 3 constant-zero pigment assays changed")
    perms=permutations_override or design["test"]["permutations"]
    result=correlated_distance(dist,expr,fine,chem,permutations=perms,seed=design["test"]["seed"],loo=True)
    if result["n_pairs"]!=design["frame"]["same_class_pairs"] or result["n_gene_axes"]!=21:
        raise ValueError("frozen common state-pair frame drift")
    prior=json.loads((ROOT/design["source"]["prior_result"]).read_text())
    if abs(prior["primary_conditional_expression_memory"]["rho"]-result["unadjusted_rho_on_this_frame"])>1e-10:
        raise ValueError("original gene-expression rho changed")
    result.update({
        "version":"v0.1",
        "status":"PETUNIEAE_PIGMENT_ABUNDANCE_ADJUSTED_REGULATORY_MEMORY_RETROSPECTIVE",
        "analysis_role":"POST_SOURCE_EXPOSURE_NEW_TEST_FROZEN_BEFORE_NEW_STATISTIC",
        "source_SHA256_verified":True,
        "design_status":design["status"],
        "zero_variance_pigment_columns":[chemistry[i] for i in zeros],
        "fine_state_counts":dict(sorted(collections.Counter(fine).items())),
        "no_new_historical_events_claimed":True,
        "no_causal_independence_claimed":True,
        "does_not_replace_original_21gene_result":True,
        "does_not_replace_original_k2_prediction_fail":True,
        "does_not_replace_ajb_or_el_science":True,
    })
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source",type=Path,required=True)
    parser.add_argument("--design",type=Path,required=True)
    parser.add_argument("--original-design",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    parser.add_argument("--permutations",type=int,default=None)
    a=parser.parse_args()
    design=json.loads(a.design.read_text())
    original=json.loads(a.original_design.read_text())
    result=run(a.source,design,original,permutations_override=a.permutations)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
