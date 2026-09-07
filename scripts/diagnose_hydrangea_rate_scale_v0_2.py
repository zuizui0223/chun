#!/usr/bin/env python3
"""Identify the high-rate likelihood plateau, not only optimizer box contact."""
from __future__ import annotations
import csv,copy,json,argparse
from pathlib import Path
import numpy as np
from Bio import Phylo
from analyze_hydrangea_mk_v0_2 import BinaryMk,ingroup_tree


def diagnose(base: Path,out: Path):
    rows=list(csv.DictReader((base/'prepared/terminal_states.csv').open()))
    states={r['accession']:{'WHITE':0,'RED':1}[r['visible_state']] for r in rows if r['sampled_clade']=='CORNIDIA'}
    trees={tag:ingroup_tree(Phylo.read(base/'trees'/f'{tag}.treefile','newick'),states)[0] for tag in ('short_3161','long_3167')}
    fits=list(csv.DictReader((base/'analysis/model_fits.csv').open()))
    for r in fits:
        t=copy.deepcopy(trees[r['alignment']])
        keep=set(r['chosen_accessions'].split(';')) if r['chosen_accessions'] else set(states)
        for tip in list(t.get_terminals()):
            if tip.name not in keep:t.prune(tip)
        t.root.branch_length=0.
        mk=BinaryMk(t,{x:states[x] for x in keep})
        a=float(r['q_white_to_red'])*mk.scale;b=float(r['q_red_to_white'])*mk.scale
        ll=mk.calculate(a,b,r['root_prior'])
        if abs(ll-float(r['log_likelihood']))>1e-6:raise ValueError('stored rate/likelihood mismatch')
        high=mk.calculate(a*1000,b*1000,r['root_prior'])
        r['loglik_gap_to_1000x_rate']=ll-high
        r['rate_scale_unidentified']=abs(ll-high)<1e-6
    out.mkdir(parents=True,exist_ok=True)
    with (out/'model_fits_diagnosed.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(fits[0]));w.writeheader();w.writerows(fits)
    result={}
    for tag in trees:
        r=[r for r in fits if r['alignment']==tag and r['sampling']=='ONE_ACCESSION_PER_SOURCE_TAXON' and r['model']=='ARD']
        usable=[a for a in r if not a['rate_scale_unidentified'] and a['optimization_bound_hit']=='False']
        result[tag]=dict(draws=len(r),usable_ARD_draws=len(usable),
            scale_unidentified_draws=[int(float(a['draw'])) for a in r if a['rate_scale_unidentified']],
            usable_ratio_min_median_max=np.quantile([float(a['rate_ratio_return_to_gain']) for a in usable],[0,.5,1]).tolist(),
            ratio_gt_one_usable=sum(float(a['rate_ratio_return_to_gain'])>1 for a in usable))
    result['criterion']='abs(logL(Q)-logL(1000*Q))<1e-6; retain ratio but hold out speed-unidentified fits from robustness count'
    result['all_primary_scale_identified']=not any(r['rate_scale_unidentified'] for r in fits if r['sampling']=='ALL_ACCESSIONS')
    (out/'rate_scale_diagnostic.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--base',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();diagnose(a.base,a.out)
