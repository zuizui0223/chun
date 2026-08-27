#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import textwrap
from pathlib import Path

import matplotlib.pyplot as plt


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def index(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["result_id"].strip(): row for row in rows}


def wrap(text: str, width: int = 60) -> str:
    return "\n".join(textwrap.wrap(text, width=width, break_long_words=False))


def draw_cards(path_base: Path, title: str, cards: list[tuple[str, str, str]]) -> None:
    fig_h = max(4.8, 1.65 * len(cards) + 1.1)
    fig, ax = plt.subplots(figsize=(11, fig_h))
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.text(0.02, 0.965, title, fontsize=15, fontweight="bold", va="top")
    usable_top = 0.88
    step = usable_top / max(len(cards), 1)
    for i, (label, claim, boundary) in enumerate(cards):
        y = usable_top - i * step
        ax.text(0.03, y, label, fontsize=12, fontweight="bold", va="top")
        ax.text(0.30, y, wrap(claim), fontsize=10.5, va="top")
        ax.text(0.30, y - step * 0.49, wrap("Boundary: " + boundary), fontsize=9, va="top")
        if i < len(cards) - 1:
            ax.plot([0.02, 0.98], [y - step * 0.78, y - step * 0.78], linewidth=0.8)
    fig.tight_layout()
    fig.savefig(path_base.with_suffix(".png"), dpi=220, bbox_inches="tight")
    fig.savefig(path_base.with_suffix(".svg"), bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    a = ap.parse_args()
    rows = read_csv(a.registry)
    by_id = index(rows)

    molecular_ids = [
        "M01_FLS_SAME_LINEAGE",
        "M02_DFR_PARALOG_SUBSTITUTION",
        "M03_ANS_COPY_DIRECTION_HETEROGENEITY",
        "M04_ANR_COPY_DIRECTION_HETEROGENEITY",
    ]
    ecology_ids = [
        "E01_UNIVERSAL_COLD_CHAIN_NOT_SUPPORTED",
        "E02_VISIBLE_HUE_POLLINATOR_ALIASING",
    ]
    missing = [rid for rid in molecular_ids + ecology_ids if rid not in by_id]
    if missing:
        raise SystemExit(f"registry missing supplementary results: {missing}")

    a.out_dir.mkdir(parents=True, exist_ok=True)
    molecular_labels = ["FLS", "DFR", "ANS/LDOX", "ANR"]
    molecular_cards = [
        (label, by_id[rid]["value_summary"], by_id[rid]["claim_boundary"])
        for label, rid in zip(molecular_labels, molecular_ids)
    ]
    draw_cards(
        a.out_dir / "FigS1_molecular_support_v0_2",
        "Figure S1. Sequence- and copy-aware support for flexible molecular implementation",
        molecular_cards,
    )

    ecology_labels = ["Climate screen", "Pollination/function screen"]
    ecology_cards = [
        (label, by_id[rid]["value_summary"], by_id[rid]["claim_boundary"])
        for label, rid in zip(ecology_labels, ecology_ids)
    ]
    draw_cards(
        a.out_dir / "FigS2_ecology_boundary_v0_2",
        "Figure S2. Ecological evidence is retained as filtering/persistence context",
        ecology_cards,
    )

    outputs = [
        "FigS1_molecular_support_v0_2.png",
        "FigS1_molecular_support_v0_2.svg",
        "FigS2_ecology_boundary_v0_2.png",
        "FigS2_ecology_boundary_v0_2.svg",
    ]
    for name in outputs:
        if not (a.out_dir / name).exists() or (a.out_dir / name).stat().st_size < 1000:
            raise SystemExit(f"supplementary figure output missing or too small: {name}")

    summary = {
        "status": "paper1_v0_2_supplementary_figures_built",
        "source_registry": str(a.registry),
        "molecular_result_ids": molecular_ids,
        "ecology_result_ids": ecology_ids,
        "scientific_results_changed": False,
        "outputs": outputs,
    }
    (a.out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
