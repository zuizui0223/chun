#!/usr/bin/env python3
"""Trim high-gap columns from admitted Angiosperms353 AA alignments and concatenate.

Each locus is independently MAFFT-aligned upstream. Columns with less than the
configured non-gap fraction are removed. Missing loci are filled with gaps.
Panel rows marked ``admission_status=quarantine`` are excluded before the
concatenated taxon set and gap fractions are computed.
"""
from __future__ import annotations
import argparse,csv,json,re
from pathlib import Path
from Bio import SeqIO

def slug(t): return re.sub(r'[^A-Za-z0-9]+','_',t).strip('_')
def read_panel(p):
    with open(p,newline='',encoding='utf-8-sig') as f:
        rows=list(csv.DictReader(f))
    return [r for r in rows if (r.get('admission_status') or 'admit').strip().lower()=='admit']
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--panel',type=Path,required=True);ap.add_argument('--align-dir',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--partition',type=Path,required=True);ap.add_argument('--summary',type=Path,required=True);ap.add_argument('--min-nongap',type=float,default=0.60);a=ap.parse_args()
    panel=read_panel(a.panel); tips=[slug(r['taxon']) for r in panel]
    if not tips: raise SystemExit('no admitted taxa in panel')
    concat={t:'' for t in tips};parts=[];start=1;used=[]
    for p in sorted(a.align_dir.glob('locus_*.aln.faa'),key=lambda x:int(re.search(r'locus_(\d+)',x.name).group(1))):
        loc=re.search(r'locus_(\d+)',p.name).group(1)
        recs={r.id:str(r.seq).upper() for r in SeqIO.parse(p,'fasta')}
        if not recs: continue
        L=len(next(iter(recs.values())))
        if any(len(s)!=L for s in recs.values()): raise SystemExit(f'non-rectangular alignment {p}')
        keep=[]
        for j in range(L):
            non=sum(1 for t in tips if t in recs and recs[t][j] not in '-.?X')
            if non/len(tips)>=a.min_nongap: keep.append(j)
        if not keep: continue
        block={t:''.join(recs[t][j] if t in recs else '-' for j in keep) for t in tips}
        blen=len(keep)
        for t in tips: concat[t]+=block[t]
        end=start+blen-1; parts.append(f'LG, locus_{loc} = {start}-{end}');used.append({'locus':loc,'raw_columns':L,'kept_columns':blen,'start':start,'end':end});start=end+1
    if not used: raise SystemExit('no aligned loci survived trimming')
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open('w') as f:
        for t in tips:
            f.write(f'>{t}\n')
            s=concat[t]
            for i in range(0,len(s),80):f.write(s[i:i+80]+'\n')
    a.partition.write_text('\n'.join(parts)+'\n')
    a.summary.write_text(json.dumps({'n_taxa':len(tips),'n_loci':len(used),'alignment_aa':len(next(iter(concat.values()))),'min_nongap':a.min_nongap,'loci':used,'claim_ceiling':'pilot concatenated AA matrix from best Angiosperms353 HSPs for admitted provenance-safe taxa; quarantined payloads excluded'},indent=2)+'\n')
    print(a.summary.read_text())
if __name__=='__main__':main()
