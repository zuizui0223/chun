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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--disposition", type=Path, required=True)
    ap.add_argument("--micro", type=Path, required=True)
    ap.add_argument("--wild-audit", type=Path, required=True)
    ap.add_argument("--ecology", type=Path, required=True)
    ap.add_argument("--figure-inputs", type=Path, required=True)
    ap.add_argument("--results", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    a = ap.parse_args()

    disposition = read_csv(a.disposition)
    micro = read_csv(a.micro)
    wild = read_csv(a.wild_audit)
    ecology = read_csv(a.ecology)
    figure_inputs = read_csv(a.figure_inputs)
    results = read_csv(a.results)

    a.out_dir.mkdir(parents=True, exist_ok=True)

    # S1: full manuscript placement map, including excluded provenance.
    write_csv(a.out_dir / "Table_S1_analysis_disposition.csv", disposition)

    # S2: primary/public sequence provenance for all current micro result IDs.
    write_csv(a.out_dir / "Table_S2_micro_sequence_source_provenance.csv", micro)

    # S3: accepted-species wild-colour source grading and seed treatment.
    write_csv(a.out_dir / "Table_S3_wild_colour_source_audit.csv", wild)

    # S4: primary ecological/pollination evidence with exact bibliographic links.
    write_csv(a.out_dir / "Table_S4_camellia_pollination_primary_evidence.csv", ecology)

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
            "file": "Table_S4_camellia_pollination_primary_evidence.csv",
            "caption": "Primary Camellia pollination, sensory, and reproductive-context studies used to evaluate visible-state aliasing and context dependence.",
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
        "supplement_version": "v0.1",
        "tables": {x["table"]: x["file"] for x in descriptions},
        "n_analysis_disposition_rows": len(disposition),
        "n_micro_source_rows": len(micro),
        "n_wild_colour_source_rows": len(wild),
        "n_ecological_primary_references": len(ecology),
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
