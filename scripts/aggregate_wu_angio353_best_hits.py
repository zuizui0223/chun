#!/usr/bin/env python3
"""Aggregate per-shard Angiosperms353 best hits across the runtime-admitted Wu panel.

This recomputes locus occupancy globally after all serialized recovery shards
have completed. It does not infer a phylogeny or join flower-colour states.
"""
from __future__ import annotations
import argparse,csv,glob,json
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--panel',type=Path,required=True)
    ap.add_argument('--best-hit-glob',required=True)
    ap.add_argument('--output-dir',type=Path,required=True)
    ap.add_argument('--min-occupancy',type=float,default=0.80)
    ap.add_argument('--expected-taxa',type=int,default=91)
    a=ap.parse_args()
    panel=list(csv.DictReader(a.panel.open(newline='',encoding='utf-8-sig')))
    taxa=[r['taxon'] for r in panel]
    assert len(taxa)==a.expected_taxa,(len(taxa),a.expected_taxa)
    assert len(taxa)==len(set(taxa))
    files=sorted(glob.glob(a.best_hit_glob,recursive=True))
    if not files: raise SystemExit('no best_hits files matched')
    rows=[]
    for p in files:
        with open(p,newline='',encoding='utf-8-sig') as f: rows.extend(csv.DictReader(f))
    seen={}
    for r in rows:
        tax=r['taxon']; loc=r['locus']
        if tax not in set(taxa): raise SystemExit(f'best hit taxon outside panel: {tax}')
        key=(tax,loc)
        score=float(r.get('bitscore') or 0)
        if key not in seen or score>float(seen[key].get('bitscore') or 0): seen[key]=r
    loci=sorted({loc for _,loc in seen},key=lambda x:int(x) if str(x).isdigit() else str(x))
    occ=[]; admitted=[]
    for loc in loci:
        present=sorted(t for t in taxa if (t,loc) in seen)
        o=len(present)/len(taxa)
        rec={'locus':loc,'n_taxa':len(present),'occupancy':o,'admitted':o>=a.min_occupancy}
        occ.append(rec)
        if rec['admitted']: admitted.append(loc)
    a.output_dir.mkdir(parents=True,exist_ok=True)
    with (a.output_dir/'locus_occupancy.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=['locus','n_taxa','occupancy','admitted']);w.writeheader();w.writerows(occ)
    allrows=[seen[k] for k in sorted(seen)]
    if allrows:
        with (a.output_dir/'best_hits_merged.csv').open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=allrows[0].keys());w.writeheader();w.writerows(allrows)
    thresholds={str(x):sum(r['occupancy']>=x for r in occ) for x in (0.8,0.9,0.95,1.0)}
    summary={'n_panel_taxa':len(taxa),'n_input_files':len(files),'n_unique_taxon_locus_hits':len(seen),'candidate_loci':len(loci),'min_occupancy':a.min_occupancy,'admitted_loci':len(admitted),'loci_by_occupancy_threshold':thresholds,'admitted_loci_ids':admitted,'claim_ceiling':'global marker-occupancy screen on runtime-admitted nuclear panel only; no tree or colour inference'}
    (a.output_dir/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))
if __name__=='__main__': main()
