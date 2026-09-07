#!/usr/bin/env python3
"""Conditional likelihood profiles and independent topology-sensitivity audit.

The 95% profile interval is an asymptotic LR interval conditional on the input
tree/model, not a posterior credible interval or an interval over phylogenies.
UFBOOT realizations are sequence-resampling sensitivity, not independent clades.
"""
from __future__ import annotations
import argparse, csv, json, copy
from pathlib import Path
import numpy as np
from scipy.optimize import minimize_scalar, brentq
from scipy.stats import chi2
from Bio import Phylo
from analyze_hydrangea_mk_v0_2 import BinaryMk, ingroup_tree, SEED


def minimum_changes(tree, states):
    costs={}
    for n in tree.find_clades(order='postorder'):
        if n.is_terminal():
            costs[id(n)]=np.array([0 if states[n.name]==s else np.inf for s in (0,1)])
        else:
            costs[id(n)]=np.array([sum(min(costs[id(c)][t]+(s!=t) for t in (0,1)) for c in n.clades) for s in (0,1)])
    v=costs[id(tree.root)]
    return int(min(v)), [int(x) for x in v]


def profile(mk, prior, fit):
    optimum=np.log(fit['rate_ratio_return_to_gain'])
    target=chi2.ppf(.95,1)
    cache={}
    def prof(x):
        key=float(x)
        if key not in cache:
            lo=max(-12.,-12.-x);hi=min(12.,12.-x)
            def f(z):return -mk.calculate(float(np.exp(z)),float(np.exp(z+x)),prior)
            grid=np.linspace(lo,hi,25)
            vals=np.array([f(z) for z in grid]); j=int(np.argmin(vals))
            candidates=[float(vals[j])]
            if j>0 and j<len(grid)-1:
                res=minimize_scalar(f,bounds=(grid[j-1],grid[j+1]),method='bounded',options={'xatol':1e-9})
                candidates.append(float(res.fun))
            cache[key]=-min(candidates)
        return cache[key]
    ll=fit['log_likelihood']
    if abs(prof(optimum)-ll)>1e-5:raise ValueError('profile/full optimization disagreement')
    def threshold(x):return 2*(ll-prof(x))-target
    bounds=[]
    for direction in (-1,1):
        last=optimum;root=None
        for step in np.linspace(.25,8,32):
            x=optimum+direction*step
            if abs(x)>=11:break
            if threshold(x)>0:
                root=brentq(threshold,min(last,x),max(last,x),xtol=1e-6);break
            last=x
        bounds.append(None if root is None else float(np.exp(root)))
    lrt=2*(ll-prof(0.))
    return dict(root_prior=prior,rate_ratio=fit['rate_ratio_return_to_gain'],
        profile95_lower=bounds[0],profile95_upper=bounds[1],
        LR_against_equal_rates=lrt,asymptotic_chi2_p=float(chi2.sf(max(0,lrt),1)),
        criterion='2*loglik_drop=chi2_1(.95); conditional_on_tree; NOT_Bayesian',
        profile_curve=[dict(rate_ratio=float(np.exp(x)),log_likelihood=prof(x)) for x in np.linspace(optimum-2,optimum+2,25)])


def run(base: Path, out: Path, bootstrap_fits: int=20, profiles_only: bool=False):
    rows=list(csv.DictReader((base/'prepared/terminal_states.csv').open()))
    states={r['accession']:{'WHITE':0,'RED':1}[r['visible_state']] for r in rows if r['sampled_clade']=='CORNIDIA'}
    previous=json.loads((base/'analysis/analysis_summary.json').read_text())['primary_fits']
    out.mkdir(parents=True,exist_ok=True)
    profiles=[];boots=[];counts=[]
    for tag in ('short_3161','long_3167'):
        tree=Phylo.read(base/'trees'/f'{tag}.treefile','newick')
        tree,mono=ingroup_tree(tree,states)
        if not mono:raise ValueError('ingroup not monophyletic in primary reconstruction')
        Phylo.write(tree,out/f'{tag}_cornidia_fullprecision.nwk','newick',format_branch_length='%1.12f')
        mk=BinaryMk(tree,states)
        for prior in ('equal','stationary'):
            fit=next(r for r in previous if r['model']=='ARD' and r['root_prior']==prior and r['alignment']==tag)
            pr=profile(mk,prior,fit);pr['alignment']=tag;profiles.append(pr)
        # Every topology is checked; a seed-frozen subset receives rate fitting.
        if profiles_only:
            continue
        trees=list(Phylo.parse(base/'trees'/f'{tag}.ufboot','newick'))
        if len(trees)!=1000:raise ValueError('expected 1000 ultrafast bootstrap realizations')
        rng=np.random.default_rng(SEED)
        chosen=set(int(i) for i in rng.choice(len(trees),size=bootstrap_fits,replace=False))
        for i,t in enumerate(trees):
            t,mono=ingroup_tree(t,states)
            m,root_m=minimum_changes(t,states)
            counts.append(dict(alignment=tag,bootstrap_index=i,monophyletic=mono,
                               minimum_changes=m,white_root_minimum=root_m[0],red_root_minimum=root_m[1]))
            if i in chosen:
                if not mono:
                    boots.append(dict(alignment=tag,bootstrap_index=i,status='NONMONOPHYLETIC_HELD_OUT'));continue
                mk=BinaryMk(t,states)
                a=mk.fit('ARD','equal',detailed=False);e=mk.fit('ER','equal',detailed=False)
                boots.append(dict(alignment=tag,bootstrap_index=i,status='FITTED',
                    rate_ratio=a['rate_ratio_return_to_gain'],delta_AIC_ARD_minus_ER=a['AIC']-e['AIC'],
                    optimization_bound_hit=a['optimization_bound_hit'],minimum_changes=m))
    def write(name, records):
        fields=sorted(set().union(*(r.keys() for r in records)))
        with (out/name).open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(records)
    write('bootstrap_model_fits.csv',boots);write('bootstrap_minimum_changes.csv',counts)
    summary=dict(profiles=profiles,bootstrap_fits_per_alignment=bootstrap_fits,seed=SEED,
        boundary='Sequence-bootstrap sensitivity and conditional ML profiles; no dated species-tree or cross-clade inference',
        bootstrap_status='NOT_REQUESTED_PROFILES_ONLY' if profiles_only else 'EXECUTED',per_alignment={})
    for tag in ('short_3161','long_3167'):
        if profiles_only:
            continue
        tt=[r for r in counts if r['alignment']==tag]
        rr=[r for r in boots if r['alignment']==tag and r['status']=='FITTED']
        interior=[r for r in rr if not r['optimization_bound_hit']]
        summary['per_alignment'][tag]=dict(total_bootstrap_topologies=len(tt),
            monophyletic=sum(r['monophyletic'] for r in tt),
            minimum_changes_quantiles=np.quantile([r['minimum_changes'] for r in tt],[0,.5,1]).tolist(),
            model_fits=len(rr),interior_model_fits=len(interior),
            rate_ratio_quantiles_interior=np.quantile([r['rate_ratio'] for r in interior],[0,.5,1]).tolist() if interior else None,
            delta_AIC_quantiles_interior=np.quantile([r['delta_AIC_ARD_minus_ER'] for r in interior],[0,.5,1]).tolist() if interior else None,
            ratio_gt_one_interior=sum(r['rate_ratio']>1 for r in interior))
    (out/'robustness_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k!='profiles'},indent=2))
    print(json.dumps([{k:v for k,v in r.items() if k!='profile_curve'} for r in profiles],indent=2))
    return summary

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--base',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--bootstrap-fits',type=int,default=20);p.add_argument('--profiles-only',action='store_true')
    a=p.parse_args();run(a.base,a.out,a.bootstrap_fits,a.profiles_only)
