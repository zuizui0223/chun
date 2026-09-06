#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

REQUIRED = {
    "reported_name", "normalized_name", "reported_anthocyanin_state",
    "primary_molecular_organ", "secondary_molecular_organ", "visible_state_context",
    "species_level_variation_flag", "dependence_group", "event_direction_status",
    "key_molecular_evidence", "notes",
}

EXPECTED = {
    "Epimedium acuminatum",
    "Epimedium leptorrhizum",
    "Epimedium epsteinii",
    "Epimedium zhushanense",
    "Epimedium sagittatum",
    "Epimedium lishihchenii",
    "Epimedium franchetii",
    "Epimedium wushanense",
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--matrix", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    with a.matrix.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            raise SystemExit("missing header")
        missing = REQUIRED.difference(reader.fieldnames)
        if missing:
            raise SystemExit(f"missing columns: {sorted(missing)}")
        rows = list(reader)

    if len(rows) != 8:
        raise SystemExit(f"expected 8 molecular accessions, found {len(rows)}")

    names = {r["normalized_name"] for r in rows}
    if names != EXPECTED:
        raise SystemExit(f"unexpected normalized taxon set: {sorted(names ^ EXPECTED)}")

    apos = [r for r in rows if r["reported_anthocyanin_state"] == "A+"]
    aminus = [r for r in rows if r["reported_anthocyanin_state"] == "A-"]
    if len(apos) != 4 or len(aminus) != 4:
        raise SystemExit("molecular study must remain 4 A+ / 4 A-")

    bad_direction = [r["normalized_name"] for r in rows if r["event_direction_status"] != "UNRESOLVED_NEEDS_ORGAN_ASR"]
    if bad_direction:
        raise SystemExit(f"historical direction assigned before organ-specific ASR: {bad_direction}")

    fr = {r["normalized_name"] for r in rows if r["dependence_group"] == "FRANCHETII_COMPLEX"}
    expected_fr = {"Epimedium franchetii", "Epimedium lishihchenii", "Epimedium zhushanense"}
    if fr != expected_fr:
        raise SystemExit(f"FRANCHETII_COMPLEX drift: {sorted(fr)}")

    for taxon in ["Epimedium acuminatum", "Epimedium leptorrhizum"]:
        row = next(r for r in rows if r["normalized_name"] == taxon)
        if "POLYMORPHIC" not in row["species_level_variation_flag"]:
            raise SystemExit(f"{taxon}: geographic colour variation must not be collapsed")

    if any(r["primary_molecular_organ"] != "PETAL_SPUR" for r in rows):
        raise SystemExit("primary molecular organ must remain PETAL_SPUR for the eight-species qPCR comparison")

    groups = sorted({r["dependence_group"] for r in rows})
    summary = {
        "version": "v0.1",
        "molecular_accessions": len(rows),
        "A_plus_accessions": len(apos),
        "A_minus_accessions": len(aminus),
        "conservative_dependence_groups": len(groups),
        "dependence_groups": groups,
        "naive_four_loss_events_forbidden": True,
        "species_state_majority_collapse_forbidden": True,
        "historical_event_direction_gate": "BLOCKED_PENDING_ORGAN_SPECIFIC_ASR",
        "second_mechanistic_anchor": "PROMISING_BUT_EVENT_ORIENTATION_BLOCKED",
        "paper1_science_changed": False,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
