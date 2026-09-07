#!/usr/bin/env python3
"""Align source-mapped Angraecinae loci and build independent ML-tree inputs."""
from __future__ import annotations
import argparse,json,subprocess
from pathlib import Path
import numpy as np
from Bio import SeqIO

LOCI=('matK','rps16','trnL','ITS')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--sequence-dir',type=Path,required=True);ap.add_argument('--out-dir',type=Path,required=True);a=ap.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
    seqs={};lengths={};tips=set();directions=[]
    for g in LOCI:
        src=a.sequence_dir/f'{g}.fasta';dest=a.out_dir/f'{g}.aligned.fasta'
        with dest.open('w') as out,(a.out_dir/f'{g}.mafft.log').open('w') as err:
            subprocess.run(['mafft','--auto','--adjustdirectionaccurately','--thread','2',str(src)],stdout=out,stderr=err,check=True)
        recs=list(SeqIO.parse(dest,'fasta'));d={}
        for r in recs:
            name=r.id
            if name.startswith('_R_'):name=name[3:];directions.append({'tip_id':name,'locus':g,'action':'REVERSE_COMPLEMENT'})
            if name in d:raise ValueError(f'duplicate aligned tip {name} in {g}')
            d[name]=str(r.seq).upper()
        sizes={len(x) for x in d.values()}
        if len(sizes)!=1:raise ValueError(f'unequal alignment row length {g}')
        seqs[g]=d;lengths[g]=sizes.pop();tips.update(d)
    tips=sorted(tips)
    if len(tips)<185:raise ValueError(f'insufficient source tips: {len(tips)}')
    variants=[('plastid_full',('matK','rps16','trnL'),0.0),('plastid50',('matK','rps16','trnL'),0.5),('all4_full',LOCI,0.0)]
    summary={'taxa_with_any_sequence':len(tips),'locus_alignment_lengths':lengths,'direction_corrections':directions,'variants':{}}
    for tag,loci,threshold in variants:
        joined={t:'' for t in tips};parts=[];start=1
        for g in loci:
            block=np.array([list(seqs[g].get(t,'?'*lengths[g])) for t in tips]);present=np.isin(block,list('ACGT')).mean(axis=0)
            keep=present>0 if threshold==0 else present>=threshold;n=int(keep.sum())
            if n==0:raise ValueError(f'empty {g} block in {tag}')
            for t,row in zip(tips,block[:,keep]):joined[t]+=''.join(row)
            parts.append(f'  charset {g} = {start}-{start+n-1};');start+=n
        fasta=a.out_dir/f'{tag}.fasta';fasta.write_text(''.join(f'>{t}\n{s}\n' for t,s in joined.items()))
        (a.out_dir/f'{tag}.nex').write_text('#nexus\nbegin sets;\n'+'\n'.join(parts)+'\nend;\n')
        summary['variants'][tag]={'loci':list(loci),'occupancy_threshold':threshold,'columns':start-1,'partition_statements':parts}
    (a.out_dir/'alignment_manifest.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
