#!/usr/bin/env python3
"""Partial-identification bounds for multivariate micro-accessibility recurrence.

The literature-coded dependence clusters contain unresolved A/F/C/P axes. Instead of
imputing expected directions, this script enumerates every admissible completion of
`unknown` entries by {up, down, same}, while keeping observed `mixed` entries fixed.

The output is an identified set / completion-space diagnostic, NOT a posterior
probability distribution. Equal counting of completions is used only to summarize how
much the conclusion depends on unresolved axes; it is not a biological prior over
mechanisms.
"""

from __future__ import annotations

import argparse
import csv
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path

AXES = ("A_change", "F_change", "C_change", "P_change")
COMPLETION_STATES = ("up", "down", "same")


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        raise ValueError("empty micro-accessibility registry")
    return rows


def collapse(rows: list[dict[str, str]]) -> dict[str, list[str]]:
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[row["dependence_cluster"]].append(row)

    out: dict[str, list[str]] = {}
    for cluster, members in sorted(groups.items()):
        sig: list[str] = []
        for axis in AXES:
            known = [m[axis].strip().lower() for m in members if m[axis].strip().lower() != "unknown"]
            if not known:
                sig.append("unknown")
            elif len(set(known)) == 1:
                sig.append(known[0])
            else:
                sig.append("mixed")
        out[cluster] = sig
    return out


def recurrence(signatures: dict[str, list[str]]) -> float:
    counts = Counter(tuple(sig) for sig in signatures.values())
    n = len(signatures)
    return sum((count / n) ** 2 for count in counts.values())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()

    rows = read_rows(args.registry)
    base = collapse(rows)
    unresolved = [
        (cluster, axis_idx)
        for cluster, sig in base.items()
        for axis_idx, value in enumerate(sig)
        if value == "unknown"
    ]
    n_completions = len(COMPLETION_STATES) ** len(unresolved)
    if n_completions > 2_000_000:
        raise ValueError(f"completion space too large for exact enumeration: {n_completions}")

    score_counts: Counter[float] = Counter()
    min_score = float("inf")
    max_score = float("-inf")
    min_example = None
    max_example = None

    for values in itertools.product(COMPLETION_STATES, repeat=len(unresolved)):
        completed = {cluster: list(sig) for cluster, sig in base.items()}
        for (cluster, axis_idx), value in zip(unresolved, values):
            completed[cluster][axis_idx] = value
        score = round(recurrence(completed), 12)
        score_counts[score] += 1
        if score < min_score:
            min_score = score
            min_example = {k: list(v) for k, v in completed.items()}
        if score > max_score:
            max_score = score
            max_example = {k: list(v) for k, v in completed.items()}

    unique_baseline = 1.0 / len(base)
    above_unique = sum(n for score, n in score_counts.items() if score > unique_baseline + 1e-12)
    at_max = score_counts[max_score]

    unknown_by_cluster = {
        cluster: [AXES[i].replace("_change", "") for i, value in enumerate(sig) if value == "unknown"]
        for cluster, sig in base.items()
    }

    summary = {
        "status": "partial_identification_exact_completion_bound",
        "n_dependence_clusters": len(base),
        "n_unresolved_cluster_axes": len(unresolved),
        "completion_states_per_unknown": list(COMPLETION_STATES),
        "n_exact_completions": n_completions,
        "base_dependence_cluster_signatures": {
            k: "|".join(v) for k, v in base.items()
        },
        "unknown_axes_by_cluster": unknown_by_cluster,
        "recurrence_identified_set": {
            "minimum": min_score,
            "maximum": max_score,
            "unique_signature_floor": unique_baseline,
        },
        "completion_space_score_counts": {
            f"{score:.12g}": n for score, n in sorted(score_counts.items())
        },
        "completion_space_fraction_above_unique_floor": above_unique / n_completions,
        "completion_space_fraction_at_maximum": at_max / n_completions,
        "minimum_example": min_example,
        "maximum_example": max_example,
        "interpretation": (
            "Literature-coded multivariate recurrence is not point-identified because unresolved "
            "mechanistic axes permit both fully unique and repeated dependence-cluster signatures."
        ),
        "critical_boundary": (
            "Completion frequencies are combinatorial sensitivity summaries only. They are not "
            "posterior probabilities and do not assume up/down/same are biologically equiprobable."
        ),
        "next_identification_step": (
            "Candidate-free raw RNA-seq resolves unknown axes under one frozen observation protocol, "
            "shrinking the identified set without outcome-directed imputation."
        ),
    }

    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    with (args.out_dir / "recurrence_completion_distribution.csv").open(
        "w", newline="", encoding="utf-8"
    ) as fh:
        writer = csv.writer(fh)
        writer.writerow(["recurrence_score", "n_completions", "fraction_of_completion_space"])
        for score, n in sorted(score_counts.items()):
            writer.writerow([score, n, n / n_completions])

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
