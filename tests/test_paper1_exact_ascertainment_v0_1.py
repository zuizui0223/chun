from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "analyze_micro_accessibility_v0_1.py"
spec = importlib.util.spec_from_file_location("micro_accessibility", SCRIPT)
micro = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(micro)


def _single_axis_row(axis: str) -> dict[str, str]:
    row = {name: "unknown" for name in micro.AXES}
    row[axis] = "up"
    return row


def test_exact_axis_null_matches_hand_enumerated_two_row_case() -> None:
    result = micro.ascertainment_exact_null(
        [_single_axis_row("A_change"), _single_axis_row("A_change")]
    )

    assert result["observed_axis_coverage"] == {
        "A_change": 2,
        "F_change": 0,
        "C_change": 0,
        "P_change": 0,
    }
    assert result["n_exact_axis_assignments"] == 16
    assert result["n_distinct_coverage_vectors"] == 10
    assert result["exact_p_A_enrichment"] == pytest.approx(1 / 16, rel=0, abs=1e-15)
    assert result["exact_p_any_axis_imbalance"] == pytest.approx(1 / 4, rel=0, abs=1e-15)


def test_paper1_luo_exact_ascertainment_contract() -> None:
    rows = micro.read_rows(ROOT / "data" / "micro_accessibility_edge_registry_v0_3.csv")
    micro.validate(rows)

    system = micro.ascertainment_exact_null(rows)
    collapsed = micro.ascertainment_exact_null(micro.collapse_dependence(rows))

    assert system["observed_axis_coverage"] == {
        "A_change": 10,
        "F_change": 5,
        "C_change": 1,
        "P_change": 3,
    }
    assert system["n_exact_axis_assignments"] == 127401984
    assert system["exact_p_A_enrichment"] == pytest.approx(
        0.0015277862548828125, abs=1e-15
    )
    assert system["exact_p_any_axis_imbalance"] == pytest.approx(
        0.003514796127507716, abs=1e-15
    )

    assert collapsed["observed_axis_coverage"] == {
        "A_change": 5,
        "F_change": 4,
        "C_change": 1,
        "P_change": 2,
    }
    assert collapsed["n_exact_axis_assignments"] == 3456
    assert collapsed["exact_p_A_enrichment"] == pytest.approx(0.078125, rel=0, abs=1e-15)
    assert collapsed["exact_p_any_axis_imbalance"] == pytest.approx(
        0.1736111111111111, abs=1e-15
    )
