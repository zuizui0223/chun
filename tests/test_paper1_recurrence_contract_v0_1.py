from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "analyze_observation_corrected_recurrence_v0_1.py"
spec = importlib.util.spec_from_file_location("paper1_recurrence", SCRIPT)
rec = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(rec)


def _candidate_free_rows() -> list[dict[str, str]]:
    rows = rec.read(ROOT / "data" / "paper1_fig2_candidate_free_signature_v0_2.csv")
    return [
        {
            "measurement_id": (
                f"{r['transition_class']}::{r['dependence_cluster']}::{r['axis']}"
            ),
            "dependence_cluster": r["dependence_cluster"],
            "transition_class": r["transition_class"],
            "axis": r["axis"],
            "direction": r["direction"],
            "status": r["status"],
            "source": (
                "paper1_fig2_candidate_free_signature_v0_2.csv;"
                f"run={r['source_run']}"
            ),
        }
        for r in rows
    ]


def _current_recurrence_contract() -> tuple[dict, dict, dict]:
    literature, _ = rec.literature(
        rec.read(ROOT / "data" / "micro_accessibility_recurrence_registry_v0_2.csv"),
        rec.read(ROOT / "data" / "micro_transition_canonical_orientation_v0_2.csv"),
    )
    candidate_free = rec.candidate(_candidate_free_rows())
    return (
        rec.contraction(literature, candidate_free),
        rec.overlap(literature, candidate_free),
        candidate_free,
    )


def test_anthocyanin_recurrence_contract() -> None:
    contraction, overlap, _ = _current_recurrence_contract()
    anth = contraction["anthocyanin_gain"]

    assert anth["common_clusters"] == [
        "CJAPONICA",
        "CRETICULATA",
        "CSIN_WHITE_PINK",
    ]

    lit = anth["literature_common_cluster_bounds"]
    assert lit["n_unresolved_cluster_axes"] == 6
    assert lit["n_exact_completions"] == 729
    assert lit["exact_signature_recurrence"]["minimum"] == pytest.approx(
        1 / 3, rel=0, abs=1e-15
    )
    assert lit["exact_signature_recurrence"]["maximum"] == pytest.approx(
        1.0, rel=0, abs=1e-15
    )
    assert lit["pairwise_axis_concordance"]["minimum"] == pytest.approx(
        1 / 3, rel=0, abs=1e-15
    )
    assert lit["pairwise_axis_concordance"]["maximum"] == pytest.approx(
        1.0, rel=0, abs=1e-15
    )

    cf = anth["candidate_free_common_cluster_bounds"]
    assert cf["exact_signature_recurrence"]["minimum"] == pytest.approx(
        1 / 3, rel=0, abs=1e-15
    )
    assert cf["exact_signature_recurrence"]["maximum"] == pytest.approx(
        1 / 3, rel=0, abs=1e-15
    )
    assert cf["pairwise_axis_concordance"]["minimum"] == pytest.approx(
        1 / 3, rel=0, abs=1e-15
    )
    assert cf["pairwise_axis_concordance"]["maximum"] == pytest.approx(
        0.5, rel=0, abs=1e-15
    )
    assert anth["literature_width"] == pytest.approx(2 / 3, rel=0, abs=1e-15)
    assert anth["candidate_free_width"] == pytest.approx(1 / 6, rel=0, abs=1e-15)
    assert anth["width_reduction"] == pytest.approx(0.5, rel=0, abs=1e-15)

    direct = overlap["anthocyanin_gain"]
    assert direct["n_comparable_resolved_cells"] == 6
    assert direct["n_agree"] == 2
    assert direct["agreement_fraction"] == pytest.approx(1 / 3, rel=0, abs=1e-15)
    conflicts = {
        (x["cluster"], x["axis"], x["literature"], x["candidate_free"])
        for x in direct["conflicts"]
    }
    assert conflicts == {
        ("CJAPONICA", "A", "up", "down"),
        ("CJAPONICA", "F", "down", "up"),
        ("CRETICULATA", "P", "down", "up"),
        ("CSIN_WHITE_PINK", "A", "up", "down"),
    }


def test_yellow_modular_recurrence_contract() -> None:
    contraction, _, _ = _current_recurrence_contract()
    yellow = contraction["yellow_development"]["candidate_free_common_cluster_bounds"]

    assert yellow["n_clusters"] == 2
    assert yellow["n_unresolved_cluster_axes"] == 0
    assert yellow["n_exact_completions"] == 1
    assert yellow["exact_signature_recurrence"]["minimum"] == pytest.approx(
        0.5, rel=0, abs=1e-15
    )
    assert yellow["exact_signature_recurrence"]["maximum"] == pytest.approx(
        0.5, rel=0, abs=1e-15
    )
    assert yellow["pairwise_axis_concordance"]["minimum"] == pytest.approx(
        0.75, rel=0, abs=1e-15
    )
    assert yellow["pairwise_axis_concordance"]["maximum"] == pytest.approx(
        0.75, rel=0, abs=1e-15
    )
