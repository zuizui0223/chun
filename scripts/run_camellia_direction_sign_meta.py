#!/usr/bin/env python3
"""Exact sign synthesis for dependence-collapsed Camellia flower-colour mechanisms.

This script is deliberately descriptive. It asks whether informative independence clusters
show the pre-specified mechanistic direction more often than expected under a symmetric
50:50 directional null. It does NOT estimate the frequency of mechanisms in nature because
the literature is selected, heterogeneous, and enriched for successful colour-mechanism studies.
"""
from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from math import comb, sqrt
from pathlib import Path

TESTS = {
    "anthocyanin_more_in_more_red": ("yes", "higher anthocyanin in the more red/pink state"),
    "downstream_anthocyanin_branch_more_active_in_more_red": ("yes", "stronger downstream anthocyanin deployment in the more-red state"),
    "competing_branch_more_active_in_less_red": ("yes", "stronger competing-branch deployment in the less-red/white/yellow state"),
    "regulatory_or_flux_evidence": ("yes", "regulatory or pathway-flux evidence associated with the colour contrast"),
    "structural_gene_loss_required": ("no", "structural-gene loss is not required for the focal contrast"),
}


def cluster_vote(values: list[str]) -> str:
    informative = {v for v in values if v in {"yes", "no"}}
    if informative == {"yes"}:
        return "yes"
    if informative == {"no"}:
        return "no"
    if informative == {"yes", "no"}:
        return "mixed"
    return "uninformative"


def binom_upper(n: int, k: int) -> float:
    return sum(comb(n, i) for i in range(k, n + 1)) / (2 ** n)


def binom_lower(n: int, k: int) -> float:
    return sum(comb(n, i) for i in range(0, k + 1)) / (2 ** n)


def wilson(successes: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    p = successes / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return centre - half, centre + half


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    with args.input.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    output = []
    for question, (support_value, interpretation) in TESTS.items():
        by_cluster: dict[str, list[str]] = defaultdict(list)
        for row in rows:
            by_cluster[row["independence_cluster"]].append(row[question])
        votes = {cluster: cluster_vote(vals) for cluster, vals in by_cluster.items()}
        informative = {c: v for c, v in votes.items() if v in {"yes", "no"}}
        n = len(informative)
        support = sum(v == support_value for v in informative.values())
        oppose = n - support
        mixed = sum(v == "mixed" for v in votes.values())
        uninformative = sum(v == "uninformative" for v in votes.values())
        lo, hi = wilson(support, n) if n else (float("nan"), float("nan"))
        one = binom_upper(n, support) if n else float("nan")
        lower = binom_lower(n, support) if n else float("nan")
        two = min(1.0, 2 * min(one, lower)) if n else float("nan")
        output.append({
            "question": question,
            "support_direction": support_value,
            "interpretation": interpretation,
            "n_independence_clusters_total": len(votes),
            "n_informative_clusters": n,
            "n_support": support,
            "n_oppose": oppose,
            "n_mixed": mixed,
            "n_uninformative": uninformative,
            "support_fraction": f"{support/n:.6f}" if n else "",
            "wilson95_low": f"{lo:.6f}" if n else "",
            "wilson95_high": f"{hi:.6f}" if n else "",
            "exact_one_sided_p_under_0_5": f"{one:.8f}" if n else "",
            "exact_two_sided_p_under_0_5": f"{two:.8f}" if n else "",
            "inference_scope": "exploratory directional recurrence; not natural mechanism frequency",
        })

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=output[0].keys())
        w.writeheader()
        w.writerows(output)


if __name__ == "__main__":
    main()
