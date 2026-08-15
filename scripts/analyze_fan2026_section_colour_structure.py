#!/usr/bin/env python3
"""Quantify traditional-section versus visible-colour structure in Fan 2026 Data S1.

Traditional Camellia sections are NOT treated as a phylogeny.  This analysis is a
coarse historical/taxonomic-structure diagnostic: if flower colour is much more
strongly partitioned among named sections than along present thermal niches,
that supports historical structure as an important macro confounder/filter.

Rows whose source `Section` is the literal country label `Vietnam` are excluded
from this section test because they are not a formal section assignment.
"""
from __future__ import annotations
import argparse,csv,json,math,pathlib,re
from collections import Counter
import numpy as np
from scipy.stats import chi2_contingency

def read(p):
    with open(p,newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))
def write(p,rows):
    p=pathlib.Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def norm_section(s):
    parts=[]
    for p in str(s or '').split(';'):
        p=re.sub(r'\s+',' ',p.strip()).lower()
        if not p:continue
        p=re.sub(r'^sect\.\s*','sect. ',p)
        parts.append(p)
    parts=sorted(set(parts))
    if not parts or parts==['vietnam']:return ''
    return parts[0] if len(parts)==1 else ';'.join(parts)

def statistic(sections,states,sec_levels,state_levels):
    si={s:i for i,s in enumerate(sec_levels)};ti={s:i for i,s in enumerate(state_levels)}
    table=np.zeros((len(sec_levels),len(state_levels)),dtype=int)
    for s,t in zip(sections,states):table[si[s],ti[t]]+=1
    row=table.sum(1,keepdims=True);col=table.sum(0,keepdims=True);n=table.sum();exp=row@col/n
    mask=exp>0
    chi=float((((table-exp)**2)/np.where(exp>0,exp,1))[mask].sum())
    return chi,table

def main():
    ap=argparse.ArgumentParser();ap.add_argument('seed',type=pathlib.Path);ap.add_argument('--summary',type=pathlib.Path,required=True);ap.add_argument('--table',type=pathlib.Path,required=True);ap.add_argument('--permutations',type=int,default=100000);a=ap.parse_args()
    rows=read(a.seed);kept=[]
    for r in rows:
        sec=norm_section(r.get('section',''))
        if sec:kept.append((r['taxon'],sec,r['colour_state']))
    secs=np.array([x[1] for x in kept],dtype=object);states=np.array([x[2] for x in kept],dtype=object)
    sec_levels=sorted(set(secs));state_levels=['A','W','Y'];obs,tab=statistic(secs,states,sec_levels,state_levels)
    n=int(tab.sum());v=math.sqrt(obs/(n*min(len(sec_levels)-1,len(state_levels)-1)))
    rng=np.random.default_rng(20260815);ge=0
    for _ in range(a.permutations):
        x,_=statistic(secs,rng.permutation(states),sec_levels,state_levels)
        if x>=obs-1e-12:ge+=1
    pperm=(ge+1)/(a.permutations+1)
    # asymptotic value retained as a descriptive secondary statistic only.
    chi2,pchi,dof,_=chi2_contingency(tab)
    trows=[]
    for i,sec in enumerate(sec_levels):
        trows.append({'section':sec,'A':int(tab[i,0]),'W':int(tab[i,1]),'Y':int(tab[i,2]),'n':int(tab[i].sum())})
    write(a.table,trows)
    summary=[{'n_species':n,'n_sections':len(sec_levels),'pearson_chi2':obs,'degrees_freedom':int(dof),'asymptotic_p':pchi,'cramers_v':v,'permutations':a.permutations,'permutation_p':pperm,'seed':20260815,'interpretation':'strong traditional-section/colour structure; section is a taxonomic-history proxy, not a nuclear phylogeny'}]
    write(a.summary,summary);print(json.dumps(summary[0],indent=2));print(json.dumps(trows,indent=2))
if __name__=='__main__':main()
