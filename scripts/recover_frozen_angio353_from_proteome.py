#!/usr/bin/env python3
"""Recover the already-frozen Angiosperms353 loci from an annotated proteome.

The admitted locus set is read from the runtime91 global occupancy artifact; this
script cannot add new loci.  It selects the highest-bitscore qualifying protein
HSP per frozen locus and writes compact sequence-bearing evidence for later
MAFFT --add / topology sensitivity analysis.
"""
from __future__ import annotations
import argparse,csv,json,re
from pathlib import Path

FIELDS=['qseqid','sseqid','pident','length','qlen','slen','evalue','bitscore','qstart','qend','sstart','send','qseq']

def locus_id(s: str) -> str:
    x=str(s).split('-')[-1]
    return x if x.isdigit() else str(s)

def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument('--taxon',required=True)
    ap.add_argument('--hits',type=Path,required=True)
    ap.add_argument('--occupancy',type=Path,required=True)
    ap.add_argument('--out-dir',type=Path,required=True)
    ap.add_argument('--min-subject-coverage',type=float,default=0.45)
    ap.add_argument('--min-aa',type=int,default=80)
    a=ap.parse_args(); a.out_dir.mkdir(parents=True,exist_ok=True)

    occ=list(csv.DictReader(a.occupancy.open(newline='',encoding='utf-8-sig')))
    frozen={r['locus'] for r in occ if str(r.get('admitted','')).lower() in {'true','1','yes'} and float(r['occupancy'])>=0.80}
    if len(frozen)!=339: raise SystemExit(f'expected 339 frozen loci, got {len(frozen)}')

    best={}
    with a.hits.open(encoding='utf-8') as f:
        for line in f:
            if not line.strip(): continue
            vals=line.rstrip('\n').split('\t')
            if len(vals)!=len(FIELDS): continue
            h=dict(zip(FIELDS,vals)); loc=locus_id(h['sseqid'])
            if loc not in frozen: continue
            length=int(h['length']); slen=max(1,int(h['slen'])); scov=length/slen
            seq=re.sub(r'[^A-Z*]','',h['qseq'].upper()).replace('*','X')
            if length<a.min_aa or scov<a.min_subject_coverage or len(seq)<a.min_aa: continue
            rec={'taxon':a.taxon,'locus':loc,'qseqid':h['qseqid'],'sseqid':h['sseqid'],
                 'pident':float(h['pident']),'aligned_aa':length,'subject_coverage':scov,
                 'evalue':float(h['evalue']),'bitscore':float(h['bitscore']),'protein_hsp_seq':seq}
            if loc not in best or rec['bitscore']>best[loc]['bitscore']: best[loc]=rec

    rows=[best[k] for k in sorted(best,key=lambda x:int(x) if x.isdigit() else x)]
    with (a.out_dir/'best_hits.csv').open('w',newline='',encoding='utf-8') as f:
        fields=list(rows[0]) if rows else ['taxon','locus']
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
    fasta=a.out_dir/'frozen_markers.faa'
    with fasta.open('w',encoding='utf-8') as f:
        for r in rows:
            f.write(f">{a.taxon.replace(' ','_')}|locus_{r['locus']}|{r['qseqid']}\n{r['protein_hsp_seq']}\n")
    summary={'taxon':a.taxon,'frozen_loci':len(frozen),'recovered_loci':len(rows),
             'recovery_fraction':len(rows)/len(frozen),'min_subject_coverage':a.min_subject_coverage,
             'min_aa':a.min_aa,'missing_loci':sorted(frozen-set(best),key=lambda x:int(x) if x.isdigit() else x),
             'claim_ceiling':'recovery of the pre-frozen 339 nuclear marker definitions from one annotated proteome; no ecological state used in marker choice and no topology inference'}
    (a.out_dir/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))

if __name__=='__main__': main()
