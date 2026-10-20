#!/usr/bin/env python3
"""Measured metabolite transfer inside known pigment identity: Petunieae.

Two original 3-compound biochemical targets, original 47 taxa and six-bit
anthocyanidin-presence classes. Source k=2 nearest same-class species predictor
is compared with the full other-same-class donor mean; no changed tree/taxa/k.
Joint 6-compound species-vector permutations preserve source covariance.
New outcome is retrospective and not an external, causal or ecological test.
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from run_petunieae_nested_regulatory_leaveoneout_prediction_v0_1 import (
    load_source, weights, loss_gain
)

COMPOUNDS=("myr_mgg","quer_mgg","kaem_mgg","Del_mgg","Pet_mgg","Malv_mgg")


def check_groups(design:dict)->tuple[list[dict],list[list[int]]]:
    expected=[
        ("FLAVONOL_CONCENTRATION",["myr_mgg","quer_mgg","kaem_mgg"]),
        ("ANTHOCYANIDIN_AMOUNT_POSITIVE_VARYING",["Del_mgg","Pet_mgg","Malv_mgg"])
    ]
    modules=design.get("two_fixed_biochemical_response_groups",[])
    if len(modules)!=len(expected):
        raise ValueError("original two biochemical targets not available")
    for m,(name,columns) in zip(modules,expected):
        if (m["id"],m["columns"])!=(name,columns) or m["n"]!=3:
            raise ValueError("frozen original measured biochemistry target membership changed")
    return modules,[[COMPOUNDS.index(x) for x in row["columns"]] for row in modules]


def group_losses(x:np.ndarray,w0:np.ndarray,w2:np.ndarray,
                 modules:list[list[int]],fine:list[str])->list[dict]:
    a=np.asarray(x,dtype=float)
    if a.ndim!=2 or a.shape[1]!=6 or len(fine)!=a.shape[0] or not np.isfinite(a).all():
        raise ValueError("six measured features and original taxon frame required")
    out=[]
    labels=np.asarray(fine)
    for ids in modules:
        if len(ids)!=3 or len(set(ids))!=3:
            raise ValueError("unaltered three original chemical features per target required")
        result=loss_gain(a[:,ids],w0,w2)
        b=result["state_only_mse"]
        n=result["phylogenetic_neighbor_mse"]
        l0=result["per_tip_state_only_mse"]
        l2=result["per_tip_neighbor_mse"]
        perclass=[]
        for key in sorted(set(fine)):
            group=labels==key
            baseline=float(l0[group].mean())
            neighbour=float(l2[group].mean())
            # Exact zero-pigment presence states can contain no variation
            # in all three target anthocyanidins. Keep these recipients in
            # the original 47-tip pooled loss; only the within-class ratio
            # (0/0) is undefined. Never drop that class after seeing outcome.
            uninformative=baseline<=1e-14
            perclass.append({
                "source_sixbit_pigment_code":key,
                "n_taxa":int(group.sum()),
                "class_mean_MSE":baseline,
                "phylogenetic_k2_MSE":neighbour,
                "gain":None if uninformative else float((baseline-neighbour)/baseline),
                "class_gain_status":("NONINFORMATIVE_ZERO_BASELINE" if uninformative
                                     else "SOURCE_CLASS_GAIN_DEFINED"),
                "all_three_metabolites_zero_in_class":bool(np.all(a[group][:,ids]==0)),
                "source_molecular_target_not_selection_test":True
            })
        omission=[]
        for row in perclass:
            # Compute retained recipient loss directly, rather than
            # subtraction of source group totals which is inaccurate for
            # the structural all-zero anthocyanidin source class.
            retained=labels!=row["source_sixbit_pigment_code"]
            remaining=int(retained.sum())
            if remaining<=0:
                raise ValueError("no original source recipient taxa remain")
            nbaseline=float(l0[retained].mean())
            nnear=float(l2[retained].mean())
            uninformative=nbaseline<=1e-14
            omission.append({
                "omitted_original_sixbit_code":row["source_sixbit_pigment_code"],
                "remaining_original_recipients":remaining,
                "recipient_only_gain":(None if uninformative else
                                       float((nbaseline-nnear)/nbaseline)),
                "gain_status":("NONINFORMATIVE_ZERO_REMAINING_BASELINE"
                               if uninformative else "SOURCE_RECIPIENT_ONLY_GAIN_DEFINED"),
                "donors_not_reselected":True
            })
        out.append({
            "n_compounds":3,
            "baseline_class_MSE":b,
            "nearest_two_MSE":n,
            "relative_gain":result["relative_gain"],
            "per_tip_baseline_MSE":l0.tolist(),
            "per_tip_nearest_two_MSE":l2.tolist(),
            "per_class":perclass,
            "recipient_only_leave_one_class":omission,
            "n_recipient_species_with_improvement":int(np.count_nonzero(l2<l0)),
            "n_recipient_species_with_worse_prediction":int(np.count_nonzero(l2>l0)),
            "donor_rule_unmodified":True
        })
    return out


def holm_two(ps:list[float])->list[float]:
    p=np.asarray(ps,dtype=float)
    if p.ndim!=1 or p.size!=2 or not np.isfinite(p).all() or (p<0).any() or (p>1).any():
        raise ValueError("exactly two valid biochemical target P values expected")
    order=np.argsort(p,kind="stable")
    out=np.empty(2)
    out[order[0]]=min(1.,2*p[order[0]])
    out[order[1]]=max(out[order[0]],p[order[1]])
    return out.tolist()


def classify(gain:float,holm_p:float)->str:
    if not np.isfinite([gain,holm_p]).all() or not 0<=holm_p<=1:
        raise ValueError("nonfinite or invalid permutation outcome")
    if gain<=0:
        return "NOT_SUPPORTED_PRACTICAL_TRANSFER"
    if holm_p>0.05:
        return "NOT_SUPPORTED_LOCALITY_AFTER_MULTIPLICITY"
    return "SUPPORTED_RETROSPECTIVE_METABOLITE_TRANSFER"


def analyze(source:Path,design:dict,original:dict,predictor:dict,
            *,iterations_override:int|None=None)->dict:
    if design["status"]!="SOURCE_EXPOSED_RETROSPECTIVE_METABOLITE_TRANSFER_HYPOTHESIS_FROZEN_BEFORE_NEW_TEST":
        raise ValueError("source-specific biochemical target design not frozen")
    response_groups,indices=check_groups(design)
    dist,fine,names,expression=load_source(source,predictor,original)
    if (len(names)!=design["original_cohort"]["n_tips"] or
        dict(sorted(collections.Counter(fine).items()))!=
        design["original_cohort"]["known_class_counts"]):
        raise ValueError("original 47-source 6-state frame drift")
    if expression.shape!=(47,21):
        raise ValueError("original source gene matrix frame drift")
    if predictor["predictor_2"]["k"]!=2:
        raise ValueError("original source k must be fixed at two")
    w0,w2=weights(dist,fine,names,k=2)
    previous=json.loads((ROOT/design["original_source"]["whole_21_gene_fixed_predictive_fail"]).read_text())
    source_full=loss_gain(expression,w0,w2)
    if (previous["decision"]!="NOT_SUPPORTED" or
        abs(previous["baseline_loss"]-source_full["state_only_mse"])>1e-10 or
        abs(previous["neighbor_loss"]-source_full["phylogenetic_neighbor_mse"])>1e-10 or
        abs(previous["observed_relative_prediction_gain"]-source_full["relative_gain"])>1e-10):
        raise ValueError("original full 21 gene prediction result changed")

    prior_flavonol=json.loads((ROOT/design["original_source"]["flavonol_expression_4_gene_prediction"]).read_text())
    if (prior_flavonol["n_taxa"]!=47 or
        abs(prior_flavonol["module_results"][1]["relative_gain_over_class_mean"]-
            0.05613676603732491)>1e-12):
        raise ValueError("original gene-flavonol source positive gain changed")

    original_table=pd.read_csv(source/original["source"]["processed_csv_path"])
    if len(original_table)!=60 or original_table["key_0"].duplicated().any():
        raise ValueError("original measured compound table identity altered")
    raw=original_table.set_index("key_0").loc[names,list(COMPOUNDS)].to_numpy(dtype=float)
    if not np.isfinite(raw).all() or (raw<0).any():
        raise ValueError("original mg/g metabolite values missing or negative")
    if np.any(raw.std(axis=0)<=1e-12):
        raise ValueError("precommitted six measured metabolites must vary across 47 taxa")
    x=np.log1p(100*raw)
    observed=group_losses(x,w0,w2,indices,fine)
    if len(observed)!=2 or any(o["n_compounds"]!=3 for o in observed):
        raise ValueError("wrong source biochemical target count")

    trials=design["null"]["iterations"] if iterations_override is None else iterations_override
    if trials<99:raise ValueError("insufficient within-pigment-state permutations")
    rng=np.random.default_rng(design["null"]["seed"])
    same_class=[np.flatnonzero(np.asarray(fine)==code) for code in sorted(set(fine))]
    null=np.empty((trials,2),dtype=float)
    for iteration in range(trials):
        order=np.arange(len(names))
        for ids in same_class:
            order[ids]=rng.permutation(ids)
        # Preserve all 6 compound values together during original within-state shuffle.
        permuted=x[order]
        for t,which in enumerate(indices):
            null[iteration,t]=loss_gain(permuted[:,which],w0,w2)["relative_gain"]
    if not np.isfinite(null).all():
        raise ValueError("nonfinite original biochemical transfer null")

    empirical=[]
    for i,obs in enumerate(observed):
        seen=obs["relative_gain"]
        empirical.append(float((1+np.count_nonzero(null[:,i]>=seen))/(trials+1)))
    adjusted=holm_two(empirical)
    results=[]
    for i,(meta,obs) in enumerate(zip(response_groups,observed)):
        results.append({
            "target_id":meta["id"],
            "measured_compound_columns":meta["columns"],
            "n_compounds":3,
            "class_mean_training_scaled_MSE":obs["baseline_class_MSE"],
            "phylogenetic_nearest_two_training_scaled_MSE":obs["nearest_two_MSE"],
            "relative_practical_prediction_gain":obs["relative_gain"],
            "original_source_locality_permutation_null_mean_gain":float(null[:,i].mean()),
            "original_source_locality_permutation_null_q025":float(np.quantile(null[:,i],.025)),
            "original_source_locality_permutation_null_q975":float(np.quantile(null[:,i],.975)),
            "source_locality_p":empirical[i],
            "holm_two_targets_p":adjusted[i],
            "decision":classify(obs["relative_gain"],adjusted[i]),
            "n_recipients_improved":obs["n_recipient_species_with_improvement"],
            "n_recipients_worse":obs["n_recipient_species_with_worse_prediction"],
            "per_original_sixbit_class":obs["per_class"],
            "recipient_only_leave_one_class":obs["recipient_only_leave_one_class"],
            "n_positive_one_class_recipient_omissions":int(sum(
                item["recipient_only_gain"] is not None and item["recipient_only_gain"]>0
                for item in obs["recipient_only_leave_one_class"])),
            "n_uninformative_one_class_recipient_omissions":int(sum(
                item["recipient_only_gain"] is None
                for item in obs["recipient_only_leave_one_class"])),
            "not_an_external_phylogenetic_radiation":True
        })
    return {
        "version":"v0.1",
        "status":"RETROSPECTIVE_ORIGINAL_METABOLITE_TRANSFER_ON_47_TIPS",
        "design_status":design["status"],
        "n_original_taxa":len(names),
        "n_original_sixbit_anthocyanidin_states":len(set(fine)),
        "class_counts":dict(sorted(collections.Counter(fine).items())),
        "fixed_nearest_k":2,
        "n_measurement_target_families":2,
        "fixed_transform":"log1p(100 * original compound mg/g)",
        "n_within_class_permutations":trials,
        "seed":design["null"]["seed"],
        "source_original_three_sha256_verified":True,
        "source_original_full_21_gene_gain_recovered":source_full["relative_gain"],
        "original_fixed_flavonol_expression_gene_predictive_gain_unchanged":0.05613676603732491,
        "target_results":results,
        "not_formal_gene_expression_vs_metabolite_effect_difference_test":True,
        "biochemical_presence_known_at_prediction_time":True,
        "not_a_pollinator_fitness_UV_phenotype_test":True,
        "not_prospective_independent_radiation_validation":True,
        "original_camellia_AJB_and_EL_science_unchanged":True
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--design",type=Path,required=True)
    p.add_argument("--original-design",type=Path,required=True)
    p.add_argument("--original-prediction-design",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--permutations",type=int)
    a=p.parse_args()
    d=json.loads(a.design.read_text(encoding="utf-8"))
    original=json.loads(a.original_design.read_text(encoding="utf-8"))
    pred=json.loads(a.original_prediction_design.read_text(encoding="utf-8"))
    result=analyze(a.source,d,original,pred,iterations_override=a.permutations)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("PETUNIEAE_METABOLITE_TRANSFER_RESULT",json.dumps(result,sort_keys=True))
    for item in result["target_results"]:
        print("BIOCHEMICAL_METABOLITE_TRANSFER_TARGET",item["target_id"],
              item["relative_practical_prediction_gain"],item["source_locality_p"],
              item["holm_two_targets_p"],item["decision"])
    print("DOES_NOT_CHANGE_ORIGINAL_FLAVONOL_GENE_MODULE_PREDICTION_OR_ECOLOGICAL_OUTCOMES")


if __name__=="__main__":
    main()
