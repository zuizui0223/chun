#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def load_csv(rel: str):
    with (ROOT / rel).open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    ledger = load_csv("data/cross_radiation_resolution_evidence_v0_1.csv")
    macro = load_json("data/cross_radiation_state_granularity_v0_3.json")
    ioch = load_json("data/iochrominae_cross_level_bridge_summary_v0_1.json")
    erica = load_json("data/erica_phenotype_axis_molecular_bridge_summary_v0_1.json")
    pet = load_json("data/petunieae_prospective_cross_level_v0_1.json")
    epi = load_json("data/epimedium_cross_level_endpoint_bridge_summary_v0_1.json")

    assert len(ledger) == 16, len(ledger)
    assert macro["fine_state_replication"]["testable_external_radiations"] == 3
    assert macro["fine_state_replication"]["supporting_external_radiations"] == 3
    assert macro["direction_result"]["testable_radiations"] == 3
    assert macro["direction_result"]["strong_direction_pass_count"] == 0
    assert macro["coarse_partition_specificity"]["enriched_radiations"] == []

    assert ioch["hue_maps_to"] == "BRANCHING_ENZYME_SUBSPACE"
    assert ioch["intensity_maps_to"] == "LATE_PATHWAY_COEXPRESSION_MODULE"

    ey = erica["phenotype_axes"]["HUE_BRANCH_YELLOW"]
    ew = erica["phenotype_axes"]["PIGMENT_DEPLETION_WHITE"]
    assert ey["branch_hydroxylation_F3_prime_H"] == "2/2"
    assert ew["unique_focal_node_classes"] == 4

    assert pet["pre_frozen_gate"] == "PETUNIEAE_PROSPECTIVE_BRIDGE_MIXED"
    assert pet["pre_frozen_gate_components"] == {
        "amount_axis_pass": False,
        "coverage_pass": True,
        "hue_axis_pass": True,
    }
    assert pet["hue_axis"]["best_subspace"] == "BRANCHING_HUE"
    assert pet["hue_axis"]["best_margin_AICc"] > 2
    assert pet["amount_axis"]["best_margin_AICc"] < 2
    assert pet["amount_axis"]["null_model"]["AICc"] < pet["amount_axis"]["models"][pet["amount_axis"]["best_subspace"]]["AICc"]
    assert pet["source_method_sensitivity_log_amount"]["fit"]["best_subspace"] == "LATE_OUTPUT"

    assert epi["cross_level_result"] == "SAME_SOURCE_ENDPOINT_CODE_WITH_RECURRENT_CORE_AND_HETEROGENEOUS_MOLECULAR_IMPLEMENTATION"

    fine = [r for r in ledger if r["endpoint"] == "fine_state_organization"]
    direction = [r for r in ledger if r["endpoint"] == "universal_direction"]
    coarse = [r for r in ledger if r["endpoint"] == "privileged_coarse_boundary"]
    hue = [r for r in ledger if r["endpoint"] == "phenotype_axis_localization" and r["phenotype_dimension"] == "hue"]
    amount = [r for r in ledger if r["endpoint"] == "phenotype_axis_localization" and r["phenotype_dimension"] == "pigment_amount_or_depletion"]

    assert len(fine) == len(direction) == len(coarse) == len(hue) == len(amount) == 3
    assert sum(r["evidence_status"] == "SUPPORT" for r in fine) == 3
    assert sum(r["evidence_status"] == "NO_STRONG_DIRECTION_SUPPORT" for r in direction) == 3
    assert sum(r["evidence_status"] == "ENRICHED" for r in coarse) == 0
    assert sum(r["evidence_status"] == "SUPPORT_BRANCHING" for r in hue) == 3
    assert sum(r["prospective_status"] == "PROSPECTIVE" for r in hue) == 1
    assert sum(r["evidence_status"] == "SUPPORT_FIXED_OUTPUT_SUBSPACE" for r in amount) == 1

    summary = {
        "version": "v0.1",
        "status": "CROSS_RADIATION_RESOLUTION_DEPENDENCE_SUPPORTED_WITH_ONE_PROSPECTIVE_HUE_COMPONENT",
        "systems_in_evidence_ledger": len(set(r["system"] for r in ledger)),
        "ledger_rows": len(ledger),
        "macro_level": {
            "fine_state_organization_support": "3/3 independent external radiations",
            "strong_universal_direction_support": "0/3 comparable radiations",
            "privileged_preselected_coarse_boundary_enriched": "0/3 radiations",
            "inference": "FINE_STATE_ORGANIZATION_REPEATS_WHILE_SHARED_COARSE_BOUNDARY_AND_DIRECTION_DO_NOT",
        },
        "molecular_level": {
            "matched_axis_systems": ["IOCHROMINAE", "CAPE_ERICA", "PETUNIEAE"],
            "hue_branching_localization_support": "3/3 systems",
            "hue_prospective_component_support": "1/1 prospectively tested system (Petunieae)",
            "amount_or_depletion_fixed_output_localization": "1/3 systems",
            "amount_or_depletion_heterogeneous_or_primary_fail": "2/3 systems",
            "petunieae_hue_margin_AICc": pet["hue_axis"]["best_margin_AICc"],
            "petunieae_amount_margin_AICc": pet["amount_axis"]["best_margin_AICc"],
            "petunieae_primary_classification": pet["pre_frozen_gate"],
            "inference": "HUE_HYDROXYLATION_LOCALIZATION_IS_MORE_CROSS_SYSTEM_STABLE_THAN_PIGMENT_AMOUNT_OR_DEPLETION_LOCALIZATION",
        },
        "complementary_endpoint_evidence": {
            "system": "EPIMEDIUM_SECT_DIPHYLLON",
            "result": epi["cross_level_result"],
            "role": "SUPPORTS_HIERARCHICAL_IMPLEMENTATION_HETEROGENEITY_BUT_USES_A_DIFFERENT_BRIDGE_DEFINITION",
        },
        "integrated_candidate": "FLOWER_COLOUR_REPEATABILITY_IS_CONCENTRATED_IN_RESOLVED_PHENOTYPE_AND_MOLECULAR_DIMENSIONS_RATHER_THAN_ONE_SHARED_COARSE_STATE_DIRECTION_OR_COMPLETE_PROGRAMME",
        "prospective_status": "PARTIALLY_PROSPECTIVE_NOT_FULLY_PROSPECTIVELY_REPLICATED",
        "pooled_numeric_estimator": "FORBIDDEN_ACROSS_HETEROGENEOUS_MACRO_AND_MOLECULAR_UNITS",
        "claim_boundary": "This synthesis combines replicated macro representation results with matched within-radiation molecular-axis results. It does not claim event-for-event micro-to-macro matching, universal causal genes, a universal colour direction, or a fully prospectively replicated law.",
        "paper1_science_changed": False,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
