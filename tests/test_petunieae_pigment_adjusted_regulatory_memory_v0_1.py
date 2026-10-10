from __future__ import annotations
import importlib.util
import json
import sys
from pathlib import Path
import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
SCRIPT=ROOT/"scripts/analyze_petunieae_pigment_adjusted_regulatory_memory_v0_1.py"
spec=importlib.util.spec_from_file_location("pigment_adjusted_regulation",SCRIPT)
mod=importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)
DESIGN=ROOT/"data/petunieae_pigment_abundance_adjusted_regulatory_memory_design_v0_1.json"


def sample():
    labels=["A"]*6+["B"]*6
    n=len(labels)
    positions=np.array([0.,.2,.6,1.2,2.1,2.9,4.0,4.4,5.2,5.8,6.7,8.1])
    D=np.abs(positions[:,None]-positions[None,:])
    chem=np.stack([np.linspace(0,3,n),np.sin(positions)+2,np.zeros(n)],axis=1)
    x=np.stack([positions,np.square(positions),np.sin(positions)+2],axis=1)
    return D,labels,chem,x


def test_ranking_source_conditions_and_one_sided_result_scope():
    d=json.loads(DESIGN.read_text())
    assert d["status"]=="RETROSPECTIVE_NEW_ESTIMAND_FIXED_BEFORE_RESIDUALIZED_OUTCOME_CALCULATION"
    assert d["test"]["permutations"]==9999
    assert d["test"]["seed"]==20261010
    assert d["frame"]["same_class_pairs"]==183
    assert d["frame"]["retained_tips"]==47
    assert len(d["covariate_adjustment"]["columns"])==9
    assert len(d["frame"]["absent_after_rare_filter"])==3
    assert d["original_positive_rho_unchanged"]==pytest.approx(0.607443846759381)
    assert d["original_k2_prediction_failure_unchanged"] is True
    assert d["evidence_status"].startswith("Retrospective")


def test_residual_projection_removes_nuisance_columns_and_preserves_pair_dependency():
    dist,labels,chem,expr=sample()
    M,rank=mod.residual_projector(labels,chem)
    assert M.shape==(12,12)
    assert 2<=rank<12
    assert np.allclose(M@M,M,atol=1e-10)
    assert np.allclose(M,M.T,atol=1e-10)
    assert np.isfinite(M@expr).all()
    assert not np.allclose(M,0)


def test_biological_outcome_not_replaced_when_adjustment_is_applied():
    dist,labels,chem,expr=sample()
    first=mod.correlated_distance(dist,expr,labels,chem,permutations=99,seed=23,loo=True)
    second=mod.correlated_distance(dist,expr,labels,chem,permutations=99,seed=23,loo=True)
    assert first==second
    assert first["n_tips"]==12
    assert first["n_pairs"]==30
    assert first["n_gene_axes"]==3
    assert first["n_pigment_axes"]==3
    assert first["permutations"]==99
    assert 0<first["p_one_sided"]<=1
    assert first["decision"] in ("RETROSPECTIVE_SUPPORT","NOT_SUPPORTED")
    assert first["leave_one_tip_out_descriptive"]["n"]==12
    assert np.isfinite(first["permutation_null_mean"])


def test_not_every_class_has_two_donors_fail_closed():
    dist,labels,chem,expr=sample()
    with pytest.raises(ValueError,match="input row mismatch"):
        mod.correlated_distance(dist[:5,:5],expr,labels,chem,permutations=10)


def test_log_transform_and_invariant_zero_pigments():
    z,zeros=mod.standardized_log(np.array([[0.,1.,1.],[0.,2.,3.],[0.,5.,4.]]),100)
    assert zeros==[0]
    assert np.allclose(z[:,0],0)
    assert np.allclose(z[:,1:].mean(axis=0),0,atol=1e-12)


def test_actual_adjusted_source_outcome_matches_fixed_design_without_reclassifying_old_results():
    r=json.loads((ROOT/"results/petunieae_pigment_adjusted_regulatory_memory_v0_1/result_v0_1.json").read_text(encoding="utf-8"))
    d=json.loads(DESIGN.read_text(encoding="utf-8"))
    assert r["status"]=="PETUNIEAE_PIGMENT_ABUNDANCE_ADJUSTED_REGULATORY_MEMORY_RETROSPECTIVE"
    assert r["analysis_role"]=="POST_SOURCE_EXPOSURE_NEW_TEST_FROZEN_BEFORE_NEW_STATISTIC"
    assert r["design_status"]==d["status"]
    assert r["n_tips"]==47 and r["n_fine_states"]==6 and r["n_pairs"]==183
    assert r["n_gene_axes"]==21 and r["n_pigment_axes"]==9
    assert r["nuisance_rank"]==12
    assert r["permutations"]==d["test"]["permutations"]==9999
    assert r["seed"]==d["test"]["seed"]==20261010
    assert r["abundance_adjusted_rho"]==pytest.approx(0.511199259788796,rel=0,abs=1e-13)
    assert r["unadjusted_rho_on_this_frame"]==pytest.approx(d["original_positive_rho_unchanged"],rel=0,abs=1e-13)
    assert r["permutation_null_mean"]==pytest.approx(0.09532723294992239,rel=0,abs=1e-13)
    assert r["permutation_centered_rho"]==pytest.approx(r["abundance_adjusted_rho"]-r["permutation_null_mean"],abs=1e-13)
    assert r["p_one_sided"]==0.0002
    assert r["decision"]=="RETROSPECTIVE_SUPPORT"
    assert r["zero_variance_pigment_columns"]==d["frame"]["absent_after_rare_filter"]
    assert r["leave_one_tip_out_descriptive"]["positive_count"]==47
    assert r["leave_one_tip_out_descriptive"]["min_rho"]>0
    assert r["no_causal_independence_claimed"] is True
    assert r["does_not_replace_original_k2_prediction_fail"] is True
    assert r["does_not_replace_ajb_or_el_science"] is True
