#!/usr/bin/env python3
"""Summarize a preregistered developmental series without selecting a favorable stage.

The input is the axis-level contrast table emitted by score_candidate_free_modules_v0_1.py.
All prespecified stages contribute equally. A mechanistic direction is called stage-consistent
only when at least four stages are estimable and >=80% of estimable stages share the sign of
the equal-weight mean Hedges' g. No expected biological direction is encoded here.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import statistics
from collections import defaultdict
from pathlib import Path

AXES = ("A", "F", "C", "P")
STAGES = ("S1", "S2", "S3", "S4", "S5")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        raise ValueError(f"empty input: {path}")
    return rows


def stage_from_contrast_id(cid: str) -> str:
    m = re.search(r"_S([1-5])_", cid)
    if not m:
        raise ValueError(f"cannot resolve stage from contrast_id={cid!r}")
    return f"S{m.group(1)}"


def direction(x: float) -> str:
    return "up" if x > 0 else "down" if x < 0 else "same"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--effects", type=Path, required=True)
    ap.add_argument("--dependence-cluster", default="CSIN_WHITE_PINK")
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()

    rows = [r for r in read_csv(args.effects) if r["dependence_cluster"] == args.dependence_cluster]
    if len(rows) != len(AXES) * len(STAGES):
        raise ValueError(f"expected {len(AXES)*len(STAGES)} stage-axis rows, found {len(rows)}")

    seen = {(stage_from_contrast_id(r["contrast_id"]), r["axis"]) for r in rows}
    expected = {(s, a) for s in STAGES for a in AXES}
    if seen != expected:
        raise ValueError(f"stage-axis grid mismatch: missing={sorted(expected-seen)}, extra={sorted(seen-expected)}")

    by_axis: dict[str, list[dict[str, object]]] = defaultdict(list)
    stage_rows: list[dict[str, object]] = []
    for r in rows:
        stage = stage_from_contrast_id(r["contrast_id"])
        g = None
        if r["effect_status"] == "ok" and r.get("hedges_g", ""):
            value = float(r["hedges_g"])
            if math.isfinite(value):
                g = value
        rec = {
            "stage": stage,
            "axis": r["axis"],
            "effect_status": r["effect_status"],
            "hedges_g": g,
            "direction": "unresolved" if g is None else direction(g),
            "n_source": int(r["n_source"]),
            "n_target": int(r["n_target"]),
        }
        stage_rows.append(rec)
        by_axis[r["axis"]].append(rec)

    axis_summary: dict[str, dict[str, object]] = {}
    for axis in AXES:
        vals = [float(r["hedges_g"]) for r in by_axis[axis] if r["hedges_g"] is not None]
        n = len(vals)
        if n:
            mean_g = sum(vals) / n
            median_g = statistics.median(vals)
            mean_direction = direction(mean_g)
            same_sign = sum(direction(v) == mean_direction for v in vals)
            sign_consistency = same_sign / n
        else:
            mean_g = median_g = None
            mean_direction = "unresolved"
            sign_consistency = None
        if n >= 4 and sign_consistency is not None and sign_consistency >= 0.8:
            status = "stage_consistent"
            primary_direction = mean_direction
        elif n >= 4:
            status = "stage_heterogeneous"
            primary_direction = "unresolved"
        else:
            status = "underidentified"
            primary_direction = "unresolved"
        axis_summary[axis] = {
            "n_stages_total": 5,
            "n_stages_estimable": n,
            "equal_weight_mean_hedges_g": mean_g,
            "median_hedges_g": median_g,
            "sign_consistency": sign_consistency,
            "status": status,
            "primary_direction": primary_direction,
            "stage_effects": {r["stage"]: r["hedges_g"] for r in sorted(by_axis[axis], key=lambda x: x["stage"])},
        }

    out = {
        "status": "candidate_free_stage_series_summarized",
        "dependence_cluster": args.dependence_cluster,
        "prespecified_stages": list(STAGES),
        "axes": axis_summary,
        "primary_rule": "all five stages retained; equal-weight mean direction is admitted only with >=4 estimable stages and >=0.8 same-sign consistency",
        "forbidden_rule": "do not select the stage with the largest or expected effect after expression inspection",
    }
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "stage_series_summary.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    fields = ["stage", "axis", "effect_status", "hedges_g", "direction", "n_source", "n_target"]
    with (args.out_dir / "stage_axis_effects.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(sorted(stage_rows, key=lambda x: (x["stage"], x["axis"])))
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
