#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    with a.registry.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if len(rows) < 10:
        raise SystemExit("candidate screen too small for frozen stop rule")

    by = {r["candidate"]: r for r in rows}
    required = {
        "Camellia", "Epimedium_sect_Diphyllon", "Petunia_long_tube_subclade",
        "Linoideae", "Hydrangea_sect_Cornidia", "Polygonatum",
        "Jasminum_indian_clade", "Linanthus", "Nicotiana",
        "Chilean_Mimulus_luteus_group", "Iochrominae",
    }
    missing = required.difference(by)
    if missing:
        raise SystemExit(f"missing candidates: {sorted(missing)}")

    if by["Camellia"]["strict_anchor_status"] != "PASS_REFERENCE_ANCHOR":
        raise SystemExit("Camellia reference role drift")

    white_like_failures = [
        "Epimedium_sect_Diphyllon", "Petunia_long_tube_subclade",
        "Linoideae", "Hydrangea_sect_Cornidia", "Polygonatum",
        "Jasminum_indian_clade",
    ]
    if any(by[x]["strict_anchor_status"].startswith("PASS") for x in white_like_failures):
        raise SystemExit("a failed white-like candidate was silently promoted")

    nonwhite = ["Chilean_Mimulus_luteus_group", "Iochrominae"]
    if any(by[x]["strict_anchor_status"] != "PASS_NONWHITE_BENCHMARK" for x in nonwhite):
        raise SystemExit("positive nonwhite benchmark missing")

    if by["Linanthus"]["strict_anchor_status"] != "FAIL_WHITE_BASELINE_CRITERION":
        raise SystemExit("modern Linanthus ancestral-state revision not retained")

    summary = {
        "version": "v0.1",
        "screened_candidates": len(rows),
        "full_reference_anchors": 1,
        "strict_second_white_like_anchors": 0,
        "positive_nonwhite_benchmarks": len(nonwhite),
        "exact_clone_search": "STOP_CURRENT_PHASE_REOPEN_ON_NEW_EVIDENCE",
        "atlas_design": "ROLE_BASED",
        "claim_of_exhaustiveness": False,
        "paper1_science_changed": False,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
