#!/usr/bin/env python3
"""Separate occurrence provenance from lower-tail estimator stability.

The input is the retained per-occurrence CHELSA table from the Fan2026 GBIF
workflow.  Record exclusions are explicit in a versioned evidence ledger and
are applied cumulatively as sensitivity stages; the raw table is never silently
mutated.

Outputs:
- A/W BIO6 comparisons under staged provenance gates;
- sample-size sensitivity after the strongest admitted gate;
- leave-one-record-out leverage of each species' BIO6 q05.

This is an admission/robustness analysis, not a phylogenetic causal model.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

STAGES = [
    ("S0_original_exact50", set()),
    ("S1_remove_documented_nonlocal", {"A_documented_nonlocal"}),
    (
        "S2_add_generic_china_center_proxy",
        {"A_documented_nonlocal", "B_add_generic_center_proxy"},
    ),
    (
        "S3_add_hard_range_metadata_conflicts",
        {
            "A_documented_nonlocal",
            "B_add_generic_center_proxy",
            "C_add_hard_range_or_metadata_conflict",
        },
    ),
]

METRICS = (
    "bio6_median",
    "bio6_min",
    "bio6_q01",
    "bio6_q05",
    "bio6_q10",
    "bio6_q20",
    "bio6_lower20_mean",
)


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    out = []
    for taxon, g in df.groupby("taxon", sort=True):
        b = np.asarray(g["bio6"], float)
        k = max(1, int(np.ceil(len(b) * 0.2)))
        out.append(
            {
                "taxon": taxon,
                "colour_state": g["colour_state"].iloc[0],
                "n_points": len(g),
                "bio6_median": np.median(b),
                "bio6_min": np.min(b),
                "bio6_q01": np.quantile(b, 0.01),
                "bio6_q05": np.quantile(b, 0.05),
                "bio6_q10": np.quantile(b, 0.10),
                "bio6_q20": np.quantile(b, 0.20),
                "bio6_lower20_mean": np.sort(b)[:k].mean(),
            }
        )
    return pd.DataFrame(out)


def permutation_test(
    x: pd.Series,
    y: pd.Series,
    n: int = 100_000,
    seed: int = 20260815,
) -> tuple[float, float, float]:
    """Monte-Carlo permutation test for difference in species means."""
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    vals = np.r_[x, y]
    nx = len(x)
    obs = x.mean() - y.mean()
    rng = np.random.default_rng(seed)
    count_two = 0
    count_lower = 0
    total = vals.sum()
    N = len(vals)
    for start in range(0, n, 10_000):
        batch = min(10_000, n - start)
        keys = rng.random((batch, N))
        idx = np.argpartition(keys, nx - 1, axis=1)[:, :nx]
        sx = vals[idx].sum(axis=1)
        d = sx / nx - (total - sx) / (N - nx)
        count_two += np.count_nonzero(np.abs(d) >= abs(obs) - 1e-12)
        count_lower += np.count_nonzero(d <= obs + 1e-12)
    return (
        obs,
        (count_two + 1) / (n + 1),
        (count_lower + 1) / (n + 1),
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("thermal_points", type=Path)
    ap.add_argument("--flags", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--permutations", type=int, default=100_000)
    args = ap.parse_args()

    points = pd.read_csv(args.thermal_points)
    flags = pd.read_csv(args.flags)

    # The live GBIF taxonomy audit established C. kissi as a FUZZY duplicate of
    # exact C. kissii; retain only the exact taxon in this branch's 50-species set.
    points = points[points["taxon"] != "Camellia kissi"].copy()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    scenario_rows = []
    strongest = None
    for si, (name, stages) in enumerate(STAGES):
        bad = set(
            flags.loc[flags["sensitivity_stage"].isin(stages), "gbif_key"]
            .astype(str)
            .tolist()
        )
        current = (
            points[~points["gbif_key"].astype(str).isin(bad)].copy()
            if stages
            else points.copy()
        )
        species = summarize(current)
        if name.startswith("S3_"):
            strongest = (current, species)

        aw = species[species["colour_state"].isin(["A", "W"])]
        for j, metric in enumerate(METRICS):
            A = aw.loc[aw["colour_state"] == "A", metric]
            W = aw.loc[aw["colour_state"] == "W", metric]
            diff, p_two, p_lower = permutation_test(
                A,
                W,
                n=args.permutations,
                seed=20260815 + si * 100 + j,
            )
            scenario_rows.append(
                {
                    "scenario": name,
                    "n_points": len(current),
                    "n_species": species["taxon"].nunique(),
                    "metric": metric,
                    "n_A": len(A),
                    "n_W": len(W),
                    "mean_A": A.mean(),
                    "mean_W": W.mean(),
                    "difference_A_minus_W": diff,
                    "two_sided_permutation_p": p_two,
                    "one_sided_p_A_lower": p_lower,
                    "n_permutations": args.permutations,
                }
            )

    pd.DataFrame(scenario_rows).to_csv(
        args.out_dir / "tail_provenance_scenario_tests.csv", index=False
    )

    assert strongest is not None
    current, species = strongest

    sample_rows = []
    for ni, n_min in enumerate((5, 10, 20, 30)):
        aw = species[
            species["colour_state"].isin(["A", "W"])
            & (species["n_points"] >= n_min)
        ]
        for j, metric in enumerate(METRICS):
            A = aw.loc[aw["colour_state"] == "A", metric]
            W = aw.loc[aw["colour_state"] == "W", metric]
            diff, p_two, p_lower = permutation_test(
                A,
                W,
                n=args.permutations,
                seed=20260900 + ni * 100 + j,
            )
            sample_rows.append(
                {
                    "n_min_per_species": n_min,
                    "metric": metric,
                    "n_A": len(A),
                    "n_W": len(W),
                    "mean_A": A.mean(),
                    "mean_W": W.mean(),
                    "difference_A_minus_W": diff,
                    "two_sided_p": p_two,
                    "one_sided_p_A_lower": p_lower,
                }
            )

    pd.DataFrame(sample_rows).to_csv(
        args.out_dir / "tail_sample_size_sensitivity.csv", index=False
    )

    loo_rows = []
    for taxon, g in current.groupby("taxon", sort=True):
        b = np.asarray(g["bio6"], float)
        q05 = np.quantile(b, 0.05)
        delta = [np.quantile(np.delete(b, i), 0.05) - q05 for i in range(len(b))]
        loo_rows.append(
            {
                "taxon": taxon,
                "colour_state": g["colour_state"].iloc[0],
                "n_points": len(b),
                "bio6_q05": q05,
                "max_abs_loo_q05_change_C": np.max(np.abs(delta)),
                "median_abs_loo_q05_change_C": np.median(np.abs(delta)),
                "max_positive_loo_q05_change_C": np.max(delta),
            }
        )

    pd.DataFrame(loo_rows).to_csv(
        args.out_dir / "q05_leave_one_record_stability.csv", index=False
    )


if __name__ == "__main__":
    main()
