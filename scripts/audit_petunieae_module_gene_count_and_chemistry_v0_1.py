#!/usr/bin/env python3
"""Outcome-opened, fixed-gene-size Petunieae pathway source decomposition.

Not an independent source or test. Enumerates *all* size-4 and size-8 panels
within fixed 9/4/8 biological modules, without gene reallocation, significance
tests, new P values, or phenotype recoding. Reports raw-vs-pigment-adjusted
ancestry-distance correlation and fraction of expression variance left by the
original 47-species nuisance projector.
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from analyze_petunieae_functional_module_memory_v0_1 import module_partition
from analyze_petunieae_pigment_adjusted_regulatory_memory_v0_1 import (
    standardized_log, residual_projector, rankcorr)
from analyze_petunieae_nested_regulatory_memory_v0_1 import within_state_pairs
from run_petunieae_nested_regulatory_leaveoneout_prediction_v0_1 import load_source


def describe(values:list[float])->dict:
    a=np.asarray(values,dtype=float)
    if a.size==0 or not np.isfinite(a).all():
        raise ValueError("nonfinite/empty source panel correlation")
    return {
        "n_gene_panels":int(a.size),
        "min_rho":float(np.min(a)),
        "p10_rho":float(np.quantile(a,.1)),
        "median_rho":float(np.median(a)),
        "p90_rho":float(np.quantile(a,.9)),
        "max_rho":float(np.max(a)),
        "positive_count":int(np.count_nonzero(a>0)),
        "panel_values_not_independent_tests":True
    }


def audit(source:Path,design:dict,modules_design:dict,
          original:dict,original_modules:dict,adjusted:dict)->dict:
    if design["status"]!="POST_OUTCOME_DESCRIPTIVE_MODULE_FEATURE_COUNT_AND_CHEMISTRY_DECOMPOSITION":
        raise ValueError("invalid diagnostic design status")
    mods,indices=module_partition(modules_design,original)
    if [m["n"] for m in mods]!=[9,4,8]:
        raise ValueError("original modules no longer have 9/4/8 source genes")
    if len(original_modules["module_results"])!=3:
        raise ValueError("unchanged original source module result absent")
    expected={"retained_taxa":47,"class_counts":{
        "000000":6,"000010":6,"000011":6,"000100":10,"000110":6,"000111":13}}
    dist,fine,names,_=load_source(source,expected,original)
    if len(names)!=47 or len(set(fine))!=6:
        raise ValueError("original 47 taxa or 6 chemical states changed")
    aa,bb=within_state_pairs(fine)
    if len(aa)!=183:
        raise ValueError("source same-chemistry frame drift")

    table=pd.read_csv(source/original["source"]["processed_csv_path"])
    if len(table)!=60 or table["key_0"].duplicated().any():
        raise ValueError("frozen source table drift")
    table=table.set_index("key_0").loc[names]
    X,xzeros=standardized_log(
        table[original["primary"]["raw_gene_expression_columns"]].to_numpy(dtype=float),1.0)
    covar=modules_design["source"]["original_adjusted_design_file"]
    adj_design=json.loads((ROOT/covar).read_text())
    chemical_columns=adj_design["covariate_adjustment"]["columns"]
    Z,zzeros=standardized_log(table[chemical_columns].to_numpy(dtype=float),100.0)
    if xzeros or sorted(chemical_columns[i] for i in zzeros)!=sorted(
            adjusted["zero_variance_pigment_columns"]):
        raise ValueError("fixed gene or pigment source columns no longer usable")
    M,nuisance_rank=residual_projector(fine,Z)
    R=M@X
    if nuisance_rank!=adjusted["nuisance_rank"]:
        raise ValueError("nuisance matrix rank changed")
    tree_rank=rankdata(dist[aa,bb],method="average").astype(float)

    def rho(v:np.ndarray,cols:tuple[int,...]|list[int])->float:
        data=v[:,cols]
        lengths=np.sqrt(np.mean((data[aa]-data[bb])**2,axis=1))
        return rankcorr(tree_rank,lengths)

    all_rho=rho(R,list(range(21)))
    if abs(all_rho-adjusted["abundance_adjusted_rho"])>1e-10:
        raise ValueError("original full-pigment-adjusted source rho drift")
    original_by_id={m["module_id"]:m for m in original_modules["module_results"]}
    rows=[]
    sizes={}
    for mod,inds in zip(mods,indices):
        module_id=mod["id"]
        unadjusted=rho(X,inds)
        corrected=rho(R,inds)
        if abs(corrected-original_by_id[module_id]["observed_rho"])>1e-11:
            raise ValueError("one original module outcome changed")
        raw=float(np.square(X[:,inds]).sum())
        after=float(np.square(R[:,inds]).sum())
        if raw<=1e-10 or after<0:
            raise ValueError("invalid residual variance")
        rows.append({
            "module_id":module_id,
            "original_genes":list(mod["genes"]),
            "n_genes":len(inds),
            "unadjusted_expression_rho":unadjusted,
            "pigment_adjusted_expression_rho":corrected,
            "adjusted_minus_raw_rho_descriptive":corrected-unadjusted,
            "fraction_of_source_standardized_expression_sum_squares_left":after/raw,
            "fraction_projected_away_by_pigment_and_sixbit_class":1-after/raw,
            "no_causal_trait_variance_interpretation":True
        })
        for k in (4,8):
            if k>len(inds):continue
            panels=[]
            for p in itertools.combinations(inds,k):
                genes=[original["primary"]["raw_gene_expression_columns"][col] for col in p]
                panels.append({"genes":genes,
                               "unadjusted_rho":rho(X,p),
                               "adjusted_rho":rho(R,p)})
            expected_panels={("LATE_ANTHOCYANIN_EXECUTION",4):126,
                ("FLAVONOL_BRANCH_AND_ACTIVATION",4):1,
                ("EARLY_SHARED_AND_REGULATORY",4):70,
                ("LATE_ANTHOCYANIN_EXECUTION",8):9,
                ("EARLY_SHARED_AND_REGULATORY",8):1}[(module_id,k)]
            if len(panels)!=expected_panels:
                raise ValueError("fixed module gene-count enumeration drift")
            sizes[f"{module_id}__size{k}"]={
                "module_id":module_id,
                "size_k":k,
                "raw":describe([p["unadjusted_rho"] for p in panels]),
                "adjusted":describe([p["adjusted_rho"] for p in panels]),
                "gene_panels":panels,
                "not_a_significance_test_or_independent_replicate":True
            }
    early=sizes["EARLY_SHARED_AND_REGULATORY__size4"]["gene_panels"]
    late=sizes["LATE_ANTHOCYANIN_EXECUTION__size4"]["gene_panels"]
    flav=sizes["FLAVONOL_BRANCH_AND_ACTIVATION__size4"]["gene_panels"]
    comparisons={}
    for field in ("adjusted_rho","unadjusted_rho"):
        comparisons[field]={
            "early_4_gene_panels_above_late_4_gene_panels":sum(
                a[field]>b[field] for a in early for b in late),
            "early_late_four_gene_panel_combinations":len(early)*len(late),
            "flavonol_fixed_4_gene_rho":flav[0][field],
            "flavonol_above_late_4_gene_panels_count":sum(
                flav[0][field]>b[field] for b in late),
            "flavonol_above_early_4_gene_panels_count":sum(
                flav[0][field]>b[field] for b in early),
            "source_panel_orderings_not_probability_or_p_value":True
        }
    return {
        "version":"v0.1",
        "status":"POST_OUTCOME_DESCRIPTIVE_SOURCE_MODULE_SIZE_AND_CHEMISTRY_DIAGNOSTIC",
        "original_source_sha256_verified":True,
        "fixed_frame_tips":47,
        "source_chemical_states":6,
        "same_sixbit_state_unordered_pairs":183,
        "nuisance_rank":nuisance_rank,
        "all_21_gene_adjusted_rho_recovered":all_rho,
        "original_all_21_gene_adjusted_result_unchanged":adjusted["decision"],
        "original_three_module_maxT_decisions_unchanged":True,
        "original_k2_predictor_remains_FAIL":True,
        "fixed_module_raw_and_residual_effects":rows,
        "all_exhaustive_gene_count_panels":sizes,
        "equal_4_gene_panel_rank_comparisons":comparisons,
        "n_new_significance_tests":0,
        "number_of_independent_biological_radiations":1,
        "not_gene_panel_effect_difference_test":True,
        "no_housekeeping_background_available":True,
        "original_Camellia_AJB_and_EL_unchanged":True
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--design",type=Path,required=True)
    p.add_argument("--module-design",type=Path,required=True)
    p.add_argument("--original-design",type=Path,required=True)
    p.add_argument("--original-module-result",type=Path,required=True)
    p.add_argument("--original-adjusted-result",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    r=audit(
        a.source,json.loads(a.design.read_text()),json.loads(a.module_design.read_text()),
        json.loads(a.original_design.read_text()),
        json.loads(a.original_module_result.read_text()),
        json.loads(a.original_adjusted_result.read_text()))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("PETUNIEAE_SIZE_AND_CHEMISTRY_SOURCE_SUMMARY",json.dumps({
        "status":r["status"],
        "modules":r["fixed_module_raw_and_residual_effects"],
        "four_gene_summary":{
            k:v["adjusted"] for k,v in r["all_exhaustive_gene_count_panels"].items()
            if k.endswith("__size4")},
        "four_gene_rank_comparisons":r["equal_4_gene_panel_rank_comparisons"]["adjusted_rho"]
    },sort_keys=True))
    print("NO_NEW_P_VALUES_MODULE_DIFFERENCE_TEST_OR_SPECIES_SELECTION")


if __name__=="__main__":
    main()
