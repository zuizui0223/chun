#!/usr/bin/env python3
"""Build Paper 1 Fig. 6: pattern without robust event identity and cross-scale synthesis."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt


def read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        rows=list(csv.DictReader(fh))
    if not rows: raise ValueError(f"empty input: {path}")
    return rows


def validate(events, synthesis):
    expected={"strict":0,"dominant":1,"strict_x_dominant_shared":0}
    got={r['scenario']:int(r['strong_robust_transitions']) for r in events}
    if got!=expected: raise ValueError(f"event gate drift: {got}")
    layers={r['layer'] for r in synthesis}
    if layers!={"molecular_anthocyanin","molecular_yellow","macro_pattern","event_identity"}:
        raise ValueError(f"synthesis layer drift: {layers}")


def panel_a(ax, events):
    order=["strict","dominant","strict_x_dominant_shared"]
    lookup={r['scenario']:r for r in events}
    labels=["Strict wild","Dominant sensitivity","Shared strict × dominant"]
    values=[int(lookup[x]['strong_robust_transitions']) for x in order]
    ax.bar(range(3),values)
    ax.set_xticks(range(3),labels,rotation=15,ha='right')
    ax.set_ylim(0,1.35)
    ax.set_ylabel("Strong robust accepted-species transitions")
    for i,v in enumerate(values):
        ax.text(i,v+0.06,str(v),ha='center',fontsize=11,weight='bold')
    ax.set_title("A  Pattern survives; individual event identity does not")
    ax.text(1.0,1.18,"Cross-scenario accepted event count = 0",ha='center',fontsize=9)


def panel_b(ax, synthesis):
    ax.axis('off'); ax.set_xlim(0,1); ax.set_ylim(0,1)
    ax.set_title("B  Cross-scale synthesis")
    lookup={r['layer']:r for r in synthesis}
    keys=["molecular_anthocyanin","molecular_yellow","macro_pattern","event_identity"]
    ys=[0.82,0.61,0.40,0.19]
    for i,(k,y) in enumerate(zip(keys,ys)):
        r=lookup[k]
        ax.text(0.05,y,r['headline'],fontsize=9.5,weight='bold',va='center')
        ax.text(0.05,y-0.075,r['value'],fontsize=8.5,va='center')
        if i < len(keys)-1:
            ax.annotate("",xy=(0.90,y-0.16),xytext=(0.90,y-0.10),arrowprops={"arrowstyle":"->","lw":1.5})
    ax.text(0.52,0.02,"Identifiable pattern ≠ identifiable event ≠ identifiable cause",ha='center',fontsize=9.5,weight='bold')


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--events',type=Path,required=True)
    ap.add_argument('--synthesis',type=Path,required=True)
    ap.add_argument('--out-dir',type=Path,required=True)
    args=ap.parse_args()
    events=read(args.events); synthesis=read(args.synthesis); validate(events,synthesis)
    args.out_dir.mkdir(parents=True,exist_ok=True)
    fig,axes=plt.subplots(1,2,figsize=(13.5,5.2),gridspec_kw={'width_ratios':[0.9,1.35]})
    panel_a(axes[0],events); panel_b(axes[1],synthesis)
    fig.suptitle("Macroevolutionary pattern can be robust even when individual events and complete mechanistic packages are not",fontsize=12)
    fig.tight_layout(rect=[0,0.02,1,0.92])
    svg=args.out_dir/'paper1_fig6_identifiability_synthesis_v0_2.svg'
    png=args.out_dir/'paper1_fig6_identifiability_synthesis_v0_2.png'
    fig.savefig(svg,bbox_inches='tight'); fig.savefig(png,dpi=300,bbox_inches='tight'); plt.close(fig)
    summary={
      'status':'paper1_fig6_identifiability_built',
      'event_rows':len(events),'synthesis_rows':len(synthesis),
      'cross_scenario_robust_events':0,
      'claim_boundary':'synthesis of frozen results; no branch-causal inference is introduced by the figure builder',
      'outputs':[str(svg),str(png)]}
    (args.out_dir/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))

if __name__=='__main__': main()
