#!/usr/bin/env python3
"""Phylogeny-conditioned Petunieae four-gene -> measured flavonol prediction.

An original-source retrospective *working Brownian+nugget phylogenetic GP*
benchmark: same 47 species, same 6 pigment code labels, same 4 measured gene
predictors, same 3 measured mg/g targets. Compare source phylo + classes
against source phylo + classes + measured gene expression using exact
leave-one-species-out penalized GLS / Gaussian kriging predictions.

The source conditional model and its parametric phylogenetic null were
fixed before opening their new numerical outcomes; none are external
validation or causal regulatory/fitness/evolutionary-decay tests.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys

from Bio import Phylo
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from run_petunieae_nested_regulatory_leaveoneout_prediction_v0_1 import load_source

GENES=("F3primeH","FLS","MYBFL","MYB12")
METABOLITES=("myr_mgg","quer_mgg","kaem_mgg")
COUNTS={"000000":6,"000010":6,"000011":6,"000100":10,"000110":6,"000111":13}


def phylo_shared_root_covariance(tree_path:Path,names:list[str])->dict:
    tree=Phylo.read(str(tree_path),"newick")
    if len(tree.get_terminals())!=60:
        raise ValueError("original source unaltered 60-tip phylogeny required")
    terminal={t.name:t for t in tree.get_terminals()}
    if any(k not in terminal for k in names) or len(names)!=len(set(names)):
        raise ValueError("source tip identity/join mismatch")
    if any(n.branch_length is not None and (not np.isfinite(n.branch_length) or n.branch_length<0)
           for n in tree.find_clades()):
        raise ValueError("negative or nonfinite original branch length")
    height=np.asarray([tree.distance(tree.root,terminal[k]) for k in names],dtype=float)
    if np.min(height)<=0 or not np.isfinite(height).all():
        raise ValueError("missing source root-to-tip dated-tree heights")
    n=len(names)
    C=np.empty((n,n),dtype=float)
    for i in range(n):
        C[i,i]=height[i]
        for j in range(i+1,n):
            x=tree.common_ancestor(terminal[names[i]],terminal[names[j]])
            C[i,j]=C[j,i]=float(tree.distance(tree.root,x))
    C=C/float(height.mean())
    C=(C+C.T)/2
    evals=np.linalg.eigvalsh(C)
    if evals[0]<=1e-8 or not np.isfinite(C).all():
        raise ValueError("original observed tree Brownian covariance not SPD")
    return {"C":C,"n_tips":n,"min_original_tip_height":float(np.min(height)),
            "max_original_tip_height":float(np.max(height)),
            "mean_tip_height":float(np.mean(height)),
            "minimum_normalized_tree_cov_eigenvalue":float(evals[0])}


def fixed_source_D(codes:list[str])->np.ndarray:
    if dict(sorted(Counter(codes).items()))!=COUNTS:
        raise ValueError("six original fine-code groups changed")
    return np.stack([np.asarray(codes)==k for k in sorted(COUNTS)],axis=1).astype(float)


def source_working_V(C:np.ndarray,lam:float)->np.ndarray:
    if not np.isfinite(lam) or not 0<=lam<1:
        raise ValueError("working fixed lambda must be between zero and one")
    n=len(C)
    if C.shape!=(n,n):
        raise ValueError("source C not square")
    V=(1.-lam)*np.eye(n)+lam*C
    if np.linalg.eigvalsh(V)[0]<=1e-8:
        raise ValueError("working Brownian+nugget covariance not SPD")
    return V


def loo_linear_kriging_operator(P:np.ndarray,D:np.ndarray,
                                X:np.ndarray|None,alpha:float)->np.ndarray:
    """Exact original-source LOO predictions Yhat=H@Y for common GP V.

    Derivation: full precision P=V^-1, heldout training-block precision
    (V_-i,-i)^-1 = P_-i,-i - (P_-i,i P_i,-i)/P_i,i.
    For each fold, fit six unpenalized class indicators plus optional fixed
    4-gene ridge in *other 46 training-only* gene z units; alpha*Var_46(gene)
    is the corresponding penalty in original log-expression coordinates.
    Then krige the heldout residual using the same fixed source tree V.
    H_ii=0 is required; no measured Y_i ever predicts itself.
    """
    n=len(D)
    if D.shape!=(n,6) or P.shape!=(n,n) or not np.isfinite(P).all():
        raise ValueError("original six-state source precision/frame required")
    if X is not None and (X.shape!=(n,4) or not np.isfinite(X).all()):
        raise ValueError("original fixed 4 gene columns required")
    if alpha<=0 or not np.isfinite(alpha):
        raise ValueError("fixed positive gene ridge penalty required")
    Z=D if X is None else np.column_stack((D,X))
    g=Z.shape[1]
    diag=np.diag(P)
    if np.min(diag)<=0:
        raise ValueError("precision diagonal not SPD")
    PZ=P@Z
    mat=Z.T@PZ
    fold=mat[None,:,:] - np.einsum("ni,nj->nij",PZ,PZ)/diag[:,None,None]
    if X is not None:
        mean=(np.sum(X,axis=0)[None,:]-X)/(n-1)
        var=(np.sum(np.square(X),axis=0)[None,:]-np.square(X))/(n-1)-np.square(mean)
        if not np.isfinite(var).all() or np.min(var)<=1e-12:
            raise ValueError("fixed 4 original gene columns not all variable in training sets")
        idx=np.arange(6,g)
        fold[:,idx,idx]+=alpha*var
    # Per-fold coefficient map from ALL Y to beta_{-i}; mathematically
    # equivalent to refitting all 46 tip GLS models explicitly.
    response=Z.T@P
    per_fold_response=(response[None,:,:] -
                       PZ[:,:,None]*P[:,None,:]/diag[:,None,None])
    coefficient=np.linalg.solve(fold,per_fold_response)
    H=np.eye(n)-P/diag[:,None]+np.einsum("ni,nij->nj",PZ,coefficient)/diag[:,None]
    if np.max(np.abs(np.diag(H)))>1e-8:
        raise ValueError("LOO operator unexpectedly includes its own Y_i")
    if np.max(np.abs(H@D-D))>1e-8:
        raise ValueError("LOO fit lost original six source-class unpenalized intercepts")
    return H


def error_metrics(Y:np.ndarray,baseline:np.ndarray,predicted:np.ndarray)->dict:
    n,p=Y.shape
    if p!=3 or n<8 or baseline.shape!=Y.shape or predicted.shape!=Y.shape:
        raise ValueError("same source 3-compound output and predictions required")
    mean=(np.sum(Y,axis=0)[None,:]-Y)/(n-1)
    var=(np.sum(np.square(Y),axis=0)[None,:]-np.square(Y))/(n-1)-np.square(mean)
    var=np.where(var>1e-12,var,1.0)
    e0=np.square(baseline-Y)/var
    e1=np.square(predicted-Y)/var
    b=float(np.mean(e0));a=float(np.mean(e1))
    if b<=1e-14 or not np.isfinite([b,a]).all():
        raise ValueError("source measured compound model has zero or invalid reference loss")
    return {"base_mse":b,"gene_mse":a,"gain":float((b-a)/b),
            "source_taxa_with_gain":int(np.count_nonzero(e1.mean(axis=1)<e0.mean(axis=1))),
            "source_taxa_with_loss":int(np.count_nonzero(e1.mean(axis=1)>e0.mean(axis=1))),
            "per_flavonol_descriptive":[
                {"compound":METABOLITES[j],"base_mse":float(np.mean(e0[:,j])),
                 "gene_mse":float(np.mean(e1[:,j])),
                 "relative_gain":float((np.mean(e0[:,j])-np.mean(e1[:,j]))/np.mean(e0[:,j]))}
                for j in range(3)]
            }


def fit_null_phylo_matrix_normal(Y:np.ndarray,D:np.ndarray,V:np.ndarray)->dict:
    P=np.linalg.solve(V,np.eye(len(V)))
    beta=np.linalg.solve(D.T@P@D,D.T@P@Y)
    residual=Y-D@beta
    sigma=residual.T@P@residual/(len(Y)-D.shape[1])
    sigma=(sigma+sigma.T)/2
    if np.linalg.eigvalsh(sigma)[0]<=1e-8:
        raise ValueError("source null metabolite residual covariance not SPD")
    return {"original_source_null_mean":D@beta,
            "source_V_cholesky":np.linalg.cholesky(V),
            "source_compound_Sigma_cholesky":np.linalg.cholesky(sigma),
            "null_metabolite_compound_Sigma_eigenvalues":np.linalg.eigvalsh(sigma).tolist(),
            "P":P}


def analyze(source:Path,design:dict,original:dict,prediction:dict,
            *,permutations_override:int|None=None)->dict:
    if design["status"]!=(
        "SOURCE_EXPOSED_NEW_PHYLOGENY_CONDITIONAL_PREDICTION_DESIGN_FROZEN_BEFORE_PHYLOGENETIC_BENCHMARK_OUTCOME"):
        raise ValueError("working phylogeny model design not frozen")
    controls=design["phylogenetic_covariance"]
    if (controls["primary_lambda"]!=.5 or
        controls["sensitivity_lambdas"]!=[.25,.75,.95] or
        design["prediction"]["alpha"]!=10):
        raise ValueError("working phylogenetic V/ridge support coefficients were changed")
    tree_dist,codes,names,Xall=load_source(source,prediction,original)
    if len(names)!=47 or Xall.shape!=(47,21):
        raise ValueError("source input tree/transcript fine-state frame changed")
    D=fixed_source_D(codes)
    actual_genes=original["primary"]["raw_gene_expression_columns"]
    gene_names=design["unchanged_frame"]["four_fixed_expression_predictors"]
    chemicals=design["unchanged_frame"]["three_fixed_measured_products"]
    if gene_names!=list(GENES) or chemicals!=list(METABOLITES):
        raise ValueError("frozen four-gene/three-original-flavonol target changed")
    X=Xall[:,[actual_genes.index(g) for g in GENES]]
    chem=pd.read_csv(source/original["source"]["processed_csv_path"])
    if len(chem)!=60 or chem["key_0"].duplicated().any():
        raise ValueError("original source measured chemical sample keys changed")
    measured=chem.set_index("key_0").loc[names,list(METABOLITES)].to_numpy(dtype=float)
    if np.min(measured)<0 or not np.isfinite(measured).all():
        raise ValueError("source flavonol concentrations negative/missing")
    Y=np.log1p(100*measured)
    prior=json.loads((ROOT/design["source"]["original_gene_product_source_positive"]).read_text())
    if prior["status"]!="SUPPORTED_RETROSPECTIVE_WITHIN_SOURCE_EXPRESSION_TO_PRODUCT_TRANSFER" or abs(
        prior["original_relative_practical_gain"]-.06420747753819912)>1e-12:
        raise ValueError("previous original class-only gene-to-product result altered")
    cov=phylo_shared_root_covariance(
        source/original["source"]["tree_path"],names)
    C=cov["C"]
    output={}
    for lam in [0,.25,.5,.75,.95]:
        V=source_working_V(C,lam)
        P=np.linalg.inv(V)
        baseline=loo_linear_kriging_operator(P,D,None,10.)@Y
        candidate=loo_linear_kriging_operator(P,D,X,10.)@Y
        output[str(lam)]=error_metrics(Y,baseline,candidate)
    # Strong reconstruction control: lambda=0 is algebraically identical to
    # prior original class+gene alpha10 training-only ridge regression.
    zero=output["0"]
    if (abs(zero["base_mse"]-prior["class_mean_scaled_MSE"])>1e-10 or
        abs(zero["gene_mse"]-prior["gene_plus_class_ridge_scaled_MSE"])>1e-10 or
        abs(zero["gain"]-prior["original_relative_practical_gain"])>1e-10):
        raise ValueError("lambda=0 did not reproduce the original source 47-fold ridge")
    lam=controls["primary_lambda"]
    V=source_working_V(C,lam)
    null_source=fit_null_phylo_matrix_normal(Y,D,V)
    P=null_source["P"]
    HB=loo_linear_kriging_operator(P,D,None,10.)
    HG=loo_linear_kriging_operator(P,D,X,10.)
    observed=output["0.5"]["gain"]
    count=(design["inferential_null"]["iterations"] if permutations_override is None
           else permutations_override)
    if count<99:
        raise ValueError("too few fixed phylogenetic model null iterations")
    rng=np.random.default_rng(design["inferential_null"]["seed"])
    null=np.empty(count)
    for i in range(count):
        simY=(null_source["original_source_null_mean"]+
              null_source["source_V_cholesky"]@rng.normal(size=Y.shape)@
              null_source["source_compound_Sigma_cholesky"].T)
        null[i]=error_metrics(simY,HB@simY,HG@simY)["gain"]
    p=float((1+np.count_nonzero(null>=observed))/(count+1))
    supported=observed>0 and p<=.05
    return {
        "version":"v0.1",
        "status":("SOURCE_MODEL_CONDITIONAL_POSITIVE" if supported else
                  "NOT_SUPPORTED_PHYLOGENY_CONDITIONAL_SOURCE_TRANSFER"),
        "original_source_exposed_retrospective_study":True,
        "source_47_tips_original_SHA_loader_passed":True,
        "source_six_original_pigment_classes":dict(sorted(Counter(codes).items())),
        "original_four_genes":list(GENES),
        "original_three_measured_products":list(METABOLITES),
        "original_n_species":47,
        "fixed_working_Brownian_plus_nugget_lambda":lam,
        "fixed_gene_alpha":10,
        "original_tree_covariance_summary":{
            k:cov[k] for k in (
                "n_tips","min_original_tip_height","max_original_tip_height",
                "mean_tip_height","minimum_normalized_tree_cov_eigenvalue")
        },
        "primary_phylogeny_plus_pigment_baseline_MSE":output["0.5"]["base_mse"],
        "primary_phylogeny_plus_pigment_plus_four_gene_MSE":output["0.5"]["gene_mse"],
        "primary_additional_expression_gain_over_phylogeny":observed,
        "source_phylogenetic_parametric_null_mean_gain":float(null.mean()),
        "source_phylogenetic_parametric_null_q025":float(np.quantile(null,.025)),
        "source_phylogenetic_parametric_null_q975":float(np.quantile(null,.975)),
        "source_model_conditional_p_one_sided":p,
        "source_model_permutations":count,
        "seed":design["inferential_null"]["seed"],
        "null_residual_compound_covariance_eigenvalues":
            null_source["null_metabolite_compound_Sigma_eigenvalues"],
        "original_lambda0_class_ridge_gain_reproduced":output["0"]["gain"],
        "observed_working_lambda_sensitivity":{
            code:{ "baseline_MSE":v["base_mse"],"four_gene_MSE":v["gene_mse"],
                   "gain":v["gain"],
                   "role":("ORIGINAL_UNADJUSTED_SOURCE" if code=="0" else
                           "FIXED_PHYLOGENY_WORKING_MODEL" if code=="0.5" else
                           "DESCRIPTIVE_LAMBDA_SENSITIVITY_NO_EXTRA_P")}
            for code,v in output.items()
        },
        "primary_source_recipient_improved":output["0.5"]["source_taxa_with_gain"],
        "primary_source_recipient_worsened":output["0.5"]["source_taxa_with_loss"],
        "primary_source_per_compound_descriptive":output["0.5"]["per_flavonol_descriptive"],
        "model_based_null_not_exact_phylogenetic_randomization":True,
        "no_causal_gene_to_product_conclusion":True,
        "no_environment_or_batch_adjustment":True,
        "no_external_radiation_replication":True,
        "original_unadjusted_source_positive_unchanged":True,
        "original_AJB_Camellia_EL_submission_unchanged":True
    }


def main()->None:
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--design",type=Path,required=True)
    p.add_argument("--original-design",type=Path,required=True)
    p.add_argument("--original-prediction-design",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--permutations",type=int,default=None)
    opts=p.parse_args()
    d=json.loads(opts.design.read_text())
    orig=json.loads(opts.original_design.read_text())
    pred=json.loads(opts.original_prediction_design.read_text())
    result=analyze(opts.source,d,orig,pred,
                   permutations_override=opts.permutations)
    opts.out.parent.mkdir(parents=True,exist_ok=True)
    opts.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("PETUNIEAE_PHYLO_CONDITIONAL_GENE_PRODUCT_SOURCE_RESULT",
          json.dumps(result,sort_keys=True))
    print("NO_CAUSAL_EVOLUTIONARY_MEMORY_OR_CROSS_RADIATION_REPLICATION")


if __name__=="__main__":
    main()
