#!/usr/bin/env python3
"""Validate the frozen run-level Camellia flower-colour meta-analysis manifest."""
from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path

EXPECTED_SEED_COUNTS = {
    "CMETA001": 15,
    "CMETA002": 15,
    "CMETA003": 15,
    "CMETA004": 15,
    "CMETA005": 6,
    "CMETA006": 9,
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest", type=Path)
    args = ap.parse_args()
    with args.manifest.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    failures: list[str] = []
    if len(rows) != 75:
        failures.append(f"expected 75 rows, found {len(rows)}")

    runs = [r["run"].strip() for r in rows]
    biosamples = [r["biosample"].strip() for r in rows]
    if len(set(runs)) != 75:
        failures.append("run accessions are not unique")
    if len(set(biosamples)) != 75:
        failures.append("BioSample accessions are not unique")

    counts = Counter(r["seed_id"].strip() for r in rows)
    if dict(counts) != EXPECTED_SEED_COUNTS:
        failures.append(f"seed counts changed: observed={dict(counts)}, expected={EXPECTED_SEED_COUNTS}")

    mapping_counts = Counter(r["mapping_status"].strip() for r in rows)
    if mapping_counts.get("resolved", 0) != 72 or mapping_counts.get("partial_colour_unresolved", 0) != 3:
        failures.append(f"mapping-status counts changed: {dict(mapping_counts)}")

    unresolved = [r for r in rows if r["mapping_status"].strip() == "partial_colour_unresolved"]
    if {r["biological_group"].strip() for r in unresolved} != {"CJ"}:
        failures.append("only CJ control samples may remain colour-unresolved")
    if {r["replicate"].strip() for r in unresolved} != {"1", "2", "3"}:
        failures.append("CJ unresolved controls must be exactly replicates 1,2,3")

    # C. sinensis pink and white: S1-S5 x three replicates each.
    for seed, colour in [("CMETA002", "pink"), ("CMETA003", "white")]:
        subset = [r for r in rows if r["seed_id"] == seed]
        observed = {(r["developmental_stage"], r["replicate"], r["visible_colour"]) for r in subset}
        expected = {(f"S{s}", str(rep), colour) for s in range(1, 6) for rep in range(1, 4)}
        if observed != expected:
            failures.append(f"{seed}: developmental stage/replicate/colour grid changed")

    # Bud-sport groups: five groups x three reps, with only CJ unresolved.
    bud = [r for r in rows if r["seed_id"] == "CMETA004"]
    by_group: dict[str, set[str]] = defaultdict(set)
    for r in bud:
        by_group[r["biological_group"]].add(r["replicate"])
    expected_groups = {"CJ", "CD", "JH", "FD", "YD"}
    if set(by_group) != expected_groups or any(reps != {"1", "2", "3"} for reps in by_group.values()):
        failures.append(f"CMETA004: bud-sport group/replicate structure changed: {dict(by_group)}")
    expected_colours = {"CD": "red", "JH": "dark_red", "FD": "pink", "YD": "white"}
    for group, colour in expected_colours.items():
        values = {r["visible_colour"] for r in bud if r["biological_group"] == group}
        if values != {colour}:
            failures.append(f"CMETA004: {group} colour changed: {values}")

    # Joy Kendrick: 3 pink + 3 red.
    joy = [r for r in rows if r["seed_id"] == "CMETA005"]
    if Counter(r["visible_colour"] for r in joy) != Counter({"pink": 3, "red": 3}):
        failures.append("CMETA005: expected three pink and three red sector samples")

    # Three-species comparison: 3 red, 3 white, 3 yellow.
    ryw = [r for r in rows if r["seed_id"] == "CMETA006"]
    if Counter(r["visible_colour"] for r in ryw) != Counter({"red": 3, "white": 3, "yellow": 3}):
        failures.append("CMETA006: expected 3 red, 3 white and 3 yellow samples")

    if failures:
        print("Camellia general-colour manifest validation FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1

    colour_counts = Counter(r["visible_colour"] for r in rows)
    print("Camellia general-colour manifest validation PASSED")
    print(f"rows={len(rows)}, unique_runs={len(set(runs))}, unique_biosamples={len(set(biosamples))}")
    print(f"seed_counts={dict(counts)}")
    print(f"mapping_status={dict(mapping_counts)}")
    print(f"sample_level_colour_counts={dict(colour_counts)}")
    print("NOTE: sample-level colour counts are not evolutionary transition counts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
