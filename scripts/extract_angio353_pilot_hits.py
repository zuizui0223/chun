#!/usr/bin/env python3
"""Extract one best translated Angiosperms353 hit per locus and species.

DIAMOND blastx output is treated as a marker-recovery screen. This is not an
orthology proof: we select the highest-bitscore HSP per locus/species, require a
minimum subject coverage and aligned amino-acid length, and retain only loci
with high panel occupancy. Downstream topology is therefore a pilot backbone,
not an exact reproduction of Wu et al. 2022's 405 low-copy genes.
"""
from __future__ import annotations
import argparse,csv,json,re
from collections import defaultdict
from pathlib import Path

FIELDS=['qseqid','sseqid','pident','length','qlen','slen','evalue','bitscore','qstart','qend','sstart','send','qseq_translated']

def slug(t): return re.sub(r'[^A-Za-z0-9]+','_',t).strip('_')
def read_panel(p):
    with open(p,newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))
def locus_id(sseqid):
    # Angiosperms353.FAA IDs end in the target locus number, e.g. Arath-4471.
    x=str(sseqid).split('-')[-1]
    return x if x.isdigit() else str(sseqid)

def fasta_write(path, records):
    with open(path,'w',encoding='utf-8') as f:
        for name,seq in records:
            f.write(f'>{name}\n')
            for i in range(0,len(seq),80): f.write(seq[i:i+80]+'\n')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--panel',type=Path,required=True)
    ap.add_argument('--hits-dir',type=Path,required=True)
    ap.add_argument('--out-dir',type=Path,required=True)
    ap.add_argument('--min-subject-coverage',type=float,default=0.45)
    ap.add_argument('--min-aa',type=int,default=80)
    ap.add_argument('--min-occupancy',type=float,default=0.80)
    a=ap.parse_args(); a.out_dir.mkdir(parents=True,exist_ok=True)
    panel=read_panel(a.panel); taxa=[r['taxon'] for r in panel]
    state={r['taxon']:r['colour_state'] for r in panel}; section={r['taxon']:r['section'] for r in panel}
    best={}; all_rows=[]
    for r in panel:
        tax=r['taxon']; p=a.hits_dir/(slug(tax)+'.tsv')
        if not p.exists(): raise SystemExit(f'missing DIAMOND output {p}')
        with p.open(encoding='utf-8') as f:
            for line in f:
                if not line.strip(): continue
                vals=line.rstrip('\n').split('\t')
                if len(vals)!=len(FIELDS): continue
                h=dict(zip(FIELDS,vals)); loc=locus_id(h['sseqid'])
                length=int(h['length']); slen=max(1,int(h['slen'])); scov=length/slen
                seq=re.sub(r'[^A-Z*]','',h['qseq_translated'].upper()).replace('*','X')
                rec={'taxon':tax,'tip':slug(tax),'colour_state':state[tax],'section':section[tax],
                     'locus':loc,'qseqid':h['qseqid'],'sseqid':h['sseqid'],'pident':float(h['pident']),
                     'aligned_aa':length,'subject_coverage':scov,'evalue':float(h['evalue']),
                     'bitscore':float(h['bitscore']),'translated_hsp_aa':len(seq)}
                if length < a.min_aa or scov < a.min_subject_coverage or len(seq)<a.min_aa: continue
                all_rows.append(rec)
                key=(tax,loc)
                if key not in best or rec['bitscore']>best[key][0]['bitscore']:
                    best[key]=(rec,seq)
    loci=sorted({loc for _,loc in best},key=lambda x:int(x) if x.isdigit() else x)
    locus_summary=[]; admitted=[]
    for loc in loci:
        present=[t for t in taxa if (t,loc) in best]
        occ=len(present)/len(taxa)
        lens=[best[(t,loc)][0]['translated_hsp_aa'] for t in present]
        row={'locus':loc,'n_taxa':len(present),'occupancy':occ,'min_hsp_aa':min(lens) if lens else 0,
             'median_hsp_aa':sorted(lens)[len(lens)//2] if lens else 0,'admitted':occ>=a.min_occupancy}
        locus_summary.append(row)
        if row['admitted']:
            admitted.append(loc)
            fasta_write(a.out_dir/f'locus_{loc}.faa',[(slug(t),best[(t,loc)][1]) for t in present])
    # Freeze best-hit table, not every HSP.
    best_rows=[v[0] for _,v in sorted(best.items())]
    with (a.out_dir/'best_hits.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(best_rows[0]) if best_rows else ['taxon']);w.writeheader();w.writerows(best_rows)
    with (a.out_dir/'locus_occupancy.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(locus_summary[0]) if locus_summary else ['locus']);w.writeheader();w.writerows(locus_summary)
    summary={'n_panel_taxa':len(taxa),'candidate_loci':len(loci),'admitted_loci':len(admitted),
             'min_occupancy':a.min_occupancy,'min_subject_coverage':a.min_subject_coverage,'min_aa':a.min_aa,
             'admitted_loci_ids':admitted,
             'claim_ceiling':'best translated HSP per Angiosperms353 locus/species; pilot marker recovery, not orthology proof'}
    (a.out_dir/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
