#!/usr/bin/env python3
"""Deterministic first-pass analysis of the micro-accessibility registry.

This script intentionally does not infer macroevolutionary transition rates. It audits
independence, summarizes recurrent mechanistic change vectors, and constructs a
minimal directed state graph only where mechanistic source/target state labels are
explicitly provided in a future registry revision.

The v0.1 null layer tests whether the observed recurrence of mechanistic change
classes exceeds a label-permutation null while preserving the number of independent
biological systems. A degree-preserving graph null is gated until explicit
mechanistic node states are sufficiently complete.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

AXES = ("A_change", "F_change", "C_change", "P_change")
VALID_CHANGE = {"up", "down", "same", "unknown"}


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

    independence = [r["independence_unit"] for r in rows]
    if len(independence) != len(set(independence)):
        raise ValueError(
            "v0.1 registry must contain one row per independence unit; "
            "correlated outcomes must be collapsed before analysis"
        )

    for row in rows:
        for axis in AXES:
            value = row[axis].strip().lower()
            if value not in VALID_CHANGE:
                raise ValueError(f"{row['edge_id']}: invalid {axis}={value!r}")
        if row["direction_status"] != "directed":
            raise ValueError(f"{row['edge_id']}: v0.1 only admits directed edges")


def signature(row: dict[str, str]) -> str:
    return "|".join(row[a].strip().lower() for a in AXES)


def recurrence_score(counts: Counter[str]) -> float:
    """Concentration of independent systems among observed change signatures.

    Sum p_k^2 is the probability that two randomly drawn independent systems share
    the same mechanistic change signature. It is descriptive and bounded [0, 1].
    """
    n = sum(counts.values())
    return sum((c / n) ** 2 for c in counts.values())


def permutation_null(rows: list[dict[str, str]], n_perm: int, seed: int) -> dict[str, object]:
    """Break cross-axis coupling while preserving each axis' marginal frequencies.

    Each permutation independently shuffles A/F/C/P change labels across biological
    systems. This preserves sample size and the marginal number of up/down/unknown
    calls on every axis while destroying recurrent multi-axis mechanistic packages.
    """
    rng = random.Random(seed)
    observed = Counter(signature(r) for r in rows)
    observed_score = recurrence_score(observed)

    axis_values = {axis: [r[axis].strip().lower() for r in rows] for axis in AXES}
    null_scores: list[float] = []

    for _ in range(n_perm):
        shuffled = {}
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
    var_null = sum((v - mean_null) ** 2 for v in null_scores) / max(1, len(null_scores) - 1)
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


def summarize(rows: list[dict[str, str]], n_perm: int, seed: int) -> dict[str, object]:
    sig_counts = Counter(signature(r) for r in rows)
    axis_counts = {axis: Counter(r[axis].strip().lower() for r in rows) for axis in AXES}
    scale_counts = Counter(r["evidence_scale"] for r in rows)
    taxon_counts = Counter(r["taxon"] for r in rows)

    anth_up = sum(r["A_change"].strip().lower() == "up" for r in rows)
    anth_down = sum(r["A_change"].strip().lower() == "down" for r in rows)
    anth_known = anth_up + anth_down + sum(
        r["A_change"].strip().lower() == "same" for r in rows
    )

    return {
        "status": "micro_layer_only_macro_gate_open",
        "n_independent_systems": len(rows),
        "n_taxa": len(taxon_counts),
        "evidence_scales": dict(sorted(scale_counts.items())),
        "axis_change_counts": {
            a: dict(sorted(c.items())) for a, c in axis_counts.items()
        },
        "mechanistic_change_signatures": dict(
            sorted(sig_counts.items(), key=lambda kv: (-kv[1], kv[0]))
        ),
        "anthocyanin_direction": {
            "known_rows": anth_known,
            "up": anth_up,
            "down": anth_down,
        },
        "cross_axis_recurrence_null": permutation_null(rows, n_perm, seed),
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

    with (args.out_dir / "signature_counts.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["mechanistic_change_signature", "n_independent_systems"])
        for sig, n in sorted(
            Counter(signature(r) for r in rows).items(),
            key=lambda kv: (-kv[1], kv[0]),
        ):
            writer.writerow([sig, n])

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
