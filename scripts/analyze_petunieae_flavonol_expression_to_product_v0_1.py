#!/usr/bin/env python3
"""Taxon-held-out Petunieae four-gene expression -> measured flavonol amounts.

Same 47 source species, six fixed anthocyanidin-presence groups. Class-only
means versus a fixed alpha=10 training-standardized ridge regression of
log1p four original gene-expression values onto log1p three observed flavonol
concentrations. Outcomes and source are retrospectively exposed. This is a
conditional prediction analysis, not causal mediation or an external trial.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

import numpy as np
import pandas as pd


GENES=("F3primeH","FLS","MYBFL","MYB12")
METABOLITES=("myr_mgg","quer_mgg","kaem_mgg")
STATES=("000000","000010","000011","000100","000110","000111")
COUNTS={"000000":6,"000010":6,"000011":6,"000100":10,"000110":6,"000111":13}


def within_class_permute(classes:list[str],rng:np.random.Generator)->np.ndarray:
    labels=np.asarray(classes)
    order=np.arange(len(labels))
    for key in sorted(set(labels)):
        idx=np.flatnonzero(labels==key)
        order[idx]=rng.permutation(idx)
    return order


def prepare_source(x:np.ndarray,y:np.ndarray,classes:list[str])->dict:
    x=np.asarray(x,dtype=float)
    y=np.asarray(y,dtype=float)
    if x.ndim!=2 or y.ndim!=2:
        raise ValueError("two-dimensional source predictors and responses required")
    n=x.shape[0]
    codes=np.asarray(classes)
    if (x.shape!=(n,4) or y.shape!=(n,3) or len(codes)!=n or n<8 or
        not np.isfinite(x).all() or not np.isfinite(y).all()):
        raise ValueError("unaltered four-gene and three-flavonol source frame required")
    counts=Counter(codes)
    if len(counts)<2 or min(counts.values())<3:
        raise ValueError("each original pigment class requires three or more taxa")

    mx=np.zeros_like(x)
    my=np.zeros_like(y)
    multiplier=np.empty(n,dtype=float)
    for klass,size in counts.items():
        idx=np.flatnonzero(codes==klass)
        mx[idx]=x[idx].mean(axis=0)
        my[idx]=y[idx].mean(axis=0)
        multiplier[idx]=size/(size-1)
    xc=x-mx
    yc=y-my
    baseline=my-yc/np.asarray([counts[k]-1 for k in codes])[:,None]

    meanx=(x.sum(axis=0)[None,:]-x)/(n-1)
    sd2x=(np.square(x).sum(axis=0)[None,:]-np.square(x))/(n-1)-np.square(meanx)
    sd2x=np.where(sd2x>1e-12,sd2x,1.0)
    meany=(y.sum(axis=0)[None,:]-y)/(n-1)
    sd2y=(np.square(y).sum(axis=0)[None,:]-np.square(y))/(n-1)-np.square(meany)
    sd2y=np.where(sd2y>1e-12,sd2y,1.0)
    return {"N":n,"Xc":xc,"Yc":yc,"groups":codes,"gamma":multiplier,
            "baseF":xc.T@xc,"baseline":baseline,
            "trainVarX":sd2x,"trainVarY":sd2y,"Y":y}


def predict_from_prepared(data:dict,alpha:float,order:np.ndarray|None=None)->np.ndarray:
    """Exact training-only 46-species ridge fits, vectorized across heldout tips.

    The fold-wise penalty in raw gene coordinates is alpha*training_gene_var,
    exactly equivalent to first training-only z-scoring the four predictors,
    then class-centering them, and fitting an unpenalized pigment-class
    intercept plus a common penalized four-gene slope across all classes.
    """
    if not np.isfinite(alpha) or not 0<alpha<1e8:
        raise ValueError("fixed positive ridge alpha required")
    n=data["N"]
    if order is None:
        order=np.arange(n)
    order=np.asarray(order,dtype=int)
    if (order.shape!=(n,) or sorted(order.tolist())!=list(range(n)) or
        np.any(data["groups"][order]!=data["groups"])):
        raise ValueError("complete whole-gene taxon permutation must preserve six-bit state")
    xc=data["Xc"][order]
    yc=data["Yc"]
    gamma=data["gamma"][:,None,None]
    cross=xc.T@yc
    lhs=np.array(data["baseF"][None,:,:]-
                 gamma*(xc[:,:,None]*xc[:,None,:]),copy=True)
    diag=np.arange(xc.shape[1])
    lhs[:,diag,diag]+=alpha*data["trainVarX"][order]
    rhs=cross[None,:,:]-gamma*(xc[:,:,None]*yc[:,None,:])
    beta=np.linalg.solve(lhs,rhs)
    return data["baseline"]+data["gamma"][:,None]*np.einsum("ni,nij->nj",xc,beta)


def loss_summary(data:dict,pred:np.ndarray)->dict:
    y=data["Y"]
    if pred.shape!=y.shape or not np.isfinite(pred).all():
        raise ValueError("invalid full biochemical output prediction")
    variance=data["trainVarY"]
    e0=np.square(data["baseline"]-y)/variance
    e1=np.square(pred-y)/variance
    baseline=float(e0.mean())
    model=float(e1.mean())
    if baseline<=1e-14:
        raise ValueError("original source overall class-mean baseline is zero")
    groups=[]
    for code in sorted(set(data["groups"])):
        idx=np.flatnonzero(data["groups"]==code)
        b=float(e0[idx].mean());r=float(e1[idx].mean())
        groups.append({"sixbit_state":str(code),"n_taxa":int(len(idx)),
                       "class_mean_MSE":b,"ridge_MSE":r,
                       "relative_gain":None if b<=1e-14 else float((b-r)/b)})
    components=[]
    for k,metabolite in enumerate(METABOLITES):
        baseline_k=float(e0[:,k].mean())
        components.append({
            "metabolite":metabolite,"baseline_MSE":baseline_k,
            "ridge_MSE":float(e1[:,k].mean()),
            "relative_gain":(None if baseline_k<=1e-14
                             else float((baseline_k-e1[:,k].mean())/baseline_k))
        })
    g=(baseline-model)/baseline
    return {"n_taxa":len(y),"baseline_mse":baseline,"ridge_mse":model,
            "relative_gain":float(g),
            "species_improved":int(np.count_nonzero(e1.mean(axis=1)<e0.mean(axis=1))),
            "species_worse":int(np.count_nonzero(e1.mean(axis=1)>e0.mean(axis=1))),
            "per_state":groups,"per_target":components,
            "per_recipient_baseline_loss":e0.mean(axis=1).tolist(),
            "per_recipient_ridge_loss":e1.mean(axis=1).tolist()}


def analyze(original_source:Path,design:dict,original:dict,prediction:dict,
            *,permutations_override:int|None=None)->dict:
    from run_petunieae_nested_regulatory_leaveoneout_prediction_v0_1 import (
        load_source,weights,loss_gain
    )
    if design["status"]!="RETROSPECTIVE_FIXED_FLAVONOL_EXPRESSION_TO_MEASURED_PRODUCT_TEST_PRE_OUTCOME":
        raise ValueError("source study biological hypothesis was not frozen")
    if (design["fixed_frame"]["biological_predictors"]!=list(GENES) or
        design["fixed_frame"]["measured_targets"]!=list(METABOLITES)):
        raise ValueError("biological gene and product source axes changed")
    if design["primary_model"]["fixed_ridge_alpha"]!=10:
        raise ValueError("fixed regularization must not be optimized after outcome")
    dist,fine,names,X21=load_source(original_source,prediction,original)
    if (len(names)!=47 or X21.shape!=(47,21) or
        dict(sorted(Counter(fine).items()))!=COUNTS):
        raise ValueError("original 47 species and six original pigment states changed")
    genes=original["primary"]["raw_gene_expression_columns"]
    ids=[genes.index(k) for k in GENES]
    x=X21[:,ids]  # original source log1p(TPM10K), already source-hash verified
    table=pd.read_csv(original_source/original["source"]["processed_csv_path"])
    if len(table)!=60 or table["key_0"].duplicated().any():
        raise ValueError("original compound assay source keys drifted")
    raw=table.set_index("key_0").loc[names,list(METABOLITES)].to_numpy(dtype=float)
    if not np.isfinite(raw).all() or (raw<0).any():
        raise ValueError("original measured flavonol mg/g invalid")
    y=np.log1p(100*raw)
    previous=json.loads((Path(__file__).resolve().parents[1]/
        design["source"]["prior_measured_metabolite_product_result"]).read_text(encoding="utf-8"))
    if (previous["status"]!="RETROSPECTIVE_ORIGINAL_METABOLITE_TRANSFER_ON_47_TIPS" or
        previous["n_original_taxa"]!=47 or
        previous["target_results"][0]["decision"]!="NOT_SUPPORTED_PRACTICAL_TRANSFER" or
        abs(previous["target_results"][0]["relative_practical_prediction_gain"]+
            0.2408027234935364)>1e-12):
        raise ValueError("frozen original flavonol amount nearest2 FAIL changed")
    W0,W2=weights(dist,fine,names,k=2)
    original_k2=loss_gain(y,W0,W2)
    if (abs(original_k2["state_only_mse"]-
            previous["target_results"][0]["class_mean_training_scaled_MSE"])>1e-10 or
        abs(original_k2["relative_gain"]-
            previous["target_results"][0]["relative_practical_prediction_gain"])>1e-10):
        raise ValueError("original 47 species measured concentration prediction source mismatch")
    state=prepare_source(x,y,fine)
    main=loss_summary(state,predict_from_prepared(state,10.))
    if abs(main["baseline_mse"]-original_k2["state_only_mse"])>1e-10:
        raise ValueError("class-only baseline violates original source fold")
    count=design["permutation"]["iterations"] if permutations_override is None else permutations_override
    if count<99:
        raise ValueError("frozen whole-taxon chemical prediction null undersampled")
    rng=np.random.default_rng(design["permutation"]["seed"])
    null=np.empty(count,dtype=float)
    for k in range(count):
        order=within_class_permute(fine,rng)
        null[k]=loss_summary(state,predict_from_prepared(state,10.,order))["relative_gain"]
    observed=main["relative_gain"]
    p=float((1+np.count_nonzero(null>=observed))/(count+1))
    positive=observed>0 and p<=.05
    alternatives={}
    for alpha in design["secondary_descriptive"]["fixed_alpha_sensitivity"]:
        if alpha not in [1,100]:
            raise ValueError("unexpected source sensitivity alpha")
        variants=loss_summary(state,predict_from_prepared(state,float(alpha)))
        alternatives[str(alpha)]={"relative_gain":variants["relative_gain"],
                                  "class_mean_MSE":variants["baseline_mse"],
                                  "ridge_MSE":variants["ridge_mse"],
                                  "no_p_value_or_hyperparameter_selection":True}
    return {
        "version":"v0.1",
        "status":("SUPPORTED_RETROSPECTIVE_WITHIN_SOURCE_EXPRESSION_TO_PRODUCT_TRANSFER"
                  if positive else "NOT_SUPPORTED_RETROSPECTIVE_EXPRESSION_TO_PRODUCT_TRANSFER"),
        "source_exposed_retrospective_analysis":True,
        "n_original_species":47,"n_original_sixbit_chemical_states":6,
        "original_class_counts":dict(sorted(Counter(fine).items())),
        "fixed_predictor_genes":list(GENES),
        "fixed_measured_flavonols":list(METABOLITES),
        "fixed_ridge_alpha":10,
        "train_standardization_source":"other 46 original tips per heldout fold only",
        "original_class_mean_MSE":main["baseline_mse"],
        "original_four_gene_ridge_MSE":main["ridge_mse"],
        "original_relative_prediction_gain":observed,
        "n_species_with_improved_prediction":main["species_improved"],
        "n_species_with_worse_prediction":main["species_worse"],
        "n_taxon_label_permutations":count,
        "seed":design["permutation"]["seed"],
        "null_mean_gain":float(null.mean()),
        "null_q025":float(np.quantile(null,.025)),
        "null_q975":float(np.quantile(null,.975)),
        "source_conditional_permutation_p_one_sided":p,
        "per_class_descriptive":main["per_state"],
        "per_measured_flavonol_descriptive":main["per_target"],
        "per_original_species_recipient_source":{
            "source_tip_identifiers":names,
            "per_tip_class_mean_loss":main["per_recipient_baseline_loss"],
            "per_tip_ridge_loss":main["per_recipient_ridge_loss"]
        },
        "alpha_sensitivity_descriptive_only":alternatives,
        "previous_flavonol_amount_original_k2_gain_unchanged":original_k2["relative_gain"],
        "original_flavonol_expression_gene_k2_gain_unchanged":0.05613676603732491,
        "source_original_CSV_tree_R_sha256_checked":True,
        "not_phylogeny_or_environment_adjusted_for_causality":True,
        "permutation_exchangeability_may_be_restricted_by_phylogeny":True,
        "no_measured_pollinator_fitness_or_UV_reflectance":True,
        "no_external_prospective_second_radiation":True,
        "original_camellia_AJB_EL_science_unchanged":True
    }


def main()->None:
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--design",type=Path,required=True)
    p.add_argument("--original-design",type=Path,required=True)
    p.add_argument("--original-prediction-design",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--permutations",type=int)
    options=p.parse_args()
    original=json.loads(options.original_design.read_text(encoding="utf-8"))
    pred=json.loads(options.original_prediction_design.read_text(encoding="utf-8"))
    d=json.loads(options.design.read_text(encoding="utf-8"))
    result=analyze(options.source,d,original,pred,
                   permutations_override=options.permutations)
    options.out.parent.mkdir(parents=True,exist_ok=True)
    options.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",
                           encoding="utf-8")
    print("PETUNIEAE_FLAVONOL_GENE_TO_PRODUCT_RESULT",json.dumps({
        k:result[k] for k in [
            "status","n_original_species","fixed_ridge_alpha",
            "original_class_mean_MSE","original_four_gene_ridge_MSE",
            "original_relative_prediction_gain","n_species_with_improved_prediction",
            "source_conditional_permutation_p_one_sided","per_measured_flavonol_descriptive",
            "alpha_sensitivity_descriptive_only"
        ]},sort_keys=True))
    print("NO_CAUSAL_GENE_TO_PRODUCT_OR_EXTERNAL_RADIATION_INFERENCE")


if __name__=="__main__":
    main()
