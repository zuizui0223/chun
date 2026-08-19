#!/usr/bin/env python3
"""Materialize per-locus protein FASTAs from globally merged Wu Angiosperms353 best hits.

Input is the frozen global-occupancy artifact produced by the runtime recovery
workflow. Only loci admitted by the frozen occupancy screen are materialized.
Flower-colour state is ignored here by design.
"""
from __future__ import annotations
import argparse,csv,json,re
from pathlib import Path


def slug(s: str) -> str:
    return re.sub(r'[^A-Za-z0-9]+','_',s).strip('_')


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--best-hits',type=Path,required=True)
    ap.add_argument('--occupancy',type=Path,required=True)
    ap.add_argument('--out-dir',type=Path,required=True)
    ap.add_argument('--min-occupancy',type=float,default=0.80)
    ap.add_argument('--min-taxa',type=int,default=4)
    a=ap.parse_args()

    occ=list(csv.DictReader(a.occupancy.open(newline='',encoding='utf-8-sig')))
    admitted={r['locus'] for r in occ if str(r.get('admitted','')).lower() in {'true','1','yes'} and float(r['occupancy'])>=a.min_occupancy}
    hits=list(csv.DictReader(a.best_hits.open(newline='',encoding='utf-8-sig')))
    by={}
    for r in hits:
        loc=r['locus']
        if loc not in admitted: continue
        seq=(r.get('translated_hsp_seq') or r.get('qseq_translated') or '').replace('*','X').upper()
        if not seq:
            # global best_hits created from per-shard compact ledgers may not yet carry sequence.
            # Fail loudly rather than infer from qseqid or another source.
            raise SystemExit(f'missing translated sequence for admitted locus {loc}, taxon {r.get("taxon")}')
        by.setdefault(loc,[]).append((r['taxon'],seq))

    a.out_dir.mkdir(parents=True,exist_ok=True)
    made=[]
    for loc in sorted(admitted,key=lambda x:int(x) if x.isdigit() else x):
        recs=by.get(loc,[])
        if len(recs)<a.min_taxa:
            raise SystemExit(f'admitted locus {loc} has only {len(recs)} sequences in merged best hits')
        p=a.out_dir/f'locus_{loc}.faa'
        with p.open('w',encoding='utf-8') as f:
            for tax,seq in sorted(recs):
                f.write(f'>{slug(tax)}\n')
                for i in range(0,len(seq),80): f.write(seq[i:i+80]+'\n')
        made.append({'locus':loc,'n_taxa':len(recs),'path':str(p)})
    summary={'admitted_loci':len(admitted),'materialized_loci':len(made),'min_occupancy':a.min_occupancy,'claim_ceiling':'protein marker FASTAs materialized only from the frozen global best-hit/occupancy artifact; no topology or colour inference'}
    (a.out_dir/'materialization_summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))

if __name__=='__main__': main()
