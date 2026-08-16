#!/usr/bin/env python3
"""Robustness analysis for the Camellia flower-colour mechanism meta-analysis.

The analysis deliberately separates:
- independence-cluster consensus;
- a micro-only slice excluding the genus-scale Fan 2026 record;
- public-raw-only evidence;
- comparison-scale coverage;
- leave-one-independence-cluster-out sensitivity.

It quantifies directional recurrence, not natural mechanism frequencies or causal
macroevolutionary transition rates.
"""
from __future__ import annotations

import argparse
import csv
import math
from collections import Counter, defaultdict
from pathlib import Path

QUESTIONS = [
    "anthocyanin_more_in_more_red",
    "downstream_anthocyanin_branch_more_active_in_more_red",
    "competing_branch_more_active_in_less_red",
    "regulatory_or_flux_evidence",
    "structural_gene_loss_required",
]


def scale_bin(scale: str) -> str:
    developmental = {
        "bud_sport_within_lineage",
        "within_genotype_spatial_petal_regions",
        "within_genotype_developmental",
        "within_species_developmental",
        "within_species_colour_variant_developmental",
    }
    within_species = {
        "within_species_between_genotypes_developmental",
        "within_species_between_cultivars",
    }
    between_taxa = {
        "between_species",
        "between_taxa_ornamental_material",
        "between_species_phylogenomic",
    }
    if scale in developmental:
        return "developmental_mosaic"
    if scale in within_species:
        return "within_species_genotype_cultivar"
    if scale in between_taxa:
        return "between_taxa_species"
    return "other"


def consensus_by_cluster(rows: list[dict[str, str]], question: str) -> dict[str, str]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        grouped[row["independence_cluster"]].append(row[question])
    out: dict[str, str] = {}
    for cluster, values in grouped.items():
        informative = {v for v in values if v in {"yes", "no"}}
        if informative == {"yes"}:
            out[cluster] = "yes"
        elif informative == {"no"}:
            out[cluster] = "no"
        elif informative == {"yes", "no"}:
            out[cluster] = "mixed"
        elif any(v == "no_evidence" for v in values):
            out[cluster] = "no_evidence"
        elif any(v == "unclear" for v in values):
            out[cluster] = "unclear"
        else:
            out[cluster] = "not_applicable"
    return out


def two_sided_sign_p(k: int, n: int) -> str:
    if n == 0:
        return ""
    lo = sum(math.comb(n, i) for i in range(0, k + 1)) / (2**n)
    hi = sum(math.comb(n, i) for i in range(k, n + 1)) / (2**n)
    return f"{min(1.0, 2 * min(lo, hi)):.8f}"


def summarize(slice_id: str, rows: list[dict[str, str]], question: str) -> dict[str, object]:
    cons = consensus_by_cluster(rows, question)
    c = Counter(cons.values())
    n = c.get("yes", 0) + c.get("no", 0)
    yes_fraction = c.get("yes", 0) / n if n else None
    return {
        "analysis_slice": slice_id,
        "question": question,
        "n_clusters": len(cons),
        "n_yes": c.get("yes", 0),
        "n_no": c.get("no", 0),
        "n_unclear": c.get("unclear", 0),
        "n_not_applicable": c.get("not_applicable", 0),
        "n_no_evidence": c.get("no_evidence", 0),
        "n_mixed": c.get("mixed", 0),
        "n_interpretable_yes_no": n,
        "yes_fraction_among_interpretable": "" if yes_fraction is None else f"{yes_fraction:.6f}",
        "exact_two_sided_sign_p": two_sided_sign_p(c.get("yes", 0), n),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path)
    ap.add_argument("--summary-output", type=Path, required=True)
    ap.add_argument("--loo-output", type=Path, required=True)
    args = ap.parse_args()

    with args.input.open(newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))

    slices: list[tuple[str, list[dict[str, str]]]] = [
        ("all_independence_clusters", rows),
        ("micro_only_excluding_GENUS_237", [r for r in rows if r["independence_cluster"] != "GENUS_237"]),
        ("public_raw_only", [r for r in rows if r["raw_status"] == "public"]),
    ]
    for b in ("developmental_mosaic", "within_species_genotype_cultivar", "between_taxa_species"):
        slices.append((f"scale_{b}", [r for r in rows if scale_bin(r["contrast_scale"]) == b]))

    summary_rows = [summarize(sid, subset, q) for sid, subset in slices for q in QUESTIONS]
    args.summary_output.parent.mkdir(parents=True, exist_ok=True)
    with args.summary_output.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(summary_rows[0]))
        w.writeheader(); w.writerows(summary_rows)

    clusters = sorted({r["independence_cluster"] for r in rows})
    loo_rows: list[dict[str, object]] = []
    for q in QUESTIONS:
        fracs: list[float] = []
        ns: list[int] = []
        for drop in clusters:
            subset = [r for r in rows if r["independence_cluster"] != drop]
            cons = consensus_by_cluster(subset, q)
            c = Counter(cons.values())
            n = c.get("yes", 0) + c.get("no", 0)
            if n:
                fracs.append(c.get("yes", 0) / n); ns.append(n)
        loo_rows.append({
            "question": q,
            "n_full_clusters": len(clusters),
            "n_leave_one_out_runs": len(clusters),
            "min_interpretable_n": min(ns) if ns else "",
            "max_interpretable_n": max(ns) if ns else "",
            "min_yes_fraction": f"{min(fracs):.6f}" if fracs else "",
            "max_yes_fraction": f"{max(fracs):.6f}" if fracs else "",
            "interpretation": "direction unchanged after dropping any one independence cluster" if fracs and min(fracs) == max(fracs) else "direction/strength changes across leave-one-cluster-out runs",
        })
    with args.loo_output.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(loo_rows[0]))
        w.writeheader(); w.writerows(loo_rows)


if __name__ == "__main__":
    main()
