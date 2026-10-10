#!/usr/bin/env python3
"""Post-outcome influence audit of the frozen 47-tip Petunieae adjusted correlation.

No new primary hypothesis, null, P value, covariate tuning, state recoding,
or replacement of the existing AJB / EL submission contracts.
"""
from __future__ import annotations
import argparse
import collections
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from analyze_petunieae_nested_regulatory_memory_v0_1 import within_state_pairs
from analyze_petunieae_pigment_adjusted_regulatory_memory_v0_1 import (
    residual_projector,
    standardized_log,
)
from run_petunieae_nested_regulatory_leaveoneout_prediction_v0_1 import load_source


def rho_within_codes(dist: np.ndarray, residual: np.ndarray, fine: list[str]) -> tuple[float, int]:
    ii, jj = within_state_pairs(fine)
    if len(ii) < 10:
        raise ValueError("too few same-code pairs")
    x = rankdata(dist[ii, jj]).astype(float)
    y = rankdata(np.sqrt(np.mean((residual[ii] - residual[jj]) ** 2, axis=1))).astype(float)
    xc, yc = x - x.mean(), y - y.mean()
    denom = np.sqrt(np.dot(xc, xc) * np.dot(yc, yc))
    if denom <= 1e-12:
        raise ValueError("uninformative rank axis")
    return float(np.dot(xc, yc) / denom), len(ii)


def influence_diagnostics(dist: np.ndarray, expr_z: np.ndarray, fine: list[str],
                          chem_z: np.ndarray, genes: list[str]) -> dict:
    n, p = expr_z.shape
    labels = sorted(set(fine))
    if len(fine) != n or dist.shape != (n, n) or chem_z.shape[0] != n or len(genes) != p:
        raise ValueError("input frame mismatch")
    if len(set(genes)) != p or p < 3 or len(labels) < 2:
        raise ValueError("gene / code panel invalid")
    if not np.isfinite(dist).all() or not np.isfinite(expr_z).all() or not np.isfinite(chem_z).all():
        raise ValueError("nonfinite source matrix")

    M, rank = residual_projector(fine, chem_z)
    residual = M @ expr_z
    base, pairs = rho_within_codes(dist, residual, fine)

    gene_drop = []
    for col, gene in enumerate(genes):
        retained = [j for j in range(p) if j != col]
        rho, num_pairs = rho_within_codes(dist, residual[:, retained], fine)
        assert num_pairs == pairs
        gene_drop.append({"excluded_gene": gene, "rho": rho})

    class_drop = []
    per_class = []
    codes = np.asarray(fine)
    for code in labels:
        keep = codes != code
        sub_codes = codes[keep].tolist()
        # Refit the full *fixed* nuisance design after deleting the code,
        # while retaining original 47-species feature standardization.
        Ms, sub_rank = residual_projector(sub_codes, chem_z[keep])
        rr, pair_count = rho_within_codes(
            dist[np.ix_(keep, keep)], Ms @ expr_z[keep], sub_codes
        )
        class_drop.append({
            "excluded_fine_code": code, "retained_tips": int(keep.sum()),
            "retained_same_code_pairs": pair_count, "nuisance_rank": sub_rank, "rho": rr
        })
        idx = np.flatnonzero(codes == code)
        # State-specific contribution under the original full-frame fit.
        sub_residual = residual[idx]
        class_rho, inner_pairs = rho_within_codes(
            dist[np.ix_(idx, idx)], sub_residual, [code] * len(idx)
        )
        per_class.append({
            "fine_code": code, "tips": len(idx),
            "same_code_pairs": inner_pairs, "within_class_rho": class_rho
        })

    return {
        "version": "v0.1",
        "status": "POST_OUTCOME_DESCRIPTIVE_INFLUENCE_DIAGNOSTIC",
        "n_tips": n, "n_gene_axes": p, "n_fine_codes": len(labels),
        "same_code_pairs": pairs, "nuisance_rank": rank,
        "original_adjusted_rho_recomputed": base,
        "leave_one_gene_out": gene_drop,
        "leave_one_fine_code_out_refit": class_drop,
        "per_code_original_fit_descriptive": per_class,
        "leave_one_gene_out_summary": {
            "positive": sum(x["rho"] > 0 for x in gene_drop),
            "min_rho": min(x["rho"] for x in gene_drop),
            "median_rho": float(np.median([x["rho"] for x in gene_drop])),
            "max_rho": max(x["rho"] for x in gene_drop),
        },
        "leave_one_fine_code_out_summary": {
            "positive": sum(x["rho"] > 0 for x in class_drop),
            "min_rho": min(x["rho"] for x in class_drop),
            "median_rho": float(np.median([x["rho"] for x in class_drop])),
            "max_rho": max(x["rho"] for x in class_drop),
        },
        "new_p_values": 0,
        "not_independent_replication": True,
        "no_causal_or_adaptive_inference": True,
        "does_not_rescue_k2_prediction_fail": True,
        "original_frozen_ajb_and_el_unchanged": True,
    }


def run(source: Path, original_design: dict, adjusted_design: dict,
        adjusted_result: dict) -> dict:
    counts = {"000000": 6, "000010": 6, "000011": 6,
              "000100": 10, "000110": 6, "000111": 13}
    dist, fine, names, gene_log = load_source(
        source, {"retained_taxa": 47, "class_counts": counts}, original_design
    )
    table = pd.read_csv(source / original_design["source"]["processed_csv_path"])
    table = table.set_index("key_0").loc[names]
    chemistry = adjusted_design["covariate_adjustment"]["columns"]
    chem_z, zeros = standardized_log(table[chemistry].to_numpy(dtype=float), 100.0)
    expr_z, gene_zero = standardized_log(np.expm1(gene_log), 1.0)
    if gene_zero or sorted(chemistry[i] for i in zeros) != sorted(
            adjusted_design["frame"]["absent_after_rare_filter"]):
        raise ValueError("frozen pigment or gene panel drift")
    genes = original_design["primary"]["raw_gene_expression_columns"]
    result = influence_diagnostics(dist, expr_z, fine, chem_z, genes)
    if (result["n_tips"] != 47 or result["same_code_pairs"] != 183
            or result["n_gene_axes"] != 21 or result["n_fine_codes"] != 6
            or abs(result["original_adjusted_rho_recomputed"]
                   - adjusted_result["abundance_adjusted_rho"]) > 1e-10):
        raise ValueError("main adjusted result / source frame drift")
    result["source_SHA256_verified"] = True  # load_source checks all 3 frozen hashes
    result["adjusted_reference_result"] = (
        "results/petunieae_pigment_adjusted_regulatory_memory_v0_1/result_v0_1.json"
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    original = json.loads(
        (ROOT / "data/petunieae_nested_regulatory_memory_preregistered_design_v0_1.json").read_text()
    )
    design = json.loads(
        (ROOT / "data/petunieae_pigment_abundance_adjusted_regulatory_memory_design_v0_1.json").read_text()
    )
    prior = json.loads(
        (ROOT / "results/petunieae_pigment_adjusted_regulatory_memory_v0_1/result_v0_1.json").read_text()
    )
    result = run(args.source, original, design, prior)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("SOURCE_IDENTITY_AND_FROZEN_RHO_PASS", result["original_adjusted_rho_recomputed"])
    print("POST_OUTCOME_LEAVE_ONE_GENE",
          json.dumps(result["leave_one_gene_out_summary"], sort_keys=True))
    print("POST_OUTCOME_LEAVE_ONE_FINE_CODE",
          json.dumps(result["leave_one_fine_code_out_summary"], sort_keys=True))
    print("POST_OUTCOME_PER_CODE",
          json.dumps(result["per_code_original_fit_descriptive"], sort_keys=True))
    print("NO_NEW_P_VALUES_OR_CAUSAL_CLAIMS")


if __name__ == "__main__":
    main()
