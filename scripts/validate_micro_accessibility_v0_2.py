#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def close(observed: float, expected: float, tol: float = 1e-12) -> None:
    if abs(observed - expected) > tol:
        raise SystemExit(f"numeric drift: observed={observed} expected={expected}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", type=Path, required=True)
    args = parser.parse_args()
    summary = json.loads(args.summary.read_text(encoding="utf-8"))

    if summary["n_biological_systems"] != 11:
        raise SystemExit("expected 11 biological systems")
    if summary["n_dependence_clusters"] != 6:
        raise SystemExit("expected 6 dependence clusters")
    if summary["macro_transition_test"]["status"] != "blocked":
        raise SystemExit("macro transition gate unexpectedly reopened")
    if summary["degree_preserving_graph_null"]["status"] != "blocked":
        raise SystemExit("graph-null gate unexpectedly reopened")

    system_recurrence = summary["system_level_recurrence_sensitivity"]
    cluster_recurrence = summary["dependence_collapsed_recurrence_primary"]
    close(system_recurrence["observed_recurrence"], 0.256198347107438)
    close(system_recurrence["permutation_p_upper"], 0.0458954104589541, 1e-15)
    close(cluster_recurrence["observed_recurrence"], 2 / 9)
    close(cluster_recurrence["permutation_p_upper"], 0.198980101989801, 1e-15)

    system_ascertainment = summary["system_level_axis_ascertainment"]
    cluster_ascertainment = summary["dependence_collapsed_axis_ascertainment"]
    if system_ascertainment["observed_axis_coverage"] != {
        "A_change": 9, "F_change": 4, "C_change": 1, "P_change": 3
    }:
        raise SystemExit("system-level axis coverage drift")
    if system_ascertainment["n_exact_axis_assignments"] != 21233664:
        raise SystemExit("system-level exact-null size drift")
    close(system_ascertainment["exact_p_A_enrichment"], 0.002788543701171875, 1e-15)
    close(system_ascertainment["exact_p_any_axis_imbalance"], 0.008607652452256944, 1e-15)

    if cluster_ascertainment["observed_axis_coverage"] != {
        "A_change": 5, "F_change": 3, "C_change": 1, "P_change": 2
    }:
        raise SystemExit("dependence-collapsed axis coverage drift")
    if cluster_ascertainment["n_exact_axis_assignments"] != 2304:
        raise SystemExit("dependence-collapsed exact-null size drift")
    close(cluster_ascertainment["exact_p_A_enrichment"], 0.046875, 1e-15)
    close(cluster_ascertainment["exact_p_any_axis_imbalance"], 0.14583333333333334, 1e-15)

    print(json.dumps({
        "status": "micro_accessibility_v0_2_valid",
        "n_biological_systems": 11,
        "n_dependence_clusters": 6,
        "system_A_enrichment_p": system_ascertainment["exact_p_A_enrichment"],
        "cluster_A_enrichment_p": cluster_ascertainment["exact_p_A_enrichment"],
        "system_recurrence_p": system_recurrence["permutation_p_upper"],
        "cluster_recurrence_p": cluster_recurrence["permutation_p_upper"],
        "boundary": "literature ascertainment updated; candidate-free five-system common set and macro gates unchanged"
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
