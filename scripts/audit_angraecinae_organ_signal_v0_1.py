#!/usr/bin/env python3
"""Test four-organ colour organization conditional on primary GREEN/WHITE status.

The null preserves each admitted tip's primary sepal GREEN/WHITE class and exchanges
whole four-organ state vectors only within those classes. This asks whether labellum/spur
organization contains phylogenetic structure beyond the coarse primary binary state.
Minimum-change scores are organization statistics, not counts of independent origins.
"""
from __future__ import annotations
import argparse,collections,copy,csv,json
from pathlib import Path
import numpy as np
from Bio import Phylo
from analyze_angraecinae_mk_v0_1 import extract_ingroup_and_prune

SEED=20260907
ORGANS=('sepal_binary','petal_binary','labellum_binary','spur_binary')
BINARY={'WHITE','GREEN'}


def sankoff_permutation(tree, states, primary, permutations=9999):
    patterns=sorted(set(states.values())); pindex={p:i for i,p in enumerate(patterns)}
    nodes=list(tree.find_clades(order='postorder')); idx={id(n):i for i,n in enumerate(nodes)}
    children=[[idx[id(c)] for c in n.clades] for n in nodes]
    leaves=list(tree.get_terminals()); names=[n.name for n in leaves]; leafidx=[idx[id(n)] for n in leaves]
    if set(names)!=set(states): raise ValueError('tree/state mismatch')
    k=len(patterns); nt=len(names)
    base=np.full((nt,k),10000,dtype=np.int16)
    for i,n in enumerate(names): base[i,pindex[states[n]]]=0
    groups=collections.defaultdict(list)
    for i,n in enumerate(names): groups[primary[n]].append(i)
    groups=[np.asarray(v,dtype=int) for v in groups.values()]
    if len(groups)!=2: raise ValueError('conditional null requires both primary classes')
    rng=np.random.default_rng(SEED); scores=[]
    for start in range(0,permutations+1,500):
        n=min(500,permutations+1-start); inds=[]
        for j in range(n):
            if start+j==0: ind=np.arange(nt)
            else:
                ind=np.arange(nt)
                for g in groups: ind[g]=rng.permutation(g)
            inds.append(ind)
        inds=np.asarray(inds); d=np.zeros((len(nodes),n,k),dtype=np.int16)
        for pos,node_i in enumerate(leafidx): d[node_i]=base[inds[:,pos]]
        for i in range(len(nodes)):
            for c in children[i]: d[i]+=np.minimum(d[c],d[c].min(axis=1)[:,None]+1)
        scores.extend(d[-1].min(axis=1).tolist())
    observed=int(scores[0]); null=np.asarray(scores[1:]); p=(1+int((null<=observed).sum()))/(len(null)+1)
    return {
        'n_tips':nt,'joint_patterns':[list(x) for x in patterns],
        'observed_minimum_changes':observed,'null_mean':float(null.mean()),
        'observed_over_null_mean':float(observed/null.mean()),
        'null_quantiles':np.quantile(null,[.025,.5,.975]).tolist(),
        'lower_tail_p':float(p),'permutations':len(null),'seed':SEED,
        'null':'Whole four-organ state vectors exchanged only within fixed primary sepal GREEN/WHITE classes.',
        'not_independent_origins':True
    }


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--trees-dir',type=Path,required=True); ap.add_argument('--sample-manifest',type=Path,required=True); ap.add_argument('--traits',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); ap.add_argument('--permutations',type=int,default=9999); a=ap.parse_args()
    samples=list(csv.DictReader(a.sample_manifest.open())); rows=list(csv.DictReader(a.traits.open())); traits={r['source_taxon']:r for r in rows}
    full_ingroup={r['tip_id'] for r in samples if r['source_group']=='ANGRAECINAE'}
    mapped={r['tip_id']:traits[r['source_taxon']] for r in samples if r['source_group']=='ANGRAECINAE' and r['trait_join_status']=='EXACT_UNIQUE' and r['source_taxon'] in traits}
    states={tip:tuple(row[o] for o in ORGANS) for tip,row in mapped.items() if all(row[o] in BINARY for o in ORGANS)}
    if len(states)<160: raise ValueError(f'insufficient exact fully-binary organ rows: {len(states)}')
    if any(v[0]!=v[1] for v in states.values()): raise ValueError('primary sepal/petal classes disagree among fully binary rows')
    result={'version':'v0.1','exact_fully_binary_tips':len(states),'pattern_counts':{'|'.join(k):v for k,v in collections.Counter(states.values()).items()},'tests':[],'paper1_science_changed':False}
    for tag in ('plastid_full','plastid50','all4_full'):
        tree=Phylo.read(a.trees_dir/f'{tag}.treefile','newick')
        t=extract_ingroup_and_prune(tree,full_ingroup,set(states)); primary={n:states[n][0] for n in states}
        test=sankoff_permutation(t,states,primary,a.permutations); test['tree']=tag; result['tests'].append(test)
    result['claim_boundary']='Conditional phylogenetic organization of four-organ source patterns beyond primary GREEN/WHITE status. Sensitivity trees are one radiation; scores are not event counts and no ecological or molecular cause is inferred.'
    a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps(result,indent=2))

if __name__=='__main__': main()
