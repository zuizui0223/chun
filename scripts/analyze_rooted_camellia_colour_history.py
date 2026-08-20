#!/usr/bin/env python3
"""Held-out visible-colour history sensitivity on a frozen rooted Camellia tree.

The nuclear tree must already be rooted independently with Polyspora. Visible
colour is joined only in this script. Missing Camellia tips remain unobserved.

This gate deliberately compares:
- Fitch parsimony root-state set;
- continuous-time 3-state Mk ER, SYM and ARD models;
- ASTRAL substitution-per-site branch lengths versus unit edge lengths;
- equal versus model-stationary root priors.

It does not treat ASTRAL branch lengths as divergence time and does not test
climate/pollinator causation.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
from pathlib import Path

import numpy as np
from Bio import Phylo
from scipy.linalg import expm
from scipy.optimize import minimize

STATES = ("A", "W", "Y")
SINDEX = {s: i for i, s in enumerate(STATES)}


def norm_name(x: str | None) -> str:
    return re.sub(r"\s+", " ", (x or "").strip().replace("_", " ")).casefold()


def read_colour(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    with path.open(newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            k = norm_name(r.get("taxon"))
            s = (r.get("colour_state") or "").strip()
            if k and s in SINDEX:
                if k in out and out[k] != s:
                    raise SystemExit(f"conflicting colour state for {k}: {out[k]} vs {s}")
                out[k] = s
    return out


def extract_camellia_crown(tree, outgroup: str):
    ok = norm_name(outgroup)
    children = list(tree.root.clades)
    containing = []
    for c in children:
        tips = {norm_name(t.name) for t in c.get_terminals() if t.name}
        containing.append(ok in tips)
    if containing.count(True) != 1:
        raise SystemExit(f"outgroup must occur in exactly one root child: {containing}")
    cam = children[1 - containing.index(True)] if len(children) == 2 else None
    if cam is None:
        candidates = [c for c, has in zip(children, containing) if not has]
        if len(candidates) != 1:
            raise SystemExit("expected exactly one Camellia crown child")
        cam = candidates[0]
    tips = [t for t in cam.get_terminals() if t.name]
    if any(not norm_name(t.name).startswith("camellia ") for t in tips):
        bad = [t.name for t in tips if not norm_name(t.name).startswith("camellia ")]
        raise SystemExit(f"non-Camellia tips inside crown: {bad[:10]}")
    return cam


def fitch(clade, colour: dict[str, str]):
    if clade.is_terminal():
        s = colour.get(norm_name(clade.name))
        return ({s} if s else set(STATES)), 0
    current = None
    changes = 0
    for ch in clade.clades:
        cs, cc = fitch(ch, colour)
        changes += cc
        if current is None:
            current = set(cs)
        else:
            inter = current & cs
            if inter:
                current = inter
            else:
                current |= cs
                changes += 1
    return current if current is not None else set(STATES), changes


def qmatrix(model: str, log_rates: np.ndarray) -> np.ndarray:
    r = np.exp(log_rates)
    Q = np.zeros((3, 3), dtype=float)
    if model == "ER":
        Q[:] = r[0]
        np.fill_diagonal(Q, 0.0)
    elif model == "SYM":
        aw, ay, wy = r
        Q[0, 1] = Q[1, 0] = aw
        Q[0, 2] = Q[2, 0] = ay
        Q[1, 2] = Q[2, 1] = wy
    elif model == "ARD":
        aw, ay, wa, wy, ya, yw = r
        Q[0, 1], Q[0, 2] = aw, ay
        Q[1, 0], Q[1, 2] = wa, wy
        Q[2, 0], Q[2, 1] = ya, yw
    else:
        raise ValueError(model)
    for i in range(3):
        Q[i, i] = -float(Q[i].sum())
    return Q


def stationary(Q: np.ndarray) -> np.ndarray:
    vals, vecs = np.linalg.eig(Q.T)
    v = np.real(vecs[:, np.argmin(np.abs(vals))])
    if np.all(v <= 0):
        v = -v
    v = np.maximum(v, 0)
    if not np.isfinite(v).all() or v.sum() <= 0:
        raise FloatingPointError("failed to obtain stationary distribution")
    return v / v.sum()


def edge_length(clade, mode: str) -> float:
    if mode == "unit":
        return 1.0
    x = clade.branch_length
    if x is None or not np.isfinite(x) or x <= 0:
        return 1e-8
    return float(x)


def pruning_vector(clade, Q: np.ndarray, mode: str, colour: dict[str, str]):
    if clade.is_terminal():
        s = colour.get(norm_name(clade.name))
        if s:
            v = np.zeros(3, dtype=float)
            v[SINDEX[s]] = 1.0
            return v, 0.0
        return np.ones(3, dtype=float), 0.0

    v = np.ones(3, dtype=float)
    log_scale = 0.0
    for ch in clade.clades:
        cv, cs = pruning_vector(ch, Q, mode, colour)
        P = expm(Q * edge_length(ch, mode))
        contrib = P @ cv
        v *= contrib
        log_scale += cs
    scale = float(v.sum())
    if not np.isfinite(scale) or scale <= 0:
        return np.full(3, np.nan), -np.inf
    return v / scale, log_scale + math.log(scale)


def likelihood_and_root(clade, model: str, log_rates: np.ndarray, mode: str, prior_mode: str, colour):
    Q = qmatrix(model, log_rates)
    prior = np.full(3, 1 / 3) if prior_mode == "equal" else stationary(Q)
    rv, log_scale = pruning_vector(clade, Q, mode, colour)
    if not np.isfinite(rv).all() or not np.isfinite(log_scale):
        return -np.inf, np.full(3, np.nan), prior
    root_raw = prior * rv
    z = float(root_raw.sum())
    if z <= 0 or not np.isfinite(z):
        return -np.inf, np.full(3, np.nan), prior
    return math.log(z) + log_scale, root_raw / z, prior


def nparams(model: str) -> int:
    return {"ER": 1, "SYM": 3, "ARD": 6}[model]


def fit_model(clade, model: str, mode: str, prior_mode: str, colour, nobs: int):
    k = nparams(model)
    branch_lengths = [edge_length(x, mode) for x in clade.find_clades(order="preorder") if x is not clade]
    med = float(np.median(branch_lengths)) if branch_lengths else 1.0
    base_rate = max(1e-3, min(1e3, 0.5 / med))
    base = math.log(base_rate)
    starts = [
        np.full(k, base),
        np.full(k, base + math.log(0.2)),
        np.full(k, base + math.log(5.0)),
    ]
    if k > 1:
        starts += [
            np.linspace(base - 0.7, base + 0.7, k),
            np.linspace(base + 0.7, base - 0.7, k),
        ]

    def objective(x):
        ll, _, _ = likelihood_and_root(clade, model, x, mode, prior_mode, colour)
        return 1e100 if not np.isfinite(ll) else -ll

    best = None
    for start in starts:
        res = minimize(objective, start, method="L-BFGS-B", bounds=[(-12, 12)] * k, options={"maxiter": 800})
        if best is None or res.fun < best.fun:
            best = res
    assert best is not None
    ll, root, prior = likelihood_and_root(clade, model, best.x, mode, prior_mode, colour)
    aic = 2 * k - 2 * ll
    aicc = aic + (2 * k * (k + 1) / (nobs - k - 1)) if nobs > k + 1 else float("inf")
    rates = np.exp(best.x)
    names = {
        "ER": ["all"],
        "SYM": ["A_W", "A_Y", "W_Y"],
        "ARD": ["A_to_W", "A_to_Y", "W_to_A", "W_to_Y", "Y_to_A", "Y_to_W"],
    }[model]
    return {
        "branch_mode": mode,
        "root_prior": prior_mode,
        "model": model,
        "k": k,
        "logLik": float(ll),
        "AIC": float(aic),
        "AICc": float(aicc),
        "optimizer_success": bool(best.success),
        "optimizer_message": str(best.message),
        "rates": {n: float(v) for n, v in zip(names, rates)},
        "prior": {s: float(prior[i]) for i, s in enumerate(STATES)},
        "root_posterior": {s: float(root[i]) for i, s in enumerate(STATES)},
        "root_top_state": STATES[int(np.argmax(root))],
        "root_top_probability": float(np.max(root)),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", type=Path, required=True)
    ap.add_argument("--colour", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--outgroup", default="Polyspora speciosa")
    a = ap.parse_args()
    a.out_dir.mkdir(parents=True, exist_ok=True)

    tree = Phylo.read(str(a.tree), "newick")
    crown = extract_camellia_crown(tree, a.outgroup)
    colour = read_colour(a.colour)
    tips = [t for t in crown.get_terminals() if t.name]
    mapped = [(t.name, colour.get(norm_name(t.name))) for t in tips]
    observed = [(x, s) for x, s in mapped if s]
    counts = {s: sum(1 for _, x in observed if x == s) for s in STATES}
    if len(tips) != 93:
        raise SystemExit(f"expected 93 Camellia tips, got {len(tips)}")
    if len(observed) < 40 or min(counts.values()) < 2:
        raise SystemExit(f"insufficient colour overlap: n={len(observed)}, counts={counts}")

    fset, fchanges = fitch(crown, colour)
    fits = []
    for mode in ("astral", "unit"):
        for prior in ("equal", "stationary"):
            for model in ("ER", "SYM", "ARD"):
                fits.append(fit_model(crown, model, mode, prior, colour, len(observed)))

    # rank only within the same branch-length/prior treatment
    for mode in ("astral", "unit"):
        for prior in ("equal", "stationary"):
            grp = [x for x in fits if x["branch_mode"] == mode and x["root_prior"] == prior]
            best = min(x["AICc"] for x in grp)
            for x in grp:
                x["delta_AICc_within_treatment"] = float(x["AICc"] - best)

    fields = [
        "branch_mode", "root_prior", "model", "k", "logLik", "AIC", "AICc",
        "delta_AICc_within_treatment", "root_top_state", "root_top_probability",
        "optimizer_success", "optimizer_message", "rates", "prior", "root_posterior",
    ]
    with (a.out_dir / "mk_model_fits.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for x in fits:
            y = dict(x)
            for k in ("rates", "prior", "root_posterior"):
                y[k] = json.dumps(y[k], sort_keys=True)
            w.writerow(y)

    with (a.out_dir / "tip_colour_join.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["taxon", "colour_state"])
        w.writeheader()
        for taxon, state in sorted(mapped):
            w.writerow({"taxon": taxon, "colour_state": state or ""})

    best_rows = {}
    for mode in ("astral", "unit"):
        for prior in ("equal", "stationary"):
            grp = [x for x in fits if x["branch_mode"] == mode and x["root_prior"] == prior]
            b = min(grp, key=lambda x: x["AICc"])
            best_rows[f"{mode}__{prior}"] = {
                "model": b["model"],
                "AICc": b["AICc"],
                "root_posterior": b["root_posterior"],
                "root_top_state": b["root_top_state"],
                "root_top_probability": b["root_top_probability"],
            }
    top_states = [x["root_top_state"] for x in best_rows.values()]
    top_probs = [x["root_top_probability"] for x in best_rows.values()]
    summary = {
        "n_camellia_tree_tips": len(tips),
        "n_colour_observed": len(observed),
        "state_counts": counts,
        "n_unobserved_tips": len(tips) - len(observed),
        "fitch_root_state_set": sorted(fset),
        "fitch_minimum_changes": int(fchanges),
        "best_model_by_treatment": best_rows,
        "best_treatment_root_top_states": top_states,
        "root_top_state_agreement": len(set(top_states)) == 1,
        "minimum_top_state_probability": float(min(top_probs)),
        "branch_length_warning": "ASTRAL branch lengths are substitution-per-site estimates, not divergence times; unit-edge fits are a topology-only sensitivity.",
        "claim_ceiling": "rooted visible-colour history sensitivity only; no ecological causation, no time-calibrated transition rate, and no micro-mechanistic branch assignment yet",
    }
    (a.out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
