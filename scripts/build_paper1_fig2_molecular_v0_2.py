#!/usr/bin/env python3
"""Build Paper 1 Fig. 2 from frozen molecular source tables.

This is a presentation-layer script only. It does not infer directions, fill missing
axes, or recalculate recurrence from raw data. Those quantities are frozen upstream.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt


AXES = ("A", "F", "C", "P")
CLUSTERS = (
    "CJAPONICA",
    "CRETICULATA",
    "CSIN_WHITE_PINK",
    "CNITIDISSIMA",
    "CPERPETUA",
)
CLASS_LABEL = {
    "anthocyanin_gain": "Anthocyanin gain",
    "yellow_development": "Yellow development",
}
METRIC_LABEL = {
    "exact_signature_recurrence": "Exact signature recurrence",
    "pairwise_axis_concordance": "Pairwise A/F/C/P concordance",
}
DIRECTION_SYMBOL = {"up": "↑", "down": "↓", "same": "=", "unresolved": "?"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        raise ValueError(f"empty input: {path}")
    return rows


def as_float(x: str) -> float:
    return float(x)


def validate(signatures: list[dict[str, str]], intervals: list[dict[str, str]], overlap: list[dict[str, str]]) -> None:
    if len(signatures) != 20:
        raise ValueError(f"expected 20 signature rows; got {len(signatures)}")
    keys = {(r["dependence_cluster"], r["axis"]) for r in signatures}
    expected = {(c, a) for c in CLUSTERS for a in AXES}
    if keys != expected:
        raise ValueError(f"signature grid drift: missing={sorted(expected-keys)} extra={sorted(keys-expected)}")
    for r in signatures:
        if r["direction"] not in DIRECTION_SYMBOL:
            raise ValueError(f"bad direction: {r}")
        if r["status"] not in {"resolved", "unresolved"}:
            raise ValueError(f"bad status: {r}")
        if r["status"] == "unresolved" and r["direction"] != "unresolved":
            raise ValueError(f"unresolved status must have unresolved direction: {r}")
    if len(intervals) != 8:
        raise ValueError(f"expected 8 interval rows; got {len(intervals)}")
    expected_intervals = {
        (tc, rg, mt)
        for tc in CLASS_LABEL
        for rg in ("literature", "candidate_free")
        for mt in METRIC_LABEL
    }
    got_intervals = {(r["transition_class"], r["regime"], r["metric"]) for r in intervals}
    if got_intervals != expected_intervals:
        raise ValueError("interval source grid is incomplete or duplicated")
    for r in intervals:
        lo, hi = as_float(r["minimum"]), as_float(r["maximum"])
        if not (0 <= lo <= hi <= 1):
            raise ValueError(f"invalid interval: {r}")
    if {r["transition_class"] for r in overlap} != set(CLASS_LABEL):
        raise ValueError("overlap table must contain both transition classes")


def plot_signature_panel(ax, signatures: list[dict[str, str]]) -> None:
    by_key = {(r["dependence_cluster"], r["axis"]): r for r in signatures}
    labels = {r["dependence_cluster"]: r["label"] for r in signatures}

    ax.set_xlim(-0.5, len(AXES) - 0.5)
    ax.set_ylim(len(CLUSTERS) - 0.5, -0.5)
    ax.set_xticks(range(len(AXES)), AXES)
    ax.set_yticks(range(len(CLUSTERS)), [labels[c] for c in CLUSTERS])
    ax.set_xlabel("Frozen pigment-state axis")

    for y, cluster in enumerate(CLUSTERS):
        for x, axis in enumerate(AXES):
            r = by_key[(cluster, axis)]
            symbol = DIRECTION_SYMBOL[r["direction"]]
            if r["status"] == "unresolved":
                text = "?"
            else:
                value = float(r["effect_value"])
                text = f"{symbol}\n{value:+.2f}"
            ax.text(x, y, text, ha="center", va="center", fontsize=9)
    for x in range(len(AXES) + 1):
        ax.axvline(x - 0.5, linewidth=0.5)
    for y in range(len(CLUSTERS) + 1):
        ax.axhline(y - 0.5, linewidth=0.5)
    ax.set_title("A  Candidate-free A/F/C/P states")


def plot_interval_panel(ax, transition_class: str, intervals: list[dict[str, str]], overlap_row: dict[str, str], panel: str) -> None:
    subset = [r for r in intervals if r["transition_class"] == transition_class]
    order = [
        ("exact_signature_recurrence", "literature"),
        ("exact_signature_recurrence", "candidate_free"),
        ("pairwise_axis_concordance", "literature"),
        ("pairwise_axis_concordance", "candidate_free"),
    ]
    lookup = {(r["metric"], r["regime"]): r for r in subset}
    y_positions = [3, 2, 1, 0]
    y_labels = []
    for y, key in zip(y_positions, order):
        r = lookup[key]
        lo, hi = as_float(r["minimum"]), as_float(r["maximum"])
        ax.hlines(y, lo, hi, linewidth=3)
        ax.plot([lo, hi], [y, y], "o")
        regime = "Literature" if r["regime"] == "literature" else "Candidate-free"
        metric = METRIC_LABEL[r["metric"]]
        y_labels.append(f"{metric}\n{regime}")
        ax.text(min(1.01, hi + 0.02), y, f"{lo:.2f}–{hi:.2f}" if hi != lo else f"{lo:.2f}", va="center", fontsize=8)

    ax.set_yticks(y_positions, y_labels)
    ax.set_xlim(0, 1.08)
    ax.set_xlabel("Identified recurrence / concordance")
    ax.set_title(f"{panel}  {CLASS_LABEL[transition_class]}")
    # Direct literature-versus-candidate-free agreement is retained in the
    # source table and summary, but not overplotted on the interval panel.


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--signatures", type=Path, required=True)
    ap.add_argument("--intervals", type=Path, required=True)
    ap.add_argument("--overlap", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()

    signatures = read_csv(args.signatures)
    intervals = read_csv(args.intervals)
    overlap = read_csv(args.overlap)
    validate(signatures, intervals, overlap)
    overlap_map = {r["transition_class"]: r for r in overlap}

    args.out_dir.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 3, figsize=(15.5, 5.8), gridspec_kw={"width_ratios": [1.45, 1, 1]})
    plot_signature_panel(axes[0], signatures)
    plot_interval_panel(axes[1], "anthocyanin_gain", intervals, overlap_map["anthocyanin_gain"], "B")
    plot_interval_panel(axes[2], "yellow_development", intervals, overlap_map["yellow_development"], "C")
    fig.suptitle("Repeated flower-colour change does not imply one recurrent whole pigment-state package", fontsize=12)
    fig.text(0.02, 0.015, "Panel A effect values: Hedges' g for red/pink contrasts; OLS S1–S5 slope for yellow trajectories. ? = unresolved under the frozen rule.", fontsize=8)
    fig.tight_layout(rect=[0, 0.045, 1, 0.93])

    svg = args.out_dir / "paper1_fig2_molecular_v0_2.svg"
    png = args.out_dir / "paper1_fig2_molecular_v0_2.png"
    fig.savefig(svg, bbox_inches="tight")
    fig.savefig(png, dpi=300, bbox_inches="tight")
    plt.close(fig)

    summary = {
        "status": "paper1_fig2_molecular_built",
        "signature_rows": len(signatures),
        "interval_rows": len(intervals),
        "overlap_rows": len(overlap),
        "source_run": "32929846096",
        "panels": {
            "A": "five-system candidate-free A/F/C/P direction/effect grid",
            "B": "anthocyanin-gain literature versus candidate-free identified sets",
            "C": "yellow-development literature versus candidate-free identified sets",
        },
        "outputs": [str(svg), str(png)],
        "claim_boundary": "presentation only; no direction inference, missing-axis imputation, or significance filtering occurs in this script",
    }
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
