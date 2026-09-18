from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
from Bio import Phylo
from io import StringIO

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "run_flowerclades51_distance_persistence_v0_1.py"
spec = importlib.util.spec_from_file_location("persistence", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_pair_same_baseline_is_without_replacement_probability():
    states = np.array(["A", "A", "B", "B"], dtype=object)
    assert mod.pair_same_baseline(states) == 1 / 3


def test_persistence_curve_declines_when_only_close_pairs_share_state():
    states = np.array(["A", "A", "B", "B"], dtype=object)
    ii, jj = np.triu_indices(4, 1)
    # AA and BB are the two shortest pairs; all cross-state pairs are long.
    dist = np.array([0.1, 0.9, 0.9, 0.9, 0.9, 0.1], dtype=float)
    curve = mod.persistence_curve(dist, ii, jj, states, n_bins=2)
    assert len(curve["bins"]) == 2
    assert curve["bins"][0]["mean_distance"] < curve["bins"][1]["mean_distance"]
    assert curve["bins"][0]["excess_retention"] > curve["bins"][1]["excess_retention"]
    assert curve["bins"][0]["p_same"] > curve["baseline_same_probability"]


def test_root_to_tip_cv_detects_ultrametric_branch_lengths():
    tree = Phylo.read(StringIO("(A:1,B:1,(C:0.5,D:0.5):0.5);"), "newick")
    assert abs(mod.root_to_tip_cv(tree)) < 1e-12


def test_relative_divergence_time_is_fraction_of_crown_depth_for_ultrametric_tree():
    tree = Phylo.read(StringIO("(A:1,B:1,(C:0.5,D:0.5):0.5);"), "newick")
    tips = tree.get_terminals()
    ii, jj = np.triu_indices(len(tips), 1)
    dist = np.array([tree.distance(tips[int(a)], tips[int(b)]) for a, b in zip(ii, jj)])
    rel = mod.relative_divergence_time(tree, dist)
    assert rel.min() >= 0
    assert rel.max() <= 1 + 1e-12
    assert np.isclose(rel.max(), 1.0)


def test_fine_only_eligibility_does_not_require_coarse_variation():
    colors = ["red"] * 10 + ["orange"] * 10
    ok, reasons = mod.fine_only_eligibility(colors, minimum_tips=20, minimum_fine_states=2)
    assert ok is True
    assert reasons == []
