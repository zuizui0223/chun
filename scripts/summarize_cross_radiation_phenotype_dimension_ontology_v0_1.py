#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ontology", type=Path, default=ROOT / "data/cross_radiation_phenotype_dimension_ontology_v0_1.csv")
    ap.add_argument("--external", type=Path, default=ROOT / "data/cross_radiation_external_source_admission_v0_1.csv")
    ap.add_argument("--benchmark", type=Path, default=ROOT / "data/cross_clade_mechanistic_recurrence_benchmark_v0_1.csv")
    ap.add_argument("--tier-summary", type=Path, default=ROOT / "data/cross_radiation_resolution_tier_expansion_summary_v0_1.json")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    ontology = read_csv(a.ontology)
    external = {r["source_id"]: r for r in read_csv(a.external)}
    benchmark = {r["benchmark_id"]: r for r in read_csv(a.benchmark)}
    old = json.loads(a.tier_summary.read_text(encoding="utf-8"))

    expected_dimensions = {
        "HUE_COMPOSITION",
        "PIGMENT_QUANTITY_CONTINUOUS",
        "PIGMENT_LOSS",
        "PIGMENT_GAIN",
        "REGAIN_FROM_COLORLESS",
    }
    assert len(ontology) == 14, len(ontology)
    assert {r["dimension"] for r in ontology} == expected_dimensions

    by_dim = {d: [r for r in ontology if r["dimension"] == d] for d in expected_dimensions}
    assert len(by_dim["HUE_COMPOSITION"]) == 5
    assert len(by_dim["PIGMENT_QUANTITY_CONTINUOUS"]) == 2
    assert len(by_dim["PIGMENT_LOSS"]) == 4
    assert len(by_dim["PIGMENT_GAIN"]) == 2
    assert len(by_dim["REGAIN_FROM_COLORLESS"]) == 1

    hue = by_dim["HUE_COMPOSITION"]
    assert all(r["recurrent_target_architecture"].startswith("BRANCH_CONTROL") for r in hue)
    assert all(r["evidence_status"] == "SUPPORT" for r in hue)
    assert {r["system"] for r in hue} == {"IOCHROMINAE", "CAPE_ERICA", "PETUNIEAE", "IPOMOEA", "PENSTEMON"}
    assert sum(r["prospective_status"] == "PROSPECTIVE_COMPONENT" for r in hue) == 1

    quantity = by_dim["PIGMENT_QUANTITY_CONTINUOUS"]
    assert {r["system"] for r in quantity} == {"IOCHROMINAE", "PETUNIEAE"}
    assert Counter(r["evidence_status"] for r in quantity) == Counter({"SUPPORT": 1, "PRIMARY_GATE_FAIL": 1})

    loss = by_dim["PIGMENT_LOSS"]
    assert {r["system"] for r in loss} == {"CAPE_ERICA", "AQUILEGIA", "EPIMEDIUM", "PETUNIA_AXILLARIS"}
    assert len({r["recurrent_target_architecture"] for r in loss}) == 4
    assert any(r["recurrent_target_architecture"] == "R2R3_MYB_AN2" for r in loss)

    gain = by_dim["PIGMENT_GAIN"]
    assert {r["system"] for r in gain} == {"CAMELLIA_ANTH_GAIN", "MIMULUS_LUTEUS_GROUP"}
    regain = by_dim["REGAIN_FROM_COLORLESS"]
    assert regain[0]["system"] == "PETUNIA_LONG_TUBE"

    # External source admissions that specifically falsify a monotonic fine-vs-coarse ordering.
    assert set(external) == {
        "PENSTEMON_F35H_2015",
        "PETUNIA_AN2_2007",
        "MIMULUS_MYB_2011",
        "WESSINGER_RAUSHER_2012",
        "ANTIRRHINUM_MYB_2006",
    }
    assert external["PENSTEMON_F35H_2015"]["source_doi"] == "10.1093/molbev/msu298"
    assert "12/13" in external["PENSTEMON_F35H_2015"]["verified_claim"]
    assert external["PETUNIA_AN2_2007"]["source_doi"] == "10.1105/tpc.106.048694"
    assert "five times independently" in external["PETUNIA_AN2_2007"]["verified_claim"]
    assert external["WESSINGER_RAUSHER_2012"]["admission_role"] == "FALSIFICATION_PRIOR_ART_CONTROL"
    assert external["ANTIRRHINUM_MYB_2006"]["dimension"] == "PIGMENT_QUANTITY_OR_PATTERN"

    # Cross-check inherited benchmark claims where a frozen project row exists.
    assert benchmark["IPOMOEA_RED"]["shared_count"] == "3/3"
    assert benchmark["AQUILEGIA_A_MINUS"]["strongest_recurrence_level"] == "LATE_PATHWAY_EXPRESSION"
    assert benchmark["EPIMEDIUM_A_MINUS"]["shared_count"] == "4/4"
    assert benchmark["PETUNIA_REGAIN"]["complete_program_recurrence"] == "0/2"
    assert benchmark["CAMELLIA_ANTH_GAIN"]["shared_count"] == "1/3"

    assert old["expanded_descriptive_stress"]["hue_branch_specific_or_finer"] == "4/4"
    assert old["expanded_descriptive_stress"]["amount_or_depletion_branch_specific_or_finer"] == "0/5"

    target_architectures = {
        d: sorted({r["recurrent_target_architecture"] for r in rs})
        for d, rs in by_dim.items()
    }

    summary = {
        "version": "v0.1",
        "status": "SPECIFICITY_ASYMMETRY_FALSIFIED_PHENOTYPE_DIMENSION_TARGET_ARCHITECTURE_RETAINED",
        "superseded_claim": "HUE_OR_HYDROXYLATION_IS_INTRINSICALLY_FINE_GRAINED_WHILE_PIGMENT_AMOUNT_OR_LOSS_IS_INTRINSICALLY_COARSE_GRAINED",
        "falsification": {
            "reason_1": "THE_OLD_AMOUNT_OR_DEPLETION_CATEGORY_CONFLATED_CONTINUOUS_PIGMENT_QUANTITY_WITH_DISCRETE_PIGMENT_LOSS",
            "reason_2": "FIXED_PIGMENT_LOSS_CAN_REPEAT_AT_SPECIFIC_R2R3_MYB_REGULATORS_OR_REGULATOR_CLASSES",
            "direct_counterexample": "PETUNIA_AXILLARIS_AN2_LOF_AT_LEAST_FIVE_INDEPENDENT_ALLELES",
            "prior_art_boundary": "WESSINGER_RAUSHER_2012_ALREADY_SYNTHESIZED_TRANSITION_TYPE_DEPENDENCE_AND_R2R3_MYB_BIAS_FOR_FIXED_PIGMENT_LOSS",
        },
        "dimension_summary": {
            "HUE_COMPOSITION": {
                "systems": 5,
                "branch_control_support": "5/5",
                "systems_list": ["IOCHROMINAE", "CAPE_ERICA", "PETUNIEAE", "IPOMOEA", "PENSTEMON"],
                "prospective_components": "1/5 (Petunieae)",
                "target_architectures": target_architectures["HUE_COMPOSITION"],
                "interpretation": "STRONG_CURRENT_CROSS_SYSTEM_TARGET_CLASS_CONCENTRATION_ON_ANTHOCYANIN_BRANCH_CONTROL",
            },
            "PIGMENT_QUANTITY_CONTINUOUS": {
                "systems": 2,
                "support_vs_primary_fail": "1/2 vs 1/2",
                "target_architectures": target_architectures["PIGMENT_QUANTITY_CONTINUOUS"],
                "interpretation": "UNDERDETERMINED_HIGHEST_INFORMATION_GAP",
            },
            "PIGMENT_LOSS": {
                "systems": 4,
                "target_architectures": target_architectures["PIGMENT_LOSS"],
                "interpretation": "TARGET_CLASS_REPEATABILITY_EXISTS_BUT_CURRENT_ADMITTED_SYSTEMS_DO_NOT_SHARE_ONE_EXACT_ARCHITECTURE",
                "prior_art_control": "R2R3_MYB_BIAS_FOR_FIXED_LOSSES_ALREADY_ESTABLISHED",
            },
            "PIGMENT_GAIN": {
                "systems": 2,
                "target_architectures": target_architectures["PIGMENT_GAIN"],
                "interpretation": "REGULATOR_OR_MODULE_REUSE_WITHOUT_COMPLETE_PROGRAMME_IDENTITY",
            },
            "REGAIN_FROM_COLORLESS": {
                "systems": 1,
                "target_architectures": target_architectures["REGAIN_FROM_COLORLESS"],
                "interpretation": "REGULATOR_CLASS_REUSE_WITH_IMPLEMENTATION_HETEROGENEITY",
            },
        },
        "retained_cross_radiation_rule": "PHENOTYPE_DIMENSION_OR_TRANSITION_CLASS_PREDICTS_WHICH_MOLECULAR_TARGET_ARCHITECTURE_IS_REUSED_BETTER_THAN_A_GLOBAL_FINE_VERSUS_COARSE_REPEATABILITY_ORDERING",
        "novelty_boundary": "TRANSITION_TYPE_DEPENDENCE_ITSELF_IS_PRIOR_ART; THE_PROGRAMME_LEVEL_CANDIDATE_IS ITS_EXPLICIT_ALIGNMENT_WITH_CROSS_RADIATION_MACRO_STATE_REPRESENTATION_AND_PROSPECTIVE_TESTING_UNDER_FROZEN_DIMENSION_DEFINITIONS",
        "next_gate": "FREEZE_A_CONTINUOUS_PIGMENT_QUANTITY_TARGET_CLASS_RULE_BEFORE_INSPECTING_OUTCOMES_IN_AN_UNUSED_INDEPENDENT_RADIATION; DO_NOT_SPEND_THE_NEXT_PROSPECTIVE_TEST_ON_ANOTHER_HUE_SYSTEM",
        "numeric_pooling": "FORBIDDEN_ACROSS_HETEROGENEOUS_EVIDENCE_UNITS",
        "claim_boundary": "The five hue systems are heterogeneous evidence types and their 5/5 target-class concentration is descriptive. Pigment-loss systems cannot be described as generally coarse or unpredictable. No first claim, pooled effect size, or universal target gene is authorized.",
        "paper1_science_changed": False,
    }

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
