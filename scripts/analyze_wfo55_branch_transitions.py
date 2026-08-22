#!/usr/bin/env python3
"""Branch endpoint-state posteriors on the WFO55 accepted-species colour history."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from Bio import Phylo

from analyze_rooted_camellia_branch_transitions import (
    DIRECTIONS,
    PAIR_TO_NAME,
    Q_from_fit,
    branch_metadata,
    edge_joint_posteriors,
    joint_to_record,
    model_weights,
    read_fit_rows,
)
from analyze_rooted_camellia_colour_history import STATES, extract_camellia_crown, norm_name


def read_seed(path: Path) -> dict[str, str]:
    out = {}
    with path.open(newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            raw = row.get("accepted_species") or row.get("taxon") or ""
            state = (row.get("colour_state") or "").strip()
            if state in STATES:
                key = norm_name(raw)
                if key in out and out[key] != state:
                    raise SystemExit(f"conflicting state for {raw}")
                out[key] = state
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", type=Path, required=True)
    ap.add_argument("--colour", type=Path, required=True)
    ap.add_argument("--fits", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--scenario", required=True)
    ap.add_argument("--outgroup", default="Polyspora speciosa")
    ap.add_argument("--expected-camellia", type=int, default=55)
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    tree = Phylo.read(str(args.tree), "newick")
    crown = extract_camellia_crown(tree, args.outgroup)
    colour = read_seed(args.colour)
    tips = [t for t in crown.get_terminals() if t.name]
    observed = [t for t in tips if norm_name(t.name) in colour]
    if len(tips) != args.expected_camellia:
        raise SystemExit(f"expected {args.expected_camellia} Camellia tips, got {len(tips)}")
    if len(observed) != len(colour):
        raise SystemExit(f"seed/tree overlap mismatch: seed={len(colour)} observed={len(observed)}")

    fits = read_fit_rows(args.fits)
    treatments = sorted({(r["branch_mode"], r["root_prior"]) for r in fits})
    if len(treatments) != 4:
        raise SystemExit(f"expected four treatments, got {treatments}")

    branches = branch_metadata(crown, colour)
    treatment_records = []
    expected_rows = []
    by_branch = {b["branch_id"]: {"meta": b, "treatments": {}} for b in branches}

    for mode, root_prior in treatments:
        rows = [r for r in fits if r["branch_mode"] == mode and r["root_prior"] == root_prior]
        if {r["model"] for r in rows} != {"ER", "SYM", "ARD"}:
            raise SystemExit(f"incomplete model set for {mode}/{root_prior}")
        weights = model_weights(rows)
        model_joints = {}
        for row in rows:
            Q = Q_from_fit(row)
            prior = [float(row["prior"][s]) for s in STATES]
            model_joints[row["model"]] = edge_joint_posteriors(crown, Q, mode, prior, colour)

        totals = {d: 0.0 for d in DIRECTIONS}
        totals["p_change"] = 0.0
        for branch in branches:
            key = branch["key"]
            J = None
            for model, weight in weights.items():
                current = weight * model_joints[model][key]
                J = current if J is None else J + current
            J /= J.sum()
            rec = {k: v for k, v in branch.items() if k != "key"}
            rec.update({"scenario": args.scenario, "branch_mode": mode, "root_prior": root_prior, "model_weights": json.dumps(weights, sort_keys=True)})
            rec.update(joint_to_record(J))
            treatment_records.append(rec)
            by_branch[branch["branch_id"]]["treatments"][(mode, root_prior)] = rec
            totals["p_change"] += rec["p_change"]
            for (i, j), direction in PAIR_TO_NAME.items():
                totals[direction] += float(J[i, j])

        expected_rows.append({"scenario": args.scenario, "branch_mode": mode, "root_prior": root_prior, "n_branches": len(branches), **{f"expected_{k}": float(v) for k, v in totals.items()}})

    with (args.out_dir / "branch_transition_posteriors_by_treatment.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(treatment_records[0]))
        w.writeheader(); w.writerows(treatment_records)

    summary_rows = []
    robust = []
    for branch_id, bundle in by_branch.items():
        meta = {k: v for k, v in bundle["meta"].items() if k != "key"}
        tr = list(bundle["treatments"].values())
        row = {"scenario": args.scenario, **meta}
        row["mean_p_change"] = sum(x["p_change"] for x in tr) / len(tr)
        row["min_p_change"] = min(x["p_change"] for x in tr)
        top_dirs = []
        for x in tr:
            directional = {d: x[f"p_{d}"] for d in DIRECTIONS}
            top_dirs.append(max(directional, key=directional.get))
        for d in DIRECTIONS:
            vals = [x[f"p_{d}"] for x in tr]
            row[f"mean_p_{d}"] = sum(vals) / len(vals)
            row[f"min_p_{d}"] = min(vals)
            row[f"max_p_{d}"] = max(vals)
        mean_dir = max(DIRECTIONS, key=lambda d: row[f"mean_p_{d}"])
        row["top_direction_by_mean"] = mean_dir
        row["top_direction_same_all_treatments"] = len(set(top_dirs)) == 1 and top_dirs[0] == mean_dir
        row["strong_robust_endpoint_transition"] = bool(row["top_direction_same_all_treatments"] and row[f"min_p_{mean_dir}"] >= 0.5)
        if row["strong_robust_endpoint_transition"]:
            robust.append({"branch_id": branch_id, "clade_hash": row["clade_hash"], "direction": mean_dir, "min_direction_p": row[f"min_p_{mean_dir}"], "mean_direction_p": row[f"mean_p_{mean_dir}"], "n_descendant_tips": row["n_descendant_tips"], "descendant_tips": row["descendant_tips"]})
        summary_rows.append(row)

    with (args.out_dir / "branch_transition_robustness.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(summary_rows[0]))
        w.writeheader(); w.writerows(summary_rows)
    with (args.out_dir / "expected_endpoint_transitions_by_treatment.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(expected_rows[0]))
        w.writeheader(); w.writerows(expected_rows)

    direction_counts = {d: sum(1 for x in robust if x["direction"] == d) for d in DIRECTIONS}
    summary = {
        "scenario": args.scenario,
        "n_camellia_tips": len(tips),
        "n_colour_observed": len(observed),
        "n_branches": len(branches),
        "n_treatments": len(treatments),
        "strong_threshold": "same top directional endpoint contrast in all four treatments AND minimum joint posterior >= 0.5",
        "n_strong_robust_endpoint_transitions": len(robust),
        "strong_direction_counts": direction_counts,
        "strong_transitions": robust,
        "claim_ceiling": "accepted-species model-averaged endpoint posteriors only; no ecological or molecular causal assignment",
    }
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
