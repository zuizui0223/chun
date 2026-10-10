from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / "data/petunieae_nested_regulatory_memory_preregistered_design_v0_1.json"
RESULT = ROOT / "results/petunieae_nested_regulatory_memory_v0_1/result_v0_1.json"
SCRIPT = ROOT / "scripts/analyze_petunieae_nested_regulatory_memory_v0_1.py"
spec = importlib.util.spec_from_file_location("petunieae_reg_memory", SCRIPT)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


def test_frozen_design_and_observation_scopes_are_separate() -> None:
    d = json.loads(DESIGN.read_text(encoding="utf-8"))
    r = json.loads(RESULT.read_text(encoding="utf-8"))
    assert d["status"] == "PRE_OUTCOME_COMMIT_FOR_NEW_RETROSPECTIVE_ANALYSIS"
    assert "RETROSPECTIVE" in d["temporal_order"]["honest_label"]
    assert r["analysis_role"] == "RETROSPECTIVE_PREDECLARED_TEST_PETUNIEAE_ONE_RADIATION"
    assert r["design_commit"] == "91b10bede74ead47953b7a838adf64d95c59b7ed"
    assert r["source_hash_verified"] is True
    assert d["source"]["osf_node"] == "zg9cu"
    assert d["frame"]["n_retained_expected"] == r["retained_tips"] == 47
    assert d["frame"]["same_fine_unordered_pairs_expected"] == 183
    assert d["frame"]["coarse_counts_expected"] == r["coarse_state_counts"]
    assert d["frame"]["fine_state_count_expected"] == len(r["fine_state_counts"]) == 6
    assert sum(r["fine_state_counts"].values()) == 47
    assert sum(v * (v - 1) // 2 for v in r["fine_state_counts"].values()) == 183
    assert len(d["primary"]["raw_gene_expression_columns"]) == r["expression_feature_count"] == 21
    assert len(d["secondary"]["pigment_columns"]) == r["pigment_feature_count"] == 9
    assert r["zero_variance_expression_columns"] == []
    assert r["zero_variance_pigment_columns"] == ["Pel_mgg", "Cyan_mgg", "Peon_mgg"]


def test_existing_retrospective_primary_and_secondary_estimators_are_frozen() -> None:
    d = json.loads(DESIGN.read_text(encoding="utf-8"))
    r = json.loads(RESULT.read_text(encoding="utf-8"))
    primary = r["primary_conditional_expression_memory"]
    secondary = r["secondary_conditional_pigment_concentration_memory"]
    assert primary["n_permutations"] == secondary["n_permutations"] == 9999
    assert primary["random_seed"] == d["primary"]["random_seed"] == 20261008
    assert secondary["random_seed"] == 20261009
    assert primary["same_fine_unordered_pairs"] == secondary["same_fine_unordered_pairs"] == 183
    assert primary["rho"] == pytest.approx(0.607443846759381, rel=0, abs=1e-12)
    assert primary["null_mean_rho"] == pytest.approx(0.16539849544922783, rel=0, abs=1e-12)
    assert primary["p_one_sided"] == pytest.approx(0.0001, rel=0, abs=1e-12)
    assert primary["status"] == "POSITIVE_EXPLORATORY"
    assert primary["leave_one_tip_out"]["positive_count"] == 47
    assert primary["leave_one_tip_out"]["min_rho"] > 0
    assert secondary["rho"] == pytest.approx(0.219859118115024, rel=0, abs=1e-12)
    assert secondary["p_one_sided"] == pytest.approx(0.0554, rel=0, abs=1e-12)
    assert secondary["p_one_sided"] > 0.05
    assert r["source_article_doi"] == d["source"]["article_doi"] == "10.1098/rspb.2023.0275"


def test_helper_fine_states_and_standardization_are_outcome_rule_consistent() -> None:
    import pandas as pd
    frame = pd.DataFrame(
        {"A": [0.0, 2.0, 0.0], "B": [1.0, 1.0, 1.0]}
    )
    assert mod.fine_sixbit(frame, ["A", "B"]) == ["01", "11", "01"]
    x, zero = mod.zscale_log(frame[["A", "B"]].to_numpy(), 1.0)
    assert zero == ["1"]
    assert np.allclose(x[:, 1], 0)
    assert np.isfinite(x).all()
    ii, jj = mod.within_state_pairs(["01", "11", "01"])
    assert ii.tolist() == [0] and jj.tolist() == [2]


def test_whole_vector_within_state_permutation_is_seed_reproducible() -> None:
    fine = ["A"] * 4 + ["B"] * 4
    coords = np.array([0.0, 0.5, 1.0, 2.0, 3.0, 3.5, 4.5, 5.0])
    dist = np.abs(coords[:, None] - coords[None, :])
    vect = np.stack([coords, coords**2, 2 * coords], axis=1)
    a = mod.conditional_memory(dist, vect, fine, permutations=99, seed=17)
    b = mod.conditional_memory(dist, vect, fine, permutations=99, seed=17)
    assert a == b
    assert a["same_fine_unordered_pairs"] == 12
    assert a["n_permutations"] == 99
    assert 0 < a["p_one_sided"] <= 1.0
    assert np.isfinite(a["rho"])


def test_new_bridge_does_not_override_frozen_el_or_paper1() -> None:
    r = json.loads(RESULT.read_text(encoding="utf-8"))
    d = json.loads(DESIGN.read_text(encoding="utf-8"))
    assert d["no_post_hoc"]["one_radiation_only"] is True
    assert d["no_post_hoc"]["no_ancestral_branch_event_claim"] is True
    assert d["no_post_hoc"]["no_ecological_causation_claim"] is True
    assert "one radiation" in r["interpretation_boundary"][0].lower()
    assert any("not proof" in s for s in r["interpretation_boundary"])
