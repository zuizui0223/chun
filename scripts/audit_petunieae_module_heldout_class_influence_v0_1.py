#!/usr/bin/env python3
"""Source-only post-outcome six-class influence for frozen module predictive gain.

Remove recipient losses from exactly one original six-bit class at a time.
This does NOT refit the k=2 source neighbor donor weights or the training
variances. No new P-values, source admission edits or inference promotions.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path


def influence(frozen:dict)->dict:
    if frozen["status"]!="RETROSPECTIVE_MODULE_HELDOUT_EXPRESSION_TRANSFER_ON_ORIGINAL_SOURCE":
        raise ValueError("invalid original source prediction result")
    if frozen["n_taxa"]!=47 or frozen["fixed_k"]!=2 or len(frozen["module_results"])!=3:
        raise ValueError("original predictive frame changed")
    if frozen["original_full_21_gene_prediction_still_FAIL"] is not True:
        raise ValueError("original source original 21 gene prediction fail missing")
    rows=[]
    seen={}
    for m in frozen["module_results"]:
        cls=m["per_original_pigment_class"]
        if len(cls)!=6 or len({z["fine_sixbit_code"] for z in cls})!=6:
            raise ValueError("six original pigment classes not represented")
        all_count=sum(int(x["n_species"]) for x in cls)
        if all_count!=47:raise ValueError("group sample coverage changed")
        orig_a=m["baseline_class_mean_MSE"]
        orig_b=m["phylogeny_nearest_two_MSE"]
        n=all_count
        # Original overall tip-mean errors must equal the source per-class
        # tip-weighted means. Never silently rely on approximate group gains.
        for target,field in ((orig_a,"class_mean_MSE"),(orig_b,"nearest_two_MSE")):
            if abs(sum(z["n_species"]*z[field] for z in cls)/n-target)>1e-12:
                raise ValueError("source group and full-frame losses inconsistent")
        per_group=[]
        for x in cls:
            count=int(x["n_species"])
            a=(n*orig_a-count*x["class_mean_MSE"])/(n-count)
            b=(n*orig_b-count*x["nearest_two_MSE"])/(n-count)
            if a<=0:raise ValueError("invalid class-omission baseline")
            per_group.append({
                "omitted_sixbit_code":x["fine_sixbit_code"],
                "omitted_species":count,
                "remaining_species":n-count,
                "same_original_training_and_donor_weights":True,
                "remaining_recipients_class_mean_MSE":a,
                "remaining_recipients_k2_MSE":b,
                "remaining_recipients_gain":(a-b)/a
            })
        names=[x["omitted_sixbit_code"] for x in per_group]
        if not seen:
            seen=Counter({name:int(x["n_species"]) for name,x in zip(names,cls)})
        else:
            if seen!=Counter({x["fine_sixbit_code"]:int(x["n_species"]) for x in cls}):
                raise ValueError("module specific source class membership changed")
        gains=[r["remaining_recipients_gain"] for r in per_group]
        rows.append({
            "module_id":m["module_id"],
            "original_module_gain":m["relative_gain_over_class_mean"],
            "original_fixed_predictive_decision":m["predictive_decision"],
            "n_positive_original_individual_classes":sum(x["gain_vs_class_mean"]>0 for x in cls),
            "n_positive_one_class_omissions":sum(v>0 for v in gains),
            "min_original_group_omission_gain":min(gains),
            "max_original_group_omission_gain":max(gains),
            "omit_one_class_rows":per_group
        })
    return {
        "version":"v0.1",
        "status":"POST_OUTCOME_SIX_CLASS_PREDICTIVE_LOSS_INFLUENCE_DESCRIPTIVE_ONLY",
        "n_original_species":47,
        "n_original_source_chemical_states":6,
        "n_original_module_tests":3,
        "module_class_influence":rows,
        "no_retraining_or_reselecting_k2_donor_weights":True,
        "no_new_statistical_pvalues_or_unequal_gene_number_inference":True,
        "no_external_or_prospective_replication":True,
        "source_module_prediction_decisions_unchanged":True,
        "original_full_21_gene_prediction_still_FAIL":True,
        "original_Camellia_AJB_and_EL_unchanged":True
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--frozen-module-result",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    d=influence(json.loads(a.frozen_module_result.read_text(encoding="utf-8")))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("PETUNIEAE_MODULE_PREDICTION_CLASS_INFLUENCE",json.dumps({
        x["module_id"]:{"gain":x["original_module_gain"],
                        "positive_one_class_omissions":x["n_positive_one_class_omissions"],
                        "min_leave_class_gain":x["min_original_group_omission_gain"],
                        "max_leave_class_gain":x["max_original_group_omission_gain"]}
        for x in d["module_class_influence"]},sort_keys=True))
    print("NO_REOPTIMIZATION_OF_PREDICTOR_OR_GENE_SET")


if __name__=="__main__":main()
