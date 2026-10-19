from __future__ import annotations

import importlib.util
import itertools
import json
from pathlib import Path
import sys

import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
SCRIPT=ROOT/"scripts/analyze_petunieae_module_heldout_transfer_v0_1.py"
spec=importlib.util.spec_from_file_location("petunieae_module_transfer",SCRIPT)
module=importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)
from run_petunieae_nested_regulatory_leaveoneout_prediction_v0_1 import (
    weights, loss_gain
)
from analyze_petunieae_functional_module_memory_v0_1 import module_partition

DESIGN=ROOT/"data/petunieae_module_heldout_transfer_design_v0_1.json"
SOURCE=ROOT/"data/petunieae_nested_regulatory_memory_preregistered_design_v0_1.json"
PRED=ROOT/"data/petunieae_nested_regulatory_leaveoneout_prediction_design_v0_1.json"
MODULE=ROOT/"data/petunieae_functional_module_memory_design_v0_1.json"
ORIGINAL_OUTCOME=ROOT/"results/petunieae_nested_regulatory_leaveoneout_prediction_v0_1/result_v0_1.json"


def dataset():
    # 8 original taxa, two classes of 4 each, all 21 gene axes immutable.
    rng=np.random.default_rng(723)
    x=rng.normal(size=(8,21))
    codes=["000000"]*4+["000111"]*4
    tips=[f"s{i}" for i in range(8)]
    dist=np.abs(np.arange(8)[:,None]-np.arange(8)[None,:]).astype(float)
    dist+=np.ones_like(dist)*.01
    np.fill_diagonal(dist,0)
    w0,w1=weights(dist,codes,tips,k=2)
    return x,codes,w0,w1


def test_frozen_module_prediction_frame_k2_and_fail_original():
    des=json.loads(DESIGN.read_text())
    orig=json.loads(SOURCE.read_text())
    pred=json.loads(PRED.read_text())
    mod=json.loads(MODULE.read_text())
    old=json.loads(ORIGINAL_OUTCOME.read_text())
    mods,inds=module_partition(mod,orig)
    assert [m["id"] for m in mods]==[x["module_id"] for x in des["fixed_cohort"]["modules"]]
    assert list(map(len,inds))==[9,4,8]
    assert pred["predictor_2"]["k"]==2\n    assert des["heldout_prediction"]["no_k_optimization"]
    assert des["fixed_cohort"]["n_species"]==47
    assert des["fixed_cohort"]["matched_species_pairs"]==183
    assert des["null"]["iterations"]==9999
    assert des["null"]["seed"]==20261019
    assert des["null"]["module_effect_difference_tested"] is False
    assert des["decision_governance"]["original_full_21_gene_predictive_FAIL_unchanged"]
    assert old["decision"]=="NOT_SUPPORTED"
    assert old["observed_relative_prediction_gain"]==pytest.approx(-0.0990780619015505)


def test_all_gene_source_losses_equal_mean_module_gene_losses_not_selected():
    X,fine,w0,w1=dataset()
    des=json.loads(MODULE.read_text())
    orig=json.loads(SOURCE.read_text())
    _,groups=module_partition(des,orig)
    ans,byclass=module.modules_losses(X,w0,w1,groups,fine)
    fast=module.gains_only(X,w0,w1,groups)
    for i,a in enumerate(ans):
        assert a["gain_vs_full_class_mean"]==pytest.approx(fast[i],abs=1e-14)
    n=np.array([len(x) for x in groups])
    full=loss_gain(X,w0,w1)
    assert np.average([r["class_mean_MSE"] for r in ans],weights=n)==pytest.approx(
        full["state_only_mse"],abs=1e-13)
    assert np.average([r["nearest_two_MSE"] for r in ans],weights=n)==pytest.approx(
        full["phylogenetic_neighbor_mse"],abs=1e-13)
    assert len(byclass)==3 and all(len(rows)==2 for rows in byclass.values())


def test_expected_random_two_loss_is_exact_enumeration_of_pair_donors():
    x,codes,w0,w1=dataset()
    mod=json.loads(MODULE.read_text());orig=json.loads(SOURCE.read_text())
    _,ids=module_partition(mod,orig)
    ans,_=module.modules_losses(x,w0,w1,ids,codes)
    # Enumerate all two-donor alternatives for each withheld taxon and
    # compare their exact mean scaled fold-training loss to the formula.
    n=len(codes)
    mu=(x.sum(axis=0)[None,:]-x)/(n-1)
    var=(np.square(x).sum(axis=0)[None,:]-np.square(x))/(n-1)-np.square(mu)
    var=np.where(var>1e-12,var,1)
    rr=np.zeros((n,x.shape[1]))
    for i,f in enumerate(codes):
        other=[j for j,g in enumerate(codes) if g==f and j!=i]
        losses=[np.square(.5*(x[a]+x[b])-x[i])/var[i]
                for a,b in itertools.combinations(other,2)]
        rr[i]=np.mean(losses,axis=0)
    for mod_index,group in enumerate(ids):
        exact=float(rr[:,group].mean())
        assert ans[mod_index]["all_random_two_donor_mean_MSE"]==pytest.approx(exact,abs=1e-13)


def test_holm_controls_3_prespecified_family_pvalues_under_dependence():
    assert module.holm_adjust([.02,.03,.5])==pytest.approx([.06,.06,.5])
    assert module.holm_adjust([.001,.02,.04])==pytest.approx([.003,.04,.04])
    with pytest.raises(ValueError):
        module.holm_adjust([.1,.2])


def test_source_missing_fails_closed_without_fabricating_module_predictions():
    d=json.loads(DESIGN.read_text())
    orig=json.loads(SOURCE.read_text())
    pred=json.loads(PRED.read_text())
    m=json.loads(MODULE.read_text())
    with pytest.raises((FileNotFoundError,ValueError)):
        module.predict(ROOT/"no_verified_2023_source",orig,pred,m,d,iterations_override=99)
