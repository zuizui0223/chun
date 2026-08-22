#!/usr/bin/env python3
"""Compare accepted-species strict vs dominant wild-colour transition posteriors."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

DIRECTIONS = ("A_to_W", "A_to_Y", "W_to_A", "W_to_Y", "Y_to_A", "Y_to_W")


def read_rows(path: Path):
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def to_bool(x):
    return str(x).strip().lower() in {"true", "1", "yes"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", type=Path, required=True)
    ap.add_argument("--dominant", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args(); args.out_dir.mkdir(parents=True, exist_ok=True)

    strict = read_rows(args.strict)
    dominant = read_rows(args.dominant)
    sby = {r["clade_hash"]: r for r in strict}
    dby = {r["clade_hash"]: r for r in dominant}
    if set(sby) != set(dby):
        raise SystemExit("strict/dominant branch sets differ")

    rows = []
    robust = []
    for h in sorted(sby):
        s = sby[h]; d = dby[h]
        if s["descendant_tips"] != d["descendant_tips"]:
            raise SystemExit(f"branch descendant mismatch for {h}")
        sdir = s["top_direction_by_mean"]
        ddir = d["top_direction_by_mean"]
        same_direction = sdir == ddir
        strict_internal = to_bool(s["strong_robust_endpoint_transition"])
        dominant_internal = to_bool(d["strong_robust_endpoint_transition"])
        cross_min = min(float(s[f"min_p_{sdir}"]), float(d[f"min_p_{ddir}"])) if same_direction else 0.0
        cross_mean = (float(s[f"mean_p_{sdir}"]) + float(d[f"mean_p_{ddir}"])) / 2 if same_direction else 0.0
        admitted = bool(same_direction and strict_internal and dominant_internal and cross_min >= 0.5)
        row = {
            "clade_hash": h,
            "strict_branch_id": s["branch_id"],
            "dominant_branch_id": d["branch_id"],
            "n_descendant_tips": s["n_descendant_tips"],
            "descendant_tips": s["descendant_tips"],
            "strict_top_direction": sdir,
            "dominant_top_direction": ddir,
            "same_direction": same_direction,
            "strict_internal_robust": strict_internal,
            "dominant_internal_robust": dominant_internal,
            "cross_scenario_min_direction_p": cross_min,
            "cross_scenario_mean_direction_p": cross_mean,
            "admitted_cross_scenario_transition": admitted,
        }
        rows.append(row)
        if admitted:
            robust.append(row)

    with (args.out_dir / "strict_dominant_branch_comparison.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)

    direction_counts = {d: sum(1 for r in robust if r["strict_top_direction"] == d) for d in DIRECTIONS}
    summary = {
        "n_branches_compared": len(rows),
        "n_cross_scenario_robust_transitions": len(robust),
        "cross_scenario_direction_counts": direction_counts,
        "cross_scenario_robust_transitions": robust,
        "admission_rule": "same top direction in strict and dominant; internally robust in all four Mk treatments in each scenario; cross-scenario minimum directional posterior >= 0.5",
        "analysis_decision": (
            "only cross-scenario robust accepted-species transitions may enter branch-climate, pollination, or micro-macro tests"
            if robust else
            "no accepted-species transition survives both strict wild-colour and dominant-colour sensitivity; branch-specific ecological or micro-macro causal tests are not currently identifiable from public hard-state data"
        ),
        "claim_ceiling": "trait-scenario robustness gate only; no ecology or molecular causation",
    }
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
