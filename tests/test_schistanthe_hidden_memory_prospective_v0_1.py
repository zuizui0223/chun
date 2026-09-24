from __future__ import annotations
import importlib.util
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts"/"run_schistanthe_hidden_memory_prospective_v0_1.py"
spec=importlib.util.spec_from_file_location("s",SCRIPT)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_same_coarse_pairs_only():
    c=np.array([0,0,1,1])
    ii,jj=mod.same_coarse_pair_indices(c)
    assert list(zip(ii.tolist(),jj.tolist()))==[(0,1),(2,3)]


def test_auc_rank_formula_perfect_order():
    y=np.array([False,False,True,True])
    ranks=np.array([1.,2.,3.,4.])
    assert np.isclose(mod.auc_from_y_ranks(y,ranks),1.0)


def test_permutation_preserves_fine_counts_within_coarse():
    fine=np.array([0,0,1,2,2,3],dtype=int)
    coarse=np.array([0,0,0,1,1,1],dtype=int)
    rng=np.random.default_rng(7)
    p=mod.permute_fine_within_coarse(fine,coarse,rng)
    for g in np.unique(coarse):
        idx=np.where(coarse==g)[0]
        assert sorted(p[idx].tolist())==sorted(fine[idx].tolist())


def test_pass_rule_requires_positive_centered_effect_and_p_le_005():
    assert mod.decision_label(0.01,0.05)=="PROSPECTIVE_SCHISTANTHE_HIDDEN_MEMORY_PASS"
    assert mod.decision_label(-0.01,0.01)=="PROSPECTIVE_SCHISTANTHE_HIDDEN_MEMORY_FAIL"
    assert mod.decision_label(0.01,0.051)=="PROSPECTIVE_SCHISTANTHE_HIDDEN_MEMORY_FAIL"
