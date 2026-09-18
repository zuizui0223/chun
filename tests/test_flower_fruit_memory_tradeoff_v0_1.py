from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "run_flower_fruit_memory_tradeoff_v0_1.py"
spec = importlib.util.spec_from_file_location("tradeoff", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_common_cross_organ_filter_removes_rare_state_from_both_organs():
    species = np.array(["a","b","c","d","e","f"], dtype=object)
    flower = np.array(["red","red","red","red","red","white"], dtype=object)
    fruit = np.array(["black","black","black","black","green","green"], dtype=object)
    keep = mod.common_cross_organ_keep_mask(flower, fruit, minimum_state_tips=2)
    assert species[keep].tolist() == ["a","b","c","d"]


def test_pair_same_baseline_without_replacement():
    states = np.array(["A","A","B","B"], dtype=object)
    assert np.isclose(mod.pair_same_baseline(states), 1/3)


def test_signed_area_is_positive_when_near_pairs_share_more_than_far_pairs():
    x = np.array([0.1, 0.4, 0.7, 1.0])
    y = np.array([0.6, 0.3, 0.1, 0.0])
    assert mod.signed_area(x, y) > 0


def test_one_sided_negative_permutation_p_is_small_for_perfect_inverse_order():
    x = np.arange(8, dtype=float)
    y = -x
    rho, p = mod.spearman_permutation_test(x, y, permutations=999, seed=7)
    assert rho < -0.99
    assert p <= 0.01
