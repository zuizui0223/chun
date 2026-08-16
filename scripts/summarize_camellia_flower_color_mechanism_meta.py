#!/usr/bin/env python3
"""Summarize the study-level directional Camellia flower-colour evidence table.

This is deliberately not an effect-size meta-analysis. Published studies use incompatible
metabolite units, expression pipelines, contrasts, cultivars/species, and replicate structures.
Each study contributes at most one directional vote per question. The output is intended to
identify repeated mechanistic directions and the data gaps that require raw-data reanalysis.
"""
from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

QUESTIONS = [
    "anthocyanin_more_in_more_red",
    "downstream_anthocyanin_branch_more_active_in_more_red",
    "competing_branch_more_active_in_less_red",
    "within_genotype_or_developmental_switch",
    "regulatory_or_flux_evidence",
    "structural_gene_loss_required",
]


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("input", type=Path)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()

    with args.input.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    out = []
    for q in QUESTIONS:
        counts = Counter(r[q] for r in rows)
        interpretable = counts.get("yes", 0) + counts.get("no", 0)
        out.append({
            "question": q,
            "n_studies_total": len(rows),
            "n_yes": counts.get("yes", 0),
            "n_no": counts.get("no", 0),
            "n_unclear": counts.get("unclear", 0),
            "n_not_applicable": counts.get("not_applicable", 0),
            "n_no_evidence": counts.get("no_evidence", 0),
            "n_interpretable_yes_no": interpretable,
            "yes_fraction_among_interpretable": (
                f"{counts.get('yes', 0) / interpretable:.6f}" if interpretable else ""
            ),
        })

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=out[0].keys())
        writer.writeheader()
        writer.writerows(out)


if __name__ == "__main__":
    main()
