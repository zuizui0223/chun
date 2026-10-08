from __future__ import annotations

import csv
import json
from pathlib import Path
from statistics import median

import pytest

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "data" / "integrated_temporal_mechanisms_evidence_gate_v0_1.json"
MANUSCRIPT = ROOT / "manuscript" / "INTEGRATED_TEMPORAL_MEMORY_MECHANISMS_V0_1_DRAFT.md"
DECISION = ROOT / "docs" / "INTEGRATED_TEMPORAL_MECHANISMS_ONE_PAPER_DECISION_V0_1.md"


def _csv(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _gate() -> dict:
    return json.loads(GATE.read_text(encoding="utf-8"))


def test_temporal_hidden_and_mechanistic_claims_match_frozen_source_rows() -> None:
    d = _gate()
    temporal = _csv(d["evidence"]["temporal"]["source"])
    hidden = _csv(d["evidence"]["hidden"]["source"])
    mechanism = _csv(d["evidence"]["mechanism"]["source"])

    assert len(temporal) == d["evidence"]["temporal"]["eligible_clades"] == 32
    assert sum(float(r["slope"]) < 0 for r in temporal) == 23
    assert median(float(r["slope"]) for r in temporal) == pytest.approx(
        d["evidence"]["temporal"]["median_slope"], rel=0, abs=1e-4
    )

    assert len(hidden) == d["evidence"]["hidden"]["eligible_clades"] == 21
    assert sum(float(r["centered_auc_effect"]) > 0 for r in hidden) == 18
    assert median(float(r["centered_auc_effect"]) for r in hidden) == pytest.approx(
        d["evidence"]["hidden"]["median_centered_auc_effect"], rel=0, abs=1e-14
    )

    assert len(mechanism) == d["evidence"]["mechanism"]["systems"] == 7
    assert len({r["system"] for r in mechanism}) == 7
    assert sum(r["system"] == "CAMELLIA" for r in mechanism) == 1


def test_cross_tier_linkage_limit_is_auditable() -> None:
    d = _gate()
    temporal = {r["clade"].upper() for r in _csv(
        d["evidence"]["temporal"]["source"]
    )}
    hidden = {r["clade"].upper() for r in _csv(
        d["evidence"]["hidden"]["source"]
    )}
    mechanism = {r["system"].upper() for r in _csv(
        d["evidence"]["mechanism"]["source"]
    )}
    assert len(hidden & temporal) == 21
    assert len(temporal & mechanism) == 0
    assert "CAMELLIA" not in temporal
    assert d["cross_tier_linkage"]["direct_named_analytic_unit_intersection_temporal32_mechanistic7"] == 0
    assert d["cross_tier_linkage"]["camellia_in_temporal32"] is False
    assert d["cross_tier_linkage"]["current_same_radiation_quantitative_mechanism_memory_association_estimated"] is False


def test_proposal_cannot_relabel_distinct_evidence_tiers_as_joint_causal_result() -> None:
    d = _gate()
    manuscript = MANUSCRIPT.read_text(encoding="utf-8")
    decision = DECISION.read_text(encoding="utf-8")
    assert d["status"] == "INTEGRATED_SINGLE_PAPER_CANDIDATE_NOT_SUBMISSION_AUTHORIZED"
    assert d["original_submission_routes_unchanged"] is True
    assert d["governance"]["no_actual_joint_parameter"] is True
    assert d["governance"]["all_replication_tiers_kept_separate"] is True
    assert d["evidence"]["mechanism"]["rates_not_poolable"] is True
    for phrase in (
        "not evidence that molecular-route variation causes temporal memory decay",
        "zero exact analytic-unit name matches",
        "does not invent an unobserved clade-level genotype-to-memory mapping",
        "three of four signed axes",
        "not a submission-ready replacement",
    ):
        assert phrase.lower() in manuscript.lower()
    assert "SINGLE-ARTICLE_SUBMISSION_HOLD" in decision
    assert "0 exact matches" in decision
    for row in d["governance"]["prior_art"]:
        assert row["doi"] in manuscript or row["doi"] in decision
