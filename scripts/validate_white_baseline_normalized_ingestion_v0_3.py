#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

REQUIRED = {
    "clade_id", "source_doi", "source_object", "source_unit", "display_organ",
    "allowed_visible_states", "polymorphism_handling", "phylogeny_unit",
    "minimum_coverage", "admission_status", "notes",
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    with a.contract.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            raise SystemExit("missing header")
        missing = REQUIRED.difference(reader.fieldnames)
        if missing:
            raise SystemExit(f"missing columns: {sorted(missing)}")
        rows = list(reader)

    if not rows:
        raise SystemExit("empty contract")

    seen = set()
    for i, r in enumerate(rows, start=2):
        key = (r["clade_id"], r["display_organ"])
        if key in seen:
            raise SystemExit(f"row {i}: duplicate clade/organ {key}")
        seen.add(key)
        try:
            cov = float(r["minimum_coverage"])
        except ValueError as e:
            raise SystemExit(f"row {i}: invalid minimum_coverage") from e
        if not 0 < cov <= 1:
            raise SystemExit(f"row {i}: minimum_coverage outside (0,1]")
        if "UNKNOWN" not in r["allowed_visible_states"].split(";"):
            raise SystemExit(f"row {i}: UNKNOWN must be an allowed state")
        if not r["polymorphism_handling"].strip():
            raise SystemExit(f"row {i}: missing polymorphism rule")

    epi = [r for r in rows if r["clade_id"] == "EPIMEDIUM_DIPHYLLON"]
    epi_organs = {r["display_organ"] for r in epi}
    required_epi = {"INNER_SEPAL", "PETAL_SPUR"}
    if not required_epi.issubset(epi_organs):
        raise SystemExit("Epimedium contract must preserve INNER_SEPAL and PETAL_SPUR separately")

    hyd = [r for r in rows if r["clade_id"] == "HYDRANGEA_CORNIDIA"]
    if not hyd or hyd[0]["display_organ"] != "FLORAL_DISPLAY_SEPAL":
        raise SystemExit("Hydrangea display organ must be explicitly typed as FLORAL_DISPLAY_SEPAL")

    ready = [r for r in rows if r["admission_status"] == "READY_FOR_EXTRACTION"]
    rebuild = [r for r in rows if r["admission_status"] == "REBUILD_REQUIRED"]
    controls = [r for r in rows if r["admission_status"] == "CONTROL_READY"]
    if len({r['clade_id'] for r in ready}) < 2:
        raise SystemExit("need at least two extraction-ready clades")
    if len({r['clade_id'] for r in rebuild}) < 1:
        raise SystemExit("need at least one original rebuild target")
    if len({r['clade_id'] for r in controls}) < 1:
        raise SystemExit("need at least one coloured-ancestor control")

    summary = {
        "version": "v0.3",
        "contract_rows": len(rows),
        "unique_clades": len({r['clade_id'] for r in rows}),
        "extraction_ready_clades": len({r['clade_id'] for r in ready}),
        "rebuild_required_clades": len({r['clade_id'] for r in rebuild}),
        "control_ready_clades": len({r['clade_id'] for r in controls}),
        "organ_typing_gate": "PASS",
        "polymorphism_preservation_gate": "PASS",
        "pooled_analysis_gate": "BLOCKED_PENDING_TRAIT_ROWS",
        "paper1_science_changed": False,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
