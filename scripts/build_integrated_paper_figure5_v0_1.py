#!/usr/bin/env python3
"""Build independent Fig. 5 panels for the integrated CHUN draft.

A: 183 within-identical-six-bit-pigment-state Petunieae tip pairs.
B: class mean vs exact random-two expectation vs fixed two-nearest predictor.

These panels intentionally have different measurement units and are NEVER
combined into one numerical regression or shown on a shared vertical axis.
No new hypothesis test is performed here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from run_petunieae_nested_regulatory_leaveoneout_prediction_v0_1 import load_source
from analyze_petunieae_nested_regulatory_memory_v0_1 import within_state_pairs

ORIGINAL = ROOT / "data/petunieae_nested_regulatory_memory_preregistered_design_v0_1.json"
DESIGN = ROOT / "data/petunieae_nested_regulatory_leaveoneout_prediction_design_v0_1.json"
REG = ROOT / "results/petunieae_nested_regulatory_memory_v0_1/result_v0_1.json"
HELDOUT = ROOT / "results/petunieae_nested_regulatory_leaveoneout_prediction_v0_1/result_v0_1.json"
DECOMP = ROOT / "results/petunieae_k2_donor_penalty_diagnostic_v0_1/result_v0_1.json"
COVERAGE = ROOT / "results/petunieae_fine_pigment_state_retention_v0_1/coverage_v0_1.json"

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def chart_data(source: Path) -> tuple[dict, dict]:
    original, design = load_json(ORIGINAL), load_json(DESIGN)
    reg, heldout, decomposed = load_json(REG), load_json(HELDOUT), load_json(DECOMP)
    coverage = load_json(COVERAGE)
    if coverage['retained_tips'] != 47 or coverage['excluded_tips'] != 12 or not coverage['three_bit_reduction_preserves_fine_partition']:
        raise ValueError('frozen pigment support boundary drift')
    if coverage['retained_variable_anthocyanidin_compounds'] != ['Del_mgg', 'Pet_mgg', 'Malv_mgg']:
        raise ValueError('non-representative variable pigment claim')
    distance, fine, names, xlog = load_source(source, design, original)
    # Use the original once-log1p expression with column z-score.
    x = np.asarray(xlog, dtype=float)
    sd = x.std(axis=0, ddof=0)
    if np.any(sd <= 0):
        raise ValueError("Expected all 21 Petunieae source expression axes to vary.")
    standardized = (x - x.mean(axis=0)) / sd
    ii, jj = within_state_pairs(fine)
    xx = np.asarray(distance[ii, jj], dtype=float)
    yy = np.sqrt(np.mean((standardized[ii] - standardized[jj]) ** 2, axis=1))
    rr = float(np.corrcoef(rankdata(xx), rankdata(yy))[0, 1])
    observed = reg["primary_conditional_expression_memory"]
    if len(names) != 47 or len(ii) != 183 or standardized.shape[1] != 21:
        raise ValueError("source figure frame changed")
    if abs(rr - observed["rho"]) > 1e-10:
        raise ValueError(f"Fig5A disagrees with frozen within-pigment state Spearman: {rr}")
    source_data = {
        "patristic_distance": xx.tolist(),
        "expression_rms": yy.tolist(),
        "rho": rr,
        "null_mean_rho": observed["null_mean_rho"],
        "pair_count": len(ii),
        "tip_count": len(names),
        "gene_count": standardized.shape[1],
        "fine_codes": [fine[int(i)] for i in ii],
        "variable_compounds": ['Del', 'Pet', 'Malv'],
        "retained_tips": coverage['retained_tips'],
        "unfiltered_tips": coverage['unfiltered_ingroup_tips'],
    }
    values = [
        heldout["baseline_loss"],
        decomposed["random_two_expected_mse"],
        heldout["neighbor_loss"],
    ]
    if not abs(values[0] - decomposed["state_only_mse"]) < 1e-10:
        raise ValueError("class baseline drift")
    if not abs(values[2] - decomposed["nearest_two_mse"]) < 1e-10:
        raise ValueError("closest-two drift")
    if not values[0] < values[2] < values[1]:
        raise ValueError("frozen class/neighborhood prediction ordering drift")
    if heldout["decision"] != "NOT_SUPPORTED" or decomposed["frozen_primary_decision"] != "NOT_SUPPORTED":
        raise ValueError("frozen negative prediction result was reclassified")
    predicted = {
        "methods": ["All same-code donors", "Random two donors\n(exact expected MSE)", "Two nearest same-code donors"],
        "mse": values,
        "locality_gain": decomposed["locality_gain_over_random_two"],
        "donor_penalty": decomposed["small_donor_penalty"],
        "net_penalty": decomposed["net_nearest_two_penalty"],
        "result": "NOT_SUPPORTED",
    }
    return source_data, predicted

def fig5a(data: dict, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.8, 5.8), layout="constrained")
    ax.scatter(data["patristic_distance"], data["expression_rms"],
               s=24, alpha=0.42, edgecolors="none", c="#326B85")
    ax.set_xlabel("Patristic distance (published source-tree units)")
    ax.set_ylabel("21-gene standardized expression RMS distance")
    ax.set_title("Fig. 5A  Gene-expression history inside identical pigment-presence states",
                 fontsize=12, loc="left")
    ax.text(.02,.98,
            f"47 tips; 183 same-six-bit-pigment pairs\nObserved Spearman rho = {data['rho']:+.3f}\n"
            f"Within-class permutation null mean rho = {data['null_mean_rho']:+.3f}; P = 0.0001",
            transform=ax.transAxes, va="top", ha="left", fontsize=9.2,
            bbox={"facecolor":"white","edgecolor":"none","alpha":0.86,"boxstyle":"round,pad=0.3"})
    ax.text(.98,.02,
            "Only Del/Pet/Malv vary after the rare-state gate (47/59 taxa).\nPairs are not independent replicates; taxon-vector permutation supplies inference.",
            transform=ax.transAxes,ha="right",va="bottom",fontsize=8.5,
            bbox={"facecolor":"white","edgecolor":"none","alpha":0.9,"boxstyle":"round,pad=0.2"})
    ax.spines[["top","right"]].set_visible(False)
    fig.savefig(out.with_suffix(".png"),dpi=250)
    fig.savefig(out.with_suffix(".svg"))
    plt.close(fig)

def fig5b(data: dict, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(9.5, 5.6))
    fig.subplots_adjust(left=0.32, right=0.97, top=0.82, bottom=0.29)
    y = np.arange(3)
    colors = ["#688393","#B3BDC5","#2B647A"]
    bars = ax.barh(y, data["mse"], height=0.58, color=colors, edgecolor="none")
    ax.set_yticks(y, data["methods"])
    ax.invert_yaxis()
    ax.set_xlim(0, 1.70)
    ax.set_xlabel("Held-out 21-gene standardized mean squared error (lower is better)")
    ax.set_title("Fig. 5B  Phylogenetic locality versus donor number",
                 fontsize=12,loc="left",pad=11)
    for rect,v in zip(bars,data["mse"]):
        ax.text(v+0.025,rect.get_y()+rect.get_height()/2,f"{v:.3f}",
                va="center",ha="left",fontsize=11,weight="semibold")
    # Report annotation BELOW the axes, rather than covering the third bar.
    fig.text(0.32,0.105,
             "Relative to the class mean: two-donor penalty +23.5%; "
             "phylogenetic recovery −13.6%; net +9.9%\n"
             "Frozen nearest-two prediction: NOT SUPPORTED",
             fontsize=9.2,ha="left",va="bottom")
    ax.spines[["top","right"]].set_visible(False)
    fig.savefig(out.with_suffix(".png"),dpi=250)
    fig.savefig(out.with_suffix(".svg"))
    plt.close(fig)

def build(source: Path, out_dir: Path) -> dict:
    data_a, data_b = chart_data(source)
    out_dir.mkdir(parents=True,exist_ok=True)
    fig5a(data_a, out_dir / "fig5a_petunieae_hidden_expression_memory")
    fig5b(data_b, out_dir / "fig5b_petunieae_heldout_prediction")
    files = sorted(p for p in out_dir.iterdir() if p.suffix in (".png",".svg"))
    summary = {
        "version":"v0.1",
        "status":"INTEGRATED_FIGURE_5_SOURCE_VERIFIED",
        "source_verified":True,
        "observed_pair_count":data_a["pair_count"],
        "fine_pigment_class_count":6,
        "retained_variable_anthocyanidins":data_a['variable_compounds'],
        "retained_tips_of_total": [data_a['retained_tips'],data_a['unfiltered_tips']],
        "observed_rho":data_a["rho"],
        "prediction_comparison":dict(zip(data_b["methods"],data_b["mse"])),
        "frozen_prediction_decision":data_b["result"],
        "mean_error_decomposition":{
            "donor_count_penalty":data_b["donor_penalty"],
            "phylogenetic_locality_gain":data_b["locality_gain"],
            "net_penalty":data_b["net_penalty"],
        },
        "figure_paths":[p.name for p in files],
        "source_sha256":{
            str(p.relative_to(ROOT)):sha256(p)
            for p in (ORIGINAL,DESIGN,REG,HELDOUT,DECOMP,COVERAGE)
        },
        "no_new_significance_test":True,
        "non_independent_species_pairs_disclosed":True,
        "no_causal_cross_radiation_claim":True,
    }
    (out_dir/"figure5_manifest_v0_1.json").write_text(
        json.dumps(summary,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return summary

def main()->None:
    a=argparse.ArgumentParser()
    a.add_argument("--source",type=Path,required=True)
    a.add_argument("--out-dir",type=Path,required=True)
    args=a.parse_args()
    result=build(args.source,args.out_dir)
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
