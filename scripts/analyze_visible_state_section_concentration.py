#!/usr/bin/env python3
"""Count-controlled screen for visible-colour concentration among Camellia sections.

This is a coarse historical-structure diagnostic, not a phylogenetic analysis.
It asks whether each visible state occupies fewer/more traditional sections than
expected after preserving the observed number of taxa per state.

The input is the exact-taxonomy GBIF/CHELSA species table. The known FUZZY GBIF
alias ``Camellia kissi`` is excluded so the analysis uses the 50 accepted taxon
units already adopted by the macro-niche audit.
"""
from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

import numpy as np


def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def normalize_section(value: str) -> str:
    parts = []
    for part in str(value or "").split(";"):
        x = part.strip().lower()
        if not x:
            continue
        if x.startswith("sect. "):
            x = x[6:]
        if x not in parts:
            parts.append(x)
    return ";".join(sorted(parts))


def shannon(values) -> float:
    counts = np.array(list(Counter(values).values()), dtype=float)
    p = counts / counts.sum()
    value = float(-(p * np.log(p)).sum())
    return 0.0 if abs(value) < 5e-15 else value


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--permutations", type=int, default=100000)
    ap.add_argument("--seed", type=int, default=20260815)
    args = ap.parse_args()

    rows = [r for r in read_csv(args.input) if r.get("taxon") != "Camellia kissi"]
    rows = [
        r for r in rows
        if r.get("colour_state") in {"A", "W", "Y"}
        and normalize_section(r.get("section", ""))
    ]

    sections = np.array([normalize_section(r["section"]) for r in rows], dtype=object)
    states = np.array([r["colour_state"] for r in rows], dtype=object)
    section_levels = sorted(set(sections))
    sec_index = {s: i for i, s in enumerate(section_levels)}
    sec_i = np.array([sec_index[s] for s in sections], dtype=int)
    state_levels = ["A", "W", "Y"]

    observed = {}
    for state in state_levels:
        vals = sections[states == state]
        observed[state] = {
            "n_species": int(len(vals)),
            "observed_section_breadth": int(len(set(vals))),
            "observed_section_entropy": shannon(vals),
        }

    rng = np.random.default_rng(args.seed)
    b = args.permutations
    breadth = np.empty((b, len(state_levels)), dtype=np.int16)
    entropy = np.empty((b, len(state_levels)), dtype=float)

    for i in range(b):
        permuted = rng.permutation(states)
        for j, state in enumerate(state_levels):
            counts = np.bincount(sec_i[permuted == state], minlength=len(section_levels))
            nz = counts[counts > 0]
            breadth[i, j] = len(nz)
            p = nz / nz.sum()
            entropy[i, j] = float(-(p * np.log(p)).sum())

    out = []
    for j, state in enumerate(state_levels):
        o = observed[state]
        lower_breadth = (
            int(np.sum(breadth[:, j] <= o["observed_section_breadth"])) + 1
        ) / (b + 1)
        lower_entropy = (
            int(np.sum(entropy[:, j] <= o["observed_section_entropy"] + 1e-12)) + 1
        ) / (b + 1)

        if o["n_species"] < 5:
            interpretation = (
                "no count-controlled evidence of unusually low section breadth/entropy; "
                f"n={o['n_species']} is severely underpowered"
            )
        elif lower_breadth < 0.05 and lower_entropy < 0.05:
            interpretation = "state is more section-concentrated than expected for its species count"
        else:
            interpretation = "no count-controlled evidence of unusually low section breadth/entropy"

        out.append({
            "visible_state": state,
            "n_species": o["n_species"],
            "n_observed_sections_total": len(section_levels),
            "observed_section_breadth": o["observed_section_breadth"],
            "expected_section_breadth_under_label_shuffle": f"{float(breadth[:, j].mean()):.5f}",
            "lower_tail_breadth_p": f"{lower_breadth:.10f}",
            "observed_section_entropy": f"{o['observed_section_entropy']:.10f}",
            "expected_section_entropy_under_label_shuffle": f"{float(entropy[:, j].mean()):.10f}",
            "lower_tail_entropy_p": f"{lower_entropy:.10f}",
            "permutations": b,
            "seed": args.seed,
            "interpretation": interpretation,
        })

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)

    for row in out:
        print(row)


if __name__ == "__main__":
    main()
