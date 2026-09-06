#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

REQUIRED = {
    "species_reported", "accepted_species", "molecular_state", "molecular_sample_unit",
    "wild_source_description", "exact_wild_population_crosswalk",
    "known_intraspecific_colour_polymorphism", "macro_phylogeny_mapping_status",
    "independent_historical_transition_status", "hplc_anthocyanidin", "petal_qpcr",
    "sepal_qpcr", "functional_assay", "notes",
}

EXPECTED_ACCEPTED = {
    "Epimedium acuminatum", "Epimedium leptorrhizum", "Epimedium epsteinii",
    "Epimedium zhushanense", "Epimedium franchetii", "Epimedium sagittatum",
    "Epimedium lishihchenii", "Epimedium wushanense",
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--table", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    with a.table.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            raise SystemExit("missing header")
        missing = REQUIRED.difference(reader.fieldnames)
        if missing:
            raise SystemExit(f"missing columns: {sorted(missing)}")
        rows = list(reader)

    if len(rows) != 8:
        raise SystemExit(f"expected exactly 8 molecular species rows, found {len(rows)}")

    accepted = {r["accepted_species"] for r in rows}
    if accepted != EXPECTED_ACCEPTED:
        raise SystemExit(f"accepted-species set drift: {sorted(accepted ^ EXPECTED_ACCEPTED)}")

    states = [r["molecular_state"] for r in rows]
    if states.count("A+") != 4 or states.count("A-") != 4:
        raise SystemExit("molecular panel must retain the published 4 A+ / 4 A- sample split")

    for i, r in enumerate(rows, start=2):
        if r["molecular_sample_unit"] != "WUHAN_GARDEN_ACCESSION_TRANSPLANTED_FROM_WILD":
            raise SystemExit(f"row {i}: sample-unit drift")
        if r["exact_wild_population_crosswalk"] != "UNRESOLVED":
            raise SystemExit(f"row {i}: exact wild-source crosswalk cannot be promoted without a new evidence version")
        if r["independent_historical_transition_status"] != "UNRESOLVED_NO_ACCESSION_EVENT_CROSSWALK":
            raise SystemExit(f"row {i}: historical independence must remain unresolved in v0.2")
        if r["hplc_anthocyanidin"] != "YES" or r["petal_qpcr"] != "YES":
            raise SystemExit(f"row {i}: published molecular measurement contract drift")

    by_species = {r["accepted_species"]: r for r in rows}
    for sp in ["Epimedium acuminatum", "Epimedium leptorrhizum"]:
        if by_species[sp]["known_intraspecific_colour_polymorphism"] != "YES_DOCUMENTED_2019":
            raise SystemExit(f"{sp}: known population colour polymorphism must be retained")

    if by_species["Epimedium epsteinii"]["species_reported"] != "E. epstenii":
        raise SystemExit("reported/accepted spelling provenance for E. epsteinii drifted")

    identified_events = sum(
        r["independent_historical_transition_status"].startswith("IDENTIFIED_") for r in rows
    )
    second_anchor_gate = "HOLD_EVENT_IDENTITY_UNRESOLVED" if identified_events < 3 else "PASS"
    if second_anchor_gate == "PASS":
        raise SystemExit("v0.2 must not pass the >=3 independent historical-transition gate")

    summary = {
        "gate_version": "v0.2",
        "molecular_rows": len(rows),
        "A_plus_rows": states.count("A+"),
        "A_minus_rows": states.count("A-"),
        "known_polymorphic_molecular_species": 2,
        "exact_wild_population_crosswalks": sum(r["exact_wild_population_crosswalk"] != "UNRESOLVED" for r in rows),
        "identified_independent_historical_transitions": identified_events,
        "second_mechanistic_anchor_gate": second_anchor_gate,
        "allowed_role": "FUNCTIONAL_MODULE_AND_ACCESSION_HISTORY_BRIDGE",
        "paper1_science_changed": False,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
