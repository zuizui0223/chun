#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, math
from pathlib import Path

PRIMARY=('sepal_binary','petal_binary')
TREES=('plastid_full','plastid50','all4_full')

def sha256(p:Path):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def rounded(x):
    if isinstance(x,float):
        return float(format(x,'.8g'))
    if isinstance(x,list): return [rounded(v) for v in x]
    if isinstance(x,dict): return {k:rounded(v) for k,v in x.items()}
    return x

def fit_summary(a,policy):
    fits=[x for x in a['fits'] if x['policy']==policy]
    profiles={(x['tree'],x['policy']):x for x in a['profiles']}
    rows=[]
    for tree in TREES:
        ard=next(x for x in fits if x['tree']==tree and x['model']=='ARD' and x['root_prior']=='equal')
        er=next(x for x in fits if x['tree']==tree and x['model']=='ER' and x['root_prior']=='equal')
        pr=profiles[(tree,policy)]
        rows.append({'tree':tree,'n_tips':ard['n_tips'],'rate_ratio_return_to_white_vs_gain_from_white':ard['rate_ratio_return_to_white_vs_gain_from_white'],'delta_AIC_ARD_minus_ER':ard['AIC']-er['AIC'],'profile95_low':pr['low'],'profile95_high':pr['high'],'LR_p_equal_rates':pr['LR_p_equal_rates'],'root_probability_white_equal_ARD':ard['root_probability_white'],'optimization_bound_hit':ard['optimization_bound_hit'],'high_rate_plateau':ard['high_rate_plateau']})
    minroot=min(x['root_probability_white'] for x in fits)
    directions=['WHITE_TO_GREEN_FASTER' if r['rate_ratio_return_to_white_vs_gain_from_white']<1 else 'GREEN_TO_WHITE_FASTER' for r in rows]
    direction=directions[0] if len(set(directions))==1 else 'MIXED'
    if direction=='WHITE_TO_GREEN_FASTER':
        prof=sum(r['profile95_high'] is not None and r['profile95_high']<1 for r in rows)
    elif direction=='GREEN_TO_WHITE_FASTER':
        prof=sum(r['profile95_low'] is not None and r['profile95_low']>1 for r in rows)
    else: prof=0
    aic=sum(r['delta_AIC_ARD_minus_ER']<=-2 for r in rows)
    return {'fits':rows,'point_direction_all_three':direction,'profiles_excluding_one_same_direction':prof,'fits_with_AIC_improvement_ge2_same_direction':aic,'min_root_probability_white_all_models_priors_trees':minroot,'robust_white_root_ge_0_8':minroot>=0.8}

def replicate_summary(result_dir:Path):
    a=json.loads((result_dir/'analysis_results.json').read_text())
    c=json.loads((result_dir/'conditional_organ_state_results.json').read_text())
    if len(a['fits'])!=72 or len(a['profiles'])!=12: raise ValueError('incomplete Mk execution')
    if len(c['tests'])!=3 or any(t['permutations']!=9999 for t in c['tests']): raise ValueError('incomplete conditional tests')
    p={policy:fit_summary(a,policy) for policy in PRIMARY}
    dir_pass=all(v['point_direction_all_three']!='MIXED' and v['profiles_excluding_one_same_direction']>=2 and v['fits_with_AIC_improvement_ge2_same_direction']>=2 for v in p.values())
    white_pass=all(v['robust_white_root_ge_0_8'] for v in p.values())
    cond={t['tree']:{'observed_minimum_changes':t['observed_minimum_changes'],'null_mean':t['null_mean'],'observed_over_null_mean':t['observed_over_null_mean'],'p':t['lower_tail_p']} for t in c['tests']}
    return {'primary':p,'directional_asymmetry_gate':'PASS' if dir_pass else 'FAIL','robust_white_root_gate':'PASS' if white_pass else 'FAIL','robust_white_root_min_probability':min(v['min_root_probability_white_all_models_priors_trees'] for v in p.values()),'conditional_organ_state_signal':{'tests':3,'p_range':[min(x['p'] for x in cond.values()),max(x['p'] for x in cond.values())],'observed_over_null_range':[min(x['observed_over_null_mean'] for x in cond.values()),max(x['observed_over_null_mean'] for x in cond.values())],'trees':cond}}

def build(resumed:Path,fresh:Path,manifest:Path):
    m=json.loads(manifest.read_text())
    root=manifest.parent
    for rel,h in m['frozen_files_sha256'].items():
        p=root/rel
        if sha256(p)!=h: raise ValueError('checksum mismatch: '+rel)
    reps={'checkpoint_resume':replicate_summary(resumed),'fresh_repeat':replicate_summary(fresh)}
    conds=[x for r in reps.values() for x in r['conditional_organ_state_signal']['trees'].values()]
    out={'version':'v0.1','status':'EXECUTED_THIRD_RADIATION_WITH_TREE_RECONSTRUCTION_SENSITIVITY','source_doi':'10.1371/journal.pone.0163194','source_terminal_rows':194,'source_ingroup_rows':189,'exact_unique_ingroup_trait_joins':186,'source_four_organ_fully_binary_rows':170,'analysis_exact_four_organ_tips':169,'tree_reconstruction_sets':m['tree_reconstruction_sets'],'replicates':reps,'directional_asymmetry_gate':'FAIL_IN_BOTH_TREE_RECONSTRUCTIONS' if all(r['directional_asymmetry_gate']=='FAIL' for r in reps.values()) else 'NOT_CONSISTENT','robust_white_root_gate':'PASS_IN_BOTH_TREE_RECONSTRUCTIONS' if all(r['robust_white_root_gate']=='PASS' for r in reps.values()) else 'NOT_CONSISTENT','robust_white_root_min_probability_across_reconstructions':min(r['robust_white_root_min_probability'] for r in reps.values()),'conditional_organ_state_signal_across_reconstructions':{'tests':len(conds),'p_range':[min(x['p'] for x in conds),max(x['p'] for x in conds)],'observed_over_null_range':[min(x['observed_over_null_mean'] for x in conds),max(x['observed_over_null_mean'] for x in conds)],'all_tests_p_0_0001':all(x['p']==0.0001 for x in conds)},'tree_reconstruction_nondeterminism_retained':True,'universal_white_direction_law':'NOT_SUPPORTED','paper1_science_changed':False,'interpretation':'Across two independently executed ML reconstruction sets, Angraecinae retains a robust WHITE root but fails the pre-frozen directional-asymmetry gate. Four-organ state structure remains phylogenetically organized conditional on coarse primary GREEN/WHITE status in all six tree tests. Tree-reconstruction variation is retained as sensitivity rather than hidden.'}
    return rounded(out)

def compare(e,a,path='summary'):
    if type(e) is not type(a): raise ValueError(path+': type mismatch')
    if isinstance(e,dict):
        if set(e)!=set(a): raise ValueError(path+': key mismatch')
        for k in e: compare(e[k],a[k],path+'.'+k)
    elif isinstance(e,list):
        if len(e)!=len(a): raise ValueError(path+': length mismatch')
        for i,(x,y) in enumerate(zip(e,a)): compare(x,y,f'{path}[{i}]')
    elif isinstance(e,float):
        if not math.isclose(e,a,rel_tol=2e-4,abs_tol=2e-5): raise ValueError(f'{path}: numeric drift {e} != {a}')
    elif e!=a: raise ValueError(path+': value mismatch')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--resumed',type=Path,required=True);ap.add_argument('--fresh',type=Path,required=True);ap.add_argument('--manifest',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--expected',type=Path);a=ap.parse_args()
    s=build(a.resumed,a.fresh,a.manifest)
    if a.expected: compare(json.loads(a.expected.read_text()),s)
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
