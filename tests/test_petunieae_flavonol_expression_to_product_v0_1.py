from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location(
    "petunieae_flavonol_gene_product",
    ROOT/"scripts/analyze_petunieae_flavonol_expression_to_product_v0_1.py"
)
m=importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(m)

DESIGN=ROOT/"data/petunieae_flavonol_expression_to_product_design_v0_1.json"

def synthetic():
    rng=np.random.default_rng(120)
    codes=["A"]*5+["B"]*4+["C"]*5
    x=rng.normal(size=(14,4))
    y=np.stack([
        1.4*x[:,0]-.6*x[:,1]+rng.normal(scale=.3,size=14),
        -.5*x[:,2]+rng.normal(scale=.3,size=14),
        rng.normal(size=14)
    ],axis=1)
    return x,y,codes


def test_train_only_gene_scaling_exactly_matches_manual_one_taxon_refits():
    x,y,codes=synthetic()
    state=m.prepare_source(x,y,codes)
    predicted=m.predict_from_prepared(state,10.)
    slow=[]
    for i,klass in enumerate(codes):
        training=np.arange(len(x))!=i
        xt,yt=x[training],y[training]
        cl=np.asarray(codes)[training]
        mean=xt.mean(axis=0);std=xt.std(axis=0,ddof=0)
        xz=(xt-mean)/std
        hold=(x[i]-mean)/std
        classx=np.array([xz[cl==s].mean(axis=0) for s in cl])
        classy=np.array([yt[cl==s].mean(axis=0) for s in cl])
        beta=np.linalg.solve(
            (xz-classx).T@(xz-classx)+10*np.eye(4),
            (xz-classx).T@(yt-classy))
        slow.append(yt[cl==klass].mean(axis=0)+(
            hold-xz[cl==klass].mean(axis=0))@beta)
    np.testing.assert_allclose(predicted,slow,rtol=1e-11,atol=1e-11)


def test_exact_original_class_mean_and_three_output_loss():
    x,y,codes=synthetic()
    data=m.prepare_source(x,y,codes)
    for i,cl in enumerate(codes):
        ids=[j for j,k in enumerate(codes) if i!=j and k==cl]
        np.testing.assert_allclose(data["baseline"][i],y[ids].mean(axis=0),atol=1e-12)
    output=m.loss_summary(data,m.predict_from_prepared(data,10.))
    assert output["n_taxa"]==14
    assert len(output["per_state"])==3
    assert len(output["per_target"])==3
    assert output["species_improved"]+output["species_worse"]<=14
    assert output["baseline_mse"]>0
    assert np.isfinite(output["relative_gain"])


def test_shuffle_intact_four_gene_vector_only_inside_original_class():
    x,y,codes=synthetic()
    rng=np.random.default_rng(900)
    order=m.within_class_permute(codes,rng)
    assert sorted(order)==list(range(14))
    assert all(codes[i]==codes[j] for i,j in enumerate(order))
    assert not np.array_equal(order,np.arange(14))
    state=m.prepare_source(x,y,codes)
    observed=m.loss_summary(state,m.predict_from_prepared(state,10.))
    permuted=m.loss_summary(state,m.predict_from_prepared(state,10.,order))
    assert np.isfinite(permuted["relative_gain"])
    assert abs(observed["baseline_mse"]-permuted["baseline_mse"])<1e-13


def test_invalid_sources_or_alpha_fail_closed():
    x,y,codes=synthetic()
    with pytest.raises(ValueError,match="four-gene"):
        m.prepare_source(x[:,:3],y,codes)
    with pytest.raises(ValueError,match="at least"):
        m.prepare_source(x,y,["A"]*13+["B"])
    state=m.prepare_source(x,y,codes)
    with pytest.raises(ValueError,match="positive ridge"):
        m.predict_from_prepared(state,-1)
    with pytest.raises(ValueError,match="preserve"):
        m.predict_from_prepared(state,10.,np.arange(14)[::-1])


def test_fixed_biological_question_and_source_outcome_are_distinct():
    d=json.loads(DESIGN.read_text(encoding="utf-8"))
    assert d["status"]=="RETROSPECTIVE_FIXED_FLAVONOL_EXPRESSION_TO_MEASURED_PRODUCT_TEST_PRE_OUTCOME"
    assert d["fixed_frame"]["n_original_species"]==47
    assert d["fixed_frame"]["biological_predictors"]==list(m.GENES)
    assert d["fixed_frame"]["measured_targets"]==list(m.METABOLITES)
    assert d["primary_model"]["fixed_ridge_alpha"]==10
    assert d["permutation"]["iterations"]==9999
    assert d["permutation"]["seed"]==20261020
    assert d["safeguards"]["source_was_outcome_exposed_before_this_new_question"]
    assert d["safeguards"]["original_flavonol_mg_g_ancestry_k2_prediction_negative_unchanged"]
    assert d["safeguards"]["no_claim_UV_reflectance_fitness_pollinator_link"]
    assert d["safeguards"]["original_camellia_AJB_EL_first_submission_unchanged"]
