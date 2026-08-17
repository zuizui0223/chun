#!/usr/bin/env python3
"""Quantify uncertainty and adversarial robustness of directional mechanism recurrence.

This analysis operates on independence-cluster consensus, not publication records.
A Beta(1,1) posterior is used only as a transparent uncertainty summary for the
selected evidence base; it is explicitly not interpreted as a natural Camellia
transition-frequency posterior because the literature is ascertained.
"""
from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path

from scipy.stats import beta

QUESTIONS = [
    "anthocyanin_more_in_more_red",
    "downstream_anthocyanin_branch_more_active_in_more_red",
    "competing_branch_more_active_in_less_red",
    "regulatory_or_flux_evidence",
    "structural_gene_loss_required",
]

CLAIM_BOUNDARY = {
    "anthocyanin_more_in_more_red": "directional recurrence only; literature ascertained, not natural frequency",
    "downstream_anthocyanin_branch_more_active_in_more_red": "directional but underpowered; effect size/heterogeneity still needed",
    "competing_branch_more_active_in_less_red": "directional recurrence only; module effect size still needed",
    "regulatory_or_flux_evidence": "strongest robustness result; not a natural transition-frequency estimate",
    "structural_gene_loss_required": "too few explicitly informative clusters to infer genus-wide loss frequency",
}


def consensus(values: list[str]) -> str:
    informative = {v for v in values if v in {"yes", "no"}}
    if informative == {"yes"}:
        return "yes"
    if informative == {"no"}:
        return "no"
    if informative == {"yes", "no"}:
        return "mixed"
    if any(v == "no_evidence" for v in values):
        return "no_evidence"
    if any(v == "unclear" for v in values):
        return "unclear"
    return "not_applicable"


def exact_sign_p(n_yes: int, n_no: int) -> float | None:
    n = n_yes + n_no
    if not n:
        return None
    k = min(n_yes, n_no)
    p = 2.0 * sum(math.comb(n, i) for i in range(k + 1)) / (2**n)
    return min(1.0, p)


def opposing_to_nonsig(n_yes: int, n_no: int) -> tuple[int, float | None]:
    m = 0
    while True:
        p = exact_sign_p(n_yes, n_no + m)
        if p is None or p >= 0.05:
            return m, p
        m += 1


def opposing_to_posterior_below(n_yes: int, n_no: int, threshold: float = 0.95) -> tuple[int, float]:
    m = 0
    while True:
        a = 1 + n_yes
        b = 1 + n_no + m
        p = 1.0 - beta.cdf(0.5, a, b)
        if p < threshold:
            return m, p
        m += 1


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    with args.input.open(newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))

    by_cluster: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_cluster[row["independence_cluster"]].append(row)

    out = []
    for q in QUESTIONS:
        states = [consensus([r[q] for r in rs]) for rs in by_cluster.values()]
        n_yes = sum(x == "yes" for x in states)
        n_no = sum(x == "no" for x in states)
        a, b = 1 + n_yes, 1 + n_no
        lo, hi = beta.ppf([0.025, 0.975], a, b)
        m_sign, p_after_sign = opposing_to_nonsig(n_yes, n_no)
        m_post, p_after_post = opposing_to_posterior_below(n_yes, n_no)
        out.append(
            {
                "question": q,
                "n_yes": n_yes,
                "n_no": n_no,
                "exact_two_sided_sign_p": exact_sign_p(n_yes, n_no),
                "beta11_posterior_mean": a / (a + b),
                "beta11_ci025": lo,
                "beta11_ci975": hi,
                "posterior_p_recurrence_gt_0_5": 1.0 - beta.cdf(0.5, a, b),
                "posterior_p_recurrence_gt_0_75": 1.0 - beta.cdf(0.75, a, b),
                "opposing_clusters_to_sign_p_ge_0_05": m_sign,
                "sign_p_after_that_many_opposing": p_after_sign,
                "opposing_clusters_to_p_gt_half_below_0_95": m_post,
                "p_gt_half_after_that_many_opposing": p_after_post,
                "claim_boundary": CLAIM_BOUNDARY[q],
            }
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fields = list(out[0])
    with args.output.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for row in out:
            formatted = dict(row)
            for key, value in list(formatted.items()):
                if isinstance(value, float):
                    formatted[key] = f"{value:.8f}"
            w.writerow(formatted)


if __name__ == "__main__":
    main()
