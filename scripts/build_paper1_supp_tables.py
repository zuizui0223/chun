#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str] | None = None) -> None:
    if not rows:
        raise SystemExit(f"refusing to write empty supplementary table: {path.name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    if fields is None:
        fields = list(rows[0])
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n", extrasaction="ignore")
        writer.writeheader(); writer.writerows(rows)


def build_ecological_v2_rows(
    studies: list[dict[str, str]], effects: list[dict[str, str]]
) -> tuple[list[dict[str, str]], list[str]]:
    source_to_study: dict[str, dict[str, str]] = {}
    for study in studies:
        source = study["source"].strip()
        if not source or source in source_to_study:
            raise SystemExit(f"ecological v2 study registry has missing/duplicate source: {source}")
        source_to_study[source] = study

    effects_by_source: dict[str, list[dict[str, str]]] = {source: [] for source in source_to_study}
    for effect in effects:
        source = effect["source"].strip()
        if source not in source_to_study:
            raise SystemExit(f"ecological effect {effect['effect_id']} has no study-registry source match")
        effects_by_source[source].append(effect)

    fields = [
        "record_type", "study_id", "year", "taxon", "ecological_axis", "design",
        "quantitative_status", "primary_outcome", "admission_status", "source",
        "study_role", "claim_ceiling", "effect_id", "effect_taxon", "visible_state",
        "contrast", "outcome", "effect_metric", "numerator_value", "denominator_value",
        "effect_value", "se_value", "variance_status", "events_num", "n_num",
        "events_den", "n_den", "independence_unit", "effect_notes",
    ]
    rows: list[dict[str, str]] = []
    for study in studies:
        linked_effects = effects_by_source[study["source"].strip()]
        records = linked_effects or [None]
        for effect in records:
            row = {
                "record_type": "effect" if effect else "context_only_study",
                "study_id": study["study_id"],
                "year": study["year"],
                "taxon": study["taxon"],
                "ecological_axis": study["ecological_axis"],
                "design": study["design"],
                "quantitative_status": study["quantitative_status"],
                "primary_outcome": study["primary_outcome"],
                "admission_status": study["admission_status"],
                "source": study["source"],
                "study_role": study["role"],
                "claim_ceiling": study["claim_ceiling"],
            }
            if effect:
                row.update({
                    "effect_id": effect["effect_id"],
                    "effect_taxon": effect["taxon"],
                    "visible_state": effect["visible_state"],
                    "contrast": effect["contrast"],
                    "outcome": effect["outcome"],
                    "effect_metric": effect["effect_metric"],
                    "numerator_value": effect["numerator_value"],
                    "denominator_value": effect["denominator_value"],
                    "effect_value": effect["effect_value"],
                    "se_value": effect["se_value"],
                    "variance_status": effect["variance_status"],
                    "events_num": effect["events_num"],
                    "n_num": effect["n_num"],
                    "events_den": effect["events_den"],
                    "n_den": effect["n_den"],
                    "independence_unit": effect["independence_unit"],
                    "effect_notes": effect["notes"],
                })
            rows.append(row)
    if {row.get("effect_id", "") for row in rows} - {""} != {e["effect_id"] for e in effects}:
        raise SystemExit("ecological v2 supplementary table lost one or more effect IDs")
    return rows, fields


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--disposition", type=Path, required=True)
    ap.add_argument("--micro", type=Path, required=True)
    ap.add_argument("--wild-audit", type=Path, required=True)
    ap.add_argument("--ecology", type=Path, required=True)
    ap.add_argument("--ecology-effects", type=Path)
    ap.add_argument("--ecology-studies", type=Path)
    ap.add_argument("--figure-inputs", type=Path, required=True)
    ap.add_argument("--results", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    a = ap.parse_args()

    disposition = read_csv(a.disposition)
    micro = read_csv(a.micro)
    wild = read_csv(a.wild_audit)
    ecology = read_csv(a.ecology)
    ecology_effects = read_csv(a.ecology_effects) if a.ecology_effects else []
    ecology_studies = read_csv(a.ecology_studies) if a.ecology_studies else []
    if bool(a.ecology_effects) != bool(a.ecology_studies):
        raise SystemExit("--ecology-effects and --ecology-studies must be supplied together")
    figure_inputs = read_csv(a.figure_inputs)
    results = read_csv(a.results)

    a.out_dir.mkdir(parents=True, exist_ok=True)

    # S1: full manuscript placement map, including excluded provenance.
    write_csv(a.out_dir / "Table_S1_analysis_disposition.csv", disposition)

    # S2: primary/public sequence provenance for all current micro result IDs.
    write_csv(a.out_dir / "Table_S2_micro_sequence_source_provenance.csv", micro)

    # S3: accepted-species wild-colour source grading and seed treatment.
    write_csv(a.out_dir / "Table_S3_wild_colour_source_audit.csv", wild)

    # S4: v0.1 primary evidence, or the versioned v0.2 study/effect registry join.
    if ecology_effects:
        ecological_rows, ecological_fields = build_ecological_v2_rows(ecology_studies, ecology_effects)
        ecological_file = "Table_S4_camellia_ecological_driver_evidence_v0_2.csv"
        write_csv(a.out_dir / ecological_file, ecological_rows, ecological_fields)
        ecological_caption = (
            "Study-level Camellia ecological-driver evidence joined to the v0.2 effect-size "
            "registry, including admission status, variance limitations, independence units, "
            "and claim ceilings."
        )
    else:
        ecological_rows = ecology
        ecological_file = "Table_S4_camellia_pollination_primary_evidence.csv"
        write_csv(a.out_dir / ecological_file, ecology)
        ecological_caption = (
            "Primary Camellia pollination, sensory, and reproductive-context studies used to "
            "evaluate visible-state aliasing and context dependence."
        )

    # S5: numerical topology/trait robustness values plotted in Main Figs 4–5.
    s5 = [r for r in figure_inputs if r["figure_id"] in {"Fig4", "Fig5"}]
    write_csv(a.out_dir / "Table_S5_topology_and_colour_robustness_values.csv", s5)

    # S6: current accepted-species root/event sensitivity + public-data boundary rows.
    wanted = {
        "H01_ACCEPTED_ROOT_W_FAVOURED_WITH_UNCERTAINTY",
        "B01_NO_ROBUST_ACCEPTED_BRANCH_EVENTS",
        "C02_PUBLIC_DATA_IDENTIFIABILITY_BOUNDARY",
        "P04_GLOBAL_MPD_TOPOLOGY_SENSITIVE",
        "P05_A_SPECIFIC_PERMISSIVITY_NOT_STRICT",
    }
    s6 = [r for r in results if r["result_id"] in wanted]
    if {r["result_id"] for r in s6} != wanted:
        raise SystemExit("Table S6 missing one or more frozen sensitivity/boundary result IDs")
    write_csv(a.out_dir / "Table_S6_trait_history_and_identifiability_sensitivity.csv", s6)

    descriptions = [
        {
            "table": "Table S1",
            "file": "Table_S1_analysis_disposition.csv",
            "caption": "Paper 1 analysis disposition. Current, sensitivity, consumed/provenance and excluded analyses are assigned explicitly to manuscript roles.",
        },
        {
            "table": "Table S2",
            "file": "Table_S2_micro_sequence_source_provenance.csv",
            "caption": "Primary/public sequence provenance for FLS, DFR, ANS/LDOX and ANR evidence used in the sequence-aware molecular synthesis.",
        },
        {
            "table": "Table S3",
            "file": "Table_S3_wild_colour_source_audit.csv",
            "caption": "Species-level wild/floristic flower-colour source audit, source grade, and strict/dominant trait treatment after WFO accepted-taxonomy normalization.",
        },
        {
            "table": "Table S4",
            "file": ecological_file,
            "caption": ecological_caption,
        },
        {
            "table": "Table S5",
            "file": "Table_S5_topology_and_colour_robustness_values.csv",
            "caption": "Frozen numerical values underlying accepted-species nuclear-topology sensitivity and local/global flower-colour phylogenetic-structure tests.",
        },
        {
            "table": "Table S6",
            "file": "Table_S6_trait_history_and_identifiability_sensitivity.csv",
            "caption": "Accepted-species ancestral-state sensitivity, negative robustness results, branch-event identifiability boundary, and superseded headline replacements.",
        },
    ]
    write_csv(a.out_dir / "supplementary_table_index.csv", descriptions, ["table", "file", "caption"])

    # Hard gates.
    if len({r["reference_id"] for r in ecology}) != len(ecology):
        raise SystemExit("duplicate ecological reference ID")
    if not all(r["full_citation"].strip() and r["doi_or_stable_url"].strip() for r in ecology):
        raise SystemExit("ecological Table S4 contains incomplete citations")
    if not any(r["manuscript_placement"] == "exclude" for r in disposition):
        raise SystemExit("Table S1 unexpectedly lacks excluded/superseded analysis rows")
    if any(r.get("source_grade", "").startswith("C_") and (r.get("strict_state") or r.get("dominant_state")) for r in wild):
        raise SystemExit("Table S3 contains C-grade source admitted into strict/dominant state seed")

    summary = {
        "supplement_version": "v0.2 ecological integration" if ecology_effects else "v0.1",
        "tables": {x["table"]: x["file"] for x in descriptions},
        "n_analysis_disposition_rows": len(disposition),
        "n_micro_source_rows": len(micro),
        "n_wild_colour_source_rows": len(wild),
        "n_ecological_primary_references": len(ecology),
        "n_ecological_v2_studies": len(ecology_studies),
        "n_ecological_v2_effects": len(ecology_effects),
        "n_ecological_v2_appendix_rows": len(ecological_rows),
        "n_topology_trait_numeric_rows": len(s5),
        "n_trait_history_boundary_rows": len(s6),
        "new_scientific_analysis": False,
        "policy": "Supplementary tables materialize frozen Paper 1 provenance/sensitivity inputs only.",
    }
    (a.out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
