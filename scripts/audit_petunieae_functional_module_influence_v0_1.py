#!/usr/bin/env python3
"""Post-outcome descriptive influence of 47 tips and six original pigment states.

No new P values, gene selection, null reruns or cross-radiation conclusions.
Each deletion refits the original 9-pigment-plus-state residual projection,
preserving all three fixed biological modules.
"""
from __future__ import annotations
import argparse, collections, json, sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import rankdata

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from analyze_petunieae_functional_module_memory_v0_1 import module_partition
from analyze_petunieae_nested_regulatory_memory_v0_1 import within_state_pairs
from analyze_petunieae_pigment_adjusted_regulatory_memory_v0_1 import (
    standardized_log, residual_projector, rankcorr)
from run_petunieae_nested_regulatory_leaveoneout_prediction_v0_1 import load_source


def audit(source:Path,design:dict,original:dict,whole:dict,adjusted:dict)->dict:
    if whole["status"]!="RETROSPECTIVE_MODULE_WIDE_SOURCE_OUTCOME_OPENED":
        raise ValueError("original post-outcome module result missing")
    modules,indices=module_partition(design,original)
    expected={"retained_taxa":47,"class_counts":{
        "000000":6,"000010":6,"000011":6,"000100":10,"000110":6,"000111":13}}
    dist,fine,names,_=load_source(source,expected,original)
    df=pd.read_csv(source/original["source"]["processed_csv_path"]).set_index("key_0").loc[names]
    x,unused=standardized_log(df[original["primary"]["raw_gene_expression_columns"]].to_numpy(dtype=float),1.)
    chem_design=json.loads((ROOT/design["source"]["original_adjusted_design_file"]).read_text())
    z,zeros=standardized_log(df[chem_design["covariate_adjustment"]["columns"]].to_numpy(dtype=float),100.)
    if unused or len(zeros)!=3:
        raise ValueError("source gene/pigment variance support drift")
    def estimate(keep:np.ndarray)->tuple[list[float],int]:
        labels=np.asarray(fine)[keep].tolist()
        d=dist[np.ix_(keep,keep)]
        a,b=within_state_pairs(labels)
        if len(a)<10:raise ValueError("not enough original same-pigment pair support")
        projector,_=residual_projector(labels,z[keep])
        residual=projector@x[keep]
        ranks=rankdata(d[a,b],method="average")
        rhos=[]
        for genes in indices:
            v=residual[:,genes]
            y=np.sqrt(np.mean((v[a]-v[b])**2,axis=1))
            rhos.append(rankcorr(ranks,y))
        return rhos,len(a)
    rho,n_pairs=estimate(np.arange(len(fine)))
    original_rho=[m["observed_rho"] for m in whole["module_results"]]
    if n_pairs!=183 or not np.allclose(rho,original_rho,atol=1e-11,rtol=0):
        raise ValueError("original all-taxon functional module results drifted")
    loo=[]
    for excluded in range(47):
        selected=np.arange(47)!=excluded
        values,pairs=estimate(selected)
        loo.append({"excluded_taxon":names[excluded],
                    "pigment_class":fine[excluded],
                    "within_fine_class_pairs":pairs,
                    "rhos":dict(zip([m["id"] for m in modules],values))})
    classloo=[]
    for state in sorted(set(fine)):
        selected=np.asarray(fine)!=state
        values,pairs=estimate(selected)
        classloo.append({"excluded_sixbit_state":state,
                         "remaining_taxa":int(selected.sum()),
                         "remaining_same_state_pairs":pairs,
                         "rhos":dict(zip([m["id"] for m in modules],values))})
    summaries={}
    for collection,rows in [("leave_one_tip",loo),("leave_one_fine_state",classloo)]:
        summ={}
        for m in modules:
            vals=[x["rhos"][m["id"]] for x in rows]
            summ[m["id"]]={
                "n":len(vals),"positive_count":sum(v>0 for v in vals),
                "min_rho":float(min(vals)),
                "median_rho":float(np.median(vals)),
                "max_rho":float(max(vals))
            }
        ordering=sum(
            row["rhos"]["EARLY_SHARED_AND_REGULATORY"]>
            row["rhos"]["FLAVONOL_BRANCH_AND_ACTIVATION"]>
            row["rhos"]["LATE_ANTHOCYANIN_EXECUTION"] for row in rows)
        summaries[collection]={
            "modules":summ,
            "n_early_above_flavonol_above_late":ordering,
            "n_total":len(rows)
        }
    return {
        "version":"v0.1",
        "status":"POST_OUTCOME_DESCRIPTIVE_PETUNIEAE_MODULE_INFLUENCE_ONLY",
        "original_source_SHA256_verified":True,
        "all_tips_original_module_rho_reproduced":dict(zip([m["id"] for m in modules],rho)),
        "n_tips":len(names),
        "n_original_same_chemical_state_pairs":n_pairs,
        "module_loo_summaries":summaries,
        "leave_one_taxon_details":loo,
        "leave_one_fine_state_details":classloo,
        "new_p_values":0,
        "independent_validations":0,
        "no_significance_or_module_difference_rescue":True,
        "original_module_maxT_decisions_unchanged":True,
        "original_all_21_gene_adjusted_rho_unchanged":adjusted["abundance_adjusted_rho"],
        "original_nearest_two_predictor_still_FAIL":True,
        "original_frozen_Camellia_AJB_and_EL_unchanged":True
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--design",type=Path,required=True)
    p.add_argument("--original-design",type=Path,required=True)
    p.add_argument("--frozen-module-result",type=Path,required=True)
    p.add_argument("--original-adjusted-result",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    r=audit(a.source,
            json.loads(a.design.read_text()),
            json.loads(a.original_design.read_text()),
            json.loads(a.frozen_module_result.read_text()),
            json.loads(a.original_adjusted_result.read_text()))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
    print("PETUNIEAE_FUNCTION_MODULE_POST_OUTCOME_INFLUENCE",json.dumps(r["module_loo_summaries"],sort_keys=True))
    print("NO_NEW_MODULE_SIGNIFICANCE_P_VALUES_OR_CAUSAL_CONCLUSIONS")


if __name__=="__main__":
    main()
