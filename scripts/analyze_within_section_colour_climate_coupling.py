#!/usr/bin/env python3
"""Test whether visible A/W differences mark climatic niche divergence within history proxies.

This is a coarse pre-phylogenetic screen. It uses only traditional sections that
contain both A and W states and only climate axes that are not lower-tail range
estimators: BIO1 median, BIO6 median, and BIO1 IQR.

For each within-section species pair we calculate Euclidean distance in globally
standardized climate space. The statistic is mean distance among different-colour
(A-W) pairs minus mean distance among same-colour (A-A or W-W) pairs. A one-sided
within-section label permutation asks whether different-colour pairs are farther
apart than expected while preserving the observed A/W counts inside each section.

Traditional sections are only a history proxy; this is not a phylogenetic branch
test and cannot establish event ordering.
"""
from __future__ import annotations

import argparse
import csv
import itertools
import json
import re
from pathlib import Path

import numpy as np


def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def norm_section(value: str) -> str:
    parts = []
    for part in str(value or "").split(";"):
        x = re.sub(r"^sect\.\s*", "", part.strip().lower())
        if x and x not in parts:
            parts.append(x)
    return ";".join(sorted(parts))


def pair_stat(rows, z, states, sections, indices):
    same = []
    diff = []
    per_section = {}
    for sec in sorted(set(sections[i] for i in indices)):
        ids = [i for i in indices if sections[i] == sec]
        s_same = []
        s_diff = []
        for i, j in itertools.combinations(ids, 2):
            d = float(np.linalg.norm(z[i] - z[j]))
            if states[i] == states[j]:
                same.append(d); s_same.append(d)
            else:
                diff.append(d); s_diff.append(d)
        per_section[sec] = {
            "n_pairs_same": len(s_same),
            "n_pairs_diff": len(s_diff),
            "mean_same": float(np.mean(s_same)) if s_same else None,
            "mean_diff": float(np.mean(s_diff)) if s_diff else None,
        }
    if not same or not diff:
        raise SystemExit("Need both same-colour and different-colour within-section pairs")
    stat = float(np.mean(diff) - np.mean(same))
    return stat, same, diff, per_section


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--pairs-output", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    ap.add_argument("--permutations", type=int, default=100000)
    ap.add_argument("--seed", type=int, default=20260815)
    args = ap.parse_args()

    rows = [r for r in read_csv(args.input) if r.get("taxon") != "Camellia kissi"]
    rows = [r for r in rows if r.get("colour_state") in {"A", "W"}]
    for r in rows:
        r["section_norm"] = norm_section(r.get("section", ""))

    metrics = ["bio1_median", "bio6_median", "bio1_iqr"]
    x = np.asarray([[float(r[m]) for m in metrics] for r in rows], dtype=float)
    z = (x - x.mean(axis=0)) / x.std(axis=0, ddof=1)
    states = np.asarray([r["colour_state"] for r in rows], dtype=object)
    sections = np.asarray([r["section_norm"] for r in rows], dtype=object)

    shared = sorted(s for s in set(sections) if set(states[sections == s]) == {"A", "W"})
    indices = [i for i, s in enumerate(sections) if s in shared]
    obs, same, diff, per_section = pair_stat(rows, z, states, sections, indices)

    pair_rows = []
    for sec in shared:
        ids = [i for i in indices if sections[i] == sec]
        for i, j in itertools.combinations(ids, 2):
            d = float(np.linalg.norm(z[i] - z[j]))
            pair_rows.append({
                "section": sec,
                "taxon1": rows[i]["taxon"],
                "state1": states[i],
                "taxon2": rows[j]["taxon"],
                "state2": states[j],
                "pair_type": "different_colour" if states[i] != states[j] else "same_colour",
                "climate_distance_core3": f"{d:.10f}",
            })

    rng = np.random.default_rng(args.seed)
    ge = 0
    perm_stats = np.empty(args.permutations, dtype=float)
    for b in range(args.permutations):
        perm = states.copy()
        for sec in shared:
            ids = np.where(sections == sec)[0]
            perm[ids] = rng.permutation(perm[ids])
        ps, _, _, _ = pair_stat(rows, z, perm, sections, indices)
        perm_stats[b] = ps
        if ps >= obs - 1e-15:
            ge += 1
    p_one = (ge + 1) / (args.permutations + 1)
    p_two = (int(np.sum(np.abs(perm_stats) >= abs(obs) - 1e-15)) + 1) / (args.permutations + 1)

    result = [{
        "metric_set": ";".join(metrics),
        "shared_sections": ";".join(shared),
        "n_shared_sections": len(shared),
        "n_species": len(indices),
        "n_A": int(np.sum(states[indices] == "A")),
        "n_W": int(np.sum(states[indices] == "W")),
        "n_same_colour_pairs": len(same),
        "n_different_colour_pairs": len(diff),
        "mean_same_colour_distance": f"{np.mean(same):.10f}",
        "mean_different_colour_distance": f"{np.mean(diff):.10f}",
        "different_minus_same": f"{obs:.10f}",
        "one_sided_p_diff_greater": f"{p_one:.10f}",
        "two_sided_p": f"{p_two:.10f}",
        "permutations": args.permutations,
        "seed": args.seed,
        "claim_ceiling": "traditional-section history-proxy screen; no lower-tail climate estimator; not a nuclear phylogenetic/event-order test",
    }]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(result[0]))
        w.writeheader(); w.writerows(result)
    with args.pairs_output.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(pair_rows[0]))
        w.writeheader(); w.writerows(pair_rows)
    args.summary.write_text(json.dumps({
        "result": result[0],
        "per_section": per_section,
        "interpretation": (
            "different visible-colour pairs are farther apart climatically within shared sections"
            if p_one < 0.05 and obs > 0 else
            "no evidence that visible A/W differences mark greater climatic divergence within shared sections"
        ),
    }, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(json.loads(args.summary.read_text()), indent=2))


if __name__ == "__main__":
    main()
