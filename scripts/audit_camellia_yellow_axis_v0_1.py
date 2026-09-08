#!/usr/bin/env python3
"""Prospective Camellia validation of an exploratory YELLOW/non-YELLOW axis."""
from __future__ import annotations
import argparse,copy,csv,json
from collections import defaultdict
from pathlib import Path
import numpy as np
from Bio import Phylo

SEED=20260908
STATES=('W','A','Y')
PARTITIONS={
    'YELLOW_AXIS':({'Y'},{'W','A'}),
    'WHITE_AXIS':({'W'},{'A','Y'}),
    'ANTHOCYANIN_AXIS':({'A'},{'W','Y'}),
}


def load_seed(path:Path):
    rows=list(csv.DictReader(path.open()))
    out={r['accepted_species'].replace(' ','_'):r['colour_state'] for r in rows}
    if len(out)!=len(rows) or not set(out.values())<=set(STATES):
        raise ValueError('seed identity/state failure')
    return out


def prune(tree,states):
    t=copy.deepcopy(tree)
    for n in list(t.get_terminals()):
        if n.name not in states:t.prune(n)
    if set(n.name for n in t.get_terminals())!=set(states):
        raise ValueError('tree/state mismatch after pruning')
    return t


def sankoff_null(tree,states,groups=None,permutations=9999,seed=SEED):
    nodes=list(tree.find_clades(order='postorder'));idx={id(n):i for i,n in enumerate(nodes)}
    children=[[idx[id(c)] for c in n.clades] for n in nodes]
    leaves=list(tree.get_terminals());names=[n.name for n in leaves];leafidx=[idx[id(n)] for n in leaves]
    labels=np.array([STATES.index(states[n]) for n in names],dtype=np.int16)
    rng=np.random.default_rng(seed);scores=[]
    if groups is None:
        group_positions=[np.arange(len(names),dtype=int)]
    else:
        group_positions=[]
        for group in groups:
            pos=np.array([i for i,n in enumerate(names) if states[n] in group],dtype=int)
            if len(pos):group_positions.append(pos)
    for start in range(0,permutations+1,500):
        m=min(500,permutations+1-start);labs=np.empty((m,len(names)),dtype=np.int16)
        for j in range(m):
            lab=labels.copy()
            if start+j!=0:
                for pos in group_positions:lab[pos]=rng.permutation(lab[pos])
            labs[j]=lab
        d=np.zeros((len(nodes),m,3),dtype=np.int16)
        for pos,node_i in enumerate(leafidx):
            d[node_i]=10000
            d[node_i,np.arange(m),labs[:,pos]]=0
        for i in range(len(nodes)):
            for c in children[i]:d[i]+=np.minimum(d[c],d[c].min(axis=1)[:,None]+1)
        scores.extend(d[-1].min(axis=1).tolist())
    return int(scores[0]),float(np.mean(scores[1:]))


def one_setting(tag,tree_path,seed_path,coding,permutations):
    seed=load_seed(seed_path);tree=Phylo.read(tree_path,'newick')
    tips={n.name for n in tree.get_terminals()};states={n:s for n,s in seed.items() if n in tips}
    expected={('FASTTREE','STRICT'):24,('FASTTREE','DOMINANT'):30,('UFBOOT','STRICT'):23,('UFBOOT','DOMINANT'):29}[(tag,coding)]
    if len(states)!=expected:raise ValueError(f'{tag}/{coding}: expected {expected} joined tips, got {len(states)}')
    if set(states.values())!=set(STATES):raise ValueError(f'{tag}/{coding}: all W/A/Y states required')
    t=prune(tree,states)
    observed,uncond=sankoff_null(t,states,None,permutations,SEED)
    gap=uncond-observed
    if gap<=0:raise ValueError(f'{tag}/{coding}: no positive fine-state organization gap')
    results=[]
    for i,(name,(a,b)) in enumerate(PARTITIONS.items()):
        obs2,cond=sankoff_null(t,states,[a,b],permutations,SEED+100*(i+1))
        if obs2!=observed:raise ArithmeticError('observed score changed across nulls')
        results.append({'partition':name,'side_a':sorted(a),'side_b':sorted(b),'conditional_null_mean':cond,'capture_fraction':(uncond-cond)/gap})
    ranked=sorted(results,key=lambda r:(-r['capture_fraction'],r['partition']))
    for rank,r in enumerate(ranked,1):r['rank']=rank
    by={r['partition']:r for r in ranked};yellow=by['YELLOW_AXIS']
    return {'setting':f'{tag}|{coding}','tree':tag,'coding':coding,'n_tips':len(states),'state_counts':{s:list(states.values()).count(s) for s in STATES},'observed_minimum_changes':observed,'unconditional_null_mean':uncond,'fine_organization_gap':gap,'partitions':ranked,'yellow_rank':yellow['rank'],'yellow_capture_fraction':yellow['capture_fraction']}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--fasttree',type=Path,required=True);p.add_argument('--ufboot',type=Path,required=True)
    p.add_argument('--strict',type=Path,required=True);p.add_argument('--dominant',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--permutations',type=int,default=9999)
    a=p.parse_args();settings=[]
    for tag,tree in [('FASTTREE',a.fasttree),('UFBOOT',a.ufboot)]:
        for coding,seed in [('STRICT',a.strict),('DOMINANT',a.dominant)]:
            settings.append(one_setting(tag,tree,seed,coding,a.permutations))
    best=sum(s['yellow_rank']==1 for s in settings);positive=sum(s['yellow_capture_fraction']>0 for s in settings)
    status='YELLOW_AXIS_VALIDATED' if best>=3 and positive==4 else ('YELLOW_AXIS_MIXED' if best==2 and positive==4 else 'YELLOW_AXIS_NOT_VALIDATED')
    out={'version':'v0.1','status':status,'seed':SEED,'permutations':a.permutations,'settings':settings,'yellow_best_settings':best,'yellow_positive_capture_settings':positive,'pre_frozen_gate':'best rank in >=3/4 AND positive capture in 4/4','claim_boundary':'Prospective Camellia validation of an exploratory visible-state partition. A PASS does not establish a shared biochemical pathway, ecology, ancestry or transition direction.','paper1_science_changed':False}
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
