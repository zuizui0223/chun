from __future__ import annotations

import importlib.util
import itertools
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
SPEC=importlib.util.spec_from_file_location(
    "diagnose_petunieae_k2", ROOT/"scripts/diagnose_petunieae_k2_donor_penalty_v0_1.py"
)
mod=importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(mod)


def toy_frame():
    names=[f"A{i}" for i in range(5)]+[f"B{i}" for i in range(5)]
    fine=["A"]*5+["B"]*5
    pos=np.array([0.,.2,.7,1.5,3.0,4.,4.4,5.2,6.0,8.])
    dist=np.abs(pos[:,None]-pos[None,:])
    x=np.stack([pos,0.3*pos**2+1,np.sin(pos)+3],axis=1)
    return x,fine,names,dist


def test_analytic_random_two_mse_equals_exhaustive_donor_pair_enumeration():
    x,fine,names,D=toy_frame()
    n=len(fine)
    exact=[]
    for i,code in enumerate(fine):
        donors=[j for j,c in enumerate(fine) if c==code and i!=j]
        train=np.delete(x,i,axis=0)
        var=np.where(train.var(axis=0,ddof=0)>1e-12,train.var(axis=0,ddof=0),1.)
        error=[]
        for a,b in itertools.combinations(donors,2):
            pred=(x[a]+x[b])/2
            error.append(np.mean((x[i]-pred)**2/var))
        exact.append(np.mean(error))
    from run_petunieae_nested_regulatory_leaveoneout_prediction_v0_1 import weights,loss_gain
    a,b=weights(D,fine,names,k=2)
    p=loss_gain(x,a,b)
    prior={"baseline_loss":p["state_only_mse"],"neighbor_loss":p["phylogenetic_neighbor_mse"],
           "observed_relative_prediction_gain":p["relative_gain"]}
    diagnostic=mod.decompose(x,fine,names,D,prior)
    assert diagnostic["random_two_expected_mse"]==pytest.approx(np.mean(exact),abs=1e-12)
    assert diagnostic["algebraic_identity_pass"] is True
    assert diagnostic["small_donor_penalty"]>=0
    assert (diagnostic["small_donor_penalty"]-diagnostic["locality_gain_over_random_two"]
            ==pytest.approx(diagnostic["net_nearest_two_penalty"],abs=1e-12))
    assert diagnostic["frozen_primary_decision"]=="NOT_SUPPORTED"
    assert diagnostic["no_new_p_value"] is True


def test_diagnostic_refuses_changes_to_original_prediction_result():
    x,fine,names,D=toy_frame()
    prior={"baseline_loss":-100.,"neighbor_loss":1.,"observed_relative_prediction_gain":0.}
    with pytest.raises(ValueError,match="pre-existing frozen prediction result drift"):
        mod.decompose(x,fine,names,D,prior)


def test_real_exact_decomposition_keeps_original_prediction_fail_frozen():
    import json
    gate=json.loads((ROOT/"data/petunieae_k2_predictor_bias_variance_decomposition_design_v0_1.json").read_text(encoding="utf-8"))
    result=json.loads((ROOT/"results/petunieae_k2_donor_penalty_diagnostic_v0_1/result_v0_1.json").read_text(encoding="utf-8"))
    original=json.loads((ROOT/"results/petunieae_nested_regulatory_leaveoneout_prediction_v0_1/result_v0_1.json").read_text(encoding="utf-8"))
    assert gate["status"]=="EXPLORATORY_DIAGNOSTIC_FIXED_AFTER_PRIMARY_PREDICTION_FAIL_BEFORE_DECOMPOSITION_OUTCOME"
    assert result["status"]=="POST_OUTCOME_EXACT_PREDICTOR_DECOMPOSITION_DESCRIPTIVE_ONLY"
    assert result["sample_tips"]==47 and result["genes"]==21 and result["donors_k"]==2
    assert result["state_only_mse"]==pytest.approx(original["baseline_loss"],abs=1e-12)
    assert result["nearest_two_mse"]==pytest.approx(original["neighbor_loss"],abs=1e-12)
    assert result["random_two_expected_mse"]==pytest.approx(1.405938861662,abs=1e-9)
    assert result["small_donor_penalty"]==pytest.approx(result["random_two_expected_mse"]-result["state_only_mse"],abs=1e-9)
    assert result["locality_gain_over_random_two"]==pytest.approx(result["random_two_expected_mse"]-result["nearest_two_mse"],abs=1e-9)
    assert result["net_nearest_two_penalty"]==pytest.approx(result["nearest_two_mse"]-result["state_only_mse"],abs=1e-9)
    assert result["small_donor_penalty"]>result["locality_gain_over_random_two"]>0
    assert result["net_nearest_two_penalty"]>0
    assert result["no_new_p_value"] is True
    assert result["frozen_primary_decision"]==original["decision"]=="NOT_SUPPORTED"
    assert len(result["per_state_descriptive"])==6
    assert sum(row["locality_gain"]>0 for row in result["per_state_descriptive"])==6
