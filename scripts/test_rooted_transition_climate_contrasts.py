#!/usr/bin/env python3
"""Test whether robust rooted colour transitions coincide with colder lineage contrasts.

This is a public-data boundary gate, not a time-series or causal analysis.
It uses the independently rooted Camellia topology and the already-frozen
model-averaged colour-transition posterior table. Climate is joined only after
those products are fixed.

Primary climate variables are species medians (BIO1 and BIO6). BIO6 q05 is
reported only as a provenance-sensitive diagnostic because earlier project
audits showed that lower-tail occurrence summaries are especially sensitive to
coordinate provenance and sample size.

For each rooted branch, the climate contrast is the median climate of observed
descendant taxa minus the median climate of observed taxa in the branch's local
sister lineage(s). Negative temperature contrasts mean the descendant lineage
is colder than its local sister context. This avoids treating ASTRAL branch
lengths as time.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
from pathlib import Path

import numpy as np
from Bio import Phylo

from analyze_rooted_camellia_colour_history import extract_camellia_crown, norm_name

PRIMARY = ("bio1_median", "bio6_median")
DIAGNOSTIC = ("bio6_q05", "bio1_iqr")
METRICS = PRIMARY + DIAGNOSTIC


def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def fnum(x):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return math.nan
    return v if np.isfinite(v) else math.nan


def read_climate(path: Path):
    out = {}
    for r in read_csv(path):
        k = norm_name(r.get("taxon"))
        if not k:
            continue
        out[k] = {
            "n_points": int(float(r.get("n_points") or 0)),
            **{m: fnum(r.get(m)) for m in METRICS},
        }
    return out


def size_class(n):
    n = int(n)
    if n == 1:
        return "terminal"
    if n <= 5:
        return "small_2_5"
    if n <= 20:
        return "medium_6_20"
    return "large_21plus"


def branch_table(crown, climate):
    rows = []
    idx = 0
    for parent in crown.find_clades(order="preorder"):
        for child in parent.clades:
            idx += 1
            desc = sorted(t.name for t in child.get_terminals() if t.name)
            sister = sorted(
                t.name
                for sib in parent.clades if sib is not child
                for t in sib.get_terminals() if t.name
            )
            digest = hashlib.sha1("|".join(desc).encode()).hexdigest()[:12]
            row = {
                "branch_id": f"B{idx:03d}",
                "clade_hash": digest,
                "n_descendant_tips": len(desc),
                "size_class": size_class(len(desc)),
                "descendant_tips": ";".join(desc),
                "sister_tips": ";".join(sister),
            }
            dk = [norm_name(x) for x in desc]
            sk = [norm_name(x) for x in sister]
            for m in METRICS:
                dv = [climate[k][m] for k in dk if k in climate and np.isfinite(climate[k][m])]
                sv = [climate[k][m] for k in sk if k in climate and np.isfinite(climate[k][m])]
                row[f"n_desc_{m}"] = len(dv)
                row[f"n_sister_{m}"] = len(sv)
                row[f"desc_median_{m}"] = float(np.median(dv)) if dv else math.nan
                row[f"sister_median_{m}"] = float(np.median(sv)) if sv else math.nan
                row[f"contrast_{m}"] = (
                    float(np.median(dv) - np.median(sv)) if dv and sv else math.nan
                )
            rows.append(row)
    return rows


def matched_null(rows, targets, metric, nperm, seed):
    rng = np.random.default_rng(seed)
    eligible = [
        r for r in rows
        if np.isfinite(r[f"contrast_{metric}"])
        and int(r[f"n_desc_{metric}"]) >= 1
        and int(r[f"n_sister_{metric}"]) >= 1
    ]
    by_class = {}
    for r in eligible:
        by_class.setdefault(r["size_class"], []).append(r)

    obs = float(np.mean([r[f"contrast_{metric}"] for r in targets]))
    null = np.empty(nperm, dtype=float)
    target_ids = {r["branch_id"] for r in targets}
    for z in range(nperm):
        chosen = []
        used = set()
        for t in targets:
            pool = [
                r for r in by_class.get(t["size_class"], [])
                if r["branch_id"] not in target_ids and r["branch_id"] not in used
            ]
            if not pool:
                pool = [
                    r for r in eligible
                    if r["branch_id"] not in target_ids and r["branch_id"] not in used
                ]
            if not pool:
                raise SystemExit("insufficient eligible branches for matched null")
            pick = pool[int(rng.integers(0, len(pool)))]
            chosen.append(pick)
            used.add(pick["branch_id"])
        null[z] = np.mean([r[f"contrast_{metric}"] for r in chosen])
    p_colder = float((np.sum(null <= obs) + 1) / (nperm + 1))
    return {
        "observed_mean_contrast": obs,
        "null_mean": float(np.mean(null)),
        "null_sd": float(np.std(null, ddof=1)),
        "matched_branch_p_colder": p_colder,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", type=Path, required=True)
    ap.add_argument("--transitions", type=Path, required=True)
    ap.add_argument("--climate", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--outgroup", default="Polyspora speciosa")
    ap.add_argument("--permutations", type=int, default=100000)
    ap.add_argument("--seed", type=int, default=20260822)
    a = ap.parse_args()
    a.out_dir.mkdir(parents=True, exist_ok=True)

    tree = Phylo.read(str(a.tree), "newick")
    crown = extract_camellia_crown(tree, a.outgroup)
    climate = read_climate(a.climate)
    brow = branch_table(crown, climate)
    if len(crown.get_terminals()) != 93 or len(brow) != 184:
        raise SystemExit(f"unexpected rooted tree: tips={len(crown.get_terminals())} branches={len(brow)}")

    transition_rows = {r["branch_id"]: r for r in read_csv(a.transitions)}
    if len(transition_rows) != 184:
        raise SystemExit(f"expected 184 transition branches, got {len(transition_rows)}")

    merged = []
    for r in brow:
        tr = transition_rows.get(r["branch_id"])
        if tr is None:
            raise SystemExit(f"missing transition row {r['branch_id']}")
        if tr.get("clade_hash") != r["clade_hash"]:
            raise SystemExit(f"branch identity mismatch for {r['branch_id']}")
        z = dict(r)
        for k, v in tr.items():
            if k not in z:
                z[k] = v
        merged.append(z)

    strong = [
        r for r in merged
        if str(r.get("strong_robust_endpoint_transition", "")).lower() == "true"
        and r.get("top_direction_by_mean") == "W_to_A"
    ]
    if len(strong) != 3:
        raise SystemExit(f"expected frozen three robust W->A branches, got {[x['branch_id'] for x in strong]}")

    metric_results = {}
    for i, m in enumerate(METRICS):
        usable = [r for r in strong if np.isfinite(r[f"contrast_{m}"])]
        info = {
            "n_robust_branches_with_contrast": len(usable),
            "branch_contrasts": {r["branch_id"]: float(r[f"contrast_{m}"]) for r in usable},
            "n_colder": sum(float(r[f"contrast_{m}"]) < 0 for r in usable),
            "n_warmer": sum(float(r[f"contrast_{m}"]) > 0 for r in usable),
        }
        if len(usable) == 3:
            info.update(matched_null(merged, usable, m, a.permutations, a.seed + i))
        metric_results[m] = info

    # The hypothesis being tested here is explicitly universal: recurrent W->A
    # realization should consistently move lineages into colder thermal context.
    # One confidently warmer robust branch is enough to reject that universal form.
    complete_primary = all(metric_results[m]["n_robust_branches_with_contrast"] == 3 for m in PRIMARY)
    any_primary_counterexample = any(metric_results[m]["n_warmer"] > 0 for m in PRIMARY)
    both_supported = all(
        metric_results[m].get("n_colder") == 3
        and metric_results[m].get("matched_branch_p_colder", 1.0) < 0.05
        for m in PRIMARY
    )
    if not complete_primary:
        status = "public_data_unidentifiable"
        reason = "one or more robust W->A branches lack local sister contrasts for primary median temperature metrics"
    elif any_primary_counterexample:
        status = "falsified_universal_direct_cold"
        reason = "at least one robust W->A branch is warmer than its local sister context on a primary temperature metric"
    elif both_supported:
        status = "supported"
        reason = "all three robust W->A branches are colder on both median temperature metrics and matched branch nulls are significant"
    else:
        status = "public_data_unidentifiable"
        reason = "direction is compatible with colder shifts but three robust events are insufficient for a decisive matched-branch result"

    fields = list(merged[0].keys())
    with (a.out_dir / "branch_climate_local_contrasts.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(merged)
    with (a.out_dir / "robust_W_to_A_climate_contrasts.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(strong)

    summary = {
        "n_camellia_tips": 93,
        "n_branches": 184,
        "n_public_climate_taxa": len(climate),
        "robust_W_to_A_branches": [r["branch_id"] for r in strong],
        "primary_metrics": list(PRIMARY),
        "diagnostic_only_metrics": list(DIAGNOSTIC),
        "metric_results": metric_results,
        "H_direct_cold_branch_status": status,
        "H_direct_cold_branch_reason": reason,
        "interpretation_boundary": "tests a universal direct thermal-context explanation for the three robust W->A endpoint branches; it does not exclude climate effects on individual branches or flowering-window weather effects mediated by pollination service",
        "provenance_boundary": "BIO6 q05 is diagnostic only because occurrence-tail estimates are provenance/sample-size sensitive in prior project audits; causal classification uses BIO1/BIO6 medians",
        "claim_ceiling": "topology-local public-data climate screen only; no time-calibrated climatic rate, no causal event order, and no pollinator inference",
    }
    (a.out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
