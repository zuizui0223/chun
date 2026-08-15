#!/usr/bin/env python3
"""Count-controlled visible-state concentration across Fan 2026 source sections.

This is a coarse historical/taxonomic-structure diagnostic, not a phylogenetic
analysis. It operates on the deterministic species seed rebuilt directly from
Fan et al. 2026 Data S1. Rows whose source `section` is the literal country label
`Vietnam` are excluded because that is not a formal section assignment.

For each visible state A/W/Y, preserve the observed state count and shuffle state
labels across the admitted species 100,000 times. Compare observed section breadth
and Shannon entropy to the resulting null distribution.
"""
from __future__ import annotations

import argparse
import csv
import math
import re
from collections import Counter
from pathlib import Path

import numpy as np


def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def norm_section(value: str) -> str:
    parts=[]
    for p in str(value or "").split(";"):
        p=re.sub(r"\s+", " ", p.strip()).lower()
        if not p or p == "vietnam":
            continue
        p=re.sub(r"^sect\.\s*", "sect. ", p)
        if p not in parts:
            parts.append(p)
    return ";".join(sorted(parts))


def shannon(values) -> float:
    c=np.array(list(Counter(values).values()), dtype=float)
    p=c/c.sum()
    return float(-(p*np.log(p)).sum())


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("input", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--section-table", type=Path, required=True)
    ap.add_argument("--permutations", type=int, default=100000)
    ap.add_argument("--seed", type=int, default=20260815)
    args=ap.parse_args()

    rows=[]
    for r in read_csv(args.input):
        sec=norm_section(r.get("section", ""))
        st=r.get("colour_state", "")
        if sec and st in {"A","W","Y"}:
            rows.append({"taxon":r["taxon"], "section":sec, "state":st})
    if not rows:
        raise SystemExit("No section-coded A/W/Y species")

    sections=np.array([r["section"] for r in rows], dtype=object)
    states=np.array([r["state"] for r in rows], dtype=object)
    state_levels=["A","W","Y"]
    section_levels=sorted(set(sections))

    observed={}
    for st in state_levels:
        vals=sections[states==st]
        observed[st]={
            "n_species":int(len(vals)),
            "breadth":int(len(set(vals))),
            "entropy":shannon(vals),
        }

    rng=np.random.default_rng(args.seed)
    b=args.permutations
    breadth=np.empty((b,3), dtype=np.int16)
    entropy=np.empty((b,3), dtype=float)
    sec_index={s:i for i,s in enumerate(section_levels)}
    sec_i=np.array([sec_index[s] for s in sections], dtype=int)
    for i in range(b):
        perm=rng.permutation(states)
        for j,st in enumerate(state_levels):
            counts=np.bincount(sec_i[perm==st], minlength=len(section_levels))
            nz=counts[counts>0]
            breadth[i,j]=len(nz)
            p=nz/nz.sum()
            entropy[i,j]=float(-(p*np.log(p)).sum())

    out=[]
    for j,st in enumerate(state_levels):
        o=observed[st]
        p_b=(int(np.sum(breadth[:,j] <= o["breadth"]))+1)/(b+1)
        p_h=(int(np.sum(entropy[:,j] <= o["entropy"]+1e-12))+1)/(b+1)
        out.append({
            "visible_state":st,
            "n_species":o["n_species"],
            "n_sections_total":len(section_levels),
            "observed_section_breadth":o["breadth"],
            "expected_section_breadth":f"{breadth[:,j].mean():.8f}",
            "lower_tail_breadth_p":f"{p_b:.10f}",
            "observed_section_entropy":f"{o['entropy']:.10f}",
            "expected_section_entropy":f"{entropy[:,j].mean():.10f}",
            "lower_tail_entropy_p":f"{p_h:.10f}",
            "permutations":b,
            "seed":args.seed,
            "interpretation":(
                "more section-concentrated than expected for state sample size"
                if p_b<0.05 and p_h<0.05 else
                "no count-controlled evidence of excess section concentration"
            ),
            "claim_ceiling":"Fan2026 traditional-section proxy; not a nuclear phylogeny or transition-rate estimate",
        })

    table=[]
    for sec in section_levels:
        rr=states[sections==sec]
        c=Counter(rr)
        table.append({"section":sec,"A":c["A"],"W":c["W"],"Y":c["Y"],"n":len(rr)})

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as fh:
        w=csv.DictWriter(fh, fieldnames=list(out[0]))
        w.writeheader(); w.writerows(out)
    with args.section_table.open("w", newline="", encoding="utf-8") as fh:
        w=csv.DictWriter(fh, fieldnames=list(table[0]))
        w.writeheader(); w.writerows(table)
    for r in out: print(r)
    for r in table: print(r)


if __name__=="__main__":
    main()
