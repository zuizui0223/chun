#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

REQUIRED = {
    "clade_id", "clade", "macro_source_doi", "source_data_object",
    "access_status", "terminal_colour_matrix_status", "phylogeny_status",
    "molecular_source_status", "ingestion_decision", "primary_blocker",
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    with a.manifest.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            raise SystemExit("missing header")
        missing = REQUIRED.difference(reader.fieldnames)
        if missing:
            raise SystemExit(f"missing columns: {sorted(missing)}")
        rows = list(reader)

    if not rows:
        raise SystemExit("empty ingestion manifest")
    ids = [r["clade_id"].strip() for r in rows]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate clade_id")

    ready_machine = [r for r in rows if r["terminal_colour_matrix_status"] == "READY_MACHINE_READABLE"]
    ready_extract = [r for r in rows if r["terminal_colour_matrix_status"] == "READY_WITH_EXTRACTION"]
    rebuild = [r for r in rows if r["terminal_colour_matrix_status"] == "REBUILD_REQUIRED"]
    hold = [r for r in rows if r["ingestion_decision"] == "HOLD"]

    if len(ready_machine) < 1:
        raise SystemExit("source gate fails: no machine-readable terminal matrix")
    if len(ready_extract) < 1:
        raise SystemExit("source gate fails: no supplement-extractable matrix")
    if len(rebuild) < 1:
        raise SystemExit("source gate fails: no original trait-rebuild target")

    for i, r in enumerate(rows, start=2):
        if not r["source_data_object"].strip():
            raise SystemExit(f"row {i}: missing source_data_object")
        if not r["primary_blocker"].strip():
            raise SystemExit(f"row {i}: missing blocker/status note")

    summary = {
        "version": "v0.2",
        "rows": len(rows),
        "ready_machine_readable": len(ready_machine),
        "ready_with_extraction": len(ready_extract),
        "rebuild_required": len(rebuild),
        "hold": len(hold),
        "source_ingestion_gate": "PASS",
        "pooled_analysis_gate": "BLOCKED",
        "paper1_science_changed": False,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
