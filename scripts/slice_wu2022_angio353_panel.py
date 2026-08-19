#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json
from pathlib import Path

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--panel',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); ap.add_argument('--shard',type=int,required=True); ap.add_argument('--n-shards',type=int,default=6); a=ap.parse_args()
    rows=list(csv.DictReader(a.panel.open(newline='',encoding='utf-8-sig')))
    assert len(rows)==93, len(rows); assert 0<=a.shard<a.n_shards
    out=[r for i,r in enumerate(rows) if i % a.n_shards == a.shard]
    assert out
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(out)
    print(json.dumps({'shard':a.shard,'n_shards':a.n_shards,'n_taxa':len(out),'first':out[0]['taxon'],'last':out[-1]['taxon']},indent=2))
if __name__=='__main__': main()
