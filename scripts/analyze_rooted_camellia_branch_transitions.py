#!/usr/bin/env python3
"""Model-averaged branch endpoint-state posteriors for rooted Camellia colour history.

Inputs are downstream products of the already-frozen rooted94 tree and PR #43
visible-colour history gate. No ecological variable enters this analysis.

For each of the four branch-length/root-prior treatments, AICc weights are used
to average ER/SYM/ARD Mk models. For every Camellia crown edge, the script
computes the posterior joint distribution of parent and child endpoint states.
The result preserves W/A/Y uncertainty rather than hard-calling transitions.

Important: endpoint-state differences are not counts of hidden changes within a
branch and ASTRAL branch lengths are not interpreted as time.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from Bio import Phylo
from scipy.linalg import expm

from analyze_rooted_camellia_colour_history import (
    STATES,
    SINDEX,
    edge_length,
    extract_camellia_crown,
    norm_name,
    qmatrix,
    read_colour,
)

DIRECTIONS = (
    "A_to_W", "A_to_Y", "W_to_A", "W_to_Y", "Y_to_A", "Y_to_W"
)
PAIR_TO_NAME = {
    (0, 1): "A_to_W", (0, 2): "A_to_Y",
    (1, 0): "W_to_A", (1, 2): "W_to_Y",
    (2, 0): "Y_to_A", (2, 1): "Y_to_W",
}
RATE_ORDER = {
    "ER": ["all"],
    "SYM": ["A_W", "A_Y", "W_Y"],
    "ARD": ["A_to_W", "A_to_Y", "W_to_A", "W_to_Y", "Y_to_A", "Y_to_W"],
}


def read_fit_rows(path: Path):
    out = []
    with path.open(newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            r = dict(r)
            r["AICc"] = float(r["AICc"])
            r["rates"] = json.loads(r["rates"])
            r["prior"] = json.loads(r["prior"])
            out.append(r)
    return out


def model_weights(rows):
    best = min(r["AICc"] for r in rows)
    raw = np.array([math.exp(-0.5 * (r["AICc"] - best)) for r in rows], dtype=float)
    raw /= raw.sum()
    return {r["model"]: float(w) for r, w in zip(rows, raw)}


def Q_from_fit(row):
    names = RATE_ORDER[row["model"]]
    rates = np.array([float(row["rates"][x]) for x in names], dtype=float)
    if np.any(rates <= 0) or not np.isfinite(rates).all():
        raise SystemExit(f"invalid fitted rates for {row['model']}: {rates}")
    return qmatrix(row["model"], np.log(rates))


def normalize(v):
    s = float(np.sum(v))
    if not np.isfinite(s) or s <= 0:
        raise FloatingPointError(f"invalid message normalization: {v}")
    return np.asarray(v, dtype=float) / s


def upward_messages(root, Q, mode, colour):
    up = {}
    trans = {}
    for node in root.find_clades(order="postorder"):
        if node.is_terminal():
            state = colour.get(norm_name(node.name))
            if state:
                v = np.zeros(3, dtype=float)
                v[SINDEX[state]] = 1.0
            else:
                v = np.ones(3, dtype=float)
            up[node] = normalize(v)
            continue
        v = np.ones(3, dtype=float)
        for child in node.clades:
            P = expm(Q * edge_length(child, mode))
            trans[(node, child)] = P
            v *= P @ up[child]
        up[node] = normalize(v)
    return up, trans


def edge_joint_posteriors(root, Q, mode, prior, colour):
    up, trans = upward_messages(root, Q, mode, colour)
    outside = {root: normalize(np.asarray(prior, dtype=float))}
    joints = {}
    for parent in root.find_clades(order="preorder"):
        if not parent.clades:
            continue
        contrib = {}
        for child in parent.clades:
            P = trans[(parent, child)]
            contrib[child] = P @ up[child]
        for child in parent.clades:
            base = outside[parent].copy()
            for sibling in parent.clades:
                if sibling is not child:
                    base *= contrib[sibling]
            P = trans[(parent, child)]
            raw = base[:, None] * P * up[child][None, :]
            z = float(raw.sum())
            if not np.isfinite(z) or z <= 0:
                raise FloatingPointError("invalid edge joint posterior")
            joints[(parent, child)] = raw / z
            outside_child = base @ P
            outside[child] = normalize(outside_child)
    return joints


def branch_metadata(root, colour):
    out = []
    idx = 0
    for parent in root.find_clades(order="preorder"):
        for child in parent.clades:
            idx += 1
            tips = sorted(t.name for t in child.get_terminals() if t.name)
            observed = [colour.get(norm_name(x)) for x in tips]
            observed = [x for x in observed if x]
            counts = {s: observed.count(s) for s in STATES}
            digest = hashlib.sha1("|".join(tips).encode()).hexdigest()[:12]
            out.append({
                "key": (parent, child),
                "branch_id": f"B{idx:03d}",
                "clade_hash": digest,
                "n_descendant_tips": len(tips),
                "n_descendant_colour_observed": len(observed),
                "descendant_A": counts["A"],
                "descendant_W": counts["W"],
                "descendant_Y": counts["Y"],
                "descendant_tips": ";".join(tips),
            })
    return out


def joint_to_record(J):
    rec = {}
    for i, a in enumerate(STATES):
        for j, b in enumerate(STATES):
            rec[f"p_{a}_to_{b}"] = float(J[i, j])
    rec["p_no_change"] = float(np.trace(J))
    rec["p_change"] = float(1.0 - np.trace(J))
    for i, s in enumerate(STATES):
        rec[f"parent_p_{s}"] = float(J[i, :].sum())
        rec[f"child_p_{s}"] = float(J[:, i].sum())
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", type=Path, required=True)
    ap.add_argument("--colour", type=Path, required=True)
    ap.add_argument("--fits", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--outgroup", default="Polyspora speciosa")
    a = ap.parse_args()
    a.out_dir.mkdir(parents=True, exist_ok=True)

    tree = Phylo.read(str(a.tree), "newick")
    crown = extract_camellia_crown(tree, a.outgroup)
    colour = read_colour(a.colour)
    tips = [t for t in crown.get_terminals() if t.name]
    observed = [t for t in tips if norm_name(t.name) in colour]
    if len(tips) != 93 or len(observed) != 45:
        raise SystemExit(f"unexpected frozen overlap: tips={len(tips)} observed={len(observed)}")

    fits = read_fit_rows(a.fits)
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
        for r in rows:
            Q = Q_from_fit(r)
            prior = np.array([float(r["prior"][s]) for s in STATES], dtype=float)
            model_joints[r["model"]] = edge_joint_posteriors(crown, Q, mode, prior, colour)

        totals = {d: 0.0 for d in DIRECTIONS}
        totals["p_change"] = 0.0
        for b in branches:
            key = b["key"]
            J = np.zeros((3, 3), dtype=float)
            for model, w in weights.items():
                J += w * model_joints[model][key]
            J /= J.sum()
            rec = {k: v for k, v in b.items() if k != "key"}
            rec.update({
                "branch_mode": mode,
                "root_prior": root_prior,
                "model_weights": json.dumps(weights, sort_keys=True),
            })
            rec.update(joint_to_record(J))
            treatment_records.append(rec)
            by_branch[b["branch_id"]]["treatments"][(mode, root_prior)] = rec
            totals["p_change"] += rec["p_change"]
            for (i, j), d in PAIR_TO_NAME.items():
                totals[d] += float(J[i, j])

        expected_rows.append({
            "branch_mode": mode,
            "root_prior": root_prior,
            "n_branches": len(branches),
            **{f"expected_{k}": float(v) for k, v in totals.items()},
        })

    treatment_fields = list(treatment_records[0].keys())
    with (a.out_dir / "branch_transition_posteriors_by_treatment.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=treatment_fields)
        w.writeheader(); w.writerows(treatment_records)

    summary_rows = []
    robust = []
    for branch_id, bundle in by_branch.items():
        meta = {k: v for k, v in bundle["meta"].items() if k != "key"}
        tr = list(bundle["treatments"].values())
        row = dict(meta)
        row["mean_p_change"] = float(np.mean([x["p_change"] for x in tr]))
        row["min_p_change"] = float(np.min([x["p_change"] for x in tr]))
        top_dirs = []
        for x in tr:
            vals = {d: x[f"p_{d.replace('_to_', '_to_')}"] if False else None for d in []}
            directional = {
                "A_to_W": x["p_A_to_W"], "A_to_Y": x["p_A_to_Y"],
                "W_to_A": x["p_W_to_A"], "W_to_Y": x["p_W_to_Y"],
                "Y_to_A": x["p_Y_to_A"], "Y_to_W": x["p_Y_to_W"],
            }
            top_dirs.append(max(directional, key=directional.get))
        for d in DIRECTIONS:
            key = f"p_{d}"
            vals = np.array([x[key] for x in tr], dtype=float)
            row[f"mean_{key}"] = float(vals.mean())
            row[f"min_{key}"] = float(vals.min())
            row[f"max_{key}"] = float(vals.max())
        mean_dir = max(DIRECTIONS, key=lambda d: row[f"mean_p_{d}"])
        row["top_direction_by_mean"] = mean_dir
        row["top_direction_same_all_treatments"] = len(set(top_dirs)) == 1 and top_dirs[0] == mean_dir
        row["strong_robust_endpoint_transition"] = bool(
            row["top_direction_same_all_treatments"] and row[f"min_p_{mean_dir}"] >= 0.5
        )
        if row["strong_robust_endpoint_transition"]:
            robust.append({
                "branch_id": branch_id,
                "direction": mean_dir,
                "min_direction_p": row[f"min_p_{mean_dir}"],
                "mean_direction_p": row[f"mean_p_{mean_dir}"],
                "n_descendant_tips": row["n_descendant_tips"],
                "descendant_tips": row["descendant_tips"],
            })
        summary_rows.append(row)

    summary_fields = list(summary_rows[0].keys())
    with (a.out_dir / "branch_transition_robustness.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=summary_fields)
        w.writeheader(); w.writerows(summary_rows)

    with (a.out_dir / "expected_endpoint_transitions_by_treatment.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(expected_rows[0].keys()))
        w.writeheader(); w.writerows(expected_rows)

    direction_counts = {d: sum(1 for x in robust if x["direction"] == d) for d in DIRECTIONS}
    summary = {
        "n_camellia_tips": len(tips),
        "n_colour_observed": len(observed),
        "n_branches": len(branches),
        "n_treatments": len(treatments),
        "strong_threshold": "same top directional endpoint contrast in all four treatments AND minimum joint posterior >= 0.5",
        "n_strong_robust_endpoint_transitions": len(robust),
        "strong_direction_counts": direction_counts,
        "strong_transitions": robust,
        "claim_ceiling": "model-averaged parent/child endpoint-state posteriors only; not hidden within-branch event counts, not time-calibrated rates, and no ecological or molecular causal assignment",
    }
    (a.out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
