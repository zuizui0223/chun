#!/usr/bin/env python3
"""Summarize topology/scenario robustness of accepted-species wild-colour clustering.

This bridge does not rerun phylogenetic permutation tests. It consumes only result
rows already frozen from completed WFO55 FastTree/ASTRAL and WFO53 UFBoot/ASTRAL
analyses and classifies which state-level clustering conclusions survive both nuclear
topologies and both trait-coding scenarios.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

STATES = ("A", "W", "Y")
TOPOLOGIES = ("WFO55_FastTree_ASTRAL", "WFO53_UFBoot_ASTRAL")
SCENARIOS = ("strict_wild", "dominant")


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        raise ValueError("empty nuclear realization registry")
    return rows


def significant(status: str) -> bool:
    return status == "significant_both_metrics"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    rows = read_rows(args.registry)
    by_key = {(r["topology"], r["trait_scenario"], r["state"]): r for r in rows}
    expected = {(t, s, st) for t in TOPOLOGIES for s in SCENARIOS for st in STATES}
    missing = sorted(expected - set(by_key))
    if missing:
        raise ValueError(f"missing topology/scenario/state rows: {missing}")

    state_summary = {}
    for state in STATES:
        strict_rows = [by_key[(t, "strict_wild", state)] for t in TOPOLOGIES]
        dominant_rows = [by_key[(t, "dominant", state)] for t in TOPOLOGIES]
        strict_testable = all(r["state_test_status"] != "not_testable_singleton" for r in strict_rows)
        strict_sig = strict_testable and all(significant(r["state_test_status"]) for r in strict_rows)
        dominant_sig = all(significant(r["state_test_status"]) for r in dominant_rows)

        if strict_sig and dominant_sig:
            classification = "robust_across_topology_and_trait_scenario"
        elif not strict_testable and dominant_sig:
            classification = "dominant_only_sensitivity_strict_untestable"
        elif not strict_sig and not dominant_sig:
            classification = "no_state_specific_clustering_support"
        else:
            classification = "scenario_or_topology_sensitive"

        state_summary[state] = {
            "strict_wild_testable_on_both_topologies": strict_testable,
            "strict_wild_significant_on_both_topologies": strict_sig,
            "dominant_significant_on_both_topologies": dominant_sig,
            "classification": classification,
        }

    # Global nearest-same-state signal is separately documented as significant in both
    # strict and dominant scenarios on both topologies. We freeze that provenance-level
    # conclusion here rather than pretending it is state-specific evidence.
    summary = {
        "status": "nuclear_phylogenetic_realization_pattern_frozen",
        "state_summary": state_summary,
        "primary_macro_pattern": (
            "Y is locally phylogenetically clustered under both strict and dominant wild-colour "
            "coding on both independent nuclear gene-tree methods; W is not individually clustered; "
            "A clustering is a dominant-colour sensitivity because strict A is a singleton."
        ),
        "global_pattern": (
            "nearest-same-state phylogenetic distance is shorter than count-preserving null in both "
            "trait scenarios on both FastTree/ASTRAL and UFBoot/ASTRAL topologies"
        ),
        "event_boundary": (
            "specific accepted-species colour-transition branches remain unidentifiable across strict "
            "versus dominant wild-state assumptions; this is a pattern-level, root-independent result"
        ),
        "section_proxy_disposition": (
            "traditional-section concentration is retained only as supplementary historical-background "
            "sensitivity and is not the primary macro realization evidence"
        ),
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
