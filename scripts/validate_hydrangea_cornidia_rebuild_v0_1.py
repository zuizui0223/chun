#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--transitions", type=Path, required=True)
    ap.add_argument("--template", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    a = ap.parse_args()

    with a.transitions.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    expected = {
        ("RED", "WHITE"): 18.011,
        ("PURPLE", "WHITE"): 4.680,
        ("WHITE", "RED"): 4.939,
        ("WHITE", "PURPLE"): 1.773,
    }
    got = {(r["source_state"], r["target_state"]): float(r["mean_transitions"]) for r in rows}
    if got != expected:
        raise SystemExit(f"published transition QC drift: {got}")

    with a.template.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        fields = set(reader.fieldnames or [])
    required = {
        "accepted_taxon", "source_taxon_name", "phylogeny_tip", "flower_type",
        "display_organ", "visible_state", "source_doi", "source_record",
        "source_locator", "agreement_status", "polymorphism_status",
        "uncertainty_class", "include_macro", "notes",
    }
    missing = required - fields
    if missing:
        raise SystemExit(f"template missing columns: {sorted(missing)}")

    to_white = expected[("RED", "WHITE")] + expected[("PURPLE", "WHITE")]
    from_white = expected[("WHITE", "RED")] + expected[("WHITE", "PURPLE")]
    ratio = to_white / from_white
    if ratio <= 1:
        raise SystemExit("falsification QC should show more published returns to white than gains from white")

    summary = {
        "version": "v0.1",
        "published_qc_rows": len(rows),
        "coloured_to_white_mean": round(to_white, 3),
        "white_to_coloured_mean": round(from_white, 3),
        "return_to_white_ratio": round(ratio, 6),
        "organ_context_required": True,
        "terminal_matrix_status": "REBUILD_REQUIRED",
        "minimum_provenance_coverage": 0.80,
        "published_qc_gate": "PASS",
        "atlas_asr_status": "NOT_RUN",
        "paper1_science_changed": False,
    }
    a.summary.parent.mkdir(parents=True, exist_ok=True)
    a.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
