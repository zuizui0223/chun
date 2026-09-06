#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--screen", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    with a.screen.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        raise SystemExit("empty screen")

    direct_auditable = [
        r for r in rows
        if r["colour_relevance"] == "DIRECT_COLOUR_CONTRAST"
        and r["auditable_raw"] == "YES"
    ]
    independent_non_amajus = [
        r for r in direct_auditable
        if "SAME_ANTIRRHINUM_LINEAGE" not in r["independence_class"]
    ]
    held_unreleased = [r for r in rows if r["admission_status"] == "HOLD"]

    # Frozen admission rule: >=3 auditable direct-colour systems, not all from one
    # Antirrhinum majus dependence lineage. Current evidence must fail closed.
    strict_pass = len(direct_auditable) >= 3 and len(independent_non_amajus) >= 1
    if strict_pass:
        raise SystemExit(
            "screen unexpectedly satisfies molecular gate; update the frozen evidence review before promotion"
        )

    summary = {
        "version": "v0.1",
        "screen_rows": len(rows),
        "auditable_direct_colour_raw_systems": len(direct_auditable),
        "auditable_direct_colour_systems_outside_amajus_dependence": len(independent_non_amajus),
        "held_unreleased_candidates": len(held_unreleased),
        "required_independent_systems": 3,
        "molecular_bridge_gate": "FAIL_HOLD",
        "recommended_role": "MACRO_TEMPORAL_SPATIAL_CONTROL",
        "next_molecular_anchor": "EPIMEDIUM_DIPHYLLON",
        "paper1_science_changed": False,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
