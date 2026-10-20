from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
SCRIPT=ROOT/"scripts/analyze_petunieae_phylo_conditional_gene_product_v0_1.py"
spec=importlib.util.spec_from_file_location("phylo_working_petunieae",SCRIPT)
m=importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(m)

DESIGN=ROOT/"data/petunieae_phylogenetic_conditional_gene_to_product_design_v0_1.json"


def source_synthetic():
    rng=np.random.default_rng(100)
    n=18
    classes=np.repeat(np.arange(6),3)
    D=np.eye(6)[classes]
    X=rng.normal(size=(n,4))
    Y=D@rng.normal(size=(6,3)) + X@rng.normal(size=(4,3)) + rng.normal(scale=.3,size=(n,3))
    B=rng.normal(size=(n,8))
    C=B@B.T/8
    d=np.diag(C)
    C=C/np.sqrt(d[:,None]*d[None,:])
    V=m.source_working_V(C,.5)
    P=np.linalg.inv(V)
    return D,X,Y,V,P


def test_exact_47_fold_kriging_operator_matches_explicit_training_only_gls():
    D,X,Y,V,P=source_synthetic()
    for designX in (None,X):
        H=m.loo_linear_kriging_operator(P,D,designX,10.)
        assert H.shape==(18,18)
        assert np.max(np.abs(np.diag(H)))<1e-10
        np.testing.assert_allclose(H@D,D,atol=1e-9)
        Z=D if designX is None else np.column_stack((D,designX))
        for i in (0,3,6,9,17):
            keep=np.arange(18)!=i
            covtrain=V[np.ix_(keep,keep)]
            Ptrain=np.linalg.inv(covtrain)
            Xt=Z[keep]
            gamma=np.zeros((Z.shape[1],Z.shape[1]))
            if designX is not None:
                gamma[np.arange(6,10),np.arange(6,10)]=10*np.var(designX[keep],axis=0)
            beta=np.linalg.solve(Xt.T@Ptrain@Xt+gamma,Xt.T@Ptrain@Y[keep])
            from_train=(Z[i]@beta+V[i,keep]@Ptrain@(Y[keep]-Xt@beta))
            np.testing.assert_allclose((H@Y)[i],from_train,atol=1e-10,rtol=1e-10)


def test_lambda_zero_is_unrelated_tip_residual_and_same_fixed_training_ridge():
    D,X,Y,V,P=source_synthetic()
    zero=np.eye(len(Y))
    H0=m.loo_linear_kriging_operator(zero,D,None,10.)
    H1=m.loo_linear_kriging_operator(zero,D,X,10.)
    from_gene=H1@Y
    baseline=H0@Y
    for i in (0,4,11,17):
        keep=np.arange(len(Y))!=i
        cl=int(np.argmax(D[i]))
        trainmean=Y[keep][D[keep,cl]==1].mean(axis=0)
        np.testing.assert_allclose(baseline[i],trainmean,atol=1e-10)
        Xt=np.column_stack((D[keep],X[keep]))
        p=np.zeros((10,10))
        p[np.arange(6,10),np.arange(6,10)]=10*np.var(X[keep],axis=0)
        beta=np.linalg.solve(Xt.T@Xt+p,Xt.T@Y[keep])
        np.testing.assert_allclose(from_gene[i],np.r_[D[i],X[i]]@beta,atol=1e-10)


def test_brownian_plus_nugget_covariance_and_model_physical_controls():
    D,X,Y,V,P=source_synthetic()
    eig=np.linalg.eigvalsh(V)
    assert np.min(eig)>0
    assert m.source_working_V(np.eye(5),0.5).shape==(5,5)
    for bad in (-.1,1.0,float("nan")):
        with pytest.raises(ValueError):
            m.source_working_V(np.eye(5),bad)
    with pytest.raises(ValueError,match="4 gene"):
        m.loo_linear_kriging_operator(P,D,X[:,:3],10.)


def test_parametric_null_returns_phylogenetically_correlated_metabolite_samples():
    D,X,Y,V,P=source_synthetic()
    a=m.fit_null_phylo_matrix_normal(Y,D,V)
    assert a["source_V_cholesky"].shape==(18,18)
    assert a["source_compound_Sigma_cholesky"].shape==(3,3)
    assert min(a["null_metabolite_compound_Sigma_eigenvalues"])>0
    assert a["original_source_null_mean"].shape==(18,3)
    sims=(a["original_source_null_mean"]+
          a["source_V_cholesky"]@np.random.default_rng(7).normal(size=(18,3))@
          a["source_compound_Sigma_cholesky"].T)
    assert np.isfinite(sims).all()
    base=m.loo_linear_kriging_operator(P,D,None,10.)@sims
    gene=m.loo_linear_kriging_operator(P,D,X,10.)@sims
    result=m.error_metrics(sims,base,gene)
    assert np.isfinite(result["gain"])
    assert result["base_mse"]>0
    assert len(result["per_flavonol_descriptive"])==3


def test_design_committed_before_original_phylogenetic_gain_and_no_causes():
    d=json.loads(DESIGN.read_text(encoding="utf-8"))
    assert d["status"].startswith("SOURCE_EXPOSED_NEW_PHYLOGENY_CONDITIONAL_PREDICTION_DESIGN")
    assert d["phylogenetic_covariance"]["primary_lambda"]==.5
    assert d["phylogenetic_covariance"]["sensitivity_lambdas"]==[.25,.75,.95]
    assert d["prediction"]["alpha"]==10
    assert d["inferential_null"]["iterations"]==9999
    assert d["inferential_null"]["seed"]==20261020
    assert d["unchanged_frame"]["n_source_taxa"]==47
    assert d["unchanged_frame"]["four_fixed_expression_predictors"]==list(m.GENES)
    assert d["unchanged_frame"]["three_fixed_measured_products"]==list(m.METABOLITES)
    assert d["governance"]["no_causal_inference"]
    assert d["governance"]["no_new_phenotype_UV_pollinator_fitness_link"]
    assert d["governance"]["integrated_CHUN_PR414_stays_DRAFT"]
    assert d["governance"]["original_camellia_AJB_and_EL_scientific_submission_assets_unchanged"]
