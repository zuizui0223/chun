#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import textwrap
from pathlib import Path

import matplotlib.pyplot as plt


def read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"empty input: {path}")
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--framework", type=Path, required=True)
    ap.add_argument("--observation", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()

    framework = read(args.framework)
    observation = read(args.observation)
    if [int(r["order"]) for r in framework] != [1, 2, 3, 4, 5, 6]:
        raise ValueError("framework order drift")

    by_regime: dict[str, dict[str, dict[str, str]]] = {}
    for row in observation:
        by_regime.setdefault(row["regime"], {})[row["feature"]] = row
    lit = by_regime["published_literature"]
    dep = by_regime["dependence_collapsed"]
    cf = by_regime["candidate_free"]

    system_coverage = [int(lit[f"{axis}_axis_system_coverage"]["value"]) for axis in "AFCP"]
    cluster_coverage = [int(dep[f"{axis}_axis_cluster_coverage"]["value"]) for axis in "AFCP"]
    if system_coverage != [9, 4, 1, 3]:
        raise ValueError(f"system literature coverage drift: {system_coverage}")
    if cluster_coverage != [5, 3, 1, 2]:
        raise ValueError(f"dependence-collapsed coverage drift: {cluster_coverage}")
    if abs(float(lit["A_enrichment_exact_p"]["value"]) - 0.002788543701171875) > 1e-15:
        raise ValueError("system A-enrichment P drift")
    if abs(float(dep["A_enrichment_exact_p"]["value"]) - 0.046875) > 1e-15:
        raise ValueError("cluster A-enrichment P drift")
    if [int(cf[k]["value"]) for k in ("canonical_systems", "canonical_cluster_axis_cells", "resolved_cluster_axis_cells", "significance_filter")] != [5, 20, 19, 0]:
        raise ValueError("candidate-free contract drift")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(16.5, 6.0), gridspec_kw={"width_ratios": [1.55, 1]})

    ax = axes[0]
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title("A  Observation-to-realization hierarchy")
    ys = [.87, .72, .57, .42, .27, .12]
    for i, (row, y) in enumerate(zip(framework, ys)):
        title = textwrap.fill(row["title"], width=23, break_long_words=False)
        ax.text(.045, y, title, fontsize=9.6, weight="bold", va="center", linespacing=1.0)
        ax.text(.39, y, row["empirical_anchor"], fontsize=8.2, va="center", wrap=True)
        if i < len(framework) - 1:
            ax.annotate("", xy=(.017, y - .08), xytext=(.017, y - .035), arrowprops={"arrowstyle": "->", "lw": 1.4})
    ax.text(.51, .015, "Each layer is measured separately; downstream outcomes do not fill upstream missing states.", ha="center", fontsize=8.4, weight="bold")

    ax = axes[1]
    ax.set_title("B  Formal database expansion strengthens the observation-process result")
    names = ["A", "F", "C", "P"]
    ax.bar(range(4), system_coverage)
    ax.set_xticks(range(4), names)
    ax.set_ylabel("Published biological systems measuring axis")
    ax.set_ylim(0, 10)
    for i, value in enumerate(system_coverage):
        ax.text(i, value + .15, str(value), ha="center", fontsize=9)
    ax.text(.37, .98, "After dependence collapse:", transform=ax.transAxes, va="top", fontsize=9.3, weight="bold")
    ax.text(.37, .90, "A/F/C/P = 5/3/1/2\nexact A-enrichment P = 0.046875", transform=ax.transAxes, va="top", fontsize=8.7)
    ax.text(.37, .72, "Candidate-free common set:", transform=ax.transAxes, va="top", fontsize=9.3, weight="bold")
    ax.text(.37, .64, "5 systems × 4 axes = 20 canonical cells\n19 resolved; 1 kept unresolved\nC. semiserrata not added without raw reads", transform=ax.transAxes, va="top", fontsize=8.5)
    ax.text(.37, .38, "Broader literature coverage updates\nascertainment, not the matched\ncandidate-free recurrence estimator.", transform=ax.transAxes, va="top", fontsize=8.8, weight="bold")

    fig.suptitle("Mechanistic feasibility, observation, recurrence, realization and event identity are distinct quantities", fontsize=12)
    fig.tight_layout(rect=[0, .02, 1, .93])
    svg = args.out_dir / "paper1_fig1_framework_v0_2_1.svg"
    png = args.out_dir / "paper1_fig1_framework_v0_2_1.png"
    fig.savefig(svg, bbox_inches="tight")
    fig.savefig(png, dpi=300, bbox_inches="tight")
    plt.close(fig)

    summary = {
        "status": "paper1_fig1_framework_v0_2_1_built",
        "system_coverage": system_coverage,
        "cluster_coverage": cluster_coverage,
        "system_A_enrichment_p": float(lit["A_enrichment_exact_p"]["value"]),
        "cluster_A_enrichment_p": float(dep["A_enrichment_exact_p"]["value"]),
        "candidate_free_systems": int(cf["canonical_systems"]["value"]),
        "scientific_change_scope": "literature ascertainment only",
        "outputs": [str(svg), str(png)],
    }
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
