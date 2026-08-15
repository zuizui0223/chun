#!/usr/bin/env python3
"""Quantify colour-state geography from the species-level Fan 2026 Data S1 seed.

The test is deliberately simple and reproducible: species are classified as
confined to the southern putative ancestral belt (South China, Southwest China,
Vietnam) versus having any sampled source area outside that belt.  It quantifies
the published qualitative geography but does not substitute for phylogenetic or
occurrence-based niche analysis.
"""
from __future__ import annotations
import argparse, csv, math, pathlib

SOUTH={"South China（SC）","Southwest China（SWC）","Vietnam"}

def fisher_one_sided_greater(a,b,c,d):
    # Table [[a,b],[c,d]]; probability of X>=a with fixed margins.
    n=a+b+c+d; r1=a+b; c1=a+c
    lo=max(0,r1-(n-c1)); hi=min(r1,c1)
    den=math.comb(n,r1)
    return sum(math.comb(c1,x)*math.comb(n-c1,r1-x)/den for x in range(a,hi+1))

def fisher_two_sided(a,b,c,d):
    n=a+b+c+d; r1=a+b; c1=a+c; den=math.comb(n,r1)
    def p(x): return math.comb(c1,x)*math.comb(n-c1,r1-x)/den
    pobs=p(a); lo=max(0,r1-(n-c1)); hi=min(r1,c1)
    return min(1.0,sum(p(x) for x in range(lo,hi+1) if p(x)<=pobs+1e-15))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('seed',type=pathlib.Path); ap.add_argument('--output',type=pathlib.Path,required=True); a=ap.parse_args()
    with a.seed.open(newline='',encoding='utf-8') as f: rows=list(csv.DictReader(f))
    for r in rows:
        areas={x.strip() for x in r.get('areas','').split(';') if x.strip()}
        r['_south_only']=bool(areas) and areas.issubset(SOUTH)
    counts={s:{True:0,False:0} for s in ('A','W','Y')}
    for r in rows:
        s=r['colour_state']; counts[s][r['_south_only']]+=1
    y=counts['Y']; non={True:counts['A'][True]+counts['W'][True],False:counts['A'][False]+counts['W'][False]}
    A=counts['A']; W=counts['W']
    out=[
        {'contrast':'Y_vs_nonY_south_only','state1_south':y[True],'state1_outside':y[False],'state2_south':non[True],'state2_outside':non[False],'odds_ratio':'inf' if y[False]==0 else (y[True]*non[False])/(y[False]*non[True]),'p_value':fisher_one_sided_greater(y[True],y[False],non[True],non[False]),'alternative':'Y more confined to southern belt'},
        {'contrast':'A_vs_W_south_only','state1_south':A[True],'state1_outside':A[False],'state2_south':W[True],'state2_outside':W[False],'odds_ratio':(A[True]*W[False])/(A[False]*W[True]),'p_value':fisher_two_sided(A[True],A[False],W[True],W[False]),'alternative':'two-sided'},
    ]
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    print('state counts',counts)
    for x in out: print(x)
if __name__=='__main__': main()
