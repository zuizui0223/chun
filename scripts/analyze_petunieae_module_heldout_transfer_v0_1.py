#!/usr/bin/env python3
"""Module-wise held-out Petunieae expression prediction from exact source data.

Target remains original log1p TPM10K gene expression. Each held-out 47-species
taxon is predicted from the same class mean or two nearest same-chemical-state
phylogenetic relatives. Module assignments and k=2 fixed before this outcome.
No gene selection, k tuning, independent test radiation or causality claim.
"""
from __future__ import annotations

import argparse
import collections
import itertools
import json
from pathlib import Path
import sys

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from run_petunieae_nested_regulatory_leaveoneout_prediction_v0_1 import (
    load_source, weights, loss_gain
)
from analyze_petunieae_functional_module_memory_v0_1 import module_partition


def modules_losses(x:np.ndarray,state_weights:np.ndarray,neighbor_weights:np.ndarray,
                   indices:list[list[int]],fine:list[str])->tuple[list[dict],dict]:
    """Same fold-wise other-46 training variance as original 21-gene result."""
    X=np.asarray(x,dtype=float)
    if X.ndim!=2 or X.shape[1]!=21 or len(fine)!=X.shape[0]:
        raise ValueError("frozen full source gene frame required")
    n=X.shape[0]
    mean46=(X.sum(axis=0)[None,:]-X)/(n-1)
    variance=(np.square(X).sum(axis=0)[None,:]-np.square(X))/(n-1)-mean46*mean46
    variance=np.where(variance>1e-12,variance,1.0)
    target_state=state_weights@X
    target_neighbor=neighbor_weights@X
    sq0=np.square(target_state-X)/variance
    sq1=np.square(target_neighbor-X)/variance
    random_noise=np.zeros_like(X)
    codes=np.asarray(fine)
    for i,code in enumerate(fine):
        ids=np.flatnonzero(codes==code)
        ids=ids[ids!=i]
        if len(ids)<2:raise ValueError("class donors fewer than 2")
        # Exact finite-population random-2 donor-mean variance about class mean;
        # no random sampling, no selection of best donors.
        N=len(ids)
        random_noise[i]=((N-2)/(2*(N-1)))*np.var(X[ids],axis=0,ddof=0)/variance[i]
    sqrandom=sq0+random_noise
    out=[]
    per_class={}
    for k,cols in enumerate(indices):
        l0=sq0[:,cols].mean(axis=1)
        l1=sq1[:,cols].mean(axis=1)
        lr=sqrandom[:,cols].mean(axis=1)
        baseline=float(l0.mean())
        near=float(l1.mean())
        random2=float(lr.mean())
        if baseline<=0 or random2<=0 or not np.isfinite([baseline,near,random2]).all():
            raise ValueError("invalid source heldout prediction loss")
        out.append({
            "module_index":k,
            "n_genes":len(cols),
            "class_mean_MSE":baseline,
            "nearest_two_MSE":near,
            "all_random_two_donor_mean_MSE":random2,
            "gain_vs_full_class_mean":(baseline-near)/baseline,
            "gain_vs_random_two_donors":(random2-near)/random2,
            "class_mean_loss_by_tip":l0.tolist(),
            "nearest_two_loss_by_tip":l1.tolist(),
            "random_two_expected_loss_by_tip":lr.tolist()
        })
        sub=[]
        for code in sorted(set(fine)):
            mask=codes==code
            b=float(l0[mask].mean());v=float(l1[mask].mean())
            sub.append({"fine_sixbit_code":code,"n_species":int(mask.sum()),
                        "class_mean_MSE":b,"nearest_two_MSE":v,
                        "gain_vs_class_mean":(b-v)/b if b>0 else None})
        per_class[str(k)]=sub
    return out,per_class


def holm_adjust(ps:list[float])->list[float]:
    p=np.asarray(ps,dtype=float)
    if p.ndim!=1 or len(p)!=3 or not np.isfinite(p).all() or np.any((p<0)|(p>1)):
        raise ValueError("three valid original module P values required")
    order=np.argsort(p,kind="stable")
    adjusted=np.empty_like(p)
    level=0.0
    for rank,idx in enumerate(order):
        level=max(level,min(1.0,(len(p)-rank)*p[idx]))
        adjusted[idx]=level
    if (adjusted+1e-14<p).any():raise ValueError("Holm adjustment smaller than raw P")
    return adjusted.tolist()


def predict(source:Path,original:dict,prediction_design:dict,
            module_design:dict,new_design:dict, *,
            iterations_override:int|None=None)->dict:
    if new_design["status"]!="RETROSPECTIVE_FIXED_MODULE_HELDOUT_TRANSFER_DESIGN_BEFORE_MODULE_PREDICTION_OUTCOME":
        raise ValueError("missing specifically frozen new prediction design")
    mods,ids=module_partition(module_design,original)
    if [m["id"] for m in mods]!=[m["module_id"] for m in new_design["fixed_cohort"]["modules"]]:
        raise ValueError("pre-fixed function module source names drift")
    distances,fine,names,X=load_source(source,prediction_design,original)
    if len(names)!=47 or X.shape!=(47,21) or len(set(fine))!=6 or        dict(sorted(collections.Counter(fine).items()))!=new_design["fixed_cohort"]["fine_state_counts"]:
        raise ValueError("retained prior 47-source frame drift")
    state,near=weights(distances,fine,names,k=prediction_design["predictor_2"]["k"])
    if prediction_design["predictor_2"]["k"]!=2:
        raise ValueError("original fixed nearest k no longer two")
    prior=json.loads((ROOT/new_design["prior_science"]["original_nested_prediction_result"]).read_text())
    full=loss_gain(X,state,near)
    if abs(full["state_only_mse"]-prior["baseline_loss"])>1e-10 or        abs(full["phylogenetic_neighbor_mse"]-prior["neighbor_loss"])>1e-10 or        abs(full["relative_gain"]-prior["observed_relative_prediction_gain"])>1e-10:
        raise ValueError("previous full 21-gene predictive FAIL does not reproduce")
    results,perclass=modules_losses(X,state,near,ids,fine)
    iterations=new_design["null"]["iterations"] if iterations_override is None else iterations_override
    if iterations<99:raise ValueError("insufficient within-state source permutations")
    seed=new_design["null"]["seed"]
    rng=np.random.default_rng(seed)
    groups=[np.flatnonzero(np.asarray(fine)==k) for k in sorted(set(fine))]
    null=np.empty((iterations,3),dtype=float)
    for k in range(iterations):
        perm=np.arange(len(fine))
        for g in groups:
            perm[g]=rng.permutation(g)
        m,_=modules_losses(X[perm],state,near,ids,fine)
        null[k]=[row["gain_vs_full_class_mean"] for row in m]
    if not np.isfinite(null).all():
        raise ValueError("permutation gain null undefined")
    ps=[float((1+int((null[:,i]>=results[i]["gain_vs_full_class_mean"]).sum()))/(iterations+1))
        for i in range(3)]
    adjusted=holm_adjust(ps)
    answers=[]
    for i,(module,row) in enumerate(zip(mods,results)):
        score=row["gain_vs_full_class_mean"]
        practical=score>0
        passed=practical and adjusted[i]<=0.05
        answers.append({
            "module_id":module["id"],
            "genes":module["genes"],
            "n_genes":row["n_genes"],
            "baseline_class_mean_MSE":row["class_mean_MSE"],
            "phylogeny_nearest_two_MSE":row["nearest_two_MSE"],
            "exact_expected_random_two_MSE":row["all_random_two_donor_mean_MSE"],
            "relative_gain_over_class_mean":score,
            "relative_gain_over_random_two":row["gain_vs_random_two_donors"],
            "locality_permutation_null_mean_gain":float(null[:,i].mean()),
            "locality_permutation_null_q025":float(np.quantile(null[:,i],.025)),
            "locality_permutation_null_q975":float(np.quantile(null[:,i],.975)),
            "locality_p_one_sided":ps[i],
            "holm_familywise_p":adjusted[i],
            "predictive_decision":(
                "SUPPORTED_EXPLORATORY_MODULE_PREDICTION" if passed
                else "NOT_SUPPORTED_PRACTICAL_TRANSFER" if not practical
                else "NOT_SUPPORTED_LOCALITY_AFTER_MULTIPLICITY"
            ),
            "original_module_membership_not_reselected":True,
            "per_original_pigment_class":perclass[str(i)]
        })
    return {
        "version":"v0.1",
        "status":"RETROSPECTIVE_MODULE_HELDOUT_EXPRESSION_TRANSFER_ON_ORIGINAL_SOURCE",
        "design_status":new_design["status"],
        "scientific_tier":"ONE_RADIATION_SOURCE_EXPOSED_RETROSPECTIVE_TEST",
        "source_shas_verified":True,
        "n_taxa":len(names),"n_original_gene_axes":21,
        "n_original_fine_pigment_classes":len(set(fine)),
        "original_fine_state_counts":dict(sorted(collections.Counter(fine).items())),
        "fixed_k":2,"n_module_tests":3,
        "module_results":answers,
        "seed":seed,"permutations":iterations,
        "original_full_21_gene_class_mean_MSE":full["state_only_mse"],
        "original_full_21_gene_k2_MSE":full["phylogenetic_neighbor_mse"],
        "original_full_21_gene_gain":full["relative_gain"],
        "original_full_21_gene_prediction_still_FAIL":True,
        "original_pigment_adjusted_module_correlations_untouched":True,
        "no_module_effect_difference_test":True,
        "no_optimization_of_k_genes_or_pigment_classes":True,
        "no_external_prospective_replication":True,
        "no_causal_ancestral_replay_or_selection_test":True,
        "frozen_camellia_AJB_and_EL_unchanged":True
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--design",type=Path,required=True)
    p.add_argument("--original-design",type=Path,required=True)
    p.add_argument("--original-prediction-design",type=Path,required=True)
    p.add_argument("--module-design",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--iterations",type=int)
    a=p.parse_args()
    d=json.loads(a.design.read_text(encoding="utf-8"))
    orig=json.loads(a.original_design.read_text(encoding="utf-8"))
    pred=json.loads(a.original_prediction_design.read_text(encoding="utf-8"))
    modules=json.loads(a.module_design.read_text(encoding="utf-8"))
    result=predict(a.source,orig,pred,modules,d,iterations_override=a.iterations)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("PETUNIEAE_MODULE_TRANSFER_FULL_RESULT",json.dumps(result,sort_keys=True))
    print("DOES_NOT_CHANGE_FROZEN_21GENE_PREDICTION_FAIL_OR_MODULE_ASSOCIATION")


if __name__=="__main__":
    main()
