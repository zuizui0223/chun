#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

EXPECTED_STATUS = "FROZEN_BEFORE_CHUN_IRIS_ROW_LEVEL_OUTCOME_INGESTION"
EXPECTED_RULE = "CHUN_INTERMEDIATE_RESOLUTION_RULE"
EXPECTED_RADIATION = "IRIS"
FORBIDDEN_OUTCOME_PATHS = [
    Path("data/iris_intermediate_resolution_traits_v0_1.csv"),
    Path("data/iris_intermediate_resolution_tree_v0_1.nwk"),
    Path("data/iris_intermediate_resolution_result_v0_1.json"),
    Path("results/iris_intermediate_resolution_v0_1"),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, required=True)
    a = ap.parse_args()

    x = json.loads(a.input.read_text(encoding="utf-8"))
    assert x["version"] == "v0.1"
    assert x["status"] == EXPECTED_STATUS
    assert x["rule_name"] == EXPECTED_RULE
    assert x["fourth_radiation"]["id"] == EXPECTED_RADIATION
    assert x["fourth_radiation"]["source_doi"] == "10.3389/fpls.2020.569811"
    assert x["exposure_log"]["prospective_label"] == "ANALYSIS_PROSPECTIVE_NOT_LITERATURE_BLINDED"

    coarse = x["nested_resolutions"]["coarse"]
    mid = x["nested_resolutions"]["intermediate"]
    fine = x["nested_resolutions"]["fine"]
    assert coarse["name"] == "PIGMENT_PRESENCE"
    assert mid["name"] == "MAJOR_PIGMENT_CLASS"
    assert fine["name"] == "VISIBLE_HUE"
    assert len(coarse["states"]) == 2
    assert len(mid["states"]) == 3
    assert len(fine["states"]) == 7

    stat = x["primary_statistic"]
    assert stat["name"] == "PAIRWISE_PHYLOGENETIC_SAME_STATE_AUC"
    assert stat["permutations"] == 9999
    assert stat["seed"] == 20260913
    assert "triplet jointly" in stat["permutation_unit"]

    decision = x["decision_rule"]
    assert "AUC_intermediate > 0.5" in decision["PASS"]
    assert "delta_intermediate_minus_coarse>0" in decision["PASS"]
    assert "delta_intermediate_minus_fine>0" in decision["PASS"]
    assert decision["NO_POST_HOC_UPGRADE"] == "Sensitivity analyses cannot upgrade MIXED/FAIL to PASS."

    assert x["primary_analysis_frame"]["outcome_independent_exclusions_only"] is True
    assert x["phylogeny_reconstruction"]["trait_blind"] is True
    assert x["phylogeny_reconstruction"]["trait_values_forbidden_during_tree_build"] is True
    assert x["paper1_science_changed"] is False

    present = [str(p) for p in FORBIDDEN_OUTCOME_PATHS if p.exists()]
    if present:
        raise SystemExit(f"Outcome files exist before preregistration freeze: {present}")

    print(json.dumps({
        "status": "PASS_PREREG_FROZEN_NO_CHUN_IRIS_OUTCOME_FILES",
        "rule": EXPECTED_RULE,
        "fourth_radiation": EXPECTED_RADIATION,
        "outcome_files_present": present,
        "paper1_science_changed": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
