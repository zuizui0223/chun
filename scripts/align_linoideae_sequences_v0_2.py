#!/usr/bin/env python3
"""Build two independent reconstruction inputs; no author tree or dating is claimed."""
from __future__ import annotations
import argparse,csv,hashlib,json,subprocess
from pathlib import Path
import numpy as np
from Bio import SeqIO
GENES=('ndhF','matK','trnLF','ITS')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--sequence-dir',type=Path,required=True);ap.add_argument('--out-dir',type=Path,required=True);a=ap.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
    seqs={};lengths={};alltips=set();direction=[]
    for g in GENES:
        dest=a.out_dir/f'{g}.aligned.fasta'
        with dest.open('w') as out,(a.out_dir/f'{g}.mafft.log').open('w') as err:
            subprocess.run(['mafft','--auto','--adjustdirectionaccurately','--thread','2',str(a.sequence_dir/f'{g}.fasta')],stdout=out,stderr=err,check=True)
        recs=list(SeqIO.parse(dest,'fasta'));seqs[g]={}
        for r in recs:
            name=r.id
            if name.startswith('_R_'):name=name[3:];direction.append({'tip_id':name,'locus':g,'action':'REVERSE_COMPLEMENT'})
            if name in seqs[g]:raise ValueError('duplicate aligned tip')
            seqs[g][name]=str(r.seq).upper()
        sizes={len(v) for v in seqs[g].values()}
        if len(sizes)!=1:raise ValueError('unequal alignment rows')
        lengths[g]=sizes.pop();alltips.update(seqs[g])
    tips=sorted(alltips)
    if 'LINO001' not in tips or len(tips)<100:raise ValueError('insufficient tips/outgroup')
    coverage=[{'tip_id':t,'loci_present':sum(t in seqs[g] for g in GENES),'ungapped_bases':sum(sum(c in 'ACGT' for c in seqs[g].get(t,'')) for g in GENES)} for t in tips]
    summary={'taxa':len(tips),'locus_lengths':lengths,'direction_corrections':direction,'coverage':coverage,'variants':{}}
    for tag,threshold in [('full',0),('occupancy50',0.5)]:
        joined={t:'' for t in tips};partitions=[];start=1
        for g in GENES:
            block=np.array([list(seqs[g].get(t,'?'*lengths[g])) for t in tips]);present=np.isin(block,list('ACGT')).mean(axis=0)
            keep=present>0 if threshold==0 else present>=threshold
            n=int(keep.sum())
            if n==0:raise ValueError('empty locus after filter')
            for t,row in zip(tips,block[:,keep]):joined[t]+=''.join(row)
            partitions.append(f'  charset {g} = {start}-{start+n-1};');start+=n
        path=a.out_dir/f'{tag}.fasta';path.write_text(''.join(f'>{t}\n{s}\n' for t,s in joined.items()))
        (a.out_dir/f'{tag}.nex').write_text('#nexus\nbegin sets;\n'+'\n'.join(partitions)+'\nend;\n')
        summary['variants'][tag]={'columns':start-1,'threshold':threshold,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'partition_statements':partitions}
    (a.out_dir/'alignment_manifest.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items() if k!='coverage'},indent=2))
if __name__=='__main__':main()
