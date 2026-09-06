#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

EXPECTED_SOURCE_IDS = {f"LIN_SRC_{i:02d}" for i in range(1, 9)}
EXPECTED_REF_NUMBERS = {"5", "6", "13", "54", "130", "131", "132", "133"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", type=Path, required=True)
    ap.add_argument("--template", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    with a.sources.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    ids = {r["source_id"] for r in rows}
    refs = {r["paper_reference_number"] for r in rows}
    if ids != EXPECTED_SOURCE_IDS:
        raise SystemExit(f"source-id drift: {sorted(ids)}")
    if refs != EXPECTED_REF_NUMBERS:
        raise SystemExit(f"reference-number drift: {sorted(refs)}")
    if any(not r["role_in_rebuild"].strip() for r in rows):
        raise SystemExit("empty rebuild role")

    with a.template.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        fields = set(reader.fieldnames or [])
    required_template = {
        "accepted_taxon", "source_taxon_name", "phylogeny_tip", "visible_state",
        "source_ids", "source_locator", "agreement_status", "wild_or_cultivar",
        "polymorphism_status", "uncertainty_class", "include_macro", "notes",
    }
    missing = required_template - fields
    if missing:
        raise SystemExit(f"template missing columns: {sorted(missing)}")

    summary = {
        "version": "v0.1",
        "frozen_source_groups": len(rows),
        "source_reference_numbers": sorted(EXPECTED_REF_NUMBERS, key=int),
        "terminal_matrix_status": "REBUILD_REQUIRED",
        "minimum_provenance_coverage": 0.80,
        "published_terminal_table_available": False,
        "paper1_science_changed": False,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
