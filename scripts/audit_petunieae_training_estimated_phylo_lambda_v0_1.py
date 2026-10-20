#!/usr/bin/env python3
"""Post-outcome training-only phylogenetic lambda sensitivity in original Petunieae.

Each held-out source species' *three product responses* are never used to
select the Brownian+nugget phylogenetic covariance weight. A multivariate
six-original-pigment-code baseline REML on the other 46 chooses one original
fixed-grid lambda. Both competitors use the same chosen lambda and same source
GLS/phylogenetic kriging; only one competitor adds the four original flavonol
associated measured expression genes. No new permutation P value is computed.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from run_petunieae_nested_regulatory_leaveoneout_prediction_v0_1 import load_source
from analyze_petunieae_phylo_conditional_gene_product_v0_1 import (
    GENES,METABOLITES,phylo_shared_root_covariance,source_working_V,
    fixed_source_D,loo_linear_kriging_operator,error_metrics)


def fold_training_reml_score(Ytrain:np.ndarray,Dtrain:np.ndarray,
                             Vtrain:np.ndarray)->float:
    """Multivariate class-only source profile REML under original 3 compounds.

    All source values are 46 training tips. Nothing about the omitted
    metabolite measurements is used in this score.
    """
    n,d=Ytrain.shape
    if d!=3 or Dtrain.shape!=(n,6) or Vtrain.shape!=(n,n) or n<=6+3:
        raise ValueError("original six-code three-metabolite training frame required")
    if not np.isfinite(Ytrain).all() or not np.isfinite(Dtrain).all():
        raise ValueError("nonfinite original training source data")
    signV,logV=np.linalg.slogdet(Vtrain)
    if signV<=0:
        raise ValueError("working molecular covariance not positive definite")
    P=np.linalg.solve(Vtrain,np.eye(n))
    A=Dtrain.T@P@Dtrain
    signA,logA=np.linalg.slogdet(A)
    if signA<=0:
        raise ValueError("one original pigment class missing from the training fold")
    beta=np.linalg.solve(A,Dtrain.T@P@Ytrain)
    E=Ytrain-Dtrain@beta
    S=(E.T@P@E)/(n-Dtrain.shape[1])
    signS,logS=np.linalg.slogdet((S+S.T)*.5)
    if signS<=0:
        raise ValueError("source metabolite residual compound covariance is singular")
    return float(-.5*(d*logV+d*logA+(n-6)*logS))


def training_only_lambda_choice(Y:np.ndarray,D:np.ndarray,C:np.ndarray,
                                lambdas:list[float])->dict:
    """Return selected lambda per heldout tip from *other 46* phenotype data.

    Uses a multivariate source REML score with all six source colour-code
    fixed intercepts and full 3-compound training residual covariance.
    """
    n=len(Y)
    if Y.shape!=(n,3) or D.shape!=(n,6) or C.shape!=(n,n) or n!=47:
        raise ValueError("the immutable original 47-tip frame required")
    if len(lambdas)!=8 or sorted(set(lambdas))!=lambdas:
        raise ValueError("source eight candidate lambda grid changed")
    order=np.arange(n)
    all_scores=[]
    selections=[]
    for i in order:
        keep=order!=i
        score=[]
        for lam in lambdas:
            V=source_working_V(C,lam)
            candidate=fold_training_reml_score(
                Y[keep],D[keep],V[np.ix_(keep,keep)])
            score.append(candidate)
        k=int(np.argmax(score))
        all_scores.append(score)
        selections.append(float(lambdas[k]))
    return {
        "lambdas":selections,
        "train46_multivariate_REML_scores":all_scores,
        "n_training_species_each_fold":46,
        "model_choice_is_conditioned_only_on_other46_Y":True
    }


def source_original_targets(source:Path,original:dict,prediction:dict,
                            expected:dict)->dict:
    distances,codes,names,all_expr=load_source(source,prediction,original)
    if len(names)!=47 or all_expr.shape!=(47,21):
        raise ValueError("source original 47 species and 21 source genes changed")
    D=fixed_source_D(codes)
    genes=original["primary"]["raw_gene_expression_columns"]
    if (expected["frozen_source_frame"]["four_expression_genes"]!=list(GENES) or
        expected["frozen_source_frame"]["three_measured_flavonols"]!=list(METABOLITES)):
        raise ValueError("original source candidate genes/metabolites changed")
    X=all_expr[:,[genes.index(g) for g in GENES]]
    csv=pd.read_csv(source/original["source"]["processed_csv_path"])
    if len(csv)!=60 or csv["key_0"].duplicated().any():
        raise ValueError("original source 60-row assay identity failed")
    mg=csv.set_index("key_0").loc[names,list(METABOLITES)].to_numpy(dtype=float)
    if not np.isfinite(mg).all() or np.min(mg)<0:
        raise ValueError("original three measured product amounts invalid")
    Y=np.log1p(100*mg)
    C=phylo_shared_root_covariance(source/original["source"]["tree_path"],names)["C"]
    return {"Y":Y,"X":X,"D":D,"C":C,"codes":codes,"names":names}


def run(source:Path,design:dict,original:dict,prediction:dict,
        original_phylogeny_result:dict)->dict:
    if design["status"]!="POST_OUTCOME_SOURCE_EXPOSED_TRAINING_ONLY_PHYLOGENETIC_COVARIANCE_SENSITIVITY":
        raise ValueError("post-outcome source sensitivity identity not preserved")
    data=source_original_targets(source,original,prediction,design)
    Y,X,D,C=(data[k] for k in ("Y","X","D","C"))
    lambdas=design["frozen_source_frame"]["lambda_grid"]
    chosen=training_only_lambda_choice(Y,D,C,lambdas)
    all_baselines=[]
    all_candidates=[]
    # All 47 original source LOO prediction rows are algebraically identical
    # to an explicit other-46 train-only penalized GLS/GP kriging fit.
    for lam in lambdas:
        V=source_working_V(C,lam)
        P=np.linalg.solve(V,np.eye(len(V)))
        Hb=loo_linear_kriging_operator(P,D,None,10.)
        Hg=loo_linear_kriging_operator(P,D,X,10.)
        all_baselines.append(Hb@Y)
        all_candidates.append(Hg@Y)
    source_tip_order=data["names"]
    rank={lam:k for k,lam in enumerate(lambdas)}
    predicted_b=np.stack([all_baselines[rank[lam]][i] for i,lam in
                          enumerate(chosen["lambdas"])])
    predicted_g=np.stack([all_candidates[rank[lam]][i] for i,lam in
                          enumerate(chosen["lambdas"])])
    out=error_metrics(Y,predicted_b,predicted_g)
    if chosen["n_training_species_each_fold"]!=46 or len(chosen["lambdas"])!=47:
        raise ValueError("training-only phylogenetic lambda selection source changed")
    for test_lam,label,baseline,gene in [
        (0.0,"0","original_lambda0_class_ridge_gain_reproduced",
         "original_lambda0_class_ridge_gain_reproduced"),
        (0.5,"0.5","primary_phylogeny_plus_pigment_baseline_MSE",
         "primary_phylogeny_plus_pigment_plus_four_gene_MSE")
    ]:
        if test_lam not in rank:
            raise ValueError("original 0 and 0.5 fixed covariance source controls absent")
        prediction_b=all_baselines[rank[test_lam]]
        prediction_g=all_candidates[rank[test_lam]]
        metrics=error_metrics(Y,prediction_b,prediction_g)
        if label=="0":
            prior=original_phylogeny_result["original_lambda0_class_ridge_gain_reproduced"]
            if abs(metrics["gain"]-prior)>1e-10:
                raise ValueError("original independent-residual original source model drift")
        else:
            if (abs(metrics["base_mse"]-original_phylogeny_result[baseline])>1e-10 or
                abs(metrics["gene_mse"]-original_phylogeny_result[gene])>1e-10):
                raise ValueError("original fixed .5 phylogenetic source model drift")
    alpha=design["frozen_source_frame"]["ridge_alpha"]
    if alpha!=10:
        raise ValueError("source ridge hyperparameter changed")
    count=Counter(str(x) for x in chosen["lambdas"])
    values=chosen["lambdas"]
    return {
        "version":"v0.1",
        "status":"POST_OUTCOME_TRAIN_ONLY_LAMBDA_GAIN_SOURCE_AUDIT_NO_NEW_P",
        "analysis_role":"POST_OUTCOME_SOURCE_EXPOSED_PREDICTION_SENSITIVITY_NO_NEW_P_VALUE",
        "source_original_47_tips_sha_check_passed":True,
        "source_fixed_six_pigment_classes":dict(sorted(Counter(data["codes"]).items())),
        "n_original_species":47,
        "original_four_gene_predictors":list(GENES),
        "original_three_flavonol_products":list(METABOLITES),
        "original_fixed_ridge_alpha":10,
        "frozen_training_only_lambda_candidates":lambdas,
        "chosen_lambda_counts":dict(sorted(count.items())),
        "chosen_lambda_mean":float(np.mean(values)),
        "selected_lambda_per_original_taxon":[
            {"source_species":name,"selected_lambda_from_other_46":lam}
            for name,lam in zip(source_tip_order,values)
        ],
        "original_class_plus_source_training_selected_phylogeny_MSE":out["base_mse"],
        "original_class_plus_source_selected_phylogeny_plus_genes_MSE":out["gene_mse"],
        "additional_gene_relative_gain":out["gain"],
        "source_taxa_improved":out["source_taxa_with_gain"],
        "source_taxa_worse":out["source_taxa_with_loss"],
        "source_measured_product_gain_by_compound_descriptive":out["per_flavonol_descriptive"],
        "prior_fixed_lambda_half_gain":original_phylogeny_result[
            "primary_additional_expression_gain_over_phylogeny"],
        "prior_fixed_lambda_half_model_p":original_phylogeny_result[
            "source_model_conditional_p_one_sided"],
        "prior_lambda0_gain":original_phylogeny_result[
            "original_lambda0_class_ridge_gain_reproduced"],
        "source_original_tree_class_gene_cohort_unmodified":True,
        "all_fold_lambdas_selected_using_only_training_metabolite_Y":True,
        "working_covariance_lambda_REML_not_causal_or_truth_proven":True,
        "no_new_statistical_P_values":True,
        "no_source_independent_radiation_replication":True,
        "no_pollinator_UV_flower_fitness_interpretation":True,
        "original_AJB_Camellia_EL_frozen_and_integrated_draft":True
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--design",type=Path,required=True)
    p.add_argument("--original-design",type=Path,required=True)
    p.add_argument("--original-prediction-design",type=Path,required=True)
    p.add_argument("--original-phylo-result",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    result=run(
        a.source,
        json.loads(a.design.read_text()),
        json.loads(a.original_design.read_text()),
        json.loads(a.original_prediction_design.read_text()),
        json.loads(a.original_phylo_result.read_text()))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n",
                     encoding="utf-8")
    print("PETUNIEAE_TRAIN_ONLY_PHYLOGENY_LAMBDA_SOURCE_RESULT",json.dumps({
        key:result[key] for key in (
            "status","chosen_lambda_counts",
            "original_class_plus_source_training_selected_phylogeny_MSE",
            "original_class_plus_source_selected_phylogeny_plus_genes_MSE",
            "additional_gene_relative_gain","source_taxa_improved",
            "source_taxa_worse")},sort_keys=True))
    print("PETUNIEAE_TRAIN_ONLY_PHYLOGENY_FULL_ORIGINAL_SOURCE_JSON",json.dumps(result,sort_keys=True))
    print("NO_NEW_PHYLOGENY_MODEL_P_OR_CAUSAL_EVOLUTIONARY_MEMORY_TEST")


if __name__=="__main__":
    main()
