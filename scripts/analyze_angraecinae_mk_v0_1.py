#!/usr/bin/env python3
"""Common two-state Mk reanalysis for organ-specific Angraecinae GREEN/WHITE states.

Uses the same verified BinaryMk likelihood engine as the Hydrangea analysis. Source states
outside GREEN/WHITE are explicitly pruned per organ/policy rather than recoded.
"""
from __future__ import annotations
import argparse,copy,csv,json,math
from pathlib import Path
from Bio import Phylo
from scipy.optimize import minimize_scalar,brentq
from scipy.stats import chi2
from analyze_hydrangea_mk_v0_2 import BinaryMk

POLICIES=('sepal_binary','petal_binary','labellum_binary','spur_binary','display_perianth_concordant','all4_concordant')
PRIMARY={'sepal_binary','petal_binary'}

def root_and_prune(tree,keep,outgroups):
    t=copy.deepcopy(tree);targets=[x for x in outgroups if x in {q.name for q in t.get_terminals()}]
    if len(targets)<2:raise ValueError('insufficient explicit outgroups in tree')
    t.root_with_outgroup(*targets)
    for tip in list(t.get_terminals()):
        if tip.name not in keep:t.prune(tip)
    t.root.branch_length=0.0
    return t

def relabel(fit,tag,policy):
    out={}
    for k,v in fit.items():
        k=k.replace('red','green').replace('nuclear_','sequence_')
        out[k]=v
    out.update(tree=tag,policy=policy,policy_role='PRIMARY_ORGAN' if policy in PRIMARY else 'SENSITIVITY',state0='WHITE',state1='GREEN',rate_ratio_return_to_white_vs_gain_from_white=out['rate_ratio_return_to_gain'])
    return out

def plateau(mk,fit):
    a=fit['q_white_to_green']*mk.scale;b=fit['q_green_to_white']*mk.scale
    delta=mk.calculate(a*1000,b*1000,fit['root_prior'])-fit['log_likelihood']
    return float(delta),bool(abs(delta)<1e-6)

def profile(mk,fit):
    if fit['model']!='ARD' or fit['root_prior']!='equal':raise ValueError('profile requires equal-root ARD')
    if fit['optimization_bound_hit'] or fit['high_rate_plateau']:raise ValueError('boundary/plateau fit cannot receive regular profile')
    best=fit['log_likelihood'];centre=math.log(fit['rate_ratio_return_to_white_vs_gain_from_white']);cut=best-chi2.ppf(.95,1)/2;cache={}
    def ll_at(r):
        r=float(r)
        if r in cache:return cache[r]
        lo=-12+abs(r)/2;hi=12-abs(r)/2
        def obj(u):return -mk.calculate(math.exp(u-r/2),math.exp(u+r/2),'equal')
        grid=[lo+(hi-lo)*i/24 for i in range(25)];vals=[obj(u) for u in grid];j=min(range(len(vals)),key=vals.__getitem__)
        a=grid[max(0,j-1)];b=grid[min(24,j+1)];opt=minimize_scalar(obj,bounds=(a,b),method='bounded',options={'xatol':1e-7});val=-min(float(opt.fun),min(vals))
        if val>best+1e-5:raise ArithmeticError('profile improves on fitted maximum')
        cache[r]=val;return val
    ans={'conditioning':'fixed_tree_organ_policy_equal_root_prior_asymptotic_profile','LR_p_equal_rates':float(chi2.sf(max(0,2*(best-ll_at(0))),1))}
    for label,end in [('low',-10.),('high',10.)]:
        grid=[centre+(end-centre)*i/34 for i in range(35)];br=None;prev=centre
        for x in grid[1:]:
            if ll_at(x)<cut:br=(prev,x);break
            prev=x
        ans[label]=math.exp(brentq(lambda z:ll_at(z)-cut,*sorted(br),xtol=1e-6)) if br else None
        ans[label+'_search_ratio_limit']=math.exp(end)
    return ans

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--trees-dir',type=Path,required=True);ap.add_argument('--sample-manifest',type=Path,required=True);ap.add_argument('--traits',type=Path,required=True);ap.add_argument('--out-dir',type=Path,required=True);a=ap.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
    samples=list(csv.DictReader(a.sample_manifest.open()));traitrows=list(csv.DictReader(a.traits.open()));traits={r['source_taxon']:r for r in traitrows}
    outgroups=[r['tip_id'] for r in samples if r['source_group']=='OUTGROUP'];mapped={r['tip_id']:traits[r['source_taxon']] for r in samples if r['trait_join_status']=='EXACT_UNIQUE' and r['source_taxon'] in traits and r['source_group']=='ANGRAECINAE'}
    fits=[];profiles=[];coverage=[]
    for tag in ('plastid_full','plastid50','all4_full'):
        tree=Phylo.read(a.trees_dir/f'{tag}.treefile','newick');tree_names={x.name for x in tree.get_terminals()}
        for policy in POLICIES:
            state={'WHITE':0,'GREEN':1};states={tip:state[row[policy]] for tip,row in mapped.items() if tip in tree_names and row[policy] in state}
            if set(states.values())!={0,1}:raise ValueError(f'{tag}/{policy} lacks both GREEN and WHITE')
            t=root_and_prune(tree,set(states),outgroups);coverage.append({'tree':tag,'policy':policy,'n_tips':len(states),'white':sum(v==0 for v in states.values()),'green':sum(v==1 for v in states.values()),'outside_binary_or_unjoined':189-len(states)})
            mk=BinaryMk(t,states)
            for prior in ('equal','stationary'):
                for model in ('ER','ARD'):
                    raw=mk.fit(model,prior);fit=relabel(raw,tag,policy);delta,flat=plateau(mk,fit);fit['rate_times_1000_delta_logL']=delta;fit['high_rate_plateau']=flat;fit['inference_status']='BOUNDARY_OR_RATE_PLATEAU_DIAGNOSTIC_ONLY' if fit['optimization_bound_hit'] or flat else 'NUMERICAL_INTERIOR_CONDITIONAL_FIT';fits.append(fit)
                    if model=='ARD' and prior=='equal' and not fit['optimization_bound_hit'] and not flat:
                        p=profile(mk,fit);p.update(tree=tag,policy=policy);profiles.append(p)
    result={'version':'v0.1','status':'EXECUTED_ORGAN_SPECIFIC_BINARY_MK','fits':fits,'profiles':profiles,'coverage':coverage,'primary_policies':sorted(PRIMARY),'sensitivity_policies':[p for p in POLICIES if p not in PRIMARY],'source_tip_join':'Only S1 sample rows with unique exact S3 taxon names are eligible. Other-colour organ states are pruned, never recoded to GREEN/WHITE.','rate_units':'sequence substitutions/site, not years','ancestral_white_imposed':False,'paper1_science_changed':False}
    (a.out_dir/'analysis_results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'fits':len(fits),'profiles':len(profiles),'coverage':coverage},indent=2))
if __name__=='__main__':main()
