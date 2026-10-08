from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
SCRIPT=ROOT/"scripts/run_petunieae_nested_regulatory_leaveoneout_prediction_v0_1.py"
spec=importlib.util.spec_from_file_location("petunieae_heldout",SCRIPT)
mod=importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


def _example():
    names=[f"a{i}" for i in range(6)]+[f"b{i}" for i in range(6)]
    fine=["A"]*6+["B"]*6
    coord=np.array([0,.2,.4,.6,.8,1,3,3.2,3.4,3.6,3.8,4.0])
    dist=np.abs(coord[:,None]-coord[None,:])+.01*(1-np.eye(12))
    expr=np.stack([coord,np.square(coord),np.sin(coord)],axis=1)
    return dist,fine,names,expr


def test_weights_hold_out_target_and_preserve_exact_fine_class():
    D,fine,names,x=_example()
    a,b=mod.weights(D,fine,names,2)
    assert a.shape==b.shape==(12,12)
    assert np.allclose(a.sum(axis=1),1)
    assert np.allclose(b.sum(axis=1),1)
    assert np.allclose(np.diag(a),0)
    assert np.allclose(np.diag(b),0)
    assert all(np.all(b[i,np.array(fine)!=fine[i]]==0) for i in range(12))
    assert all(np.count_nonzero(b[i])==2 for i in range(12))
    assert np.count_nonzero(a[0])==5


def test_predeclared_paired_prediction_returns_finite_seed_reproducible_result():
    D,fine,names,x=_example()
    a=mod.calculate(D,fine,names,x,k=2,permutations=99,seed=20261008)
    b=mod.calculate(D,fine,names,x,k=2,permutations=99,seed=20261008)
    assert a==b
    assert a["retained_tips"]==12
    assert a["neighbor_k"]==2
    assert a["expression_genes"]==3
    assert 0<a["p_one_sided"]<=1
    assert np.isfinite(a["observed_relative_prediction_gain"])
    assert len(a["per_class_descriptive"])==2
    assert a["leave_one_fine_class_out_descriptive"]["n"]==2


def test_unsupported_empty_class_and_single_tip_control_rejected():
    D,fine,names,x=_example()
    with pytest.raises(ValueError,match="fine state cannot supply"):
        mod.weights(D,["A"]+["B"]*11,names,2)
    with pytest.raises(ValueError,match="distance/tip frame"):
        mod.weights(D[:10,:10],fine,names,2)


def test_training_standardization_excludes_test_tip_and_zero_variance_safe():
    D,fine,names,x=_example()
    W0,W1=mod.weights(D,fine,names,2)
    x=np.concatenate([x,np.ones((12,1))],axis=1)
    r=mod.loss_gain(x,W0,W1)
    assert np.isfinite(r["relative_gain"])
    assert len(r["per_tip_state_only_mse"])==12
    assert len(r["per_tip_neighbor_mse"])==12
    assert np.isfinite(r["state_only_mse"])
