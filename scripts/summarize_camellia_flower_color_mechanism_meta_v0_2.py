#!/usr/bin/env python3
"""Summarize Camellia flower-colour directional evidence with dependence safeguards.

Outputs three descriptive layers per mechanistic question:
1. all study records;
2. public-raw-data study records only;
3. independence-cluster consensus, collapsing repeated work on the same focal taxon/system.

This is not a pooled effect-size model. The purpose is to quantify directional recurrence while
making obvious where repeated publications on C. japonica or C. reticulata would otherwise be
double-counted. A cluster is `mixed` if it contains both yes and no evidence; unclear/NA records
do not determine consensus.
"""
from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path

QUESTIONS = [
    "anthocyanin_more_in_more_red",
    "downstream_anthocyanin_branch_more_active_in_more_red",
    "competing_branch_more_active_in_less_red",
    "within_genotype_or_developmental_switch",
    "regulatory_or_flux_evidence",
    "structural_gene_loss_required",
]


def summarize_values(values: list[str]) -> dict[str, str | int | float]:
    c = Counter(values)
    interpretable = c.get("yes", 0) + c.get("no", 0)
    return {
        "n_records": len(values),
        "n_yes": c.get("yes", 0),
        "n_no": c.get("no", 0),
        "n_unclear": c.get("unclear", 0),
        "n_not_applicable": c.get("not_applicable", 0),
        "n_no_evidence": c.get("no_evidence", 0),
        "n_mixed": c.get("mixed", 0),
        "n_interpretable_yes_no": interpretable,
        "yes_fraction_among_interpretable": (
            f"{c.get('yes', 0) / interpretable:.6f}" if interpretable else ""
        ),
    }


def cluster_consensus(rows: list[dict[str, str]], question: str) -> list[str]:
    by_cluster: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        by_cluster[row["independence_cluster"]].append(row[question])
    consensus = []
    for values in by_cluster.values():
        informative = {v for v in values if v in {"yes", "no"}}
        if informative == {"yes"}:
            consensus.append("yes")
        elif informative == {"no"}:
            consensus.append("no")
        elif informative == {"yes", "no"}:
            consensus.append("mixed")
        elif any(v == "no_evidence" for v in values):
            consensus.append("no_evidence")
        elif any(v == "unclear" for v in values):
            consensus.append("unclear")
        else:
            consensus.append("not_applicable")
    return consensus


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("input", type=Path)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()

    with args.input.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    out: list[dict[str, object]] = []
    for q in QUESTIONS:
        layers = {
            "all_studies": [r[q] for r in rows],
            "public_raw_studies": [r[q] for r in rows if r["raw_status"] == "public"],
            "independence_cluster_consensus": cluster_consensus(rows, q),
        }
        for layer, values in layers.items():
            summary = summarize_values(values)
            out.append({"question": q, "layer": layer, **summary})

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fields = list(out[0].keys())
    with args.output.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(out)


if __name__ == "__main__":
    main()
