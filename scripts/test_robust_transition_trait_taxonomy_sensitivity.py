#!/usr/bin/env python3
"""Sensitivity of robust W->A branches to wild-colour polymorphism/taxonomy audit.

This is deliberately downstream of the frozen rooted94 topology. It does not
change marker recovery, alignment, gene trees, or rooting. It only asks whether
the three PR #44 W->A branches survive after predeclared trait-quality edits:

- strict_wild_taxonomy: ambiguous A/W wild descriptions are missing; known
  duplicate colour observations from synonymized names are missing.
- dominant_wild_taxonomy: 'rare white' taxa can retain dominant A, while true
  A/W alternatives and duplicate synonym observations remain missing.

Mk ER/SYM/ARD models are refit separately for each scenario. Thus sensitivity
is not evaluated using rates estimated from the baseline colour labels.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np
from Bio import Phylo

from analyze_rooted_camellia_colour_history import (
    STATES,
    extract_camellia_crown,
    fit_model,
    norm_name,
    read_colour,
)
from analyze_rooted_camellia_branch_transitions import (
    DIRECTIONS,
    PAIR_TO_NAME,
    Q_from_fit,
    branch_metadata,
    edge_joint_posteriors,
    joint_to_record,
)

TARGET_BRANCHES = ("B011", "B073", "B083")


def read_rows(path: Path):
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def akaike_weights(rows):
    best = min(float(r["AICc"]) for r in rows)
    x = np.array([math.exp(-0.5 * (float(r["AICc"]) - best)) for r in rows], dtype=float)
    x /= x.sum()
    return {r["model"]: float(w) for r, w in zip(rows, x)}


def apply_scenario(base: dict[str, str], audit_rows, scenario: str):
    out = dict(base)
    edits = []
    field = {"strict_wild_taxonomy": "strict_state", "dominant_wild_taxonomy": "dominant_state"}[scenario]
    for r in audit_rows:
        k = norm_name(r["taxon"])
        old = out.get(k, "")
        expected = (r.get("fan_state") or "").strip()
        if expected and old and old != expected:
            raise SystemExit(f"Fan-state audit mismatch for {r['taxon']}: {old} != {expected}")
        new = (r.get(field) or "").strip()
        if new not in {"", "A", "W", "Y"}:
            raise SystemExit(f"bad {field} for {r['taxon']}: {new}")
        if new:
            out[k] = new
        else:
            out.pop(k, None)
        edits.append({
            "taxon": r["taxon"], "scenario": scenario, "old_state": old,
            "new_state": new, "wild_colour_status": r["wild_colour_status"],
            "accepted_species": r["accepted_species"], "taxonomy_action": r["taxonomy_action"],
        })
    return out, edits


def fit_scenario(crown, colour):
    nobs = sum(1 for t in crown.get_terminals() if norm_name(t.name) in colour)
    fits = []
    for mode in ("astral", "unit"):
        for prior in ("equal", "stationary"):
            for model in ("ER", "SYM", "ARD"):
                fits.append(fit_model(crown, model, mode, prior, colour, nobs))
    return nobs, fits


def branch_posteriors(crown, colour, fits):
    branches = branch_metadata(crown, colour)
    by_branch = {b["branch_id"]: {"meta": b, "treatments": {}} for b in branches}
    treatments = sorted({(r["branch_mode"], r["root_prior"]) for r in fits})
    for mode, prior_name in treatments:
        rows = [r for r in fits if r["branch_mode"] == mode and r["root_prior"] == prior_name]
        weights = akaike_weights(rows)
        model_joints = {}
        for r in rows:
            Q = Q_from_fit(r)
            prior = np.array([float(r["prior"][s]) for s in STATES], dtype=float)
            model_joints[r["model"]] = edge_joint_posteriors(crown, Q, mode, prior, colour)
        for b in branches:
            J = np.zeros((3, 3), dtype=float)
            for model, w in weights.items():
                J += w * model_joints[model][b["key"]]
            J /= J.sum()
            rec = joint_to_record(J)
            rec["branch_mode"] = mode
            rec["root_prior"] = prior_name
            by_branch[b["branch_id"]]["treatments"][(mode, prior_name)] = rec
    return by_branch


def summarize_branch(branch_id, bundle):
    meta = {k: v for k, v in bundle["meta"].items() if k != "key"}
    tr = list(bundle["treatments"].values())
    top_dirs = []
    means = {}
    mins = {}
    for d in DIRECTIONS:
        vals = np.array([x[f"p_{d}"] for x in tr], dtype=float)
        means[d] = float(vals.mean())
        mins[d] = float(vals.min())
    for x in tr:
        directional = {d: x[f"p_{d}"] for d in DIRECTIONS}
        top_dirs.append(max(directional, key=directional.get))
    top = max(DIRECTIONS, key=lambda d: means[d])
    strong = len(set(top_dirs)) == 1 and top_dirs[0] == top and mins[top] >= 0.5
    return {
        **meta,
        "branch_id": branch_id,
        "top_direction_by_mean": top,
        "top_direction_same_all_treatments": len(set(top_dirs)) == 1 and top_dirs[0] == top,
        "mean_top_direction_p": means[top],
        "min_top_direction_p": mins[top],
        "strong_robust_endpoint_transition": strong,
        **{f"mean_p_{d}": means[d] for d in DIRECTIONS},
        **{f"min_p_{d}": mins[d] for d in DIRECTIONS},
    }


def taxonomy_audit(path: Path):
    rows = read_rows(path)
    legacy = [r["legacy_tip"] for r in rows]
    accepted = sorted({r["accepted_species"] for r in rows})
    groups = {}
    for r in rows:
        groups.setdefault(r["accepted_species"], []).append(r["legacy_tip"])
    return {
        "legacy_tip_count": len(legacy),
        "accepted_species_group_count": len(accepted),
        "collapse_ratio": len(accepted) / len(legacy),
        "groups": {k: sorted(v) for k, v in sorted(groups.items())},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", type=Path, required=True)
    ap.add_argument("--colour", type=Path, required=True)
    ap.add_argument("--trait-audit", type=Path, required=True)
    ap.add_argument("--b011-taxonomy", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--outgroup", default="Polyspora speciosa")
    a = ap.parse_args()
    a.out_dir.mkdir(parents=True, exist_ok=True)

    tree = Phylo.read(str(a.tree), "newick")
    crown = extract_camellia_crown(tree, a.outgroup)
    if len(crown.get_terminals()) != 93:
        raise SystemExit("rooted crown is not 93 Camellia tips")
    base = read_colour(a.colour)
    audit_rows = read_rows(a.trait_audit)

    scenario_defs = {
        "baseline_fan": base,
    }
    all_edits = []
    for scenario in ("strict_wild_taxonomy", "dominant_wild_taxonomy"):
        c, edits = apply_scenario(base, audit_rows, scenario)
        scenario_defs[scenario] = c
        all_edits.extend(edits)

    scenario_summaries = {}
    branch_rows = []
    fit_rows = []
    for scenario, colour in scenario_defs.items():
        nobs, fits = fit_scenario(crown, colour)
        by_branch = branch_posteriors(crown, colour, fits)
        target = []
        strong_all = []
        for branch_id, bundle in by_branch.items():
            x = summarize_branch(branch_id, bundle)
            x["scenario"] = scenario
            if x["strong_robust_endpoint_transition"]:
                strong_all.append(x)
            if branch_id in TARGET_BRANCHES:
                target.append(x)
                branch_rows.append(x)
        fit_best = {}
        for mode in ("astral", "unit"):
            for prior in ("equal", "stationary"):
                grp = [r for r in fits if r["branch_mode"] == mode and r["root_prior"] == prior]
                b = min(grp, key=lambda r: r["AICc"])
                fit_best[f"{mode}__{prior}"] = {
                    "model": b["model"], "AICc": b["AICc"],
                    "root_top_state": b["root_top_state"],
                    "root_top_probability": b["root_top_probability"],
                }
        for r in fits:
            fit_rows.append({
                "scenario": scenario, "branch_mode": r["branch_mode"], "root_prior": r["root_prior"],
                "model": r["model"], "AICc": r["AICc"], "root_top_state": r["root_top_state"],
                "root_top_probability": r["root_top_probability"],
            })
        scenario_summaries[scenario] = {
            "n_colour_observed": nobs,
            "best_model_by_treatment": fit_best,
            "target_branches": target,
            "n_strong_robust_endpoint_transitions_all_tree": len(strong_all),
            "strong_robust_endpoint_transitions_all_tree": [
                {k: x[k] for k in (
                    "branch_id", "top_direction_by_mean", "min_top_direction_p",
                    "mean_top_direction_p", "n_descendant_tips", "descendant_tips"
                )} for x in strong_all
            ],
        }

    taxonomy = taxonomy_audit(a.b011_taxonomy)
    baseline_target = {x["branch_id"]: x for x in scenario_summaries["baseline_fan"]["target_branches"]}
    strict_target = {x["branch_id"]: x for x in scenario_summaries["strict_wild_taxonomy"]["target_branches"]}
    dominant_target = {x["branch_id"]: x for x in scenario_summaries["dominant_wild_taxonomy"]["target_branches"]}
    retained_strict = [b for b in TARGET_BRANCHES if strict_target[b]["strong_robust_endpoint_transition"]]
    retained_dominant = [b for b in TARGET_BRANCHES if dominant_target[b]["strong_robust_endpoint_transition"]]

    summary = {
        "baseline_target_branches": list(TARGET_BRANCHES),
        "baseline_reproduced": all(baseline_target[b]["strong_robust_endpoint_transition"] for b in TARGET_BRANCHES),
        "strict_retained_target_branches": retained_strict,
        "dominant_retained_target_branches": retained_dominant,
        "b011_taxonomy_audit": taxonomy,
        "scenario_summaries": scenario_summaries,
        "claim_ceiling": "targeted robust-branch trait/taxonomy sensitivity; known audited polymorphism and duplicate colour observations are tested, but this is not yet a full 93-tip accepted-taxonomy tree collapse",
    }
    (a.out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    with (a.out_dir / "target_branch_sensitivity.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(branch_rows[0].keys()))
        w.writeheader(); w.writerows(branch_rows)
    with (a.out_dir / "mk_fit_sensitivity.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(fit_rows[0].keys()))
        w.writeheader(); w.writerows(fit_rows)
    with (a.out_dir / "applied_trait_edits.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(all_edits[0].keys()))
        w.writeheader(); w.writerows(all_edits)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
