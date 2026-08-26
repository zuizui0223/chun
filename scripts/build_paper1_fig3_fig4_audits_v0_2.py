#!/usr/bin/env python3
"""Build Paper 1 audit figures 3 and 4 from the frozen numeric input registry."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt


def read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        raise ValueError(f"empty input: {path}")
    return rows


def index(rows):
    return {r["input_id"]: r for r in rows}


def val(idx, key):
    return float(idx[key]["value"])


def validate(idx):
    expected = {
        "F3_LEGACY_TIPS": 93,
        "F3_ACCEPTED_SPECIES": 55,
        "F3_PROVISIONAL_HARD": 35,
        "F3_STRICT_SEED": 24,
        "F3_DOMINANT_SEED": 30,
        "F3_DEMOTED": 11,
        "F4_TOTAL_SPLITS": 50,
        "F4_SHARED_SPLITS": 46,
        "F4_RF": 8,
        "F4_NRF": 0.08,
        "F4_JACCARD": 0.8519,
    }
    missing = set(expected) - set(idx)
    if missing:
        raise ValueError(f"missing frozen numeric inputs: {sorted(missing)}")
    for k, x in expected.items():
        if abs(val(idx, k) - x) > 1e-9:
            raise ValueError(f"numeric drift for {k}: {val(idx,k)} != {x}")
    if idx["F3_ACCEPTED_SPECIES"]["result_id"] != "T01_WFO_ACCEPTED_TAXONOMY":
        raise ValueError("taxonomy result-id drift")
    if idx["F3_STRICT_SEED"]["result_id"] != "T02_WILD_COLOUR_AUDIT":
        raise ValueError("wild-colour result-id drift")
    if idx["F4_NRF"]["result_id"] != "P01_NUCLEAR_TOPOLOGY_CONCORDANCE":
        raise ValueError("topology result-id drift")


def arrow(ax, x0, x1, y, left, right, subtitle=""):
    ax.annotate("", xy=(x1, y), xytext=(x0, y), arrowprops={"arrowstyle": "->", "lw": 2})
    ax.text(x0, y + 0.13, left, ha="center", va="bottom", fontsize=10, weight="bold")
    ax.text(x1, y + 0.13, right, ha="center", va="bottom", fontsize=10, weight="bold")
    if subtitle:
        ax.text((x0 + x1) / 2, y - 0.15, subtitle, ha="center", va="top", fontsize=8)


def build_fig3(idx, out_dir):
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.5))
    a, b = axes
    a.axis("off")
    a.set_xlim(0, 1); a.set_ylim(0, 1)
    a.set_title("A  Accepted-taxonomy attrition")
    arrow(a, 0.18, 0.82, 0.52, "93 legacy tips", "55 accepted species", "WFO Plant List 2026-06 normalization")
    a.text(0.5, 0.2, "20 accepted groups contain >1 legacy tip", ha="center", fontsize=9)

    b.axis("off")
    b.set_xlim(0, 1); b.set_ylim(0, 1)
    b.set_title("B  Wild-colour evidence attrition")
    b.text(0.5, 0.82, "35 provisional hard states", ha="center", fontsize=10, weight="bold")
    b.annotate("", xy=(0.28, 0.38), xytext=(0.5, 0.73), arrowprops={"arrowstyle": "->", "lw": 2})
    b.annotate("", xy=(0.72, 0.38), xytext=(0.5, 0.73), arrowprops={"arrowstyle": "->", "lw": 2})
    b.text(0.28, 0.28, "Strict wild seed\n24 species", ha="center", fontsize=10, weight="bold")
    b.text(0.72, 0.28, "Dominant sensitivity\n30 species", ha="center", fontsize=10, weight="bold")
    b.text(0.5, 0.08, "11 provisional hard labels demoted in strict analysis", ha="center", fontsize=8.5)

    fig.suptitle("Taxonomy and trait evidence are filtered before macroevolutionary inference", fontsize=12)
    fig.tight_layout(rect=[0, 0.02, 1, 0.92])
    svg=out_dir/'paper1_fig3_evidence_attrition_v0_2.svg'; png=out_dir/'paper1_fig3_evidence_attrition_v0_2.png'
    fig.savefig(svg, bbox_inches='tight'); fig.savefig(png, dpi=300, bbox_inches='tight'); plt.close(fig)
    return [str(svg),str(png)]


def build_fig4(idx, out_dir):
    total=int(val(idx,'F4_TOTAL_SPLITS')); shared=int(val(idx,'F4_SHARED_SPLITS'))
    nrf=val(idx,'F4_NRF'); jac=val(idx,'F4_JACCARD'); rf=int(val(idx,'F4_RF'))
    fig, ax = plt.subplots(figsize=(9.5,4.5))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
    ax.set_title("Accepted-species nuclear topology concordance")
    ax.text(0.18,0.64,"FastTree / ASTRAL",ha='center',fontsize=10,weight='bold')
    ax.text(0.82,0.64,"IQ-TREE / UFBoot / ASTRAL",ha='center',fontsize=10,weight='bold')
    ax.annotate("",xy=(0.70,0.58),xytext=(0.30,0.58),arrowprops={"arrowstyle":"<->","lw":2})
    ax.text(0.5,0.72,f"{shared}/{total} nontrivial splits shared",ha='center',fontsize=13,weight='bold')
    ax.text(0.5,0.45,f"normalized RF = {nrf:.2f}    ·    split Jaccard = {jac:.4f}    ·    RF difference = {rf}",ha='center',fontsize=10)
    ax.text(0.5,0.23,"Four nontrivial splits differ; downstream colour patterns are therefore checked on both topologies.",ha='center',fontsize=9)
    fig.tight_layout()
    svg=out_dir/'paper1_fig4_topology_concordance_v0_2.svg'; png=out_dir/'paper1_fig4_topology_concordance_v0_2.png'
    fig.savefig(svg,bbox_inches='tight'); fig.savefig(png,dpi=300,bbox_inches='tight'); plt.close(fig)
    return [str(svg),str(png)]


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--numeric-inputs',type=Path,required=True)
    ap.add_argument('--out-dir',type=Path,required=True)
    args=ap.parse_args()
    rows=read(args.numeric_inputs); idx=index(rows); validate(idx)
    args.out_dir.mkdir(parents=True,exist_ok=True)
    outputs=build_fig3(idx,args.out_dir)+build_fig4(idx,args.out_dir)
    summary={
      'status':'paper1_fig3_fig4_audits_built',
      'numeric_registry':str(args.numeric_inputs),
      'fig3_contract':'93 legacy tips -> 55 accepted species; 35 provisional hard states -> strict 24 / dominant 30; 11 strict demotions',
      'fig4_contract':'46/50 nontrivial splits shared; normalized RF=0.08; split Jaccard=0.8519',
      'claim_boundary':'audit/concordance figures only; no trait-history or causal inference',
      'outputs':outputs,
    }
    (args.out_dir/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    main()
