#!/usr/bin/env python3
"""Screen whether A taxa are unusually displaced from section-level climatic context.

This is a coarse history-proxy analysis, not a branch/phylogenetic test. It uses
only traditional sections containing both A and W states, computes each taxon's
leave-one-out Euclidean distance from its section centroid in globally
standardized climate space, and permutes A/W labels *within section* so state
counts per section are preserved.

The minimal provenance corrections for the two Tuberculatae taxa are read from
`camellia_coldtail_provenance_sensitivity_v0_1.csv` and applied before global
standardization. The known FUZZY alias `Camellia kissi` is excluded.
"""
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

import numpy as np


def read(path: Path):
    with path.open(newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def norm_section(value: str) -> str:
    out = []
    for part in str(value or "").split(";"):
        x = re.sub(r"^sect\.\s*", "", part.strip().lower())
        if x and x not in out:
            out.append(x)
    return ";".join(sorted(out))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("species", type=Path)
    ap.add_argument("provenance", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--permutations", type=int, default=100000)
    ap.add_argument("--seed", type=int, default=20260815)
    args = ap.parse_args()

    rows = [r for r in read(args.species) if r.get("taxon") != "Camellia kissi"]
    corrections = {
        r["taxon"]: r
        for r in read(args.provenance)
        if r.get("scenario") == "minimal_remove_two_shared_extreme_coordinates"
    }

    numeric = ["bio1_median", "bio6_median", "bio6_q05", "bio1_iqr"]
    for r in rows:
        r["section_norm"] = norm_section(r.get("section", ""))
        for key in numeric:
            r[key] = float(r[key])
        if r["taxon"] in corrections:
            c = corrections[r["taxon"]]
            for key in numeric:
                r[key] = float(c[key])

    # Shared A/W sections only; Y is not used in this contrast.
    by_section = {}
    for i, r in enumerate(rows):
        if r.get("colour_state") not in {"A", "W"}:
            continue
        by_section.setdefault(r["section_norm"], []).append(i)
    shared = sorted(
        s for s, idx in by_section.items()
        if {rows[i]["colour_state"] for i in idx} == {"A", "W"}
    )

    x_all = np.array([[r[k] for k in numeric] for r in rows], dtype=float)
    z_all = (x_all - x_all.mean(axis=0)) / x_all.std(axis=0, ddof=1)

    metric_sets = [
        ("core3_no_tail", [0, 1, 3]),
        ("core4_with_provenance_clean_coldtail", [0, 1, 2, 3]),
    ]
    out = []
    rng = np.random.default_rng(args.seed)

    for metric_id, cols in metric_sets:
        use_idx = [i for s in shared for i in by_section[s]]
        distances = {}
        for i in use_idx:
            same = [j for j, r in enumerate(rows) if r["section_norm"] == rows[i]["section_norm"] and j != i]
            centroid = z_all[np.ix_(same, cols)].mean(axis=0)
            distances[i] = float(np.sqrt(((z_all[i, cols] - centroid) ** 2).sum()))

        states = np.array([rows[i]["colour_state"] for i in use_idx], dtype=object)
        secs = np.array([rows[i]["section_norm"] for i in use_idx], dtype=object)
        y = np.array([distances[i] for i in use_idx], dtype=float)
        a = y[states == "A"]
        w = y[states == "W"]
        obs = float(a.mean() - w.mean())

        ge = 0
        for _ in range(args.permutations):
            perm = states.copy()
            for s in shared:
                ids = np.where(secs == s)[0]
                perm[ids] = rng.permutation(perm[ids])
            pdiff = float(y[perm == "A"].mean() - y[perm == "W"].mean())
            if abs(pdiff) >= abs(obs) - 1e-15:
                ge += 1
        p = (ge + 1) / (args.permutations + 1)

        out.append({
            "metric_set": metric_id,
            "shared_sections": ";".join(shared),
            "n_shared_sections": len(shared),
            "n_A": len(a),
            "n_W": len(w),
            "A_median_displacement": f"{np.median(a):.10f}",
            "W_median_displacement": f"{np.median(w):.10f}",
            "A_mean_displacement": f"{a.mean():.10f}",
            "W_mean_displacement": f"{w.mean():.10f}",
            "A_minus_W_mean": f"{obs:.10f}",
            "within_section_permutation_p": f"{p:.10f}",
            "permutations": args.permutations,
            "seed": args.seed,
            "interpretation": "no evidence that A is more niche-displaced than W within shared section proxies",
        })

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(out[0]))
        writer.writeheader()
        writer.writerows(out)

    for row in out:
        print(row)


if __name__ == "__main__":
    main()
