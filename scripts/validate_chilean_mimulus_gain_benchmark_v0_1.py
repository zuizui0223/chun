#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from itertools import combinations
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--events", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    with a.events.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if len(rows) != 3:
        raise SystemExit(f"expected exactly 3 independent gains, found {len(rows)}")
    if any(r["event_independence"] != "INDEPENDENT_GAIN" for r in rows):
        raise SystemExit("all three events must be independently supported gains")
    if any(r["ancestral_context"] != "ancestral yellow monkeyflower background" for r in rows):
        raise SystemExit("ancestral yellow context drift")
    if any(r["molecular_target_class"] != "PATHWAY_SPECIFIC_REGULATOR" for r in rows):
        raise SystemExit("module-level R2R3-MYB regulatory recurrence not retained")

    regions = [r["genomic_region"] for r in rows]
    if sorted(regions) != ["pla1", "pla1", "pla2"]:
        raise SystemExit(f"unexpected genomic regions: {regions}")
    pair_matches = sum(a == b for a, b in combinations(regions, 2))
    pair_total = 3
    exact_gene_resolved = [r for r in rows if not r["exact_causal_gene"].startswith("UNRESOLVED")]
    if len(exact_gene_resolved) != 1 or exact_gene_resolved[0]["exact_causal_gene"] != "MYB5a/NEGAN":
        raise SystemExit("exact-gene resolution gate drift")

    summary = {
        "version": "v0.1",
        "independent_gain_events": 3,
        "module_class_recurrence": 1.0,
        "maximum_exact_region_recurrence": 2 / 3,
        "pairwise_region_concordance": pair_matches / pair_total,
        "exact_gene_resolved_events": 1,
        "exact_gene_recurrence": "NOT_ESTIMABLE",
        "atlas_role": "YELLOW_BASELINE_REGULATORY_GAIN_BENCHMARK",
        "paper1_science_changed": False,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
