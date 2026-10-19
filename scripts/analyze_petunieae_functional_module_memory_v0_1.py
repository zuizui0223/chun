#!/usr/bin/env python3
"""Retrospective Petunieae pathway-module memory on unchanged pigment-adjusted source.

This distinguishes output, flavonol, and mixed upstream/regulatory source axes.
It does not test module-vs-module effect differences, causal mechanisms, or
general phylogenetic conservation against unavailable housekeeping controls.
Design was frozen before the *module* outcomes were calculated.
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
from analyze_petunieae_pigment_adjusted_regulatory_memory_v0_1 import (
    standardized_log, residual_projector, rankcorr
)


def module_partition(design:dict,original:dict)->tuple[list[dict],list[list[int]]]:
    genes=original["primary"]["raw_gene_expression_columns"]
    if genes!=design["frame"]["all_21_source_genes"] or len(genes)!=21:
        raise ValueError("original 21 genes or original column order changed")
    modules=design["functionally_mapped_nonoverlapping_modules"]
    if len(modules)!=3 or any(int(module["n"])!=len(module["genes"]) for module in modules):
        raise ValueError("three fixed modules required")
    counts=collections.Counter(gene for module in modules for gene in module["genes"])
    if set(counts)!=set(genes) or any(n!=1 for n in counts.values()):
        raise ValueError("21 genes must be partitioned exactly once into 3 fixed modules")
    if {m["id"]:m["n"] for m in modules}!={
        "LATE_ANTHOCYANIN_EXECUTION":9,
        "FLAVONOL_BRANCH_AND_ACTIVATION":4,
        "EARLY_SHARED_AND_REGULATORY":8
    }:
        raise ValueError("original published biological modules changed")
    return modules,[[genes.index(g) for g in module["genes"]] for module in modules]


def run(source:Path,design:dict,original:dict,adjusted:dict,
        *,permutations_override:int|None=None)->dict:
    if design["status"]!="RETROSPECTIVE_MODULE_FUNCTION_MAPPING_FIXED_BEFORE_MODULE_OUTCOME_OPENING":
        raise ValueError("missing independently frozen module source study design")
    mods,indices=module_partition(design,original)
    if adjusted["status"]!="PETUNIEAE_PIGMENT_ABUNDANCE_ADJUSTED_REGULATORY_MEMORY_RETROSPECTIVE":
        raise ValueError("prior pigment-adjusted result source status changed")
    predicted={"retained_taxa":47,"class_counts":{
        "000000":6,"000010":6,"000011":6,"000100":10,"000110":6,"000111":13}}
    dist,fine,names,_=load_source(source,predicted,original)
    if len(names)!=47 or len(set(fine))!=6:
        raise ValueError("frozen original 47 species and 6 chemical classes changed")
    i,j=within_state_pairs(fine)
    if len(i)!=183:
        raise ValueError("unchanged six-bit biochemical pair frame required")
    df=pd.read_csv(source/original["source"]["processed_csv_path"])
    if df["key_0"].duplicated().any() or len(df)!=60:
        raise ValueError("original processed source table keys drifted")
    df=df.set_index("key_0").loc[names]
    raw_genes=original["primary"]["raw_gene_expression_columns"]
    expr,expr_zero=standardized_log(df[raw_genes].to_numpy(dtype=float),1.0)
    chemistry=adjusted["zero_variance_pigment_columns"]
    pigment_columns=design["source"]["original_adjusted_design_file"]
    adj_design=json.loads((ROOT/pigment_columns).read_text(encoding="utf-8"))
    pigment_names=adj_design["covariate_adjustment"]["columns"]
    chem,chem_zero=standardized_log(df[pigment_names].to_numpy(dtype=float),100.)
    if expr_zero or sorted(pigment_names[v] for v in chem_zero)!=sorted(chemistry):
        raise ValueError("full expression/pigment feature support drift")
    projector,rank=residual_projector(fine,chem)
    residual=projector@expr
    xr=rankdata(dist[i,j],method="average").astype(float)
    def calc(X:np.ndarray,selection:list[int])->float:
        z=X[:,selection]
        y=np.sqrt(np.mean((z[i]-z[j])**2,axis=1))
        return rankcorr(xr,y)

    full=calc(residual,list(range(21)))
    if abs(full-adjusted["abundance_adjusted_rho"])>1e-10:
        raise ValueError("original 21-gene adjusted rho changed")
    if abs(full-design["expression_and_chemistry_residualization"]["original_whole_gene_rho_required"])>1e-10:
        raise ValueError("stored pre-module original rho contract changed")
    if rank!=adjusted["nuisance_rank"]:
        raise ValueError("original nuisance projection rank changed")

    obs=[calc(residual,inds) for inds in indices]
    permcount=(permutations_override if permutations_override is not None else
               design["permutation"]["iterations"])
    if permcount<99:raise ValueError("insufficient taxon-label permutations")
    rng=np.random.default_rng(design["permutation"]["seed"])
    groups=[np.flatnonzero(np.asarray(fine)==code) for code in sorted(set(fine))]
    null=np.empty((permcount,3))
    for b in range(permcount):
        order=np.arange(len(names))
        for group in groups:
            order[group]=rng.permutation(group)
        permuted=projector@residual[order]
        for k,inds in enumerate(indices):
            null[b,k]=calc(permuted,inds)
    if not np.isfinite(null).all():
        raise ValueError("nonfinite permutation statistics")
    familymax=np.max(null,axis=1)
    result=[]
    for k,module in enumerate(mods):
        seen=float(obs[k]);distribution=null[:,k]
        mean=float(distribution.mean())
        nominal=float((1+np.count_nonzero(distribution>=seen))/(permcount+1))
        maxp=float((1+np.count_nonzero(familymax>=seen))/(permcount+1))
        if maxp+1e-15<nominal:
            raise ValueError("maxT adjusted P smaller than nominal P")
        result.append({
            "module_id":module["id"],
            "source_biological_role":module["role"],
            "genes":module["genes"],
            "n_genes":len(module["genes"]),
            "observed_rho":seen,
            "permutation_null_mean_rho":mean,
            "null_centered_rho":seen-mean,
            "null_q025":float(np.quantile(distribution,.025)),
            "null_q975":float(np.quantile(distribution,.975)),
            "p_nominal":nominal,
            "p_maxT_familywise":maxp,
            "retrospective_fwer_signal":bool(seen>mean and maxp<=0.05),
            "not_a_housekeeping_or_neutral_gene_negative_control":True
        })
    return {
        "version":"v0.1",
        "status":"RETROSPECTIVE_MODULE_WIDE_SOURCE_OUTCOME_OPENED",
        "source_study":"Wheeler et al. 2023 Petunieae, DOI 10.1098/rspb.2023.0275",
        "source_sha256_verified":True,
        "design_status":design["status"],
        "analysis_role":"ONE_RADIATION_RETROSPECTIVE_FUNCTIONAL_MODULE_EXPLORATION",
        "n_tips":47,"n_exact_sixbit_chemical_states":6,"n_same_fine_state_pairs":183,
        "n_original_expression_genes":21,
        "n_modules":3,"nuisance_rank":rank,
        "original_full_21_gene_adjusted_rho_reproduced":full,
        "original_full_21_gene_p_unchanged":adjusted["p_one_sided"],
        "full_21_gene_retrospective_decision_unchanged":adjusted["decision"],
        "permutations":permcount,
        "seed":design["permutation"]["seed"],
        "module_results":result,
        "module_source_marginal_null_maxT_mean":float(familymax.mean()),
        "module_effect_difference_tested":False,
        "negative_control_housekeeping_panel_available":False,
        "no_causal_branch_or_pollinator_inference":True,
        "not_an_independent_radiation_replication":True,
        "original_nearest_two_predictor_still_FAIL":True,
        "original_camellia_AJB_and_EL_science_unchanged":True
    }


def main()->None:
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--module-design",type=Path,required=True)
    p.add_argument("--original-design",type=Path,required=True)
    p.add_argument("--original-adjusted-result",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--permutations",type=int,default=None)
    a=p.parse_args()
    design=json.loads(a.module_design.read_text(encoding="utf-8"))
    orig=json.loads(a.original_design.read_text(encoding="utf-8"))
    adjusted=json.loads(a.original_adjusted_result.read_text(encoding="utf-8"))
    result=run(a.source,design,orig,adjusted,permutations_override=a.permutations)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("PETUNIEAE_FUNCTIONAL_MODULE_MEMORY_RESULTS",json.dumps(result,sort_keys=True))
    print("NO_MODULE_SIGNIFICANCE_DIFFERENCE_TEST_OR_GENERAL_UNIVERSALITY_CLAIM")


if __name__=="__main__":
    main()
