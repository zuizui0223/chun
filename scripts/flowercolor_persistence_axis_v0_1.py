#!/usr/bin/env python3
from __future__ import annotations

from typing import Any

import numpy as np

ULTRAMETRIC_MAX_REL_DEV = 1e-5


def tree_axis_diagnostics(tree) -> dict[str, Any]:
    """Classify a branch-length tree as relative-time-like only if root-to-tip
    distances are effectively equal under the frozen tolerance.
    """
    tips = tree.get_terminals()
    if len(tips) < 2:
        raise ValueError("tree requires at least two terminal tips")
    rtt = np.asarray([float(tree.distance(tree.root, tip)) for tip in tips], dtype=float)
    if not np.all(np.isfinite(rtt)) or np.any(rtt < 0):
        raise ValueError("root-to-tip distances must be finite and non-negative")
    mean = float(rtt.mean())
    if mean <= 0:
        raise ValueError("tree height must be positive")
    cv = float(rtt.std(ddof=0) / mean)
    max_rel = float(np.max(np.abs(rtt - mean)) / mean)
    axis_class = (
        "RELATIVE_DIVERGENCE_TIME"
        if max_rel <= ULTRAMETRIC_MAX_REL_DEV
        else "NORMALIZED_PATRISTIC_DISTANCE"
    )
    return {
        "tip_count": len(tips),
        "tree_height": mean,
        "root_to_tip_cv": cv,
        "max_relative_root_to_tip_deviation": max_rel,
        "axis_class": axis_class,
    }


def persistence_curve(
    distance: np.ndarray,
    same: np.ndarray,
    *,
    bins: np.ndarray,
) -> list[dict[str, Any]]:
    """Summarize same-state sharing along a frozen normalized phylogenetic axis.

    The baseline is fixed by the observed state frequencies because the total
    number of same-state pairs is invariant to tip-label permutation.
    """
    d = np.asarray(distance, dtype=float)
    y = np.asarray(same, dtype=bool)
    edges = np.asarray(bins, dtype=float)
    if d.ndim != 1 or y.ndim != 1 or len(d) != len(y) or len(d) == 0:
        raise ValueError("distance and same must be non-empty one-dimensional arrays of equal length")
    if edges.ndim != 1 or len(edges) < 2 or np.any(np.diff(edges) <= 0):
        raise ValueError("bins must be a strictly increasing one-dimensional array")
    if not np.all(np.isfinite(d)):
        raise ValueError("distance contains non-finite values")

    baseline = float(y.mean())
    rows: list[dict[str, Any]] = []
    for k, (lo, hi) in enumerate(zip(edges[:-1], edges[1:])):
        mask = (d >= lo) & (d <= hi if k == len(edges) - 2 else d < hi)
        n = int(mask.sum())
        p = float(y[mask].mean()) if n else None
        rows.append(
            {
                "bin_index": k,
                "axis_min": float(lo),
                "axis_max": float(hi),
                "pair_count": n,
                "same_probability": p,
                "baseline_same_probability": baseline,
                "excess_same_probability": (p - baseline) if p is not None else None,
            }
        )
    return rows
