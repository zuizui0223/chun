#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import matplotlib.pyplot as plt


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def save(fig, out: Path, stem: str) -> None:
    fig.savefig(out / f"{stem}.svg", bbox_inches="tight")
    fig.savefig(out / f"{stem}.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def box(ax, x, y, text, width=0.2, height=0.14, fontsize=10):
    from matplotlib.patches import FancyBboxPatch
    patch = FancyBboxPatch(
        (x - width / 2, y - height / 2), width, height,
        boxstyle="round,pad=0.02", fill=False, linewidth=1.4,
    )
    ax.add_patch(patch)
    ax.text(x, y, text, ha="center", va="center", fontsize=fontsize)


def arrow(ax, x1, y1, x2, y2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="->", lw=1.3))


def fig1(out: Path, v: dict[str, float]):
    fig, ax = plt.subplots(figsize=(14, 6.5))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    xs = [0.11, 0.37, 0.63, 0.88]
    widths = [0.18, 0.19, 0.20, 0.18]
    texts = [
        "Literature alternatives\nabiotic / pollinator /\nmolecular constraint",
        "Micro re-analysis\nmultiple molecular routes\nwithin pigment modules",
        "Accepted-species macro pattern\nlocal same-colour\nphylogenetic conservatism",
        "Public-data boundary\npattern identifiable\nevents not identifiable",
    ]
    for x, w, t in zip(xs, widths, texts):
        box(ax, x, 0.67, t, w, 0.21, 9.5)
    arrow(ax, xs[0] + widths[0] / 2, 0.67, xs[1] - widths[1] / 2, 0.67)
    arrow(ax, xs[1] + widths[1] / 2, 0.67, xs[2] - widths[2] / 2, 0.67)
    arrow(ax, xs[2] + widths[2] / 2, 0.67, xs[3] - widths[3] / 2, 0.67)
    ax.text(0.24, 0.76, "test", ha="center", fontsize=9)
    ax.text(0.50, 0.76, "scale up", ha="center", fontsize=9)
    ax.text(0.755, 0.76, "audit", ha="center", fontsize=9)
    ax.text(0.11, 0.27, f"Universal cold-chain screen\none-sided P = {v['F1_CLIMATE_P']:.5f}", ha="center", va="center", fontsize=10)
    ax.text(0.37, 0.27, f"Hue–pollinator diagnostic\npermutation P = {v['F1_POLLINATOR_P']:.5f}", ha="center", va="center", fontsize=10)
    ax.text(0.63, 0.27, "Question shifts from\n‘How is colour generated?’ to\n‘Why is a state retained?’", ha="center", va="center", fontsize=10)
    ax.text(0.88, 0.27, "Next causal test requires\npopulation-resolved phenotype,\npollination service and expression", ha="center", va="center", fontsize=10)
    ax.set_title("Fig. 1  Hypothesis trajectory from molecular generation to evolutionary persistence", fontsize=14)
    save(fig, out, "Fig1_hypothesis_trajectory")


def fig2(out: Path, v: dict[str, float]):
    fig, ax = plt.subplots(figsize=(13, 7))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    ax.set_title("Fig. 2  Recurrent pigment modules can use different molecular implementations", fontsize=14)
    xs = [0.17, 0.50, 0.83]
    box(ax, xs[0], 0.70, "FLS\nsame-lineage recurrence", 0.23, 0.16, 11)
    box(ax, xs[1], 0.70, "DFR\nparalog substitution", 0.23, 0.16, 11)
    box(ax, xs[2], 0.70, "ANS/LDOX + ANR\ncopy-aware heterogeneity", 0.23, 0.16, 11)
    ax.text(xs[0], 0.47,
            f"CDS identity {v['F2_FLS_CDS_ID']:.3f}%\nprotein identity {v['F2_FLS_PROT_ID']:.2f}%\nsister support {v['F2_FLS_TREE_SUPPORT']:.3f}",
            ha="center", va="center", fontsize=9.5)
    ax.text(xs[1], 0.47,
            f"CjDFR vs CsDFRa\n{v['F2_DFR_A_ID']:.3f}% protein identity\nsource copy = CsDFRb2\n{v['F2_DFR_B2_ID']:.3f}% to CjDFR",
            ha="center", va="center", fontsize=9.5)
    ax.text(xs[2], 0.47,
            "Mapped copies can move\nin opposite red/white directions\nstrict species-native node\nrecurrence remains unresolved",
            ha="center", va="center", fontsize=9.5)
    arrow(ax, 0.17, 0.30, 0.50, 0.30)
    arrow(ax, 0.50, 0.30, 0.83, 0.30)
    ax.text(0.50, 0.35, "increasing implementation flexibility", ha="center", fontsize=9.5)
    ax.text(0.50, 0.16, "Cross-scale prediction: pathway/module accessibility may be more repeatable than exact-node reuse.", ha="center", fontsize=10.5)
    save(fig, out, "Fig2_micro_implementation_modes")


def fig3(out: Path, v: dict[str, float]):
    fig, ax = plt.subplots(figsize=(12, 6.5))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    ax.set_title("Fig. 3  Taxonomy and wild-colour auditing sharply reduce usable macro trait states", fontsize=14)
    x0, x1, x2, x3 = 0.10, 0.35, 0.60, 0.87
    box(ax, x0, 0.61, f"{int(v['F3_LEGACY_TIPS'])}\nlegacy Camellia tips", 0.17, 0.17, 11)
    box(ax, x1, 0.61, f"{int(v['F3_ACCEPTED_SPECIES'])}\nWFO accepted species", 0.18, 0.17, 11)
    box(ax, x2, 0.61, f"{int(v['F3_PROVISIONAL_HARD'])}\nprovisional hard\ncolour states", 0.18, 0.17, 11)
    box(ax, x3, 0.72, f"{int(v['F3_STRICT_SEED'])}\nstrict wild seed", 0.17, 0.14, 11)
    box(ax, x3, 0.42, f"{int(v['F3_DOMINANT_SEED'])}\ndominant sensitivity", 0.17, 0.14, 11)
    arrow(ax, x0 + 0.085, 0.61, x1 - 0.09, 0.61)
    arrow(ax, x1 + 0.09, 0.61, x2 - 0.09, 0.61)
    arrow(ax, x2 + 0.09, 0.65, x3 - 0.085, 0.72)
    arrow(ax, x2 + 0.09, 0.56, x3 - 0.085, 0.42)
    ax.text(0.225, 0.69, "taxonomy", ha="center", fontsize=9)
    ax.text(0.475, 0.69, "trait join", ha="center", fontsize=9)
    ax.text(0.745, 0.78, "strict wild evidence", ha="center", fontsize=9)
    ax.text(0.745, 0.43, "dominant sensitivity", ha="center", fontsize=9)
    ax.text(0.60, 0.27, f"{int(v['F3_DEMOTED'])} provisional hard labels demoted in strict analysis", ha="center", fontsize=11)
    ax.text(0.50, 0.13, "Polymorphism, dominant/rare alternatives and insufficient exact-colour evidence are not forced into strict species-level states.", ha="center", fontsize=10)
    save(fig, out, "Fig3_taxonomy_trait_audit")


def fig4(out: Path, v: dict[str, float]):
    fig, ax = plt.subplots(figsize=(9, 6))
    shared = v["F4_SHARED_SPLITS"]
    total = v["F4_TOTAL_SPLITS"]
    heights = [shared, total - shared]
    labels = ["shared splits", "unique per tree"]
    bars = ax.bar(labels, heights)
    ax.set_ylabel("Nontrivial accepted-species splits")
    ax.set_ylim(0, max(heights) * 1.25)
    for b, val in zip(bars, heights):
        ax.text(b.get_x() + b.get_width()/2, b.get_height() + 0.8, f"{int(val)}", ha="center", va="bottom")
    ax.text(0.52, 0.82,
            f"Split recall = {shared/total:.2f}\nJaccard = {v['F4_JACCARD']:.4f}\nRF difference = {int(v['F4_RF'])} (= 4 + 4 unique)\nnormalized RF = {v['F4_NRF']:.2f}",
            transform=ax.transAxes, ha="center", va="center", fontsize=11)
    ax.set_title("Fig. 4  Accepted-species nuclear topology is highly concordant across gene-tree methods", fontsize=13)
    save(fig, out, "Fig4_nuclear_topology_sensitivity")


def fig5(out: Path, v: dict[str, float]):
    fig, ax = plt.subplots(figsize=(11, 7))
    rows = [
        ("FastTree strict — nearest", v["F5_FAST_STRICT_NEAR"], "nearest"),
        ("FastTree dominant — nearest", v["F5_FAST_DOM_NEAR"], "nearest"),
        ("UFBoot strict — nearest", v["F5_UF_STRICT_NEAR"], "nearest"),
        ("UFBoot dominant — nearest", v["F5_UF_DOM_NEAR"], "nearest"),
        ("FastTree strict — global MPD", v["F5_FAST_STRICT_MPD"], "mpd"),
        ("FastTree dominant — global MPD", v["F5_FAST_DOM_MPD"], "mpd"),
        ("UFBoot strict — global MPD", v["F5_UF_STRICT_MPD"], "mpd"),
        ("UFBoot dominant — global MPD", v["F5_UF_DOM_MPD"], "mpd"),
    ]
    y = list(range(len(rows)))[::-1]
    x = [-math.log10(max(p, 1e-12)) for _, p, _ in rows]
    for yi, xi, (_, p, kind) in zip(y, x, rows):
        ax.scatter([xi], [yi], marker="o" if kind == "nearest" else "x", s=75)
        ax.text(xi + 0.08, yi, f"P={p:.5g}", va="center", fontsize=9)
    ax.axvline(-math.log10(0.05), linestyle="--", linewidth=1)
    ax.set_yticks(y, [r[0] for r in rows])
    ax.set_xlabel("−log10(permutation P)")
    ax.set_title("Fig. 5  Local same-colour conservatism survives topology sensitivity; global MPD does not", fontsize=13)
    ax.text(0.99, 0.02, "circle = nearest-same-colour; x = global same-state MPD", transform=ax.transAxes, ha="right", fontsize=9)
    save(fig, out, "Fig5_colour_conservatism_robustness")


def fig6(out: Path, v: dict[str, float]):
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    ax.set_title("Fig. 6  The public-data boundary: robust pattern, no robust causal event", fontsize=14)
    box(ax, 0.20, 0.70, f"strict wild seed\nrobust branches = {int(v['F6_STRICT_EVENTS'])}", 0.23, 0.16, 11)
    box(ax, 0.50, 0.70, f"dominant sensitivity\nrobust branches = {int(v['F6_DOM_EVENTS'])}", 0.23, 0.16, 11)
    box(ax, 0.80, 0.70, f"shared across scenarios\nrobust branches = {int(v['F6_SHARED_EVENTS'])}", 0.23, 0.16, 11)
    arrow(ax, 0.315, 0.70, 0.385, 0.70)
    arrow(ax, 0.615, 0.70, 0.685, 0.70)
    box(ax, 0.50, 0.43, "Stop branch-specific causal modelling\nwith current public hard-state data", 0.35, 0.15, 11)
    arrow(ax, 0.80, 0.60, 0.61, 0.50)
    ax.text(0.50, 0.20,
            "Empirical handoff: population morph frequencies • UV–visible spectra • pigment chemistry • nectar/morphology\n"
            "visitation + single-visit pollen deposition • exclusion + fruit/seed set • flowering-window weather • paralog-specific expression",
            ha="center", va="center", fontsize=10)
    save(fig, out, "Fig6_public_data_boundary")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", type=Path, required=True)
    ap.add_argument("--inputs", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()

    registry = {r["result_id"]: r for r in read_csv(args.registry)}
    rows = read_csv(args.inputs)
    values: dict[str, float] = {}
    for r in rows:
        rid = r["result_id"]
        if rid not in registry:
            raise SystemExit(f"numeric input {r['input_id']} references unknown result {rid}")
        if registry[rid]["status"] == "superseded" or registry[rid]["manuscript_role"] == "exclude":
            raise SystemExit(f"numeric input {r['input_id']} references excluded/superseded result {rid}")
        values[r["input_id"]] = float(r["value"])

    expected = {
        "F1_CLIMATE_P","F1_POLLINATOR_P","F2_FLS_CDS_ID","F2_FLS_PROT_ID","F2_FLS_TREE_SUPPORT",
        "F2_DFR_A_ID","F2_DFR_B2_ID","F3_LEGACY_TIPS","F3_ACCEPTED_SPECIES","F3_PROVISIONAL_HARD",
        "F3_STRICT_SEED","F3_DOMINANT_SEED","F3_DEMOTED","F4_TOTAL_SPLITS","F4_SHARED_SPLITS","F4_RF",
        "F4_NRF","F4_JACCARD","F5_FAST_STRICT_NEAR","F5_FAST_DOM_NEAR","F5_UF_STRICT_NEAR",
        "F5_UF_DOM_NEAR","F5_FAST_STRICT_MPD","F5_FAST_DOM_MPD","F5_UF_STRICT_MPD","F5_UF_DOM_MPD",
        "F6_STRICT_EVENTS","F6_DOM_EVENTS","F6_SHARED_EVENTS",
    }
    missing = sorted(expected - set(values))
    if missing:
        raise SystemExit(f"missing figure inputs: {missing}")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    fig1(args.out_dir, values)
    fig2(args.out_dir, values)
    fig3(args.out_dir, values)
    fig4(args.out_dir, values)
    fig5(args.out_dir, values)
    fig6(args.out_dir, values)

    svg = sorted(p.name for p in args.out_dir.glob("Fig*.svg"))
    png = sorted(p.name for p in args.out_dir.glob("Fig*.png"))
    if len(svg) != 6 or len(png) != 6:
        raise SystemExit(f"expected 6 SVG + 6 PNG, got svg={svg}, png={png}")
    summary = {
        "figure_set": "Paper1 Main Fig1-Fig6 v0.1",
        "n_svg": len(svg),
        "n_png": len(png),
        "svg_files": svg,
        "png_files": png,
        "numeric_input_rows": len(rows),
        "registry_guard": "all numeric inputs reference non-superseded Paper 1 result IDs",
        "scientific_boundary": "figure generation only; no new analysis",
    }
    (args.out_dir / "figure_build_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
