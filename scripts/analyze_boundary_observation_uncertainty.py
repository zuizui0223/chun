#!/usr/bin/env python3
"""Propagate occurrence-sampling uncertainty for Camellia BIO6 lower boundaries.

This script acts on the strongest currently declared provenance sensitivity
(S3) and deliberately treats species BIO6 q05 as an estimated observation,
not an error-free trait.

Two uncertainty layers are reported for the A-vs-W q05 contrast:
1. within-species occurrence resampling, conditional on the observed taxon set;
2. nested species + occurrence resampling, as a non-phylogenetic diagnostic.

The ordinary empirical bootstrap of a low quantile is biased at small n. To
avoid interpreting that finite-sample bootstrap bias as a biological A-W shift,
within-species bootstrap deviations are centered on each taxon's bootstrap mean
and then added to the observed q05. This preserves the observed point estimate
while propagating sampling dispersion. This remains a diagnostic, not a final
measurement-error model and not a substitute for a dated nuclear phylogeny.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

S3_STAGES = {
    "A_documented_nonlocal",
    "B_add_generic_center_proxy",
    "C_add_hard_range_or_metadata_conflict",
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("thermal_points", type=Path)
    ap.add_argument("--flags", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--replicates", type=int, default=5000)
    args = ap.parse_args()

    points = pd.read_csv(args.thermal_points)
    flags = pd.read_csv(args.flags)
    points = points[points["taxon"] != "Camellia kissi"].copy()
    bad = set(
        flags.loc[flags["sensitivity_stage"].isin(S3_STAGES), "gbif_key"]
        .astype(str)
        .tolist()
    )
    points = points[~points["gbif_key"].astype(str).isin(bad)].copy()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(20260815)
    boot: dict[str, np.ndarray] = {}
    obs: dict[str, float] = {}
    states: dict[str, str] = {}
    species_rows = []

    for taxon, g in points.groupby("taxon", sort=True):
        values = np.asarray(g["bio6"], float)
        n = len(values)
        samples = rng.choice(values, size=(args.replicates, n), replace=True)
        q = np.quantile(samples, 0.05, axis=1)
        observed = float(np.quantile(values, 0.05))
        boot[taxon] = q
        obs[taxon] = observed
        states[taxon] = str(g["colour_state"].iloc[0])
        species_rows.append(
            {
                "taxon": taxon,
                "colour_state": states[taxon],
                "n_points": n,
                "bio6_q05": observed,
                "bootstrap_mean_q05": float(q.mean()),
                "bootstrap_bias": float(q.mean() - observed),
                "bootstrap_se": float(q.std(ddof=1)),
                "bootstrap_q025": float(np.quantile(q, 0.025)),
                "bootstrap_q975": float(np.quantile(q, 0.975)),
            }
        )

    species = pd.DataFrame(species_rows)
    species.to_csv(args.out_dir / "boundary_q05_bootstrap_by_species.csv", index=False)
    (
        species.groupby("colour_state", sort=True)
        .agg(
            n_species=("taxon", "size"),
            median_n_points=("n_points", "median"),
            median_bootstrap_se=("bootstrap_se", "median"),
            mean_bootstrap_se=("bootstrap_se", "mean"),
        )
        .reset_index()
        .to_csv(args.out_dir / "boundary_q05_bootstrap_by_state.csv", index=False)
    )

    a_taxa = [t for t in obs if states[t] == "A"]
    w_taxa = [t for t in obs if states[t] == "W"]
    observed_diff = float(
        np.mean([obs[t] for t in a_taxa]) - np.mean([obs[t] for t in w_taxa])
    )
    boot_mean = {t: float(boot[t].mean()) for t in obs}

    occurrence_diff = np.empty(args.replicates)
    for b in range(args.replicates):
        av = [obs[t] + (boot[t][b] - boot_mean[t]) for t in a_taxa]
        wv = [obs[t] + (boot[t][b] - boot_mean[t]) for t in w_taxa]
        occurrence_diff[b] = np.mean(av) - np.mean(wv)

    rng_nested = np.random.default_rng(20260816)
    nested_diff = np.empty(args.replicates)
    for b in range(args.replicates):
        aa = rng_nested.choice(a_taxa, size=len(a_taxa), replace=True)
        ww = rng_nested.choice(w_taxa, size=len(w_taxa), replace=True)
        av, wv = [], []
        for t in aa:
            j = rng_nested.integers(args.replicates)
            av.append(obs[t] + (boot[t][j] - boot_mean[t]))
        for t in ww:
            j = rng_nested.integers(args.replicates)
            wv.append(obs[t] + (boot[t][j] - boot_mean[t]))
        nested_diff[b] = np.mean(av) - np.mean(wv)

    summary = pd.DataFrame(
        [
            {
                "analysis": "observed_S3",
                "n_A": len(a_taxa), "n_W": len(w_taxa),
                "point_estimate_A_minus_W": observed_diff,
                "q025": np.nan, "median": observed_diff, "q975": np.nan,
                "fraction_A_lower": float(observed_diff < 0),
                "interpretation": "point estimate",
            },
            {
                "analysis": "within_species_occurrence_bootstrap_centered",
                "n_A": len(a_taxa), "n_W": len(w_taxa),
                "point_estimate_A_minus_W": observed_diff,
                "q025": float(np.quantile(occurrence_diff, 0.025)),
                "median": float(np.median(occurrence_diff)),
                "q975": float(np.quantile(occurrence_diff, 0.975)),
                "fraction_A_lower": float(np.mean(occurrence_diff < 0)),
                "interpretation": "occurrence-resampling uncertainty conditional on observed species set",
            },
            {
                "analysis": "nested_species_plus_occurrence_bootstrap",
                "n_A": len(a_taxa), "n_W": len(w_taxa),
                "point_estimate_A_minus_W": observed_diff,
                "q025": float(np.quantile(nested_diff, 0.025)),
                "median": float(np.median(nested_diff)),
                "q975": float(np.quantile(nested_diff, 0.975)),
                "fraction_A_lower": float(np.mean(nested_diff < 0)),
                "interpretation": "adds nonphylogenetic species-resampling uncertainty; diagnostic only",
            },
        ]
    )
    summary.to_csv(args.out_dir / "boundary_q05_aw_uncertainty_summary.csv", index=False)


if __name__ == "__main__":
    main()
