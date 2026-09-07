#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

EXPECTED_A = {
    "Hydrangea serratifolia",
    "Hydrangea seemannii",
    "Hydrangea integrifolia",
}
EXPECTED_I = {
    "Hydrangea tapalapensis",
    "Hydrangea sousae",
    "Hydrangea steyermarkii",
    "Hydrangea breedlovei",
    "Hydrangea nahaensis",
    "Hydrangea nebulicola",
    "Hydrangea otontepecensis",
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--states", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    with a.states.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    if len(rows) != 10:
        raise SystemExit(f"expected 10 source-backed taxa, found {len(rows)}")

    taxa = [r["accepted_taxon"] for r in rows]
    if len(set(taxa)) != len(taxa):
        raise SystemExit("duplicate accepted_taxon rows are not allowed in this species-level recovery layer")

    a_taxa = {r["accepted_taxon"] for r in rows if r["evidence_group"] == "CLADE_A_EXPLICIT_WHITE"}
    i_taxa = {r["accepted_taxon"] for r in rows if r["evidence_group"] == "CLADE_I_EXPLICIT_WHITE"}
    if a_taxa != EXPECTED_A:
        raise SystemExit(f"clade A recovered taxon set drifted: {sorted(a_taxa)}")
    if i_taxa != EXPECTED_I:
        raise SystemExit(f"clade I recovered taxon set drifted: {sorted(i_taxa)}")

    if any(r["visible_state"] != "WHITE" for r in rows):
        raise SystemExit("this frozen source-text recovery contains only explicitly white terminal taxa")
    if any(r["source_doi"] != "10.3389/fpls.2021.661522" for r in rows):
        raise SystemExit("unexpected source DOI")
    if any(r["agreement_status"] != "SOURCE_TEXT_EXPLICIT" for r in rows):
        raise SystemExit("all rows must remain explicit source-text assertions")
    if any(r["phylogeny_tip"] != "UNRESOLVED_TO_EXACT_ACCESSION_TIP" for r in rows):
        raise SystemExit("exact accession-tip mapping must not be invented in this layer")
    if any(r["include_macro"] != "0" for r in rows):
        raise SystemExit("text-recovered rows cannot enter macro ASR before exact tip mapping")

    states = Counter(r["visible_state"] for r in rows)
    summary = {
        "version": "v0.1",
        "source_backed_terminal_taxa": len(rows),
        "clade_A_explicit_white_taxa": len(a_taxa),
        "clade_I_explicit_white_taxa": len(i_taxa),
        "visible_states": dict(sorted(states.items())),
        "macro_rows_ready": sum(int(r["include_macro"]) for r in rows),
        "exact_tip_mapping_status": "PENDING",
        "terminal_matrix_status": "PARTIAL_SOURCE_RECOVERY",
        "minimum_provenance_coverage": 0.80,
        "coverage_denominator_status": "UNRESOLVED_UNTIL_SUPPLEMENT_OR_TREE_TIP_LIST",
        "atlas_asr_status": "NOT_RUN",
        "conflicting_source_sentence_excluded": True,
        "paper1_science_changed": False,
    }

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
