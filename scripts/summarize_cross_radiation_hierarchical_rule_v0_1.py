#!/usr/bin/env python3
"""Derive the three-radiation flower-colour rule from authoritative summaries.

This script deliberately separates (1) robust ancestral WHITE, (2) supported
transition direction, and (3) fine-state phylogenetic organization conditional
on a coarser colour class. It does not treat topology/alignment sensitivities as
independent biological replications.
"""
from __future__ import annotations
import argparse,json,math
from pathlib import Path


def hydrangea(path: Path):
    x=json.loads(path.read_text())
    primary=x['primary_fits']
    eq_ard=[r for r in primary if r['model']=='ARD' and r['root_prior']=='equal']
    if len(eq_ard)!=2: raise ValueError('Hydrangea primary equal-root ARD set changed')
    # A strong direction would need both a profile excluding 1 and >=2 AIC gain.
    strong=[]
    for ard in eq_ard:
        er=next(r for r in primary if r['alignment']==ard['alignment'] and r['model']=='ER' and r['root_prior']=='equal')
        excludes=(ard['profile95_upper']<1 or ard['profile95_lower']>1)
        strong.append(excludes and ard['AIC']<=er['AIC']-2)
    min_root=min(float(r['root_probability_white']) for r in primary)
    ratios=[float(r['rate_ratio_return_to_gain']) for r in eq_ard]
    return {
      'id':'HYDRANGEA_CORNIDIA','source_to_tree_reanalysis':True,
      'robust_white_root':bool(min_root>=0.8),'minimum_root_probability_white':min_root,
      'strong_direction_supported':bool(all(strong)),
      'regular_equal_root_rate_ratio_range':[min(ratios),max(ratios)],
      'point_direction':'COLOURED_TO_WHITE_FASTER_POINT_ESTIMATE',
      'fine_state_conditional_test':'NOT_TESTABLE_WITH_CURRENT_INGROUP_BINARY_WHITE_RED_CODING',
      'fine_state_dimension':None,
      'claim_boundary':'Two nuclear-tree treatments are one radiation; profile intervals are conditional on fixed trees.'}


def linoideae(path: Path):
    x=json.loads(path.read_text())
    union=[r for r in x['union_primary_fits'] if r['root_prior']=='equal']
    regular=[]
    for ard in [r for r in union if r['model']=='ARD']:
        if ard['optimization_bound_hit'] or ard['high_rate_plateau']: continue
        er=next(r for r in union if r['alignment']==ard['alignment'] and r['model']=='ER')
        prof=next((p for p in x['regular_conditional_profiles'] if p['alignment']==ard['alignment'] and p['coding']=='UNION'),None)
        excludes=bool(prof and ((prof['high'] is not None and prof['high']<1) or (prof['low'] is not None and prof['low']>1)))
        regular.append({'alignment':ard['alignment'],'ratio':ard['rate_ratio_return_to_gain'],'strong':excludes and ard['AIC']<=er['AIC']-2})
    if not regular: raise ValueError('no regular Linoideae UNION ARD fits')
    fine=x['hue_signal_conditional_on_white_status']
    fine_supported=(fine['tests']>=1 and max(fine['p_range'])<=0.0001 and max(fine['observed_over_null_range'])<1)
    return {
      'id':'LINOIDEAE','source_to_tree_reanalysis':True,
      'robust_white_root':x['ancestral_white_admission']=='ROBUST_WHITE',
      'minimum_root_probability_white':None,
      'strong_direction_supported':bool(any(r['strong'] for r in regular)),
      'regular_union_rate_ratio_range':[min(r['ratio'] for r in regular),max(r['ratio'] for r in regular)],
      'point_direction':'WHITE_TO_NONWHITE_FASTER_IN_REGULAR_UNION_POINT_ESTIMATES',
      'fine_state_conditional_test':'SUPPORTED' if fine_supported else 'NOT_SUPPORTED',
      'fine_state_dimension':'HUE',
      'fine_state_tests':fine['tests'],'fine_state_p_range':fine['p_range'],
      'fine_state_observed_over_null_range':fine['observed_over_null_range'],
      'claim_boundary':'Tree/source-coding sensitivities are correlated settings within one radiation; hue signal does not identify ecological or molecular cause.'}


def angraecinae(path: Path):
    x=json.loads(path.read_text())
    fine=x['conditional_organ_state_signal_across_reconstructions']
    fine_supported=(fine['tests']==6 and fine['all_tests_p_0_0001'] and max(fine['observed_over_null_range'])<1)
    return {
      'id':'ANGRAECINAE','source_to_tree_reanalysis':True,
      'robust_white_root':x['robust_white_root_gate']=='PASS_IN_BOTH_TREE_RECONSTRUCTIONS',
      'minimum_root_probability_white':x['robust_white_root_min_probability_across_reconstructions'],
      'strong_direction_supported':x['directional_asymmetry_gate']!='FAIL_IN_BOTH_TREE_RECONSTRUCTIONS',
      'point_direction':'WHITE_TO_GREEN_FASTER_POINT_ESTIMATES_BUT_GATE_FAILS',
      'tree_reconstruction_sets':len(x['tree_reconstruction_sets']),
      'fine_state_conditional_test':'SUPPORTED' if fine_supported else 'NOT_SUPPORTED',
      'fine_state_dimension':'FLORAL_ORGAN_CONFIGURATION',
      'fine_state_tests':fine['tests'],'fine_state_p_range':fine['p_range'],
      'fine_state_observed_over_null_range':fine['observed_over_null_range'],
      'claim_boundary':'Two executed ML reconstruction sets are sensitivities within one radiation; organ signal does not identify ecological or molecular cause.'}


def build(hyd:Path,lino:Path,ang:Path):
    clades=[hydrangea(hyd),linoideae(lino),angraecinae(ang)]
    directional=[c for c in clades if c['strong_direction_supported']]
    robust_white=[c for c in clades if c['robust_white_root']]
    nested=[c for c in clades if c['fine_state_conditional_test']!='NOT_TESTABLE_WITH_CURRENT_INGROUP_BINARY_WHITE_RED_CODING']
    nested_supported=[c for c in nested if c['fine_state_conditional_test']=='SUPPORTED']
    # A direct sufficiency test exists because Angraecinae has robust WHITE ancestry
    # while failing the pre-frozen direction gate.
    white_sufficient=all(c['strong_direction_supported'] for c in robust_white) if robust_white else None
    out={
      'version':'v0.1',
      'status':'THREE_RADIATION_DIRECTION_AUDIT_TWO_RADIATION_FINE_STATE_REPLICATION',
      'external_radiations_evaluated':len(clades),
      'clades':clades,
      'direction_rule':{
        'strong_direction_pass_count':len(directional),
        'universal_white_transition_direction':'NOT_SUPPORTED',
        'point_estimates_are_not_used_as_law':True,
        'interpretation':'The three source-to-tree reanalyses do not yield a shared supported transition-rate direction.'},
      'ancestry_direction_decoupling':{
        'robust_white_root_radiations':[c['id'] for c in robust_white],
        'robust_white_root_sufficient_for_supported_direction':white_sufficient,
        'direct_counterexample':'ANGRAECINAE' if any(c['id']=='ANGRAECINAE' and c['robust_white_root'] and not c['strong_direction_supported'] for c in clades) else None,
        'interpretation':'A robust WHITE ancestral state can coexist with failure to support directional rate asymmetry.'},
      'hierarchical_fine_state_rule':{
        'testable_external_radiations':len(nested),
        'supporting_external_radiations':len(nested_supported),
        'supporting_ids':[c['id'] for c in nested_supported],
        'dimensions':[c['fine_state_dimension'] for c in nested_supported],
        'status':'REPLICATED_CANDIDATE_2_OF_2_TESTABLE_EXTERNAL_RADIATIONS' if len(nested)==2 and len(nested_supported)==2 else 'NOT_REPLICATED_UNDER_CURRENT_GATE',
        'candidate_rule':'Coarse ancestral/display state constrains the evolutionary state space without fixing a universal transition direction; phylogenetic organization can persist at finer hue or organ levels after conditioning on the coarse colour class.',
        'law_status':'NOT_YET_A_UNIVERSAL_LAW',
        'next_gate':'Test at least one additional independent radiation with a nested fine-state representation under the same conditional-null logic.'},
      'paper1_science_changed':False,
      'claim_boundary':'Sensitivity trees, alignments, source codings and reconstruction repeats are not counted as independent radiations. The replicated fine-state result currently comes from Linoideae and Angraecinae only; Hydrangea lacks a comparable nested fine-state ingroup test in the current coding.'}
    }
    return out


def compare(e,a,path='summary'):
    if type(e) is not type(a): raise ValueError(path+': type mismatch')
    if isinstance(e,dict):
        if set(e)!=set(a): raise ValueError(path+': key mismatch')
        for k in e: compare(e[k],a[k],path+'.'+k)
    elif isinstance(e,list):
        if len(e)!=len(a): raise ValueError(path+': length mismatch')
        for i,(x,y) in enumerate(zip(e,a)): compare(x,y,f'{path}[{i}]')
    elif isinstance(e,float):
        if not math.isclose(e,a,rel_tol=1e-8,abs_tol=1e-10): raise ValueError(f'{path}: numeric drift {e} != {a}')
    elif e!=a: raise ValueError(f'{path}: value drift {e!r} != {a!r}')

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--hydrangea',type=Path,default=Path('data/hydrangea_source_reanalysis_v0_2/frozen_results.json'))
    p.add_argument('--linoideae',type=Path,default=Path('data/linoideae_source_reanalysis_v0_2/analysis_summary.json'))
    p.add_argument('--angraecinae',type=Path,default=Path('data/angraecinae_source_reanalysis_v0_1/analysis_summary.json'))
    p.add_argument('--out',type=Path,required=True);p.add_argument('--expected',type=Path)
    a=p.parse_args(); result=build(a.hydrangea,a.linoideae,a.angraecinae)
    if a.expected: compare(json.loads(a.expected.read_text()),result)
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
