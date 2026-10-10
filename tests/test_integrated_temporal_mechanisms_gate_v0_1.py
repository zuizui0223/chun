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
    assert "0 exact named analysis-unit matches" in decision
    for row in d["governance"]["prior_art"]:
        assert row["doi"] in manuscript or row["doi"] in decision


def test_integrated_single_radiation_bridge_is_matched_but_not_cross_radiation_causal() -> None:
    d = _gate()
    b = d["cross_tier_linkage"]["new_single_radiation_matched_petunieae_bridge"]
    r = json.loads((ROOT / b["source"]).read_text(encoding="utf-8"))
    assert b["status"] == "POSITIVE_EXPLORATORY"
    assert b["same_tree_tips"] == r["retained_tips"] == 47
    assert b["exact_six_anthocyanidin_presence_class_pair_count"] == 183
    assert b["gene_expression_dimensions"] == 21
    assert b["expression_distance_tree_distance_spearman_rho"] == pytest.approx(
        r["primary_conditional_expression_memory"]["rho"], rel=0, abs=1e-14
    )
    assert b["within_fine_permutation_one_sided_p"] == r["primary_conditional_expression_memory"]["p_one_sided"] == 0.0001
    assert b["leave_one_tip_out_positive_count"] == 47
    assert b["earlier_pigment_memory_test_is_same_47_tip_source"] is True
    assert b["not_joint_32_by_7_mechanism_memory_slope"] is True
    assert d["cross_tier_linkage"]["current_same_radiation_quantitative_mechanism_memory_association_estimated"] is False
    assert "RETROSPECTIVE" in b["prospective_status"]
    assert "independent" in d["governance"]["submission_decision"].lower()


def test_predeclared_nearest_two_prediction_failure_is_not_promoted_to_success() -> None:
    d = _gate()
    bridge = d["cross_tier_linkage"]["new_single_radiation_matched_petunieae_bridge"]
    recorded = bridge["heldout_prediction"]
    result = json.loads((ROOT / recorded["source"]).read_text(encoding="utf-8"))
    design = json.loads((ROOT / recorded["design"]).read_text(encoding="utf-8"))
    assert recorded["status"] == "NOT_SUPPORTED_PREDECLARED_POSITIVE_GAIN"
    assert result["decision"] == "NOT_SUPPORTED"
    assert recorded["state_only_loss"] == pytest.approx(result["baseline_loss"], rel=0, abs=1e-12)
    assert recorded["two_nearest_loss"] == pytest.approx(result["neighbor_loss"], rel=0, abs=1e-12)
    assert recorded["relative_gain"] == pytest.approx(
        result["observed_relative_prediction_gain"], rel=0, abs=1e-12
    )
    assert recorded["relative_gain"] < 0
    assert result["p_one_sided"] == recorded["within_class_whole_vector_permutation_p_greater_observed"] == 0.0014
    assert result["neighbor_k"] == design["predictor_2"]["k"] == 2
    assert result["retained_tips"] == design["retained_taxa"] == 47
    assert result["not_prospective_independent_validation"] is True
    assert "K2_PREDICTIVE_TRANSFER_FAIL" in d["governance"]["single_paper_status_after_heldout"]
    manuscript = MANUSCRIPT.read_text(encoding="utf-8")
    decision_doc = DECISION.read_text(encoding="utf-8")
    assert "1.13838" in manuscript and "1.25117" in manuscript
    assert "positive-gain requirement" in manuscript
    assert "9.91%" in decision_doc


def test_retained_pigment_state_coverage_limits_six_compound_generalization() -> None:
    d=_gate()
    b=d["cross_tier_linkage"]["new_single_radiation_matched_petunieae_bridge"]
    source=b["fine_state_coverage"]
    cov=json.loads((ROOT/source["source"]).read_text(encoding="utf-8"))
    assert (source["unfiltered_ingroup_tips"],source["retained_tips"],source["excluded_tips"]) == (59,47,12)
    assert source["retained_fine_states"] == cov["fine_states_retained"] == 6
    assert source["unfiltered_fine_states"] == cov["fine_states_unfiltered"] == 15
    assert source["actually_variable_compounds"] == cov["retained_variable_anthocyanidin_compounds"]
    assert source["structurally_absent_on_retained_frame"] == cov["retained_constant_zero_anthocyanidin_compounds"]
    assert source["all_pelargonidin_cyanidin_peonidin_positive_taxa_excluded"] is True
    assert cov["three_bit_reduction_preserves_fine_partition"] is True
    manuscript=MANUSCRIPT.read_text(encoding="utf-8")
    decision=DECISION.read_text(encoding="utf-8")
    assert "all taxa showing detectable pelargonidin, cyanidin or peonidin" in manuscript
    assert "six nominal assay dimensions reduce to three" in manuscript
    assert "Pelargonidin, cyanidin and peonidin are constant zero" in decision
    assert b["fine_state_coverage"]["no_source_outcome_reopened"] is True


def test_pigment_abundance_adjusted_gene_memory_keeps_positive_and_negative_evidence_distinct() -> None:
    gate = _gate()
    bridge = gate["cross_tier_linkage"]["new_single_radiation_matched_petunieae_bridge"]
    field = bridge["pigment_abundance_adjusted_regulatory_memory"]
    recorded = json.loads((ROOT / field["source"]).read_text(encoding="utf-8"))
    design = json.loads((ROOT / field["design"]).read_text(encoding="utf-8"))
    assert field["status"] == "RETROSPECTIVE_SUPPORT_AFTER_NINE_PIGMENT_AND_FINE_STATE_LINEAR_ADJUSTMENT"
    assert recorded["status"] == "PETUNIEAE_PIGMENT_ABUNDANCE_ADJUSTED_REGULATORY_MEMORY_RETROSPECTIVE"
    assert design["status"] == "RETROSPECTIVE_NEW_ESTIMAND_FIXED_BEFORE_RESIDUALIZED_OUTCOME_CALCULATION"
    assert recorded["n_tips"] == field["cohort_tips"] == 47
    assert recorded["n_pairs"] == field["same_fine_state_pairs"] == 183
    assert recorded["n_gene_axes"] == 21 and recorded["n_pigment_axes"] == 9
    assert recorded["nuisance_rank"] == 12
    assert recorded["unadjusted_rho_on_this_frame"] == pytest.approx(field["original_gene_expression_distance_rho"],abs=1e-12)
    assert recorded["abundance_adjusted_rho"] == pytest.approx(field["pigment_abundance_adjusted_gene_expression_distance_rho"],abs=1e-12)
    assert recorded["permutation_null_mean"] == pytest.approx(field["residual_permutation_null_mean"],abs=1e-12)
    assert recorded["permutation_centered_rho"] == pytest.approx(field["centered_residual_rho"],abs=1e-12)
    assert recorded["p_one_sided"] == field["upper_tail_permutation_p"] == 0.0002
    assert recorded["decision"] == "RETROSPECTIVE_SUPPORT"
    assert recorded["leave_one_tip_out_descriptive"]["positive_count"] == 47
    assert recorded["zero_variance_pigment_columns"] == field["zero_variance_assayed_pigment_components"]
    assert recorded["no_causal_independence_claimed"] is True
    assert recorded["does_not_replace_original_k2_prediction_fail"] is True
    assert bridge["heldout_prediction"]["status"] == "NOT_SUPPORTED_PREDECLARED_POSITIVE_GAIN"
    assert gate["governance"]["no_actual_joint_parameter"] is True
    assert "GENERALIZATION" in gate["governance"]["single_paper_status_after_pigment_adjustment"]

    man = MANUSCRIPT.read_text(encoding="utf-8")
    decision = DECISION.read_text(encoding="utf-8")
    for token in ("+0.51120", "+0.09533", "0.0002", "rank **12**"):
        assert token in man
    assert "0.0002" in decision and "does not exhaust" in decision.lower()
    assert "not an independent" in decision.lower() or "not independent" in decision.lower()
