#!/usr/bin/env python3
"""Validate the frozen Nicotiana HOLD result without opening the biological endpoint."""
from __future__ import annotations

import json
import math
from pathlib import Path

RESULT = Path("analysis/nicotiana_fine_state_falsification_result_v1.json")
GENERATED_TRAIT = Path("analysis/_generated/nicotiana_source_v1/trait_audit.json")
GENERATED_TREE = Path("analysis/_generated/nicotiana_opentree_v1/summary.json")


def main():
    r = json.loads(RESULT.read_text(encoding="utf-8"))
    assert r["classification"] == "HOLD_OBSERVATION_REGIME"
    assert r["endpoint_computed"] is False
    assert r["paper1_science_changed"] is False

    trait = r["trait_admission"]
    assert trait["eligible_taxon_units"] == 21
    assert all(trait["pre_tree_gates"].values())
    assert trait["definite_coarse_taxon_counts"] == {
        "CHLOROPHYLL_ABSENT": 5,
        "CHLOROPHYLL_PRESENT": 16,
    }

    tree = r["tree_admission"]
    assert tree["eligible_trait_taxa"] == 21
    assert tree["n_admitted_unique_ott"] == 17
    assert tree["n_tree_overlap"] == 17
    assert tree["coverage_fraction_of_eligible"] >= 0.80
    assert tree["frozen_coverage_gate_80pct"] is True
    assert tree["frozen_minimum_n_20_gate"] is False
    assert tree["endpoint_allowed"] is False
    assert tree["n_ott_collision_groups"] == 0
    assert tree["tnrs_status_counts"] == {
        "EXACT": 17,
        "REJECT_2_EXACT_MATCHES": 2,
        "REJECT_0_EXACT_MATCHES": 2,
    }

    rejected = {x["query"]: x for x in tree["rejected_queries"]}
    assert set(rejected) == {
        "Nicotiana attenuata",
        "Nicotiana obtusifolia var. obtusifolia",
        "Nicotiana obtusifolia var. palmeri",
        "Nicotiana undulata",
    }
    assert len({x["ott_id"] for x in rejected["Nicotiana attenuata"]["candidate_exact_matches"]}) == 2
    assert len({x["ott_id"] for x in rejected["Nicotiana undulata"]["candidate_exact_matches"]}) == 2
    assert rejected["Nicotiana obtusifolia var. obtusifolia"]["candidate_exact_matches"] == []
    assert rejected["Nicotiana obtusifolia var. palmeri"]["candidate_exact_matches"] == []

    if GENERATED_TRAIT.exists():
        g = json.loads(GENERATED_TRAIT.read_text(encoding="utf-8"))["summary"]
        assert g["eligible_taxon_units"] == trait["eligible_taxon_units"]
        assert g["definite_coarse_taxon_counts"] == trait["definite_coarse_taxon_counts"]
        assert all(g["pre_tree_admission_checks"].values())

    if GENERATED_TREE.exists():
        g = json.loads(GENERATED_TREE.read_text(encoding="utf-8"))
        assert g["eligible_trait_taxa"] == tree["eligible_trait_taxa"]
        assert g["tnrs_status_counts"] == tree["tnrs_status_counts"]
        assert g["n_admitted_unique_ott"] == tree["n_admitted_unique_ott"]
        assert g["n_tree_overlap"] == tree["n_tree_overlap"]
        assert math.isclose(g["coverage_fraction_of_eligible"], tree["coverage_fraction_of_eligible"], rel_tol=0, abs_tol=1e-15)
        assert g["frozen_coverage_gate_80pct"] is True
        assert g["frozen_minimum_n_20_gate"] is False
        assert g["endpoint_allowed"] is False
        generated_rejected = {x["query"]: x for x in g.get("rejected_queries", [])}
        if generated_rejected:
            assert generated_rejected == rejected

    # The endpoint implementation may exist, but no generated biological result
    # is admissible while endpoint_allowed=false.
    generated_endpoint = Path("analysis/_generated/nicotiana_falsification_v1/result.json")
    assert not generated_endpoint.exists(), "Nicotiana biological endpoint was opened despite frozen HOLD gate"

    print("validated Nicotiana fifth-radiation HOLD_OBSERVATION_REGIME: 17/21 exact tree tips, endpoint unopened")


if __name__ == "__main__":
    main()
