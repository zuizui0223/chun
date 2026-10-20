from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
PATH=ROOT/"scripts/audit_petunieae_training_estimated_phylo_lambda_v0_1.py"
spec=importlib.util.spec_from_file_location("petunieae_training_reml",PATH)
m=importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(m)
DESIGN=ROOT/"data/petunieae_training_estimated_phylo_lambda_diagnostic_v0_1.json"
PRIOR=ROOT/"results/petunieae_phylo_conditional_gene_product_v0_1/result_v0_1.json"


def fixture():
    rng=np.random.default_rng(1492)
    classes=["000000"]*6+["000010"]*6+["000011"]*6+["000100"]*10+["000110"]*6+["000111"]*13
    D=m.fixed_source_D(classes)
    n=47
    # Scaled positive-definite correlated original-like tree covariance.
    A=rng.normal(size=(n,12))
    C=A@A.T/12
    heights=np.sqrt(np.diag(C))
    C=C/heights[:,None]/heights[None,:]
    Y=D@rng.normal(size=(6,3))+rng.normal(size=(n,3))
    return Y,D,C,classes


def test_reml_is_training_only_excluding_heldout_metabolite_response():
    Y,D,C,classes=fixture()
    grid=[0,.1,.25,.5,.75,.9,.95,.99]
    result=m.training_only_lambda_choice(Y,D,C,grid)
    assert len(result["lambdas"])==47
    assert len(result["train46_multivariate_REML_scores"])==47
    assert all(len(s)==8 for s in result["train46_multivariate_REML_scores"])
    assert result["model_choice_is_conditioned_only_on_other46_Y"]
    changed=np.array(Y,copy=True)
    changed[11]=np.array([10000.0,-10000.0,5000])
    modified=m.training_only_lambda_choice(changed,D,C,grid)
    np.testing.assert_allclose(
        result["train46_multivariate_REML_scores"][11],
        modified["train46_multivariate_REML_scores"][11],
        rtol=0,atol=1e-11)
    assert result["lambdas"][11]==modified["lambdas"][11]


def test_reml_score_matches_manual_original_training_multivariate_profile():
    Y,D,C,_=fixture()
    T=np.arange(47)!=12
    V=m.source_working_V(C,.5)
    v=V[np.ix_(T,T)]
    calc=m.fold_training_reml_score(Y[T],D[T],v)
    P=np.linalg.inv(v)
    A=D[T].T@P@D[T]
    beta=np.linalg.inv(A)@D[T].T@P@Y[T]
    E=Y[T]-D[T]@beta
    S=E.T@P@E/40
    expected=-.5*(3*np.linalg.slogdet(v)[1]
                  +3*np.linalg.slogdet(A)[1]+40*np.linalg.slogdet(S)[1])
    assert calc==pytest.approx(expected,abs=1e-10)
    with pytest.raises(ValueError):
        m.fold_training_reml_score(Y[:6],D[:6],v[:6,:6])


def test_frozen_original_47_tip_source_assumptions_are_not_redefined():
    d=json.loads(DESIGN.read_text(encoding="utf-8"))
    prior=json.loads(PRIOR.read_text(encoding="utf-8"))
    assert d["status"]=="POST_OUTCOME_SOURCE_EXPOSED_TRAINING_ONLY_PHYLOGENETIC_COVARIANCE_SENSITIVITY"
    assert d["frozen_source_frame"]["species_count"]==47
    assert d["frozen_source_frame"]["lambda_grid"]==[0,.1,.25,.5,.75,.9,.95,.99]
    assert d["frozen_source_frame"]["four_expression_genes"]==list(m.GENES)
    assert d["frozen_source_frame"]["three_measured_flavonols"]==list(m.METABOLITES)
    assert d["lambda_training_selection"]["no_lambda_hyperparameter_choice_from_candidate_gain"]
    assert d["controls"]["no_new_phylogenetic_parametric_null"]
    assert prior["status"]=="NOT_SUPPORTED_PHYLOGENY_CONDITIONAL_SOURCE_TRANSFER"
    assert prior["source_model_conditional_p_one_sided"]==.3439
    assert prior["original_lambda0_class_ridge_gain_reproduced"]==pytest.approx(
        .06420747753819912)
    assert d["interpretation"]["source_specific_retrospective_post_outcome_sensitivity"]
    assert d["interpretation"]["original_camellia_AJB_EL_frozen"]


SAVED=ROOT/"results/petunieae_training_estimated_phylo_lambda_v0_1/result_v0_1.json"


def test_actual_source_training_only_lambda_refit_retains_negative_gene_product_gain():
    x=json.loads(SAVED.read_text(encoding="utf-8"))
    assert x["status"]=="POST_OUTCOME_TRAIN_ONLY_LAMBDA_GAIN_SOURCE_AUDIT_NO_NEW_P"
    assert x["source_original_47_tips_sha_check_passed"]
    assert x["n_original_species"]==47
    assert x["chosen_lambda_counts"]=={"0.75":46,"0.9":1}
    assert sum(x["chosen_lambda_counts"].values())==47
    assert [row["source_species"] for row in x["selected_lambda_per_original_taxon"]
            if row["selected_lambda_from_other_46"]==0.9]==["BOAN"]
    assert x["original_four_gene_predictors"]==list(m.GENES)
    assert x["original_three_flavonol_products"]==list(m.METABOLITES)
    assert x["original_fixed_ridge_alpha"]==10
    assert x["frozen_training_only_lambda_candidates"]==[0,.1,.25,.5,.75,.9,.95,.99]
    assert x["original_class_plus_source_training_selected_phylogeny_MSE"]==pytest.approx(
        1.2388799997322677,abs=1e-12)
    assert x["original_class_plus_source_selected_phylogeny_plus_genes_MSE"]==pytest.approx(
        1.3185161555311964,abs=1e-12)
    assert x["additional_gene_relative_gain"]==pytest.approx(
        -0.06428076635036381,abs=1e-12)
    assert x["source_taxa_improved"]==21 and x["source_taxa_worse"]==26
    assert x["prior_fixed_lambda_half_gain"]==pytest.approx(-0.04208292517617994)
    assert x["prior_fixed_lambda_half_model_p"]==0.3439
    assert x["prior_lambda0_gain"]==pytest.approx(0.06420747753819912)
    assert x["all_fold_lambdas_selected_using_only_training_metabolite_Y"]
    assert x["no_new_statistical_P_values"] is True
    assert x["working_covariance_lambda_REML_not_causal_or_truth_proven"] is True
    assert x["original_AJB_Camellia_EL_frozen_and_integrated_draft"] is True
