#!/usr/bin/env python3
"""Dependence-aware first-pass analysis of short-timescale Camellia accessibility.

The registry stores individual biological systems but also a broader dependence
cluster (for example multiple C. japonica studies). The primary recurrence test is
therefore run after collapsing systems within each dependence cluster. A system-level
analysis is retained as a descriptive sensitivity only.

The script also audits mechanistic-axis ascertainment. For each row it preserves the
number of resolved A/F/C/P axes and enumerates every axis-symmetric assignment of
those resolved slots. This gives an exact conditional null for whether anthocyanin-
axis coverage or overall axis imbalance is stronger than expected solely from how
many axes each system/cluster resolved.

No macroevolutionary transition rates are inferred here. A degree-preserving graph
null remains gated until explicit mechanistic source/target states are sufficiently
complete; visible-colour labels are never substituted for biochemical states.
"""

from __future__ import annotations

import argparse
import csv
import itertools
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

AXES = ("A_change", "F_change", "C_change", "P_change")
VALID_CHANGE = {"up", "down", "same", "unknown"}
COLLAPSED_CHANGE = VALID_CHANGE | {"mixed"}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        raise ValueError("micro-accessibility registry is empty")
    return rows


def validate(rows: list[dict[str, str]]) -> None:
    required = {
        "edge_id",
        "system_id",
        "dependence_cluster",
        "taxon",
        "evidence_scale",
        "source_state_visible",
        "target_state_visible",
        "direction_status",
        "independence_unit",
        "source",
        *AXES,
    }
    missing = required - set(rows[0])
    if missing:
        raise ValueError(f"missing columns: {sorted(missing)}")

    edge_ids = [r["edge_id"] for r in rows]
    if len(edge_ids) != len(set(edge_ids)):
        raise ValueError("edge_id values must be unique")

    system_ids = [r["system_id"] for r in rows]
    if len(system_ids) != len(set(system_ids)):
        raise ValueError("v0.1 requires one row per biological system")

    independence = [r["independence_unit"] for r in rows]
    if len(independence) != len(set(independence)):
        raise ValueError("independence_unit values must be unique at the system-row level")

    for row in rows:
        if not row["dependence_cluster"].strip():
            raise ValueError(f"{row['edge_id']}: missing dependence_cluster")
        for axis in AXES:
            value = row[axis].strip().lower()
            if value not in VALID_CHANGE:
                raise ValueError(f"{row['edge_id']}: invalid {axis}={value!r}")
        if row["direction_status"] != "directed":
            raise ValueError(f"{row['edge_id']}: v0.1 only admits directed edges")


def signature(row: dict[str, str]) -> str:
    return "|".join(row[a].strip().lower() for a in AXES)


def recurrence_score(counts: Counter[str]) -> float:
    """Simpson concentration of mechanistic change signatures."""
    n = sum(counts.values())
    return sum((c / n) ** 2 for c in counts.values())


def permutation_null(
    rows: list[dict[str, str]], n_perm: int, seed: int
) -> dict[str, object]:
    """Break cross-axis direction coupling while preserving each axis' marginals."""
    rng = random.Random(seed)
    observed = Counter(signature(r) for r in rows)
    observed_score = recurrence_score(observed)

    axis_values = {axis: [r[axis].strip().lower() for r in rows] for axis in AXES}
    null_scores: list[float] = []

    for _ in range(n_perm):
        shuffled: dict[str, list[str]] = {}
        for axis, vals in axis_values.items():
            vals2 = list(vals)
            rng.shuffle(vals2)
            shuffled[axis] = vals2

        perm_counts: Counter[str] = Counter()
        for i in range(len(rows)):
            sig = "|".join(shuffled[a][i] for a in AXES)
            perm_counts[sig] += 1
        null_scores.append(recurrence_score(perm_counts))

    ge = sum(v >= observed_score - 1e-15 for v in null_scores)
    p_upper = (ge + 1) / (n_perm + 1)
    mean_null = sum(null_scores) / len(null_scores)
    var_null = sum((v - mean_null) ** 2 for v in null_scores) / max(
        1, len(null_scores) - 1
    )
    sd_null = math.sqrt(var_null)
    z = None if sd_null == 0 else (observed_score - mean_null) / sd_null

    return {
        "observed_recurrence": observed_score,
        "null_mean": mean_null,
        "null_sd": sd_null,
        "z_vs_null": z,
        "permutation_p_upper": p_upper,
        "n_permutations": n_perm,
        "seed": seed,
    }


def collapse_dependence(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[row["dependence_cluster"]].append(row)

    collapsed: list[dict[str, str]] = []
    for cluster in sorted(groups):
        members = groups[cluster]
        out: dict[str, str] = {
            "edge_id": cluster,
            "system_id": cluster,
            "dependence_cluster": cluster,
            "taxon": "|".join(sorted({m["taxon"] for m in members})),
            "evidence_scale": "dependence_cluster_consensus",
            "source_state_visible": "not_used",
            "target_state_visible": "not_used",
            "direction_status": "directed",
            "independence_unit": cluster,
            "source": "cluster_consensus",
            "n_member_systems": str(len(members)),
        }
        for axis in AXES:
            known = [
                m[axis].strip().lower()
                for m in members
                if m[axis].strip().lower() != "unknown"
            ]
            if not known:
                value = "unknown"
            elif len(set(known)) == 1:
                value = known[0]
            else:
                value = "mixed"
            if value not in COLLAPSED_CHANGE:
                raise AssertionError(value)
            out[axis] = value
        collapsed.append(out)
    return collapsed


def direction_summary(rows: list[dict[str, str]], axis: str) -> dict[str, int]:
    counts = Counter(r[axis].strip().lower() for r in rows)
    return dict(sorted(counts.items()))


def axis_coverage(rows: list[dict[str, str]]) -> dict[str, int]:
    return {
        axis: sum(r[axis].strip().lower() != "unknown" for r in rows)
        for axis in AXES
    }


def ascertainment_exact_null(rows: list[dict[str, str]]) -> dict[str, object]:
    """Exact axis-symmetric ascertainment null conditional on row-wise coverage.

    If a row resolves k of the four A/F/C/P axes, every C(4,k) assignment of those
    k resolved slots is given equal weight under the null. The Cartesian product over
    rows is enumerated by dynamic programming over coverage vectors, so no Monte Carlo
    approximation or arbitrary seed enters the ascertainment p-values.

    `mixed` counts as resolved because the axis was measured/interpreted but known
    member systems disagreed in direction.
    """
    observed = axis_coverage(rows)
    observed_counts = tuple(observed[a] for a in AXES)
    observed_a_enrichment = observed_counts[0] - sum(observed_counts[1:]) / 3
    observed_max_gap = max(observed_counts) - min(observed_counts)

    resolved_per_row = [
        sum(r[a].strip().lower() != "unknown" for a in AXES) for r in rows
    ]

    distribution: Counter[tuple[int, int, int, int]] = Counter({(0, 0, 0, 0): 1})
    total_assignments = 1
    for k in resolved_per_row:
        choices = list(itertools.combinations(range(4), k))
        total_assignments *= len(choices)
        updated: Counter[tuple[int, int, int, int]] = Counter()
        for coverage, multiplicity in distribution.items():
            for choice in choices:
                nxt = list(coverage)
                for idx in choice:
                    nxt[idx] += 1
                updated[tuple(nxt)] += multiplicity
        distribution = updated

    if sum(distribution.values()) != total_assignments:
        raise AssertionError("exact ascertainment null enumeration is inconsistent")

    n_a_extreme = 0
    n_gap_extreme = 0
    for coverage, multiplicity in distribution.items():
        a_enrichment = coverage[0] - sum(coverage[1:]) / 3
        gap = max(coverage) - min(coverage)
        if a_enrichment >= observed_a_enrichment - 1e-15:
            n_a_extreme += multiplicity
        if gap >= observed_max_gap:
            n_gap_extreme += multiplicity

    return {
        "observed_axis_coverage": observed,
        "observed_A_minus_mean_other_coverage": observed_a_enrichment,
        "observed_max_minus_min_coverage": observed_max_gap,
        "exact_p_A_enrichment": n_a_extreme / total_assignments,
        "exact_p_any_axis_imbalance": n_gap_extreme / total_assignments,
        "n_exact_axis_assignments": total_assignments,
        "n_distinct_coverage_vectors": len(distribution),
        "resolved_axis_count_per_row": resolved_per_row,
        "null_conditioning": "resolved-axis count per row preserved; axis labels exchangeable under null",
        "method": "exact combinatorial dynamic-programming enumeration",
    }


def summarize(rows: list[dict[str, str]], n_perm: int, seed: int) -> dict[str, object]:
    collapsed = collapse_dependence(rows)
    system_sig_counts = Counter(signature(r) for r in rows)
    cluster_sig_counts = Counter(signature(r) for r in collapsed)
    scale_counts = Counter(r["evidence_scale"] for r in rows)
    taxon_counts = Counter(r["taxon"] for r in rows)

    return {
        "status": "micro_layer_dependence_aware_macro_gate_open",
        "n_biological_systems": len(rows),
        "n_dependence_clusters": len(collapsed),
        "n_taxa_labels": len(taxon_counts),
        "evidence_scales": dict(sorted(scale_counts.items())),
        "system_level_axis_change_counts": {
            axis: direction_summary(rows, axis) for axis in AXES
        },
        "dependence_collapsed_axis_change_counts": {
            axis: direction_summary(collapsed, axis) for axis in AXES
        },
        "system_level_mechanistic_change_signatures": dict(
            sorted(system_sig_counts.items(), key=lambda kv: (-kv[1], kv[0]))
        ),
        "dependence_collapsed_mechanistic_change_signatures": dict(
            sorted(cluster_sig_counts.items(), key=lambda kv: (-kv[1], kv[0]))
        ),
        "system_level_recurrence_sensitivity": permutation_null(rows, n_perm, seed),
        "dependence_collapsed_recurrence_primary": permutation_null(
            collapsed, n_perm, seed
        ),
        "system_level_axis_ascertainment": ascertainment_exact_null(rows),
        "dependence_collapsed_axis_ascertainment": ascertainment_exact_null(collapsed),
        "dependence_clusters": [
            {
                "cluster": r["dependence_cluster"],
                "n_member_systems": int(r["n_member_systems"]),
                "signature": signature(r),
            }
            for r in collapsed
        ],
        "macro_transition_test": {
            "status": "blocked",
            "reason": (
                "accepted-species nuclear-tree branch transitions are not yet an "
                "admitted identifiable input; no macro transition weights are imputed"
            ),
        },
        "degree_preserving_graph_null": {
            "status": "blocked",
            "reason": (
                "explicit mechanistic source/target node states are incomplete in v0.1; "
                "visible-colour labels are forbidden as substitutes"
            ),
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--permutations", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=230223)
    args = ap.parse_args()

    rows = read_rows(args.registry)
    validate(rows)
    summary = summarize(rows, args.permutations, args.seed)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    with (args.out_dir / "summary.json").open("w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    with (args.out_dir / "system_signature_counts.csv").open(
        "w", newline="", encoding="utf-8"
    ) as fh:
        writer = csv.writer(fh)
        writer.writerow(["mechanistic_change_signature", "n_biological_systems"])
        for sig, n in sorted(
            Counter(signature(r) for r in rows).items(),
            key=lambda kv: (-kv[1], kv[0]),
        ):
            writer.writerow([sig, n])

    collapsed = collapse_dependence(rows)
    with (args.out_dir / "dependence_cluster_signatures.csv").open(
        "w", newline="", encoding="utf-8"
    ) as fh:
        writer = csv.writer(fh)
        writer.writerow(["dependence_cluster", "n_member_systems", "signature"])
        for r in collapsed:
            writer.writerow(
                [r["dependence_cluster"], r["n_member_systems"], signature(r)]
            )

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
