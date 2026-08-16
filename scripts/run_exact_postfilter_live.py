#!/usr/bin/env python3
"""Resolve frozen thermal species against live GBIF taxonomy, then run exact postfilter."""
from __future__ import annotations
import argparse, csv, pathlib, subprocess, sys
from run_camellia_gbif_worldclim_niche import gbif_match

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--species',type=pathlib.Path,required=True); ap.add_argument('--out-dir',type=pathlib.Path,required=True); a=ap.parse_args(); a.out_dir.mkdir(parents=True,exist_ok=True)
    with a.species.open(newline='',encoding='utf-8-sig') as f: rows=list(csv.DictReader(f))
    matches=[]
    for r in rows:
        m=gbif_match(r['taxon']); matches.append({'taxon':r['taxon'],**m})
        print(r['taxon'],m.get('usageKey'),m.get('rank'),m.get('matchType'),m.get('status'),flush=True)
    mp=a.out_dir/'live_gbif_matches.csv'
    with mp.open('w',newline='',encoding='utf-8') as f:
        fields=[]; seen=set()
        for r in matches:
            for k in r:
                if k not in seen: fields.append(k); seen.add(k)
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(matches)
    cmd=[sys.executable,'scripts/postfilter_exact_gbif_thermal_results.py','--species',str(a.species),'--matches',str(mp),'--out-dir',str(a.out_dir/'exact')]
    return subprocess.call(cmd)
if __name__=='__main__': raise SystemExit(main())
