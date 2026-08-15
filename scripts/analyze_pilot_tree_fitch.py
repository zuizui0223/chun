#!/usr/bin/env python3
"""Compute root-independent minimum binary state changes on an unrooted pilot tree.

The Newick is midpoint-rooted only to traverse it; for unordered binary Fitch
parsimony the minimum change score is root independent. Scores are reported for
A vs non-A and Y vs non-Y. No gain/loss direction or reactivation is inferred.
"""
from __future__ import annotations
import argparse,csv,json,re
from pathlib import Path
from Bio import Phylo

def slug(t): return re.sub(r'[^A-Za-z0-9]+','_',t).strip('_')
def read_panel(p):
    with open(p,newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))
def fitch(clade, states):
    if clade.is_terminal():
        if clade.name not in states: raise KeyError(clade.name)
        return {states[clade.name]},0
    sets=[]; score=0
    for ch in clade.clades:
        s,n=fitch(ch,states);sets.append(s);score+=n
    cur=sets[0]
    for s in sets[1:]:
        inter=cur & s
        if inter:cur=inter
        else:cur=cur | s;score+=1
    return cur,score

def is_monophyletic(tree, positive):
    positive=set(positive)
    if not positive:return None
    mrca=tree.common_ancestor(list(positive))
    desc={x.name for x in mrca.get_terminals()}
    return desc==positive

def nearest_state_pairs(tree, panel, target_state):
    bytip={slug(r['taxon']):r for r in panel}; positives=[t for t,r in bytip.items() if r['colour_state']==target_state]
    out=[]
    for t in positives:
        best=None
        for u,r in bytip.items():
            if u==t or r['colour_state']==target_state:continue
            d=tree.distance(t,u)
            if best is None or d<best[0]: best=(d,u,r['colour_state'],r['section'])
        if best:
            out.append({'target_state':target_state,'tip':t,'taxon':bytip[t]['taxon'],'section':bytip[t]['section'],'nearest_nonstate_tip':best[1],'nearest_nonstate_taxon':bytip[best[1]]['taxon'],'nearest_nonstate_state':best[2],'nearest_nonstate_section':best[3],'tree_distance':best[0]})
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--tree',type=Path,required=True);ap.add_argument('--panel',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--pairs-output',type=Path,required=True);a=ap.parse_args()
    panel=read_panel(a.panel); bytip={slug(r['taxon']):r for r in panel}
    tree=Phylo.read(a.tree,'newick')
    tips={x.name for x in tree.get_terminals()}
    expected=set(bytip)
    if tips!=expected: raise SystemExit(f'tip mismatch missing={sorted(expected-tips)} extra={sorted(tips-expected)}')
    # Root only for traversal. Fitch minimum for binary unordered states is root independent.
    try: tree.root_at_midpoint()
    except Exception: pass
    results=[]
    for target in ('A','Y'):
        states={t:(1 if r['colour_state']==target else 0) for t,r in bytip.items()}
        rootset,score=fitch(tree.root,states)
        positive=[t for t,x in states.items() if x==1]
        results.append({'contrast':f'{target}_vs_non{target}','n_positive':len(positive),'n_negative':len(states)-len(positive),'fitch_min_changes':score,'positive_monophyletic':is_monophyletic(tree,positive),'root_direction_inferred':False,'reactivation_inferred':False,'interpretation':('one-change topology-compatible' if score==1 else f'at least {score} state changes required on this pilot topology'),'claim_ceiling':'unrooted pilot topology; minimum unordered state changes only; no gain/loss direction, timing, selection or reactivation'})
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(results[0]));w.writeheader();w.writerows(results)
    pairs=nearest_state_pairs(tree,panel,'A')+nearest_state_pairs(tree,panel,'Y')
    with a.pairs_output.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(pairs[0]) if pairs else ['target_state']);w.writeheader();w.writerows(pairs)
    print(json.dumps(results,indent=2))
if __name__=='__main__':main()
