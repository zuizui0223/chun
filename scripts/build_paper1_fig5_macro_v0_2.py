#!/usr/bin/env python3
"""Build Paper 1 Fig. 5 from frozen accepted-species macro source tables.

Presentation layer only. It visualizes topology/coding robustness and does not infer
ancestral states, branch transitions, or ecological causes.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        raise ValueError(f"empty input: {path}")
    return rows


def validate(nearest: list[dict[str, str]], robustness: list[dict[str, str]]) -> None:
    if len(nearest) != 4:
        raise ValueError(f"expected four topology x coding nearest-same rows; got {len(nearest)}")
    expected = {
        ("FastTree/ASTRAL", "strict"),
        ("FastTree/ASTRAL", "dominant"),
        ("IQ-TREE/UFBoot-ASTRAL", "strict"),
        ("IQ-TREE/UFBoot-ASTRAL", "dominant"),
    }
    if {(r["topology"], r["coding"]) for r in nearest} != expected:
        raise ValueError("nearest-same source does not contain exactly the four frozen scenarios")
    for r in nearest:
        obs = float(r["observed_nearest_same"])
        null = float(r["null_mean_nearest_same"])
        p = float(r["p_value"])
        if not (obs < null and 0 <= p <= 1):
            raise ValueError(f"nearest-same contract drift: {r}")
    if len(robustness) != 8:
        raise ValueError(f"expected eight robustness rows; got {len(robustness)}")
    if {r["claim_id"] for r in robustness} != {"GLOBAL_MPD", "A_SPECIFIC"}:
        raise ValueError("robustness table must contain GLOBAL_MPD and A_SPECIFIC only")


def label_scenario(r: dict[str, str]) -> str:
    topo = "FastTree" if r["topology"].startswith("FastTree") else "UFBoot"
    coding = "strict wild" if r["coding"] == "strict" else "dominant sensitivity"
    return f"{topo} · {coding}"


def panel_a(ax, nearest: list[dict[str, str]]) -> None:
    order = [
        ("FastTree/ASTRAL", "strict"),
        ("FastTree/ASTRAL", "dominant"),
        ("IQ-TREE/UFBoot-ASTRAL", "strict"),
        ("IQ-TREE/UFBoot-ASTRAL", "dominant"),
    ]
    lookup = {(r["topology"], r["coding"]): r for r in nearest}
    y = list(range(3, -1, -1))
    labels = []
    for yi, key in zip(y, order):
        r = lookup[key]
        obs = float(r["observed_nearest_same"])
        null = float(r["null_mean_nearest_same"])
        ax.hlines(yi, obs, null, linewidth=2.5)
        ax.plot(obs, yi, "o", markersize=7)
        ax.plot(null, yi, "s", markersize=6)
        ax.text(null + 0.08, yi, f"P={r['p_label']}", va="center", fontsize=8)
        labels.append(label_scenario(r))
    ax.set_yticks(y, labels)
    ax.set_xlim(3.0, 5.35)
    ax.set_xlabel("Nearest same-colour edge distance")
    ax.set_title("A  Local colour conservatism survives topology and coding")
    ax.text(3.04, -0.62, "● observed   ■ count-preserving null mean   (lower observed = local clustering)", fontsize=8)
    ax.grid(axis="x", linewidth=0.4, alpha=0.4)


def short_status(row: dict[str, str]) -> str:
    status = row["status"]
    if status == "not_estimable":
        return "N/A\nstrict A singleton"
    if status == "demoted":
        return f"demoted\nP={row['p_label']}"
    if status == "sensitivity_positive":
        return f"sensitivity +\nP={row['p_label']}"
    return status


def panel_b(ax, robustness: list[dict[str, str]]) -> None:
    ax.axis("off")
    columns = [
        ("FastTree/ASTRAL", "strict", "FastTree\nstrict"),
        ("FastTree/ASTRAL", "dominant", "FastTree\ndominant"),
        ("IQ-TREE/UFBoot-ASTRAL", "strict", "UFBoot\nstrict"),
        ("IQ-TREE/UFBoot-ASTRAL", "dominant", "UFBoot\ndominant"),
    ]
    row_defs = [
        ("GLOBAL_MPD", "Global same-colour MPD"),
        ("A_SPECIFIC", "A-specific clustering"),
    ]
    lookup = {(r["claim_id"], r["topology"], r["coding"]): r for r in robustness}
    ax.set_xlim(0, 5.25)
    ax.set_ylim(0, 3.1)
    ax.text(0, 2.92, "B  Robust main pattern versus demoted sensitivities", fontsize=11, weight="bold")
    for j, (_topo, _coding, label) in enumerate(columns):
        ax.text(1.45 + j * 0.92, 2.48, label, ha="center", va="center", fontsize=8.5, weight="bold")
    for i, (claim_id, row_label) in enumerate(row_defs):
        y = 1.65 - i * 1.02
        ax.text(0.02, y, row_label, va="center", fontsize=9, weight="bold")
        for j, (topo, coding, _label) in enumerate(columns):
            r = lookup[(claim_id, topo, coding)]
            ax.text(1.45 + j * 0.92, y, short_status(r), ha="center", va="center", fontsize=8)
    ax.text(0.02, 0.05, "Retained headline: nearest-same-colour local conservatism. Global MPD is topology-sensitive; A-specific clustering is coding-sensitive.", fontsize=8)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--nearest", type=Path, required=True)
    ap.add_argument("--robustness", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()

    nearest = read_csv(args.nearest)
    robustness = read_csv(args.robustness)
    validate(nearest, robustness)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(14.5, 5.4), gridspec_kw={"width_ratios": [1.05, 1.35]})
    panel_a(axes[0], nearest)
    panel_b(axes[1], robustness)
    fig.suptitle("Accepted wild flower colours show robust local, not universal global, phylogenetic structure", fontsize=12)
    fig.tight_layout(rect=[0, 0.035, 1, 0.93])

    svg = args.out_dir / "paper1_fig5_macro_v0_2.svg"
    png = args.out_dir / "paper1_fig5_macro_v0_2.png"
    fig.savefig(svg, bbox_inches="tight")
    fig.savefig(png, dpi=300, bbox_inches="tight")
    plt.close(fig)

    summary = {
        "status": "paper1_fig5_macro_built",
        "nearest_rows": len(nearest),
        "robustness_rows": len(robustness),
        "headline": "nearest-same-colour local conservatism survives topology and wild-colour coding",
        "demoted": ["global same-colour MPD", "strict A-specific clustering"],
        "claim_boundary": "unrooted pattern visualization only; no ancestral-state, transition-event, or causal inference",
        "outputs": [str(svg), str(png)],
    }
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
