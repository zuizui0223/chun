from __future__ import annotations
import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
PATH = ROOT / "scripts/audit_petunieae_regulatory_influence_v0_1.py"
spec = importlib.util.spec_from_file_location("petunieae_influence", PATH)
assert spec is not None and spec.loader is not None
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def miniature():
    rng = np.random.default_rng(20261010)
    fine = ["000010"] * 6 + ["000111"] * 6
    pos = np.array([0., .25, .5, 1.2, 1.7, 2.5, 4.1, 4.6, 5.1, 5.8, 6.4, 7.])
    dist = np.abs(pos[:, None] - pos[None, :])
    chemistry = np.column_stack([np.sin(pos), pos, np.zeros(len(pos))])
    expression = np.column_stack([
        np.cos(pos), pos ** 2, np.sin(2 * pos), rng.normal(size=len(pos))
    ])
    return dist, expression, fine, chemistry, ["gA", "gB", "gC", "gD"]


def test_independently_recomputes_frozen_model_structure_without_optimization():
    dist, expr, fine, chem, genes = miniature()
    original_expr = expr.copy()
    ans = mod.influence_diagnostics(dist, expr, fine, chem, genes)
    assert ans["n_tips"] == 12
    assert ans["n_gene_axes"] == 4
    assert ans["n_fine_codes"] == 2
    assert ans["same_code_pairs"] == 30
    assert len(ans["leave_one_gene_out"]) == 4
    assert [v["excluded_gene"] for v in ans["leave_one_gene_out"]] == genes
    assert len(ans["leave_one_fine_code_out_refit"]) == 2
    assert len(ans["per_code_original_fit_descriptive"]) == 2
    assert [v["same_code_pairs"] for v in ans["per_code_original_fit_descriptive"]] == [15, 15]
    assert all(np.isfinite(x["rho"]) for x in ans["leave_one_gene_out"])
    assert all(np.isfinite(x["rho"]) for x in ans["leave_one_fine_code_out_refit"])
    assert all(np.isfinite(x["within_class_rho"]) for x in ans["per_code_original_fit_descriptive"])
    assert ans["new_p_values"] == 0
    assert ans["not_independent_replication"] is True
    assert ans["no_causal_or_adaptive_inference"] is True
    assert ans["does_not_rescue_k2_prediction_fail"] is True
    assert ans["original_frozen_ajb_and_el_unchanged"] is True
    np.testing.assert_array_equal(expr, original_expr)


def test_deterministic_no_cherry_picked_axes_or_codings():
    inp = miniature()
    first = mod.influence_diagnostics(*inp)
    second = mod.influence_diagnostics(*inp)
    assert first == second
    assert len({x["excluded_fine_code"] for x in first["leave_one_fine_code_out_refit"]}) == 2


def test_fail_closed_on_broken_tip_panel_or_duplicate_gene():
    dist, expr, fine, chem, genes = miniature()
    with pytest.raises(ValueError, match="input frame mismatch"):
        mod.influence_diagnostics(dist[:6, :6], expr, fine, chem, genes)
    with pytest.raises(ValueError, match="gene / code panel invalid"):
        mod.influence_diagnostics(dist, expr, fine, chem, ["x", "x", "y", "z"])


def test_exact_no_new_inference_contract():
    from json import loads
    result_path = ROOT / "results/petunieae_pigment_adjusted_regulatory_memory_v0_1/result_v0_1.json"
    original = loads(result_path.read_text(encoding="utf-8"))
    assert original["n_tips"] == 47
    assert original["n_gene_axes"] == 21
    assert original["n_pairs"] == 183
    assert original["abundance_adjusted_rho"] == pytest.approx(.511199259788796, abs=1e-12)
    assert original["decision"] == "RETROSPECTIVE_SUPPORT"
