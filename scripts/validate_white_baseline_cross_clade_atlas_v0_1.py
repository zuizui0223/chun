#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

REQUIRED = {
    "clade_id", "clade", "role", "ancestral_state", "ancestral_support",
    "derived_colour_space", "transition_signal", "within_species_variation",
    "molecular_layer", "ecology_layer", "phylogeny_auditability",
    "ancestral_score", "transition_score", "molecular_score", "ecology_score",
    "auditability_score", "total_score", "phase1_status", "macro_source_doi",
    "molecular_source_doi", "notes",
}
SCORES = [
    "ancestral_score", "transition_score", "molecular_score",
    "ecology_score", "auditability_score",
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--atlas", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    with a.atlas.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            raise SystemExit("missing header")
        missing = REQUIRED.difference(reader.fieldnames)
        if missing:
            raise SystemExit(f"missing required columns: {sorted(missing)}")
        rows = list(reader)

    if not rows:
        raise SystemExit("atlas is empty")

    seen = set()
    for i, row in enumerate(rows, start=2):
        cid = row["clade_id"].strip()
        if not cid:
            raise SystemExit(f"row {i}: empty clade_id")
        if cid in seen:
            raise SystemExit(f"row {i}: duplicate clade_id {cid}")
        seen.add(cid)

        vals = []
        for col in SCORES:
            try:
                v = int(row[col])
            except ValueError as e:
                raise SystemExit(f"row {i}: non-integer {col}") from e
            if v not in (0, 1, 2):
                raise SystemExit(f"row {i}: {col}={v}, expected 0/1/2")
            vals.append(v)
        total = int(row["total_score"])
        if total != sum(vals):
            raise SystemExit(f"row {i}: total_score={total}, expected {sum(vals)}")

        if row["role"].startswith("white_like") and int(row["ancestral_score"]) < 1:
            raise SystemExit(f"row {i}: white-like admission lacks ancestral support")
        if not row["phase1_status"].strip():
            raise SystemExit(f"row {i}: empty phase1_status")

    white_supported = [r for r in rows if r["role"].startswith("white_like") and int(r["ancestral_score"]) >= 1]
    nonwhite_controls = [r for r in rows if "control" in r["role"] and not r["role"].startswith("white_like")]
    mechanistic = [r for r in rows if int(r["molecular_score"]) == 2]

    if len(white_supported) < 3:
        raise SystemExit(f"macro gate fails: only {len(white_supported)} supported white-like clades")
    if len(nonwhite_controls) < 2:
        raise SystemExit(f"control gate fails: only {len(nonwhite_controls)} non-white controls")

    summary = {
        "atlas_version": "v0.1",
        "rows": len(rows),
        "supported_white_like_clades": len(white_supported),
        "nonwhite_or_transition_controls": len(nonwhite_controls),
        "strong_molecular_rows": len(mechanistic),
        "macro_literature_admission_gate": "PASS",
        "pooled_analysis_gate": "NOT_YET_TESTED",
        "paper1_science_changed": False,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
