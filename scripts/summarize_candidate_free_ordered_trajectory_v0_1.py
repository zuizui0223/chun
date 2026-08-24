#!/usr/bin/env python3
"""Summarize a prespecified five-stage candidate-free pigment-module trajectory.

Primary inference uses all ordered S1-S5 stage means. No endpoint or stage pair is
selected from the expression outcome. For each A/F/C/P axis the script reports:
- per-stage mean module score and replication;
- OLS slope across the five prespecified stage means;
- an exact two-sided 5! stage-order permutation P-value for |slope|;
- adjacent-step direction consistency with the fitted slope;
- S5-S1 endpoint delta as sensitivity only.

No expected biological direction is encoded as a pass/fail condition.
"""

from __future__ import annotations

import argparse
import csv
import itertools
import json
import math
from collections import defaultdict
from pathlib import Path

STAGES = ["S1", "S2", "S3", "S4", "S5"]
STAGE_X = [1.0, 2.0, 3.0, 4.0, 5.0]
AXES = ["A", "F", "C", "P"]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        raise ValueError(f"empty input: {path}")
    return rows


def mean(xs: list[float]) -> float:
    return sum(xs) / len(xs)


def ols_slope(y: list[float]) -> float:
    if len(y) != len(STAGE_X):
        raise ValueError("five ordered stage means are required")
    xbar = mean(STAGE_X)
    ybar = mean(y)
    denom = sum((x - xbar) ** 2 for x in STAGE_X)
    return sum((x - xbar) * (v - ybar) for x, v in zip(STAGE_X, y)) / denom


def exact_order_p(y: list[float], observed_slope: float) -> float:
    threshold = abs(observed_slope) - 1e-15
    extreme = 0
    total = 0
    for perm in itertools.permutations(y):
        total += 1
        if abs(ols_slope(list(perm))) >= threshold:
            extreme += 1
    if total != math.factorial(5):
        raise AssertionError(total)
    return extreme / total


def stage_from_condition(condition: str) -> str | None:
    tail = condition.rsplit("_", 1)[-1]
    return tail if tail in STAGES else None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scores", type=Path, required=True)
    ap.add_argument("--dependence-cluster", default="CNITIDISSIMA")
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()

    rows = read_csv(args.scores)
    grouped: dict[tuple[str, str], list[float]] = defaultdict(list)

    for row in rows:
        if row.get("dependence_cluster") != args.dependence_cluster:
            continue
        if row.get("axis") not in AXES:
            continue
        if row.get("score_status") != "admitted":
            continue
        stage = stage_from_condition(row.get("condition_id", ""))
        if stage is None:
            continue
        value = row.get("module_score", "")
        if value == "":
            continue
        grouped[(row["axis"], stage)].append(float(value))

    axis_out: dict[str, object] = {}
    stage_rows: list[dict[str, object]] = []

    for axis in AXES:
        means: list[float] = []
        resolved_all = True
        stage_summary: dict[str, object] = {}
        for stage in STAGES:
            vals = grouped.get((axis, stage), [])
            record = {
                "axis": axis,
                "stage": stage,
                "stage_index": STAGES.index(stage) + 1,
                "n": len(vals),
                "mean_module_score": mean(vals) if vals else None,
            }
            stage_rows.append(record)
            stage_summary[stage] = {
                "n": len(vals),
                "mean_module_score": mean(vals) if vals else None,
            }
            if not vals:
                resolved_all = False
            else:
                means.append(mean(vals))

        if not resolved_all:
            axis_out[axis] = {
                "status": "incomplete_stage_trajectory",
                "n_stages_resolved": sum(bool(grouped.get((axis, s), [])) for s in STAGES),
                "stages": stage_summary,
                "slope": None,
                "exact_order_p_two_sided": None,
                "adjacent_direction_consistency": None,
                "endpoint_delta_S5_minus_S1": None,
            }
            continue

        slope = ols_slope(means)
        p = exact_order_p(means, slope)
        if slope > 0:
            direction = "up"
        elif slope < 0:
            direction = "down"
        else:
            direction = "flat"

        diffs = [b - a for a, b in zip(means[:-1], means[1:])]
        if slope > 0:
            consistent = sum(d > 0 for d in diffs) / 4
        elif slope < 0:
            consistent = sum(d < 0 for d in diffs) / 4
        else:
            consistent = sum(abs(d) < 1e-15 for d in diffs) / 4

        axis_out[axis] = {
            "status": "computed_all_five_prespecified_stages",
            "n_stages_resolved": 5,
            "stages": stage_summary,
            "slope": slope,
            "trend_direction": direction,
            "exact_order_p_two_sided": p,
            "adjacent_direction_consistency": consistent,
            "endpoint_delta_S5_minus_S1": means[-1] - means[0],
        }

    args.out_dir.mkdir(parents=True, exist_ok=True)
    with (args.out_dir / "stage_module_means.csv").open("w", newline="", encoding="utf-8") as fh:
        fields = ["axis", "stage", "stage_index", "n", "mean_module_score"]
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(stage_rows)

    summary = {
        "status": "candidate_free_ordered_trajectory",
        "dependence_cluster": args.dependence_cluster,
        "prespecified_stages": STAGES,
        "primary_statistic": "OLS slope across all five prespecified stage means",
        "uncertainty_test": "exact two-sided permutation over all 5! stage-order assignments",
        "axes": axis_out,
        "endpoint_rule": "S1-to-S5 delta is sensitivity only and cannot replace the ordered trajectory",
        "forbidden_rule": "do not choose the stage pair or developmental window with the largest observed module separation",
        "direction_rule": "no expected A/F/C/P direction is required for workflow success",
    }
    (args.out_dir / "trajectory_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
