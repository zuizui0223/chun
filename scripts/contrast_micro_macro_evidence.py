#!/usr/bin/env python3
"""Contrast recurrence evidence at micro/mechanistic and macro cold-niche scales.

This is an evidence-consistency diagnostic, not an estimate of biological
mechanism frequency. Input evidence units come from selected literatures and
therefore may be publication-biased.
"""

from __future__ import annotations

import argparse
import csv
from fractions import Fraction
from pathlib import Path


def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def beta_gt_beta_a1_vs_33(a: int) -> Fraction:
    """P(X>Y) for X~Beta(a,1), Y~Beta(3,3), exact for integer a.

    F_Beta(3,3)(x) = 10x^3 - 15x^4 + 6x^5.
    f_Beta(a,1)(x) = a*x^(a-1).
    """
    return a * (
        Fraction(10, a + 3)
        - Fraction(15, a + 4)
        + Fraction(6, a + 5)
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--micro", required=True, type=Path)
    ap.add_argument("--macro", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()

    micro = read_csv(args.micro)
    macro = read_csv(args.macro)

    micro_by_q = {r["question"]: r for r in micro}
    strict = next(r for r in macro if r["analysis"] == "strict_universal_cold_uv_enabler")
    if (int(strict["n_support"]), int(strict["n_evidence_units"])) != (2, 4):
        raise SystemExit("strict macro evidence changed; update exact Beta comparison derivation")

    # Beta(1,1) priors. 8/8 -> Beta(9,1); 6/6 -> Beta(7,1);
    # macro 2/4 -> Beta(3,3).
    p_reg = beta_gt_beta_a1_vs_33(9)
    p_anth = beta_gt_beta_a1_vs_33(7)

    # Verify the micro counts against the frozen directional table.
    reg = micro_by_q["regulatory_or_flux_evidence"]
    anth = micro_by_q["anthocyanin_more_in_more_red"]
    if (int(reg["n_support"]), int(reg["n_informative_clusters"])) != (8, 8):
        raise SystemExit("micro regulatory/flux counts changed")
    if (int(anth["n_support"]), int(anth["n_informative_clusters"])) != (6, 6):
        raise SystemExit("micro anthocyanin counts changed")

    rows = [
        {
            "contrast": "micro_regulatory_flux_recurrence_vs_macro_cold_enabler",
            "micro_beta_posterior": "Beta(9,1)",
            "macro_beta_posterior": "Beta(3,3)",
            "p_micro_support_rate_gt_macro_support_rate": f"{float(p_reg):.9f}",
            "exact_fraction": f"{p_reg.numerator}/{p_reg.denominator}",
            "interpretation": "selected evidence is much more consistently recurrent at the mechanistic accessibility layer than as a universal cold/high-UV enabling relationship",
        },
        {
            "contrast": "micro_anthocyanin_direction_vs_macro_cold_enabler",
            "micro_beta_posterior": "Beta(7,1)",
            "macro_beta_posterior": "Beta(3,3)",
            "p_micro_support_rate_gt_macro_support_rate": f"{float(p_anth):.9f}",
            "exact_fraction": f"{p_anth.numerator}/{p_anth.denominator}",
            "interpretation": "red/pink anthocyanin direction is highly recurrent at micro/mechanistic scale but does not translate into a universal macro cold-enabler signal",
        },
    ]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)
    for r in rows:
        print(r)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
