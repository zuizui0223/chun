#!/usr/bin/env python3
"""Small dependence-aware diagnostic for Camellia pollination-function evidence.

This is deliberately NOT an effect-size meta-analysis. Published studies use
incommensurable designs (exclusion, hand-pollination, behavioral choice,
single-visit deposition, seasonal comparison). The script asks only:

1. Is human-visible W/A/Y a deterministic pollinator-functional state?
2. Is there detectable association between coarse hue and broad pollinator class
   in the current primary-evidence seed?
3. How often does the same species show environment/season-dependent reproductive
   niche modulation while visible hue is unchanged?

The seed is small and literature-availability ascertained, so exact tests are
reported as diagnostics, not natural frequencies.
"""
from __future__ import annotations

import argparse
import csv
import itertools
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def mutual_information(hues, funcs):
    n = len(hues)
    hc = Counter(hues)
    fc = Counter(funcs)
    jc = Counter(zip(hues, funcs))
    out = 0.0
    for (h, f), c in jc.items():
        out += (c / n) * math.log((c * n) / (hc[h] * fc[f]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path)
    ap.add_argument("--summary-output", type=Path, required=True)
    ap.add_argument("--hue-output", type=Path, required=True)
    args = ap.parse_args()

    rows = read_csv(args.input)
    hues = [r["visible_state"] for r in rows]
    funcs = [r["pollinator_function_class"] for r in rows]

    observed_mi = mutual_information(hues, funcs)
    # Enumerate the exact unique assignments preserving pollinator-class totals.
    unique_assignments = set(itertools.permutations(funcs))
    null_mi = [mutual_information(hues, list(p)) for p in unique_assignments]
    exact_p = sum(v >= observed_mi - 1e-15 for v in null_mi) / len(null_mi)

    by_hue = defaultdict(list)
    for r in rows:
        by_hue[r["visible_state"]].append(r)

    hue_rows = []
    n_multitaxon = 0
    n_heterogeneous = 0
    for hue in sorted(by_hue):
        rr = by_hue[hue]
        classes = sorted(set(r["pollinator_function_class"] for r in rr))
        if len(rr) >= 2:
            n_multitaxon += 1
            if len(classes) > 1:
                n_heterogeneous += 1
        hue_rows.append({
            "visible_state": hue,
            "n_taxa": len(rr),
            "n_pollinator_function_classes": len(classes),
            "pollinator_function_classes": ";".join(classes),
            "deterministic_within_current_seed": "yes" if len(classes) == 1 else "no",
            "taxa": ";".join(r["taxon"] for r in rr),
        })

    modulation = [r for r in rows if r.get("environmental_or_seasonal_modulation", "") not in {"", "not_tested"}]
    spectral = [r for r in rows if r.get("spectral_or_sensory_evidence", "") not in {"", "none_in_this_source"}]

    summary = {
        "n_taxa": len(rows),
        "visible_state_counts": dict(Counter(hues)),
        "pollinator_function_counts": dict(Counter(funcs)),
        "mutual_information_nats": observed_mi,
        "exact_unique_label_assignments": len(unique_assignments),
        "exact_association_p": exact_p,
        "n_multitaxon_visible_states": n_multitaxon,
        "n_multitaxon_visible_states_with_functional_heterogeneity": n_heterogeneous,
        "fraction_multitaxon_visible_states_heterogeneous": n_heterogeneous / n_multitaxon if n_multitaxon else None,
        "n_taxa_with_environment_or_season_pollinator_modulation": len(modulation),
        "modulation_taxa": [r["taxon"] for r in modulation],
        "n_taxa_with_direct_spectral_or_sensory_evidence": len(spectral),
        "spectral_taxa": [r["taxon"] for r in spectral],
        "interpretation": (
            "visible hue is not a deterministic pollinator-functional state in the current seed; "
            "the exact hue-function association is not resolved with the small literature-ascertained sample; "
            "environment/season can alter reproductive-niche use without visible hue change"
        ),
        "claim_ceiling": (
            "diagnostic synthesis of heterogeneous primary studies; not an effect-size meta-analysis, "
            "not a natural-frequency estimate, and not phylogenetically corrected"
        ),
    }

    args.summary_output.parent.mkdir(parents=True, exist_ok=True)
    args.summary_output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    with args.hue_output.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(hue_rows[0]))
        w.writeheader(); w.writerows(hue_rows)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
