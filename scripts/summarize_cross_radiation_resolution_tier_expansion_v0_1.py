#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def rows(path: Path):
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", type=Path, default=ROOT / "data/cross_radiation_resolution_tier_expansion_v0_1.csv")
    ap.add_argument("--benchmark", type=Path, default=ROOT / "data/cross_clade_mechanistic_recurrence_benchmark_v0_1.csv")
    ap.add_argument("--petunieae", type=Path, default=ROOT / "data/petunieae_prospective_cross_level_v0_1.json")
    ap.add_argument("--iochrominae", type=Path, default=ROOT / "data/iochrominae_cross_level_bridge_summary_v0_1.json")
    ap.add_argument("--erica", type=Path, default=ROOT / "data/erica_phenotype_axis_molecular_bridge_summary_v0_1.json")
    ap.add_argument("--erica-mechanisms", type=Path, default=ROOT / "data/erica_white_yellow_mechanisms_v0_1.csv")
    ap.add_argument("--epimedium", type=Path, default=ROOT / "data/epimedium_cross_level_endpoint_bridge_summary_v0_1.json")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    ledger = rows(a.ledger)
    benchmark = {r["benchmark_id"]: r for r in rows(a.benchmark)}
    pet = load_json(a.petunieae)
    ioch = load_json(a.iochrominae)
    erica = load_json(a.erica)
    erica_mech = rows(a.erica_mechanisms)
    epi = load_json(a.epimedium)

    # Ledger structure is frozen before summary calculation.
    assert len(ledger) == 10, len(ledger)
    assert {r["tier"] for r in ledger} == {"M1", "M2", "M3", "M4"}

    m1 = [r for r in ledger if r["tier"] == "M1"]
    paired_systems = {"IOCHROMINAE", "CAPE_ERICA", "PETUNIEAE"}
    assert len(m1) == 6
    assert {r["system"] for r in m1} == paired_systems
    for system in paired_systems:
        sr = [r for r in m1 if r["system"] == system]
        assert len(sr) == 2
        assert {r["phenotype_dimension"] for r in sr} == {
            "HUE_OR_HYDROXYLATION",
            "PIGMENT_AMOUNT_OR_DEPLETION",
        }

    hue_m1 = [r for r in m1 if r["phenotype_dimension"] == "HUE_OR_HYDROXYLATION"]
    amount_m1 = [r for r in m1 if r["phenotype_dimension"] == "PIGMENT_AMOUNT_OR_DEPLETION"]
    assert len(hue_m1) == len(amount_m1) == 3
    assert sum(r["specificity_class"] == "BRANCH_SPECIFIC_OR_FINER" for r in hue_m1) == 3
    assert sum(r["specificity_class"] == "BRANCH_SPECIFIC_OR_FINER" for r in amount_m1) == 0
    assert sum(r["specificity_class"] == "MODULE_OR_CORE" for r in amount_m1) == 1
    assert sum(r["specificity_class"] == "DIVERSE_OR_PRIMARY_FAIL" for r in amount_m1) == 2

    # Rebuild the paired M1 claims from their frozen source receipts rather than trusting the ledger text.
    assert ioch["same_radiation"] == "IOCHROMINAE"
    assert ioch["source_species_scope"] == 28
    assert ioch["hue_maps_to"] == "BRANCHING_ENZYME_SUBSPACE"
    assert ioch["intensity_maps_to"] == "LATE_PATHWAY_COEXPRESSION_MODULE"

    assert erica["same_radiation"] == "CAPE_ERICA"
    ey = erica["phenotype_axes"]["HUE_BRANCH_YELLOW"]
    ew = erica["phenotype_axes"]["PIGMENT_DEPLETION_WHITE"]
    assert ey["taxa"] == 2
    assert ey["branch_hydroxylation_F3_prime_H"] == "2/2"
    assert ew["taxa"] == 6
    assert ew["unique_focal_node_classes"] == 4
    assert ew["branch_hydroxylation_F3_prime_H"] == "0/6"
    yellow_mech = [r for r in erica_mech if r["target_state"] == "YELLOW"]
    white_mech = [r for r in erica_mech if r["target_state"] == "WHITE"]
    assert len(yellow_mech) == 2 and {r["focal_node"] for r in yellow_mech} == {"F3_PRIME_H"}
    assert len(white_mech) == 6 and len({r["focal_node"] for r in white_mech}) == 4

    assert pet["pre_frozen_gate"] == "PETUNIEAE_PROSPECTIVE_BRIDGE_MIXED"
    assert pet["pre_frozen_gate_components"]["hue_axis_pass"] is True
    assert pet["pre_frozen_gate_components"]["amount_axis_pass"] is False
    assert pet["hue_axis"]["best_subspace"] == "BRANCHING_HUE"
    assert abs(pet["hue_axis"]["best_margin_AICc"] - 11.60282936) < 1e-8
    assert abs(pet["amount_axis"]["best_margin_AICc"] - 0.44436806) < 1e-8
    amount_best = pet["amount_axis"]["best_subspace"]
    assert pet["amount_axis"]["null_model"]["AICc"] < pet["amount_axis"]["models"][amount_best]["AICc"]
    assert pet["source_method_sensitivity_log_amount"]["fit"]["best_subspace"] == "LATE_OUTPUT"

    # External tiers are qualitative stress tests because observation regimes and denominators differ.
    m2 = [r for r in ledger if r["tier"] == "M2"]
    m3 = [r for r in ledger if r["tier"] == "M3"]
    m4 = [r for r in ledger if r["tier"] == "M4"]
    assert len(m2) == 1 and m2[0]["system"] == "IPOMOEA"
    assert m2[0]["specificity_class"] == "BRANCH_SPECIFIC_OR_FINER"
    assert benchmark["IPOMOEA_RED"]["shared_count"] == "3/3"
    assert benchmark["IPOMOEA_RED"]["strongest_recurrence_level"] == "EXACT_GENE_REGULATORY"

    assert {r["system"] for r in m3} == {"AQUILEGIA", "EPIMEDIUM"}
    assert all(r["specificity_class"] == "MODULE_OR_CORE" for r in m3)
    assert benchmark["AQUILEGIA_A_MINUS"]["strongest_recurrence_level"] == "LATE_PATHWAY_EXPRESSION"
    assert benchmark["EPIMEDIUM_A_MINUS"]["shared_count"] == "4/4"
    assert benchmark["EPIMEDIUM_A_MINUS"]["strongest_recurrence_level"] == "CORE_MODULE"
    assert epi["cross_level_result"] == "SAME_SOURCE_ENDPOINT_CODE_WITH_RECURRENT_CORE_AND_HETEROGENEOUS_MOLECULAR_IMPLEMENTATION"
    assert epi["historical_event_independence"] == "FAIL_HOLD_NOT_ESTIMATED"

    assert len(m4) == 1 and m4[0]["system"] == "PETUNIA"
    assert benchmark["PETUNIA_REGAIN"]["shared_count"] == "2/2"
    assert benchmark["PETUNIA_REGAIN"]["complete_program_recurrence"] == "0/2"

    # Expanded descriptive comparison. This is deliberately not an inferential meta-analysis.
    hue_all = hue_m1 + m2
    amount_all = amount_m1 + m3
    hue_classes = Counter(r["specificity_class"] for r in hue_all)
    amount_classes = Counter(r["specificity_class"] for r in amount_all)
    assert len(hue_all) == 4
    assert hue_classes == Counter({"BRANCH_SPECIFIC_OR_FINER": 4})
    assert len(amount_all) == 5
    assert amount_classes == Counter({"MODULE_OR_CORE": 3, "DIVERSE_OR_PRIMARY_FAIL": 2})

    summary = {
        "version": "v0.1",
        "status": "PAIRED_SPECIFICITY_ASYMMETRY_SURVIVES_EXTERNAL_TIER_STRESS",
        "primary_paired_M1": {
            "systems": ["IOCHROMINAE", "CAPE_ERICA", "PETUNIEAE"],
            "hue_branch_specific_or_finer": "3/3",
            "amount_or_depletion_branch_specific_or_finer": "0/3",
            "amount_or_depletion_module_or_core": "1/3",
            "amount_or_depletion_diverse_or_primary_fail": "2/3",
            "prospective_component": "PETUNIEAE_HUE_PASS_AMOUNT_FAIL",
            "petunieae_hue_margin_AICc": pet["hue_axis"]["best_margin_AICc"],
            "petunieae_amount_margin_AICc": pet["amount_axis"]["best_margin_AICc"],
        },
        "expanded_descriptive_stress": {
            "hue_or_hydroxylation_systems": ["IOCHROMINAE", "CAPE_ERICA", "PETUNIEAE", "IPOMOEA"],
            "hue_branch_specific_or_finer": "4/4",
            "hue_specificity_classes": dict(sorted(hue_classes.items())),
            "amount_or_depletion_systems": ["IOCHROMINAE", "CAPE_ERICA", "PETUNIEAE", "AQUILEGIA", "EPIMEDIUM"],
            "amount_or_depletion_branch_specific_or_finer": "0/5",
            "amount_or_depletion_module_or_core": "3/5",
            "amount_or_depletion_diverse_or_primary_fail": "2/5",
            "amount_or_depletion_specificity_classes": dict(sorted(amount_classes.items())),
            "interpretation": "DESCRIPTIVE_SPECIFICITY_CONTRAST_ONLY_HETEROGENEOUS_OBSERVATION_REGIMES",
        },
        "external_stress": {
            "M2_hue_branching": {
                "system": "IPOMOEA",
                "result": "EXACT_GENE_REGULATORY_F3_PRIME_H_IN_3_OF_3_ROBUST_RED_ORIGINS",
                "alignment": "SUPPORTS_FINE_BRANCH_SPECIFIC_LOCALIZATION_OUTSIDE_M1",
            },
            "M3_depletion_or_loss": {
                "systems": ["AQUILEGIA", "EPIMEDIUM"],
                "results": [
                    "AQUILEGIA_LATE_PATHWAY_EXPRESSION_RECURRENCE_WITHOUT_UNIVERSAL_EXACT_REGULATOR",
                    "EPIMEDIUM_ANS_CORE_4_OF_4_WITH_BROADER_IMPLEMENTATION_HETEROGENEITY",
                ],
                "alignment": "SUPPORTS_RECURRENCE_AT_COARSER_MODULE_OR_CORE_LEVEL_OUTSIDE_M1",
            },
            "M4_regain": {
                "system": "PETUNIA",
                "result": "R2R3_MYB_REGULATOR_CLASS_2_OF_2_WITH_COMPLETE_IMPLEMENTATION_0_OF_2",
                "alignment": "SUPPORTS_HIERARCHICAL_REPEATABILITY_NOT_AXIS_SPECIFICITY",
            },
        },
        "revised_inference": "BOTH_HUE_AND_PIGMENT_LOSS_CAN_REPEAT_BUT_THEIR_MOST_STABLE_REPEATABILITY_OCCURS_AT_DIFFERENT_MECHANISTIC_RESOLUTIONS",
        "specificity_candidate": "HUE_OR_HYDROXYLATION_CAN_RECUR_AT_BRANCHING_ENZYME_OR_EXACT_REGULATORY_LEVEL_WHEREAS_PIGMENT_DEPLETION_OR_LOSS_MORE_OFTEN_RECURS_AT_LATE_PATHWAY_OR_CORE_MODULE_LEVEL_WITH_HETEROGENEOUS_IMPLEMENTATION",
        "superseded_binary_wording": "HUE_STABLE_WHILE_DEPLETION_UNSTABLE",
        "prospective_status": "ONE_PAIRED_PROSPECTIVE_SYSTEM_ONLY",
        "numeric_pooling": "FORBIDDEN_ACROSS_TIERS_AND_OBSERVATION_REGIMES",
        "independence_boundary": "M1_PAIRED_SYSTEMS_ARE_PRIMARY; M2_M3_ARE_EXTERNAL_QUALITATIVE_STRESS_TESTS_AND_SYSTEM_REUSE_IS_NOT_COUNTED_AS_ADDITIONAL_INDEPENDENT_REPLICATION",
        "claim_boundary": "The 4/4 versus 0/5 expanded counts are descriptive stress-test summaries across heterogeneous observation regimes, not a significance test or pooled effect size. The result is a resolution-specificity pattern, not a universal gene rule and not proof that depletion transitions cannot recur at fine resolution.",
        "paper1_science_changed": False,
    }

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
