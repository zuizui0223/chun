#!/usr/bin/env python3
"""Summarize macro flower-colour/environment evidence without mixing unlike endpoints.

This is deliberately conservative. It does NOT pool effect sizes from studies
that measure different traits (visible red, UV bullseye size, colour disparity,
etc.). Instead it separates the strict causal proxy question
"does stronger floral pigmentation consistently associate with colder/high-UV
niches at macroevolutionary scale?" from broader colour-lability evidence.
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

DIRECT = {
    "macro_support_cold_uv_pigmentation": "support",
    "micro_support_macro_no_support": "null",
    "camellia_counterexample_redness_not_cold_enabler": "oppose",
}


def binom_two_sided(k: int, n: int, p: float = 0.5) -> float:
    if n == 0:
        return float("nan")
    probs = [math.comb(n, i) * p**i * (1-p)**(n-i) for i in range(n+1)]
    pk = probs[k]
    return min(1.0, sum(x for x in probs if x <= pk + 1e-15))


def beta_tail_gt_half(alpha: int, beta: int) -> float:
    # For integer alpha/beta, P(Beta(alpha,beta)>0.5) equals a binomial tail.
    n = alpha + beta - 1
    return sum(math.comb(n, j) * 0.5**n for j in range(alpha, n+1))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    with args.input.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    direct = []
    for r in rows:
        code = r["chun_recoded_direction"].strip()
        if code in DIRECT:
            direct.append((r["study_id"], DIRECT[code]))

    counts = {x: sum(1 for _, y in direct if y == x) for x in ("support", "null", "oppose")}

    # Analysis A: strict test. Null and oppose both count against a universal
    # cold/UV-enabler proposition.
    n_strict = len(direct)
    k_strict = counts["support"]
    alpha_strict = 1 + k_strict
    beta_strict = 1 + (n_strict - k_strict)

    # Analysis B: directional-only sensitivity; remove macro-null but keep
    # explicit counterexamples as opposing evidence.
    n_dir = counts["support"] + counts["oppose"]
    k_dir = counts["support"]
    alpha_dir = 1 + k_dir
    beta_dir = 1 + counts["oppose"]

    out = [
        {
            "analysis": "strict_universal_cold_uv_enabler",
            "n_evidence_units": n_strict,
            "n_support": k_strict,
            "n_null": counts["null"],
            "n_oppose": counts["oppose"],
            "support_fraction": f"{k_strict/n_strict:.6f}" if n_strict else "",
            "exact_two_sided_p_under_0_5": f"{binom_two_sided(k_strict,n_strict):.8f}" if n_strict else "",
            "beta11_p_support_rate_gt_0_5": f"{beta_tail_gt_half(alpha_strict,beta_strict):.8f}",
            "interpretation": "tests whether direct macro evidence consistently supports floral pigmentation as a cold/high-UV enabler; null and counterexample evidence count against universality",
        },
        {
            "analysis": "directional_only_excluding_macro_null",
            "n_evidence_units": n_dir,
            "n_support": k_dir,
            "n_null": 0,
            "n_oppose": counts["oppose"],
            "support_fraction": f"{k_dir/n_dir:.6f}" if n_dir else "",
            "exact_two_sided_p_under_0_5": f"{binom_two_sided(k_dir,n_dir):.8f}" if n_dir else "",
            "beta11_p_support_rate_gt_0_5": f"{beta_tail_gt_half(alpha_dir,beta_dir):.8f}",
            "interpretation": "sensitivity analysis excluding a macro-null radiation but retaining explicit opposing evidence",
        },
        {
            "analysis": "broader_environment_associated_colour_reorganization",
            "n_evidence_units": len(rows),
            "n_support": sum(r["chun_recoded_direction"].startswith("macro_support") for r in rows),
            "n_null": counts["null"],
            "n_oppose": counts["oppose"],
            "support_fraction": "",
            "exact_two_sided_p_under_0_5": "",
            "beta11_p_support_rate_gt_0_5": "",
            "interpretation": "descriptive only: includes heterogeneous endpoints such as colour disparity, pollinator structure and Camellia geography; not pooled statistically",
        },
    ]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fields = list(out[0])
    with args.output.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(out)

    for r in out:
        print(r)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
