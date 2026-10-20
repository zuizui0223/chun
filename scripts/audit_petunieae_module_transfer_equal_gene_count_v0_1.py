#!/usr/bin/env python3
"""Post-outcome descriptive feature-count sensitivity for Petunieae k2 transfer.

Compare *all* original-gene within-module 4-gene panels using unchanged
47-species expression matrix and exact original k2/fine-class donor weights.
Also omit each one of the four flavonol-related genes, without optimizing.
Panel observations are highly overlapping and NOT independent tests.
"""
from __future__ import annotations

import argparse
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
from analyze_petunieae_module_heldout_transfer_v0_1 import gains_only


def summarize(rows:list[dict])->dict:
    a=np.asarray([r["relative_gain_vs_original_class_mean"] for r in rows],dtype=float)
    if a.size==0 or not np.isfinite(a).all():
        raise ValueError("empty/nonfinite gene subset gain")
    return {
        "n_panels":len(rows),
        "n_positive_gain":int(np.count_nonzero(a>0)),
        "median_gain":float(np.median(a)),
        "min_gain":float(np.min(a)),
        "max_gain":float(np.max(a)),
        "q10_gain":float(np.quantile(a,.1)),
        "q90_gain":float(np.quantile(a,.9)),
        "all_shared_gene_panels_not_independent_evidence":True
    }


def analyze(source:Path,original:dict,original_prediction:dict,module_design:dict,
            frozen_transfer:dict)->dict:
    if frozen_transfer["status"]!="RETROSPECTIVE_MODULE_HELDOUT_EXPRESSION_TRANSFER_ON_ORIGINAL_SOURCE":
        raise ValueError("original three module practical outcomes unavailable")
    mods,cols=module_partition(module_design,original)
    src_frame={"retained_taxa":47,"class_counts":{
        "000000":6,"000010":6,"000011":6,"000100":10,"000110":6,"000111":13}}
    d,fine,names,X=load_source(source,src_frame,original)
    if len(names)!=47 or X.shape!=(47,21) or len(set(fine))!=6:
        raise ValueError("original source frame changed")
    W0,W1=weights(d,fine,names,k=2)
    original_full=loss_gain(X,W0,W1)
    if abs(original_full["relative_gain"]-frozen_transfer["original_full_21_gene_gain"])>1e-11:
        raise ValueError("original full 21-gene result changed")
    prior_gains=[r["relative_gain_over_class_mean"] for r in frozen_transfer["module_results"]]
    recovered=gains_only(X,W0,W1,cols)
    if not np.allclose(prior_gains,recovered,atol=1e-12,rtol=0):
        raise ValueError("prior module gains do not reproduce")
    symbols=original["primary"]["raw_gene_expression_columns"]
    bysize={}
    for m,indices in zip(mods,cols):
        gene_indices=list(indices)
        panels=[]
        for subset in itertools.combinations(gene_indices,4):
            value=gains_only(X,W0,W1,[list(subset)])[0]
            panels.append({
                "genes":[symbols[v] for v in subset],
                "relative_gain_vs_original_class_mean":value,
                "improves_class_mean":bool(value>0)
            })
        if len(panels)!={"LATE_ANTHOCYANIN_EXECUTION":126,
                         "FLAVONOL_BRANCH_AND_ACTIVATION":1,
                         "EARLY_SHARED_AND_REGULATORY":70}[m["id"]]:
            raise ValueError("exhaustive four-gene source coverage incomplete")
        bysize[m["id"]]={"source_module_genes":m["genes"],
                         "summary":summarize(panels),
                         "all_four_gene_source_panels":panels}
    fixed_flav=frozen_transfer["module_results"][1]["relative_gain_over_class_mean"]
    flav_panel=bysize["FLAVONOL_BRANCH_AND_ACTIVATION"]["all_four_gene_source_panels"]
    if len(flav_panel)!=1 or abs(flav_panel[0]["relative_gain_vs_original_class_mean"]-fixed_flav)>1e-12:
        raise ValueError("original complete flavonol four-gene transfer drift")
    relative={}
    for key in ("LATE_ANTHOCYANIN_EXECUTION","EARLY_SHARED_AND_REGULATORY"):
        panels=bysize[key]["all_four_gene_source_panels"]
        comparison=np.asarray([p["relative_gain_vs_original_class_mean"] for p in panels])
        relative[key]={
            "n_other_four_gene_panels":len(panels),
            "n_other_panels_with_strictly_lower_gain_than_fixed_flavonol":int(np.count_nonzero(comparison<fixed_flav)),
            "n_other_panels_with_strictly_higher_gain_than_fixed_flavonol":int(np.count_nonzero(comparison>fixed_flav)),
            "gene_panels_overlap_not_empirical_P":True
        }
    flav_inds=list(cols[1])
    dropped=[]
    for omit in flav_inds:
        genes=[v for v in flav_inds if v!=omit]
        val=gains_only(X,W0,W1,[genes])[0]
        dropped.append({
            "excluded_original_flavonol_gene":symbols[omit],
            "remaining_three_genes":[symbols[v] for v in genes],
            "relative_gain_vs_full_pigment_class_mean":val,
            "positive_gain":bool(val>0),
            "not_a_new_module_predictor_or_significance_test":True
        })
    return {
        "version":"v0.1",
        "status":"POST_OUTCOME_EXHAUSTIVE_SOURCE_PREDICTIVE_GENE_COUNT_AUDIT",
        "n_source_species":47,
        "n_source_pigment_presence_classes":6,
        "n_original_source_genes":21,
        "fixed_heldout_k":2,
        "original_frozen_full_21_gene_gain":original_full["relative_gain"],
        "frozen_three_module_gains_reproduced":dict(zip([m["id"] for m in mods],recovered)),
        "exhaustive_same_four_gene_count_module_panels":bysize,
        "fixed_flavonol_four_gene_gain":fixed_flav,
        "flavonol_relative_to_other_source_four_gene_panels":relative,
        "flavonol_drop_one_gene_descriptive":dropped,
        "flavonol_full_module_Holm_P_unchanged":frozen_transfer["module_results"][1]["holm_familywise_p"],
        "n_new_P_values":0,
        "no_gene_selection_or_new_null":True,
        "no_between_module_statistical_significance_test":True,
        "no_new_independent_radiation":True,
        "no_causal_flavonol_gene_claim":True,
        "original_Camellia_AJB_and_EL_science_unchanged":True
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--original-design",type=Path,required=True)
    p.add_argument("--original-prediction-design",type=Path,required=True)
    p.add_argument("--module-design",type=Path,required=True)
    p.add_argument("--frozen-transfer-result",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    data=[json.loads(x.read_text(encoding="utf-8")) for x in (
        a.original_design,a.original_prediction_design,
        a.module_design,a.frozen_transfer_result)]
    out=analyze(a.source,*data)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("PETUNIEAE_PREDICTION_FOUR_GENE_SOURCE_SIZES",json.dumps({
        name:v["summary"] for name,v in out["exhaustive_same_four_gene_count_module_panels"].items()
    },sort_keys=True))
    print("PETUNIEAE_FLAVONOL_FEATURE_COUNT_CONTROL",json.dumps({
        "flav":out["fixed_flavonol_four_gene_gain"],
        "other_comparisons":out["flavonol_relative_to_other_source_four_gene_panels"],
        "drop_one":out["flavonol_drop_one_gene_descriptive"]
    },sort_keys=True))
    print("NO_POST_OUTCOME_PANEL_SELECTION_OR_NEW_SIGNIFICANCE_INFERENCE")


if __name__=="__main__":
    main()
