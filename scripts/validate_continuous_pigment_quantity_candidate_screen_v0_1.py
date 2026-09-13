#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def false_token(x: str) -> bool:
    return x.strip().lower() in {"false", "0", "no"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate", type=Path, required=True)
    ap.add_argument("--screen", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    gate = json.loads(a.gate.read_text(encoding="utf-8"))
    screen = rows(a.screen)

    # The prediction and admission rule were frozen on main before this screen.
    assert gate["version"] == "v0.1"
    assert gate["status"] == "FROZEN_BEFORE_FOURTH_RADIATION_CANDIDATE_OUTCOME_INSPECTION"
    assert gate["primary_prediction"]["phenotype_dimension"] == "PIGMENT_QUANTITY_CONTINUOUS"
    assert gate["primary_prediction"]["predicted_target_family"] == "OUTPUT_CONTROL"
    assert gate["candidate_admission"]["minimum_matched_taxa"] == 20
    assert gate["candidate_search"]["maximum_source_publications_screened"] == 20
    assert gate["candidate_admission"]["decisive_target_class_outcome_must_not_be_inspected_before_admission"] is True

    assert len(screen) == 18, len(screen)
    assert [int(r["screen_order"]) for r in screen] == list(range(1, 19))
    unique_publications = {r["source_doi"] for r in screen}
    assert len(unique_publications) == 17, len(unique_publications)
    assert len(unique_publications) <= gate["candidate_search"]["maximum_source_publications_screened"]

    # This screen is methods/metadata only. No decisive project-side target outcome is allowed in.
    assert all(false_token(r["decisive_target_outcome_inspected"]) for r in screen)
    assert all(r["admission_status"] == "UNQUALIFIED" for r in screen)
    assert not any(r["admission_status"] == "PASS" for r in screen)

    # The first 11 rows are an exhaustive pass over the unused clades already present in the
    # pre-existing v0.5 atlas. Their previous molecular-layer metadata are sufficient to fail
    # admission without opening quantity-association outcomes.
    atlas_rows = screen[:11]
    assert {r["radiation"] for r in atlas_rows} == {
        "ANTIRRHINEAE",
        "HYDRANGEA_CORNIDIA",
        "LINOIDEAE",
        "POLYGONATUM_VERTICILLATA",
        "ANGRAECINAE",
        "SILENE_PHYSOLYCHNIS",
        "EUONYMUS",
        "NICOTIANA",
        "LINANTHUS",
        "ACER",
        "DALECHAMPIA",
    }
    assert all(r["exclusion_reason"].startswith("PREEXISTING_ATLAS_") for r in atlas_rows)

    # Seven externally surfaced plausible sources were then checked under the same frozen gate.
    external_rows = screen[11:]
    assert {r["radiation"] for r in external_rows} == {
        "RHODODENDRON_30_SPECIES",
        "RHODODENDRON_4_SPECIES",
        "RUELLIA_10_SPECIES",
        "ACHIMENES_10_SPECIES",
        "CHILOGLOTTIS_5_SPECIES",
        "DENDROBIUM_HYBRID",
        "PAEONIA_LACTIFLORA_3_CULTIVARS",
    }

    # Rhododendron is the only screened external source with enough phenotype taxa and direct
    # continuous quantity, but its 30-species chemistry study lacks a same-taxon molecular matrix.
    rh30 = next(r for r in screen if r["radiation"] == "RHODODENDRON_30_SPECIES")
    assert int(rh30["matched_taxa"]) == 30
    assert rh30["continuous_quantity_available"] == "true"
    assert rh30["molecular_matrix_available"] == "false"
    assert rh30["admission_status"] == "UNQUALIFIED"

    # Every other external source fails before any target-class model could be computed.
    for r in external_rows:
        if r["radiation"] == "RHODODENDRON_30_SPECIES":
            continue
        n = int(r["matched_taxa"])
        assert n < gate["candidate_admission"]["minimum_matched_taxa"], (r["radiation"], n)

    reasons = Counter(r["exclusion_reason"] for r in screen)
    summary = {
        "version": "v0.1",
        "status": "NO_QUALIFIED_UNUSED_RADIATION_AFTER_BOUNDED_SCREEN",
        "frozen_gate_version": gate["version"],
        "candidate_frames_screened": len(screen),
        "unique_source_publications_screened": len(unique_publications),
        "maximum_source_publications_allowed": gate["candidate_search"]["maximum_source_publications_screened"],
        "preexisting_atlas_unused_clades_screened": len(atlas_rows),
        "external_plausible_sources_screened": len(external_rows),
        "qualified_candidates": 0,
        "decisive_target_outcomes_inspected": 0,
        "closest_candidate": {
            "radiation": "RHODODENDRON_30_SPECIES",
            "source_doi": "10.1111/plb.12649",
            "phenotype_taxa": 30,
            "continuous_quantity": True,
            "blocking_requirement": "NO_SAME_TAXON_MOLECULAR_MATRIX",
        },
        "search_scope": "EXHAUSTIVE_WITHIN_PREEXISTING_UNUSED_ATLAS_CLADES_PLUS_BOUNDED_EXTERNAL_PLAUSIBILITY_SCREEN_NOT_A_GLOBAL_SYSTEMATIC_REVIEW",
        "decision": "NO_QUALIFIED_UNUSED_RADIATION",
        "stop_rule": "DO_NOT_RELAX_THRESHOLDS_OR_CONTINUE_CANDIDATE_HUNTING; REOPEN_ONLY_FOR_A_NEWLY_RELEASED_OR_PREVIOUSLY_UNAVAILABLE_SOURCE_THAT_SATISFIES_ALL_FROZEN_ADMISSION_FIELDS_BEFORE_PROJECT_SIDE_TARGET_CLASS_OUTCOME_INSPECTION",
        "exclusion_reason_counts": dict(sorted(reasons.items())),
        "paper1_science_changed": False,
    }

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
