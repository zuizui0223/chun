#!/usr/bin/env python3
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import io
import json
import re
import zipfile
from pathlib import Path

import numpy as np
from Bio import Phylo
from scipy.stats import spearmanr, rankdata

CSV_SHA='a253308785e4cbd0e361b3ca04cdfdae29c523eefa843375cebf8030ee0874af'
TREES_SHA='ae5c82945e5bf9c29bcabc52d6029acd8d4f5be1fe9141fad95918eacb4f674d'
SEED=20260918
PERMUTATIONS=99999

def sha256_file(path:Path)->str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()

def norm_tip(x:str)->str:
    return re.sub(r'\s+',' ',str(x).strip().replace('_',' ')).lower()

def common_cross_organ_keep_mask(flower, fruit, minimum_state_tips:int=5)->np.ndarray:
    flower=np.asarray(flower,dtype=object)
    fruit=np.asarray(fruit,dtype=object)
    if len(flower)!=len(fruit):
        raise ValueError('flower and fruit arrays differ in length')
    keep=np.ones(len(flower),dtype=bool)
    while True:
        fc=collections.Counter(flower[keep].tolist())
        rc=collections.Counter(fruit[keep].tolist())
        next_keep=keep.copy()
        for idx in np.where(keep)[0]:
            if fc[flower[idx]] < minimum_state_tips or rc[fruit[idx]] < minimum_state_tips:
                next_keep[idx]=False
        if np.array_equal(next_keep,keep):
            return keep
        keep=next_keep

def pair_same_baseline(states:np.ndarray)->float:
    states=np.asarray(states,dtype=object)
    n=len(states)
    if n<2:
        return float('nan')
    counts=collections.Counter(states.tolist())
    same=sum(v*(v-1)//2 for v in counts.values())
    total=n*(n-1)//2
    return same/total

def signed_area(x,y)->float:
    x=np.asarray(x,dtype=float); y=np.asarray(y,dtype=float)
    return float(np.trapezoid(y,x))

def root_to_tip_cv(tree)->float:
    vals=np.array([tree.distance(tree.root,t) for t in tree.get_terminals()],dtype=float)
    m=float(vals.mean())
    return float(vals.std(ddof=0)/m) if m>0 else float('nan')

def relative_divergence_depth(tree, distances:np.ndarray)->np.ndarray:
    cv=root_to_tip_cv(tree)
    if not np.isfinite(cv) or cv>1e-8:
        raise ValueError(f'non-ultrametric source tree, root-to-tip CV={cv}')
    h=float(np.mean([tree.distance(tree.root,t) for t in tree.get_terminals()]))
    if h<=0:
        raise ValueError('non-positive crown height')
    x=np.asarray(distances,dtype=float)/(2*h)
    if np.nanmin(x)<-1e-12 or np.nanmax(x)>1+1e-8:
        raise ValueError('relative divergence depth outside [0,1]')
    return x

def memory_curve(rel_time:np.ndarray, ii:np.ndarray, jj:np.ndarray, states:np.ndarray, n_bins:int=10)->dict:
    states=np.asarray(states,dtype=object)
    same=states[ii]==states[jj]
    baseline=pair_same_baseline(states)
    denom=1-baseline
    order=np.argsort(rel_time,kind='stable')
    groups=np.array_split(order,min(n_bins,len(order)))
    bins=[]
    for b,idx in enumerate(groups,1):
        if not len(idx): continue
        p=float(np.mean(same[idx]))
        excess=(p-baseline)/denom
        bins.append({'bin':b,'n_pairs':int(len(idx)),'t':float(np.mean(rel_time[idx])),'p_same':p,'excess':float(excess)})
    x=np.array([b['t'] for b in bins],float)
    y=np.array([b['excess'] for b in bins],float)
    slope=float(np.polyfit(x,y,1)[0])
    area=signed_area(x,y)
    return {'baseline_same_probability':baseline,'slope':slope,'area':area,'bins':bins}

def spearman_permutation_test(x,y,permutations:int=PERMUTATIONS,seed:int=SEED)->tuple[float,float]:
    x=np.asarray(x,dtype=float); y=np.asarray(y,dtype=float)
    xr=rankdata(x,method="average").astype(float); yr=rankdata(y,method="average").astype(float)
    xr-=xr.mean(); yr-=yr.mean()
    denom=float(np.sqrt(np.dot(xr,xr)*np.dot(yr,yr)))
    rho=float(np.dot(xr,yr)/denom)
    rng=np.random.default_rng(seed)
    count=0
    batch=5000
    done=0
    while done<permutations:
        b=min(batch,permutations-done)
        perms=np.empty((b,len(yr)),dtype=float)
        for j in range(b): perms[j]=rng.permutation(yr)
        null=perms@xr/denom
        count += int(np.count_nonzero(null <= rho))
        done += b
    return rho,(1+count)/(permutations+1)

def analyse(csv_path:Path, trees_path:Path, permutations:int=PERMUTATIONS, seed:int=SEED)->dict:
    if sha256_file(csv_path)!=CSV_SHA or sha256_file(trees_path)!=TREES_SHA:
        raise SystemExit('source hash mismatch')
    rows=collections.defaultdict(list)
    with csv_path.open(newline='',encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            rows[r['clade'].strip()].append((r['species'].strip(),r['flower_color'].strip(),r['fruit_color'].strip()))
    z=zipfile.ZipFile(trees_path)
    members={Path(m).stem.lower():m for m in z.namelist() if not m.endswith('/') and not m.startswith('__MACOSX/') and not m.endswith('.DS_Store')}
    details={}
    for clade in sorted(rows):
        vals=rows[clade]
        sp=np.array([v[0] for v in vals],object)
        flower=np.array([v[1] for v in vals],object)
        fruit=np.array([v[2] for v in vals],object)
        keep=common_cross_organ_keep_mask(flower,fruit,5)
        sp,flower,fruit=sp[keep],flower[keep],fruit[keep]
        reasons=[]
        if len(sp)<20: reasons.append('COMMON_TIPS_LT_20')
        if len(set(flower.tolist()))<2: reasons.append('FLOWER_STATES_LT_2')
        if len(set(fruit.tolist()))<2: reasons.append('FRUIT_STATES_LT_2')
        if reasons:
            details[clade]={'status':'HOLD_COMMON_CROSS_ORGAN_FRAME','eligible_tips':int(len(sp)),'reasons':reasons}
            continue
        tree=Phylo.read(io.StringIO(z.read(members[clade.lower()]).decode('utf-8-sig')),'newick')
        rb={norm_tip(s):(fl,fr) for s,fl,fr in zip(sp,flower,fruit)}
        tips=[t for t in tree.get_terminals() if norm_tip(t.name) in rb]
        fstate=np.array([rb[norm_tip(t.name)][0] for t in tips],object)
        rstate=np.array([rb[norm_tip(t.name)][1] for t in tips],object)
        n=len(tips)
        ii,jj=np.triu_indices(n,1)
        dist=np.array([tree.distance(tips[int(a)],tips[int(b)]) for a,b in zip(ii,jj)],float)
        rel=relative_divergence_depth(tree,dist)
        fm=memory_curve(rel,ii,jj,fstate)
        rm=memory_curve(rel,ii,jj,rstate)
        details[clade]={
            'status':'CROSS_ORGAN_MEMORY_COMPLETE','eligible_tips':n,'root_to_tip_cv':root_to_tip_cv(tree),
            'flower_states':len(set(fstate.tolist())),'fruit_states':len(set(rstate.tolist())),
            'flower':fm,'fruit':rm,'area_difference_flower_minus_fruit':fm['area']-rm['area']
        }
    z.close()
    complete={k:v for k,v in details.items() if v['status']=='CROSS_ORGAN_MEMORY_COMPLETE'}
    names=sorted(complete)
    fa=np.array([complete[k]['flower']['area'] for k in names],float)
    ra=np.array([complete[k]['fruit']['area'] for k in names],float)
    fs=np.array([complete[k]['flower']['slope'] for k in names],float)
    rs=np.array([complete[k]['fruit']['slope'] for k in names],float)
    rho_area,p_area=spearman_permutation_test(fa,ra,permutations,seed)
    rho_slope,p_slope=spearman_permutation_test(fs,rs,permutations,seed+1)
    loo=[]
    for i,k in enumerate(names):
        mask=np.ones(len(names),bool); mask[i]=False
        loo_rho=float(spearmanr(fa[mask],ra[mask]).statistic)
        loo.append({'held_out':k,'rho':loo_rho})
    neg_loo=sum(x['rho']<0 for x in loo)
    flower_dom=int(np.sum(fa>ra)); fruit_dom=int(np.sum(ra>fa)); tied=int(np.sum(np.isclose(fa,ra,atol=1e-12)))
    passed=bool(rho_area<0 and p_area<=0.05)
    return {
        'version':'v0.1',
        'status':'FLOWER_FRUIT_MEMORY_TRADEOFF_PASS' if passed else 'FLOWER_FRUIT_MEMORY_TRADEOFF_FAIL',
        'source_sha256':{'final_dataset.csv':CSV_SHA,'trees.zip':TREES_SHA},
        'eligible_clades':len(names),'hold_clades':len(details)-len(names),
        'primary_test':{'metric':'signed_excess_retention_area','rho':rho_area,'p_one_sided_permutation':p_area,'permutations':permutations,'seed':seed,'decision':'PASS' if passed else 'FAIL'},
        'secondary_slope_test':{'rho':rho_slope,'p_one_sided_permutation':p_slope},
        'leave_one_clade_out':{'negative_rho_count':neg_loo,'total':len(loo),'details':loo},
        'dominance_counts':{'flower_memory_stronger':flower_dom,'fruit_memory_stronger':fruit_dom,'tied':tied},
        'clades':names,
        'results':details,
        'claim_boundary':[
            'retrospective cross-organ derived analysis',
            'not independent of the published flower-fruit color-lability tradeoff',
            'no causal energetic allocation, pollinator, disperser, climate, or pigment mechanism identified',
            'clade is the inferential replication unit'
        ],
        'paper1_science_changed':False,'el_v0_2_science_changed':False
    }

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--csv',type=Path,required=True); ap.add_argument('--trees',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); ap.add_argument('--permutations',type=int,default=PERMUTATIONS); args=ap.parse_args()
    out=analyse(args.csv,args.trees,args.permutations,SEED)
    args.out.parent.mkdir(parents=True,exist_ok=True); args.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:out[k] for k in ['status','eligible_clades','hold_clades','primary_test','secondary_slope_test','dominance_counts']},indent=2))

if __name__=='__main__': main()
