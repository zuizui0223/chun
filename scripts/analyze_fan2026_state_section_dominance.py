#!/usr/bin/env python3
"""Quantify whether each visible state is dominated by one traditional section.

Input is the frozen full Fan2026 formal-section colour table. For each state,
compute the largest fraction of that state's species contributed by any one
traditional section. Shuffle A/W/Y species labels across the same section-size
structure while preserving total state counts to obtain an exact Monte-Carlo
null. This is a history-proxy diagnostic, not an origin-count analysis.
"""
from __future__ import annotations
import argparse,csv
from collections import Counter
from pathlib import Path
import numpy as np

def read(p):
    with Path(p).open(newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('table',type=Path);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--permutations',type=int,default=100000);ap.add_argument('--seed',type=int,default=20260815);a=ap.parse_args()
    rows=read(a.table)
    labels=[];sections=[]
    for r in rows:
        for st in ('A','W','Y'):
            n=int(r[st]); labels.extend([st]*n); sections.extend([r['section']]*n)
    labels=np.array(labels,dtype=object); sections=np.array(sections,dtype=object)
    states=['A','W','Y']; rng=np.random.default_rng(a.seed); b=a.permutations
    def metrics(lbl,st):
        vals=sections[lbl==st]; c=Counter(vals); n=len(vals); maxsec,maxn=max(c.items(),key=lambda x:(x[1],x[0])); occupied=set(c); total_occ=sum(np.sum(sections==s) for s in occupied)
        return maxsec,maxn/n,n/total_occ,total_occ-n
    obs={st:metrics(labels,st) for st in states}
    maxshare={st:np.empty(b) for st in states}; purity={st:np.empty(b) for st in states}
    for i in range(b):
        p=rng.permutation(labels)
        for st in states:
            _,ms,pu,_=metrics(p,st); maxshare[st][i]=ms; purity[st][i]=pu
    out=[]
    for st in states:
        maxsec,ms,pu,other=obs[st]
        pmax=(int(np.sum(maxshare[st]>=ms-1e-15))+1)/(b+1)
        ppur=(int(np.sum(purity[st]>=pu-1e-15))+1)/(b+1)
        out.append({'visible_state':st,'n_species':int(np.sum(labels==st)),'dominant_section':maxsec,'observed_max_section_share':f'{ms:.10f}','expected_max_section_share':f'{maxshare[st].mean():.10f}','upper_tail_max_share_p':f'{pmax:.10f}','observed_occupied_section_purity':f'{pu:.10f}','expected_occupied_section_purity':f'{purity[st].mean():.10f}','upper_tail_purity_p':f'{ppur:.10f}','other_state_species_inside_occupied_sections':other,'permutations':b,'seed':a.seed,'interpretation':('one-section dominance far exceeds state-count expectation' if pmax<0.05 else 'no count-controlled excess one-section dominance'),'claim_ceiling':'traditional-section history proxy; does not distinguish single origin from repeated gain/loss or introgression'})
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
    for r in out:print(r)
if __name__=='__main__':main()
