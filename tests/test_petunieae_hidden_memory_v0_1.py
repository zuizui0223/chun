from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts"/"analyze_petunieae_hidden_memory_v0_1.py"
spec=importlib.util.spec_from_file_location("pet_hidden",SCRIPT)
if spec is None or spec.loader is None:
    raise RuntimeError("module load failed")
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_same_coarse_pairs_only():
    coarse=np.array([0,0,1,1,1])
    ii,jj=mod.same_coarse_pair_indices(coarse)
    assert list(zip(ii.tolist(),jj.tolist()))==[(0,1),(2,3),(2,4),(3,4)]


def test_auc_from_fixed_ranks_perfect_order():
    y=np.array([0,0,1,1],dtype=bool)
    ranks=np.array([1.,2.,3.,4.])
    assert np.isclose(mod.auc_from_y_ranks(y,ranks),1.0)


def test_within_coarse_permutation_preserves_group_counts():
    fine=np.array([0,0,1,2,2,3],dtype=int)
    coarse=np.array([0,0,0,1,1,1],dtype=int)
    rng=np.random.default_rng(11)
    p=mod.permute_fine_within_coarse(fine,coarse,rng)
    for g in np.unique(coarse):
        idx=np.where(coarse==g)[0]
        assert sorted(p[idx].tolist())==sorted(fine[idx].tolist())


def test_centered_effect_uses_null_mean():
    assert np.isclose(mod.centered_effect(0.7,np.array([0.6,0.62,0.64])),0.08)
