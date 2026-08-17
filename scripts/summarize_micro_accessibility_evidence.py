#!/usr/bin/env python3
"""Summarize micro-only Camellia pigment accessibility evidence.

The primary quantity is an *evidence recurrence count*: the number of biological
independence clusters in which a node/module is explicitly reported to change.
It is NOT divided by all studies because assay opportunities differ and the
true denominator is unknown. Macro/phylogenetic evidence is excluded upstream
from the ledger by design.
"""
from __future__ import annotations
import argparse,csv
from collections import defaultdict
from pathlib import Path


def yn(x: str) -> bool:
    return x.strip().lower() == 'yes'


def tier(n_clusters: int, n_functional: int) -> str:
    if n_clusters >= 3 and n_functional >= 1:
        return 'A_recurrent_functionally_anchored'
    if n_clusters >= 3:
        return 'A_recurrent'
    if n_clusters >= 2 and n_functional >= 1:
        return 'B_repeated_functionally_anchored'
    if n_clusters >= 2:
        return 'B_repeated'
    if n_functional >= 1:
        return 'C_single_functional'
    return 'C_single'


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument('input',type=Path)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    with args.input.open(newline='',encoding='utf-8') as fh:
        rows=list(csv.DictReader(fh))
    groups=defaultdict(list)
    for r in rows:
        groups[(r['resolution'],r['feature'],r['module'])].append(r)
    out=[]
    for (resolution,feature,module),rs in sorted(groups.items()):
        clusters=sorted({r['independence_cluster'] for r in rs})
        scales=sorted({r['scale_class'] for r in rs})
        public_clusters=sorted({r['independence_cluster'] for r in rs if yn(r['public_raw_direct'])})
        functional_clusters=sorted({r['independence_cluster'] for r in rs if yn(r['functional_validation'])})
        directions=sorted({r['direction'] for r in rs if r['direction']})
        orthology=sorted({r['orthology_status'] for r in rs if r['orthology_status']})
        n=len(clusters);nf=len(functional_clusters)
        out.append({
            'resolution':resolution,
            'feature':feature,
            'module':module,
            'n_independent_micro_clusters':n,
            'n_scale_classes':len(scales),
            'n_public_raw_clusters':len(public_clusters),
            'n_functional_validation_clusters':nf,
            'evidence_tier':tier(n,nf),
            'independence_clusters':';'.join(clusters),
            'scale_classes':';'.join(scales),
            'direction_labels':';'.join(directions),
            'orthology_statuses':';'.join(orthology),
            'primary_macro_predictor':'n_independent_micro_clusters',
            'claim_boundary':'evidence recurrence/ranking only; unknown assay opportunity denominator prevents interpretation as a natural transition probability'
        })
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('w',newline='',encoding='utf-8') as fh:
        w=csv.DictWriter(fh,fieldnames=list(out[0]))
        w.writeheader();w.writerows(out)

if __name__=='__main__':main()
