#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import matplotlib.pyplot as plt


CROSS_SPECIES_IDS = [
    "ECO_BIRD_JAPONICA_FRUIT",
    "ECO_BIRD_PETELOTII_FRUIT",
    "ECO_BIRD_OLEIFERA_FRUIT",
]
OLEIFERA_REPLICATION_IDS = [
    "ECO_BIRD_OLEIFERA_FRUIT",
    "ECO_BEE_OLEIFERA_LIU2025_CAGE",
]


def read_effects(path: Path) -> dict[str, dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    effects = {row["effect_id"]: row for row in rows}
    if len(effects) != len(rows):
        raise SystemExit("ecological effect registry contains duplicate effect IDs")
    required = set(CROSS_SPECIES_IDS + OLEIFERA_REPLICATION_IDS)
    missing = sorted(required - set(effects))
    if missing:
        raise SystemExit(f"ecological Fig. 6 is missing effect IDs: {missing}")
    return effects


def response_ratio(row: dict[str, str]) -> float:
    if row["effect_metric"] != "lnRR" or not row["effect_value"]:
        raise SystemExit(f"{row['effect_id']} is not a usable lnRR effect")
    if row.get("numerator_value") and row.get("denominator_value"):
        numerator = float(row["numerator_value"])
        denominator = float(row["denominator_value"])
        if numerator > 0 and denominator > 0:
            return numerator / denominator
    return math.exp(float(row["effect_value"]))


def close_enough(observed: float, expected: float, tolerance: float = 5e-4) -> bool:
    return math.isclose(observed, expected, rel_tol=tolerance, abs_tol=tolerance)


def save(fig, out_dir: Path) -> list[str]:
    names = []
    for suffix, kwargs in (("svg", {}), ("png", {"dpi": 240})):
        path = out_dir / f"Fig6_ecological_filtering.{suffix}"
        fig.savefig(path, bbox_inches="tight", **kwargs)
        names.append(path.name)
    plt.close(fig)
    return names


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", type=Path, required=True)
    ap.add_argument("--effects", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    a = ap.parse_args()
    a.out_dir.mkdir(parents=True, exist_ok=True)

    summary = json.loads(a.summary.read_text(encoding="utf-8"))
    effects = read_effects(a.effects)
    cross = summary["cross_species_pollinator_service"]
    oleifera = summary["oleifera_within_species_service_replication"]
    reliability = summary["pollinator_reliability_gradients"]
    mediation = summary["climate_season_pollinator_mediation"]
    abiotic = summary["direct_abiotic_floral_pigment"]

    cross_rows = [effects[effect_id] for effect_id in CROSS_SPECIES_IDS]
    cross_rr = [response_ratio(row) for row in cross_rows]
    computed_cross_mean = math.exp(sum(math.log(value) for value in cross_rr) / len(cross_rr))
    if not close_enough(computed_cross_mean, float(cross["geometric_mean_RR"])):
        raise SystemExit("cross-species Fig. 6 values drift from ecological summary")

    oleifera_rows = [effects[effect_id] for effect_id in OLEIFERA_REPLICATION_IDS]
    oleifera_rr = [response_ratio(row) for row in oleifera_rows]
    computed_oleifera_mean = math.exp(sum(math.log(value) for value in oleifera_rr) / len(oleifera_rr))
    if not close_enough(computed_oleifera_mean, float(oleifera["geometric_mean_RR"])):
        raise SystemExit("within-species Fig. 6 values drift from ecological summary")

    fig = plt.figure(figsize=(13.5, 8.5))
    grid = fig.add_gridspec(2, 2, height_ratios=[1.0, 1.08])

    ax = fig.add_subplot(grid[0, 0])
    labels = [
        f"{row['taxon'].replace('Camellia ', 'C. ')} ({row['visible_state']})"
        for row in cross_rows
    ]
    y = list(range(len(labels)))
    ax.barh(y, cross_rr)
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.axvline(1, linestyle="--", linewidth=1, color="0.25")
    ax.set_xlabel("Fruit-set response ratio: access / bird exclusion")
    ax.set_title("A  Cross-species pollinator-service magnitude")
    for index, value in enumerate(cross_rr):
        ax.text(value + 0.08, index, f"{value:.2f}x", va="center")
    ax.text(
        0.98,
        0.05,
        f"geometric mean = {cross['geometric_mean_RR']:.2f}x\n"
        f"leave-one-out = {cross['leave_one_out_RR_min']:.2f}-{cross['leave_one_out_RR_max']:.2f}x",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=10,
    )

    ax = fig.add_subplot(grid[0, 1])
    labels = ["bird access\nZhang 2024", "A. cerana cage\nLiu 2025"]
    ax.bar(labels, oleifera_rr)
    ax.axhline(1, linestyle="--", linewidth=1, color="0.25")
    ax.set_ylabel("Fruit-set response ratio")
    ax.set_ylim(0, max(oleifera_rr) * 1.45)
    ax.set_title("B  Independent service replication within C. oleifera")
    for index, value in enumerate(oleifera_rr):
        ax.text(index, value + 0.07, f"{value:.2f}x", ha="center")
    ax.text(
        0.04,
        0.96,
        f"2-study geometric mean = {oleifera['geometric_mean_RR']:.2f}x\n"
        f"reliability gradients = {reliability['expected_direction_count']}/"
        f"{reliability['k_effect_rows']} expected",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=9.8,
        bbox=dict(boxstyle="round,pad=0.3", fill=False),
    )

    ax = fig.add_subplot(grid[1, :])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title("C  Conditional ecological filtering: supported mechanism, unresolved history")
    boxes = [
        (0.08, 0.61, "Molecular\naccessibility", "multiple routes"),
        (0.27, 0.61, "Latent floral state", "pigment / spectra\nreward / phenology"),
        (
            0.55,
            0.61,
            "Pollinator service\n/ reliability",
            f"RR {cross['geometric_mean_RR']:.2f} across A/W/Y\n"
            f"{reliability['expected_direction_count']}/{reliability['k_effect_rows']} gradients",
        ),
        (0.76, 0.61, "Reproductive\nsuccess", "service-dependent"),
        (0.93, 0.61, "Evolutionary\npersistence", "local colour\nconservatism"),
    ]
    for x, y0, title, subtitle in boxes:
        ax.text(
            x,
            y0,
            title,
            ha="center",
            va="center",
            fontsize=10.5,
            bbox=dict(boxstyle="round,pad=0.45", fill=False),
        )
        ax.text(x, y0 - 0.20, subtitle, ha="center", va="center", fontsize=9)
    for x1, x2 in ((0.13, 0.21), (0.34, 0.47), (0.63, 0.70), (0.82, 0.88)):
        ax.annotate("", xy=(x2, 0.61), xytext=(x1, 0.61), arrowprops=dict(arrowstyle="->", lw=1.2))
    ax.text(
        0.55,
        0.91,
        "Flowering-window climate / season",
        ha="center",
        va="center",
        fontsize=10.5,
        bbox=dict(boxstyle="round,pad=0.4", fill=False),
    )
    ax.text(0.55, 0.79, f"{mediation['k_studies']} studies / {mediation['k_taxa']} taxa", ha="center", fontsize=9)
    ax.annotate("", xy=(0.55, 0.70), xytext=(0.55, 0.84), arrowprops=dict(arrowstyle="->", lw=1.2))
    ax.annotate("", xy=(0.47, 0.61), xytext=(0.34, 0.84), arrowprops=dict(arrowstyle="->", lw=1.0))
    ax.text(
        0.50,
        0.12,
        f"Direct abiotic floral-pigment evidence: {abiotic['k_independent_experiments']} independent experiment "
        "(cold + darkness confounded)\nAccepted-species transition causation: not identifiable across strict and "
        "dominant wild-colour scenarios",
        ha="center",
        va="center",
        fontsize=9.8,
    )
    fig.suptitle(
        "Fig. 6  Reproductive-service filtering is quantitatively supported, "
        "but historical colour-transition causation remains unresolved",
        fontsize=14,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    output_files = save(fig, a.out_dir)

    figure_summary = {
        "figure": "Fig6 ecological filtering v2",
        "source_summary": str(a.summary),
        "source_effect_registry": str(a.effects),
        "cross_species_effect_ids": CROSS_SPECIES_IDS,
        "oleifera_replication_effect_ids": OLEIFERA_REPLICATION_IDS,
        "cross_species_geometric_mean_RR": computed_cross_mean,
        "oleifera_geometric_mean_RR": computed_oleifera_mean,
        "output_files": output_files,
        "claim_boundary": "mechanism/service support; no accepted-species branch-causal assignment",
    }
    (a.out_dir / "Fig6_ecological_filtering_build_summary.json").write_text(
        json.dumps(figure_summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(figure_summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
