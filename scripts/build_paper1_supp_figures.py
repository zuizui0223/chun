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


def fig_s1(rows, out):
    fig, ax = plt.subplots(figsize=(9, 6))
    order = [
        ("strict", "ASTRAL_lengths"),
        ("strict", "unit_edges"),
        ("dominant", "ASTRAL_lengths"),
        ("dominant", "unit_edges"),
    ]
    labels = []
    mids = []
    errs = []
    for scenario, mode in order:
        r = next(x for x in rows if x["scenario"] == scenario and x["topology_or_mode"] == mode)
        lo, hi = float(r["value_min"]), float(r["value_max"])
        labels.append(f"{scenario}\n{mode.replace('_',' ')}")
        mids.append((lo + hi) / 2)
        errs.append((hi - lo) / 2)
    x = range(len(labels))
    ax.errorbar(list(x), mids, yerr=errs, fmt="o", capsize=5)
    ax.axhline(0.5, linestyle="--", linewidth=1)
    ax.set_xticks(list(x), labels)
    ax.set_ylim(0, 1)
    ax.set_ylabel("Model-averaged crown P(W)")
    ax.set_title("Fig. S1  Accepted-species ancestral-colour sensitivity")
    ax.text(0.02, 0.03, "W is favoured, but unit-edge topology retains W/Y uncertainty; this is a sensitivity result, not a headline.", transform=ax.transAxes, fontsize=9)
    save(fig, out, "FigS1_root_state_sensitivity")


def fig_s2(rows, out):
    fig, ax = plt.subplots(figsize=(11, 7))
    plot_rows = [r for r in rows if r["p_value"]]
    labels = [f"{r['topology_or_mode']} {r['scenario']} {r['metric']}" for r in plot_rows]
    vals = [-math.log10(float(r["p_value"])) for r in plot_rows]
    y = list(range(len(labels)))[::-1]
    for yi, v, r in zip(y, vals, plot_rows):
        ax.scatter([v], [yi], s=65)
        ax.text(v + 0.06, yi, f"P={float(r['p_value']):.4g}", va="center", fontsize=8.5)
    ax.axvline(-math.log10(0.05), linestyle="--", linewidth=1)
    ax.set_yticks(y, labels)
    ax.set_xlabel("−log10(permutation P)")
    ax.set_title("Fig. S2  State-specific colour clustering sensitivity")
    ax.text(0.99, 0.02, "Strict A is not testable because A=1 after wild-colour auditing; W is not individually significant.", transform=ax.transAxes, ha="right", fontsize=9)
    save(fig, out, "FigS2_state_specific_clustering")


def fig_s3(rows, out):
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    ax.set_title("Fig. S3  Legacy W→A events do not survive wild-colour and accepted-taxonomy sensitivity", fontsize=13)
    stages = [
        (0.12, 0.66, "Legacy 93-tip\nhard labels", 3),
        (0.38, 0.66, "Targeted wild/taxonomy\nstress test", 0),
        (0.64, 0.66, "WFO55 strict\naccepted species", 0),
        (0.88, 0.66, "Strict × dominant\nshared events", 0),
    ]
    from matplotlib.patches import FancyBboxPatch
    for x, y, label, n in stages:
        p = FancyBboxPatch((x-0.09,y-0.10),0.18,0.20,boxstyle="round,pad=0.02",fill=False,linewidth=1.4)
        ax.add_patch(p)
        ax.text(x,y+0.035,label,ha="center",va="center",fontsize=9.5)
        ax.text(x,y-0.065,f"robust W→A = {n}",ha="center",va="center",fontsize=10)
    for a,b in zip(stages[:-1],stages[1:]):
        ax.annotate("", xy=(b[0]-0.10,0.66), xytext=(a[0]+0.10,0.66), arrowprops=dict(arrowstyle="->",lw=1.3))
    ax.text(0.51, 0.30, "Dominant accepted-species sensitivity contains 1 W→A branch, but it is not shared with the strict wild-colour scenario.", ha="center", fontsize=10)
    ax.text(0.51, 0.16, "Falsification path: stronger trait/taxonomy evidence removes the legacy event-level headline rather than strengthening it.", ha="center", fontsize=10)
    save(fig, out, "FigS3_legacy_event_falsification")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", type=Path, required=True)
    ap.add_argument("--registry", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    a = ap.parse_args()

    rows = read_csv(a.inputs)
    registry = {r["result_id"]: r for r in read_csv(a.registry)}
    for r in rows:
        rid = r["result_id"]
        if rid not in registry:
            raise SystemExit(f"unknown result ID: {rid}")
        # Superseded result is permitted only in Fig S3 as an explicitly falsified historical input.
        if registry[rid]["status"] == "superseded" and r["figure_id"] != "FigS3":
            raise SystemExit(f"superseded result {rid} used outside Fig S3")
    a.out_dir.mkdir(parents=True, exist_ok=True)
    fig_s1([r for r in rows if r["figure_id"] == "FigS1"], a.out_dir)
    fig_s2([r for r in rows if r["figure_id"] == "FigS2"], a.out_dir)
    fig_s3([r for r in rows if r["figure_id"] == "FigS3"], a.out_dir)

    svg = sorted(x.name for x in a.out_dir.glob("FigS*.svg"))
    png = sorted(x.name for x in a.out_dir.glob("FigS*.png"))
    if len(svg) != 3 or len(png) != 3:
        raise SystemExit(f"expected 3 supplementary figures, got svg={svg}, png={png}")
    summary = {
        "supplementary_figure_version": "v0.1",
        "figures": ["FigS1_root_state_sensitivity", "FigS2_state_specific_clustering", "FigS3_legacy_event_falsification"],
        "svg_count": len(svg),
        "png_count": len(png),
        "superseded_result_policy": "allowed only in Fig S3 and explicitly labelled as falsified historical analysis",
        "new_scientific_analysis": False,
    }
    (a.out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
