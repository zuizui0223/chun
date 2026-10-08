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


def test_exact_signature_concentration_floor_is_zero_matching_pairs() -> None:
    """For n clusters, Simpson R=1/n means zero identical unordered cluster pairs."""
    _, _, candidate_free = _current_recurrence_contract()

    for transition_class, n_clusters, n_completions in (
        ("anthocyanin_gain", 3, 3),
        ("yellow_development", 2, 1),
    ):
        signature_map = candidate_free[transition_class]
        assert len(signature_map) == n_clusters
        result = rec.bounds(signature_map)
        assert result["n_exact_completions"] == n_completions

        # R = sum_s (c_s/n)^2, so the fraction of pairs with an identical
        # COMPLETE signature is M = (n*R - 1)/(n - 1).
        for bound in ("minimum", "maximum"):
            concentration = result["exact_signature_recurrence"][bound]
            assert concentration == pytest.approx(
                1 / n_clusters, rel=0, abs=1e-15
            )
            matching_pair_fraction = (
                n_clusters * concentration - 1
            ) / (n_clusters - 1)
            assert matching_pair_fraction == pytest.approx(
                0.0, rel=0, abs=1e-15
            )


def test_yellow_sign_only_modular_agreement_is_three_of_four_axes() -> None:
    """Directional module reuse is not identical complete-signature replay."""
    _, _, candidate_free = _current_recurrence_contract()
    signatures = candidate_free["yellow_development"]
    assert set(signatures) == {"CNITIDISSIMA", "CPERPETUA"}

    cn = dict(zip(rec.AXES, signatures["CNITIDISSIMA"]))
    cp = dict(zip(rec.AXES, signatures["CPERPETUA"]))
    assert {a for a in rec.AXES if cn[a] == cp[a]} == {"A", "C", "P"}
    assert {a for a in rec.AXES if cn[a] != cp[a]} == {"F"}
