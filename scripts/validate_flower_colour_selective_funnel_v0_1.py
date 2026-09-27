#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

REQUIRED = {
    "system", "evidence_scale", "current_variation_layer", "fixed_or_macro_layer",
    "molecular_comparability", "direct_same_system_test", "role", "primary_source",
    "open_data_source", "status", "notes",
}

REQUIRED_ROLES = {
    "DIRECT_SELECTIVE_FUNNEL_BENCHMARK",
    "DIRECT_MUTATION_SPECTRUM_BENCHMARK",
    "MACRO_TEMPORAL_SPATIAL_BRIDGE",
    "TRANS_SPECIFIC_POLYMORPHISM_CONTROL",
    "MICRO_MACRO_ECOLOGY_CONTROL",
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--evidence", type=Path, required=True)
    ap.add_argument("--ontology", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    with a.evidence.open(newline="", encoding="utf-8") as fh:
        r = csv.DictReader(fh)
        if r.fieldnames is None:
            raise SystemExit("evidence header missing")
        miss = REQUIRED.difference(r.fieldnames)
        if miss:
            raise SystemExit(f"evidence missing columns: {sorted(miss)}")
        rows = list(r)

    if len(rows) < 5:
        raise SystemExit("need >=5 complementary evidence systems")
    roles = {x["role"] for x in rows}
    if not REQUIRED_ROLES.issubset(roles):
        raise SystemExit(f"missing roles: {sorted(REQUIRED_ROLES - roles)}")
    direct = [x for x in rows if x["direct_same_system_test"] == "yes"]
    if len(direct) < 2:
        raise SystemExit("need >=2 direct same-system/cross-scale tests")
    if not any(x["system"] == "IOCHROMINAE" and x["open_data_source"].startswith("10.5061/dryad") for x in rows):
        raise SystemExit("Iochrominae open-data benchmark missing")
    if not any(x["system"] == "MIMULUS_LEWISII" for x in rows):
        raise SystemExit("Mimulus mutation-spectrum benchmark missing")

    with a.ontology.open(newline="", encoding="utf-8") as fh:
        o = list(csv.DictReader(fh))
    if len(o) < 10:
        raise SystemExit("molecular target ontology too small")
    if not any(x["ontology_level_1"] == "UNKNOWN" for x in o):
        raise SystemExit("ontology must retain UNKNOWN rather than phenotype-impute")
    if not any(x["ontology_level_1"] == "YELLOW_PIGMENT_MODULE" for x in o):
        raise SystemExit("ontology must type yellow pigment mechanisms")
    if not any(x["ontology_level_1"] == "COPIGMENT_MODULE" for x in o):
        raise SystemExit("ontology must include copigment branch")

    summary = {
        "version": "v0.1",
        "evidence_systems": len(rows),
        "evidence_roles": sorted(roles),
        "direct_same_system_tests": len(direct),
        "ontology_rows": len(o),
        "selective_funnel_prior_art_acknowledged": True,
        "pooled_cross_clade_test_gate": "BLOCKED_PENDING_ROW_LEVEL_RECODING",
        "paper1_science_changed": False,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
