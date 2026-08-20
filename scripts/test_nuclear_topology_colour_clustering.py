#!/usr/bin/env python3
"""Join visible colour only after an independent nuclear topology is frozen.

Tests whether A/W/Y tips are more clustered than count-preserving random sets on
an unrooted topology using edge-count MPD and MNTD.
"""
from __future__ import annotations
import argparse,csv,json,re
from collections import deque
from pathlib import Path
import numpy as np
from Bio import Phylo

def key(x): return re.sub(r'\s+',' ',(x or '').strip().replace('_',' ')).casefold()
def rows(p):
    with open(p,newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))
def matrix(p):
    t=Phylo.read(str(p),'newick'); adj={}
    for a in t.find_clades(order='level'):
        adj.setdefault(a,[])
        for b in a.clades: adj.setdefault(b,[]);adj[a].append(b);adj[b].append(a)
    tips=[x for x in t.get_terminals() if x.name]; names=[key(x.name) for x in tips]
    if len(set(names))!=len(names): raise SystemExit('duplicate normalized tips')
    D=np.zeros((len(tips),len(tips)),dtype=np.int16)
    for i,s in enumerate(tips):
        q=deque([(s,0)]); seen={s}; dm={s:0}
        while q:
            u,d=q.popleft()
            for v in adj[u]:
                if v not in seen: seen.add(v);dm[v]=d+1;q.append((v,d+1))
        for j,v in enumerate(tips): D[i,j]=dm[v]
    return names,D
def metrics(D):
    n=len(D)
    tri=D[np.triu_indices(n,1)]
    X=D.astype(float).copy();np.fill_diagonal(X,np.inf)
    return float(np.mean(tri)),float(np.mean(np.min(X,axis=1)))
def test(state,idx,D,nperm,rng):
    n=len(idx)
    if n<2:return {'state':state,'n_state':n}
    om,ont=metrics(D[np.ix_(idx,idx)]); nm=np.empty(nperm); nn=np.empty(nperm);N=len(D)
    for z in range(nperm):
        x=rng.choice(N,n,replace=False);nm[z],nn[z]=metrics(D[np.ix_(x,x)])
    return {'state':state,'n_state':n,'observed_mpd_edges':om,'expected_mpd_edges':float(nm.mean()),'mpd_cluster_p':float((np.sum(nm<=om)+1)/(nperm+1)),'observed_mntd_edges':ont,'expected_mntd_edges':float(nn.mean()),'mntd_cluster_p':float((np.sum(nn<=ont)+1)/(nperm+1))}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--tree',type=Path,required=True);ap.add_argument('--fan-colour',type=Path,required=True);ap.add_argument('--out-dir',type=Path,required=True);ap.add_argument('--permutations',type=int,default=100000);ap.add_argument('--seed',type=int,default=20260820);a=ap.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
    names,D=matrix(a.tree); col={}
    for r in rows(a.fan_colour):
        k=key(r.get('taxon'));s=(r.get('colour_state') or '').strip()
        if k and s in {'A','W','Y'}: col[k]=s
    ti=[i for i,n in enumerate(names) if n in col]; st=[col[names[i]] for i in ti]; PD=D[np.ix_(ti,ti)];rng=np.random.default_rng(a.seed)
    out=[test(s,[i for i,x in enumerate(st) if x==s],PD,a.permutations,rng) for s in ['A','W','Y']]
    with (a.out_dir/'nuclear_colour_clustering.csv').open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
    A=out[0]; summary={'tree_tips':len(names),'visible_colour_overlap':len(st),'state_counts':{s:st.count(s) for s in ['A','W','Y']},'distance_metric':'unrooted topology edge count','permutations':a.permutations,'A_result':A,'A_lineage_clustering_status':'supported' if A.get('mpd_cluster_p',1)<.05 and A.get('mntd_cluster_p',1)<.05 else 'partial_or_not_supported','claim_ceiling':'approximate-gene-tree, root-independent topology screen only; no ancestral-state or causal claim'}
    (a.out_dir/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
