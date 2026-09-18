#!/usr/bin/env python3
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import io
import json
import math
import re
import zipfile
from pathlib import Path

import numpy as np
from Bio import Phylo
from scipy.optimize import minimize_scalar
from scipy.stats import friedmanchisquare, wilcoxon

CSV_SHA='a253308785e4cbd0e361b3ca04cdfdae29c523eefa843375cebf8030ee0874af'
TREES_SHA='ae5c82945e5bf9c29bcabc52d6029acd8d4f5be1fe9141fad95918eacb4f674d'
LAMBDA_LO=1e-4
LAMBDA_HI=1e4
MAP={
 'black':('DARK','NONWHITE'),
 'purple':('COOL','NONWHITE'),
 'green':('COOL','NONWHITE'),
 'orange':('WARM','NONWHITE'),
 'pink':('WARM','NONWHITE'),
 'red':('WARM','NONWHITE'),
 'white':('WHITE','WHITE'),
 'yellow':('WARM','NONWHITE'),
}
RES=('coarse','intermediate','fine')


def sha256_file(p:Path)->str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):
            h.update(b)
    return h.hexdigest()


def norm(x:str)->str:
    return re.sub(r'\s+',' ',str(x).strip().replace('_',' ')).lower()


def pair_same_baseline(states:np.ndarray)->float:
    states=np.asarray(states,dtype=object)
    n=len(states)
    counts=collections.Counter(states.tolist())
    return sum(v*(v-1) for v in counts.values())/(n*(n-1))


def half_depth(lam:float)->float:
    return math.log(2.0)/float(lam)


def root_to_tip_cv(tree)->float:
    x=np.array([tree.distance(tree.root,t) for t in tree.get_terminals()],float)
    return float(x.std(ddof=0)/x.mean())


def relative_divergence_depth(tree,dist:np.ndarray)->np.ndarray:
    cv=root_to_tip_cv(tree)
    if not np.isfinite(cv) or cv>1e-8:
        raise ValueError(f'non-ultrametric tree cv={cv}')
    h=float(np.mean([tree.distance(tree.root,t) for t in tree.get_terminals()]))
    d=np.asarray(dist,float)/(2*h)
    if np.nanmin(d)<-1e-12 or np.nanmax(d)>1+1e-8:
        raise ValueError('relative depth outside [0,1]')
    return d


def model_probability(d:np.ndarray,q:float,lam:float)->np.ndarray:
    p=q+(1-q)*np.exp(-lam*np.asarray(d,float))
    return np.clip(p,1e-12,1-1e-12)


def fit_lambda(d:np.ndarray,same:np.ndarray,q:float)->dict:
    d=np.asarray(d,float)
    y=np.asarray(same,bool)
    if not (0<q<1):
        raise ValueError('q must be in (0,1)')
    log_lo,log_hi=math.log(LAMBDA_LO),math.log(LAMBDA_HI)
    def nll(loglam):
        p=model_probability(d,q,math.exp(float(loglam)))
        return -float(np.sum(np.where(y,np.log(p),np.log1p(-p))))
    opt=minimize_scalar(nll,bounds=(log_lo,log_hi),method='bounded',options={'xatol':1e-10})
    lam=float(math.exp(opt.x))
    pnull=np.clip(q,1e-12,1-1e-12)
    null_ll=float(np.sum(np.where(y,math.log(pnull),math.log1p(-pnull))))
    pll=-float(opt.fun)
    near_lower=lam <= LAMBDA_LO*1.001
    near_upper=lam >= LAMBDA_HI/1.001
    return {
      'lambda':lam,
      'half_depth_ln2_over_lambda':half_depth(lam),
      'pseudo_loglik':pll,
      'null_loglik':null_ll,
      'pseudo_loglik_gain_over_q':pll-null_ll,
      'boundary':'LOWER' if near_lower else ('UPPER' if near_upper else 'INTERIOR'),
      'optimization_success':bool(opt.success),
    }


def states_for_fine(fine:np.ndarray)->dict[str,np.ndarray]:
    return {
      'fine':fine,
      'intermediate':np.array([MAP[x][0] for x in fine],object),
      'coarse':np.array([MAP[x][1] for x in fine],object),
    }


def analyse(csv_path:Path,trees_path:Path)->dict:
    if sha256_file(csv_path)!=CSV_SHA or sha256_file(trees_path)!=TREES_SHA:
        raise SystemExit('source hash mismatch')
    src=collections.defaultdict(list)
    with csv_path.open(newline='',encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            src[r['clade'].strip()].append((r['species'].strip(),r['flower_color'].strip()))
    z=zipfile.ZipFile(trees_path)
    members={Path(m).stem.lower():m for m in z.namelist() if not m.endswith('/') and not m.startswith('__MACOSX/') and not m.endswith('.DS_Store')}
    details={}
    for clade in sorted(src):
        vals=src[clade]
        counts=collections.Counter(x[1] for x in vals)
        rare={k for k,v in counts.items() if v<5}
        retained=[x for x in vals if x[1] not in rare]
        fine_raw=[x[1] for x in retained]
        int_raw=[MAP[x][0] for x in fine_raw]
        coarse_raw=[MAP[x][1] for x in fine_raw]
        reasons=[]
        if len(retained)<20: reasons.append('COMMON_TIPS_LT_20')
        if len(set(fine_raw))<2: reasons.append('FINE_STATES_LT_2')
        if len(set(int_raw))<2: reasons.append('INTERMEDIATE_STATES_LT_2')
        if len(set(coarse_raw))<2: reasons.append('COARSE_STATES_LT_2')
        if reasons:
            details[clade]={'status':'HOLD_COMMON_FRAME','reasons':reasons,'eligible_tips':len(retained)}
            continue
        tree=Phylo.read(io.StringIO(z.read(members[clade.lower()]).decode('utf-8-sig')),'newick')
        rb={norm(s):c for s,c in retained}
        tips=[t for t in tree.get_terminals() if norm(t.name) in rb]
        fine=np.array([rb[norm(t.name)] for t in tips],object)
        st=states_for_fine(fine)
        n=len(tips)
        ii,jj=np.triu_indices(n,1)
        dist=np.array([tree.distance(tips[int(a)],tips[int(b)]) for a,b in zip(ii,jj)],float)
        d=relative_divergence_depth(tree,dist)
        res={}
        for name in RES:
            s=st[name]
            same=s[ii]==s[jj]
            q=pair_same_baseline(s)
            fit=fit_lambda(d,same,q)
            res[name]={'q':q,'states':len(set(s.tolist())),**fit}
        details[clade]={
          'status':'RELATIVE_TIME_HALFDEPTH_COMPLETE',
          'eligible_tips':n,
          'root_to_tip_cv':root_to_tip_cv(tree),
          'resolutions':res,
        }
    z.close()

    comp={k:v for k,v in details.items() if v['status']=='RELATIVE_TIME_HALFDEPTH_COMPLETE'}
    names=sorted(comp)
    arrays={r:np.array([comp[k]['resolutions'][r]['half_depth_ln2_over_lambda'] for k in names],float) for r in RES}
    lambdas={r:np.array([comp[k]['resolutions'][r]['lambda'] for k in names],float) for r in RES}
    fr=friedmanchisquare(arrays['coarse'],arrays['intermediate'],arrays['fine'])
    pairwise={}
    if fr.pvalue<=0.05:
        for a,b in [('coarse','intermediate'),('coarse','fine'),('intermediate','fine')]:
            w=wilcoxon(arrays[a],arrays[b],alternative='two-sided',zero_method='wilcox')
            pairwise[f'{a}_vs_{b}']={'statistic':float(w.statistic),'p_two_sided':float(w.pvalue)}
    winners=collections.Counter()
    for k in names:
        vals={r:comp[k]['resolutions'][r]['half_depth_ln2_over_lambda'] for r in RES}
        mx=max(vals.values())
        ws=[r for r,v in vals.items() if np.isclose(v,mx,rtol=1e-8,atol=1e-12)]
        winners['+'.join(ws)]+=1
    summary={
      'median_half_depth':{r:float(np.median(arrays[r])) for r in RES},
      'q25_half_depth':{r:float(np.quantile(arrays[r],0.25)) for r in RES},
      'q75_half_depth':{r:float(np.quantile(arrays[r],0.75)) for r in RES},
      'median_lambda':{r:float(np.median(lambdas[r])) for r in RES},
      'friedman':{'statistic':float(fr.statistic),'p_value':float(fr.pvalue)},
      'pairwise_if_friedman_significant':pairwise,
      'largest_half_depth_counts':dict(sorted(winners.items())),
      'upper_lambda_boundary_counts':{r:int(sum(comp[k]['resolutions'][r]['boundary']=='UPPER' for k in names)) for r in RES},
      'lower_lambda_boundary_counts':{r:int(sum(comp[k]['resolutions'][r]['boundary']=='LOWER' for k in names)) for r in RES},
    }
    return {
      'version':'v0.1',
      'status':'FLOWERCLADES51_RELATIVE_TIME_HALFDEPTH_RESULT',
      'source_sha256':{'final_dataset.csv':CSV_SHA,'trees.zip':TREES_SHA},
      'completed_clades':len(names),
      'hold_clades':len(details)-len(names),
      'clades':names,
      'cross_resolution':summary,
      'results':details,
      'absolute_time_claim_allowed':False,
      'inference_boundary':'clade is inferential unit; pairwise Bernoulli likelihood is pseudo-likelihood used to define a within-clade decay estimand',
      'independent_replication':False,
      'paper1_science_changed':False,
      'el_v0_2_science_changed':False,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--csv',type=Path,required=True)
    ap.add_argument('--trees',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    out=analyse(a.csv,a.trees)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps({
      'status':out['status'],
      'completed_clades':out['completed_clades'],
      'cross_resolution':out['cross_resolution'],
    },indent=2))


if __name__=='__main__':
    main()
