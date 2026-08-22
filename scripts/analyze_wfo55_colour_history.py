#!/usr/bin/env python3
"""Accepted-species visible-colour history on the frozen WFO55 nuclear tree."""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

from Bio import Phylo

from analyze_rooted_camellia_colour_history import (
    STATES,
    SINDEX,
    extract_camellia_crown,
    fitch,
    fit_model,
    norm_name,
)


def read_seed(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    with path.open(newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            raw = row.get("accepted_species") or row.get("taxon") or ""
            state = (row.get("colour_state") or "").strip()
            key = norm_name(raw)
            if key and state in SINDEX:
                if key in out and out[key] != state:
                    raise SystemExit(f"conflicting state for {raw}: {out[key]} vs {state}")
                out[key] = state
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", type=Path, required=True)
    ap.add_argument("--colour", type=Path, required=True)
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
    mapped = [(t.name, colour.get(norm_name(t.name))) for t in tips]
    observed = [(x, s) for x, s in mapped if s]
    counts = {s: sum(1 for _, x in observed if x == s) for s in STATES}

    if len(tips) != args.expected_camellia:
        raise SystemExit(f"expected {args.expected_camellia} Camellia tips, got {len(tips)}")
    absent = sorted(k for k in colour if k not in {norm_name(t.name) for t in tips})
    if absent:
        raise SystemExit(f"colour seed contains taxa absent from tree: {absent}")
    if len(observed) != len(colour):
        raise SystemExit(f"seed/tree overlap mismatch: seed={len(colour)} observed={len(observed)}")
    if len(observed) < 12 or sum(v > 0 for v in counts.values()) < 2:
        raise SystemExit(f"insufficient colour information: n={len(observed)} counts={counts}")

    fset, fchanges = fitch(crown, colour)
    fits = [
        fit_model(crown, model, mode, prior, colour, len(observed))
        for mode in ("astral", "unit")
        for prior in ("equal", "stationary")
        for model in ("ER", "SYM", "ARD")
    ]

    treatments = {}
    for mode in ("astral", "unit"):
        for prior in ("equal", "stationary"):
            grp = [x for x in fits if x["branch_mode"] == mode and x["root_prior"] == prior]
            best_aicc = min(x["AICc"] for x in grp)
            raw = [math.exp(-0.5 * (x["AICc"] - best_aicc)) for x in grp]
            denom = sum(raw)
            for x, r in zip(grp, raw):
                x["delta_AICc_within_treatment"] = float(x["AICc"] - best_aicc)
                x["akaike_weight_within_treatment"] = float(r / denom)
            avg = {
                s: sum(x["akaike_weight_within_treatment"] * x["root_posterior"][s] for x in grp)
                for s in STATES
            }
            z = sum(avg.values())
            avg = {s: float(v / z) for s, v in avg.items()}
            best = min(grp, key=lambda x: x["AICc"])
            treatments[f"{mode}__{prior}"] = {
                "best_model": best["model"],
                "best_AICc": best["AICc"],
                "model_weights": {x["model"]: x["akaike_weight_within_treatment"] for x in grp},
                "model_averaged_root_posterior": avg,
                "model_averaged_top_state": max(avg, key=avg.get),
                "model_averaged_top_probability": max(avg.values()),
            }

    fields = [
        "branch_mode", "root_prior", "model", "k", "logLik", "AIC", "AICc",
        "delta_AICc_within_treatment", "akaike_weight_within_treatment",
        "root_top_state", "root_top_probability", "optimizer_success", "optimizer_message",
        "rates", "prior", "root_posterior",
    ]
    with (args.out_dir / "mk_model_fits.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for x in fits:
            y = dict(x)
            for k in ("rates", "prior", "root_posterior"):
                y[k] = json.dumps(y[k], sort_keys=True)
            w.writerow(y)

    with (args.out_dir / "tip_colour_join.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["taxon", "colour_state"])
        w.writeheader()
        for taxon, state in sorted(mapped):
            w.writerow({"taxon": taxon, "colour_state": state or ""})

    tops = [x["model_averaged_top_state"] for x in treatments.values()]
    probs = [x["model_averaged_top_probability"] for x in treatments.values()]
    summary = {
        "scenario": args.scenario,
        "n_camellia_tree_tips": len(tips),
        "n_colour_observed": len(observed),
        "state_counts": counts,
        "n_unobserved_tips": len(tips) - len(observed),
        "fitch_root_state_set": sorted(fset),
        "fitch_minimum_changes": int(fchanges),
        "treatments": treatments,
        "model_averaged_top_states": tops,
        "model_averaged_root_state_agreement": len(set(tops)) == 1,
        "minimum_model_averaged_top_probability": float(min(probs)),
        "claim_ceiling": "accepted-species wild-colour history sensitivity only; no ecological causation or time-calibrated rates",
    }
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
