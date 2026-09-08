#!/usr/bin/env python3
"""Derive the cross-radiation hierarchical flower-colour rule v0.2.

The decision layer keeps three distinct questions separate:
1) supported transition-rate direction, where three source-to-tree Mk systems are testable;
2) robust ancestral WHITE, where only systems with a compatible root analysis are judged;
3) nested fine-state organization conditional on a coarse colour/pigment class.

Sensitivity trees, source codings and posterior trees are never counted as independent
biological radiations.
"""
from __future__ import annotations
import argparse, json, math
from pathlib import Path


def hydrangea(path: Path):
    x=json.loads(path.read_text()); primary=x['primary_fits']
    eq_ard=[r for r in primary if r['model']=='ARD' and r['root_prior']=='equal']
    if len(eq_ard)!=2: raise ValueError('Hydrangea primary equal-root ARD set changed')
    strong=[]
    for ard in eq_ard:
        er=next(r for r in primary if r['alignment']==ard['alignment'] and r['model']=='ER' and r['root_prior']=='equal')
        excludes=(ard['profile95_upper']<1 or ard['profile95_lower']>1)
        strong.append(excludes and ard['AIC']<=er['AIC']-2)
    min_root=min(float(r['root_probability_white']) for r in primary)
    ratios=[float(r['rate_ratio_return_to_gain']) for r in eq_ard]
    return {
      'id':'HYDRANGEA_CORNIDIA','direction_testable':True,'source_to_tree_reanalysis':True,
      'robust_white_root_testable':True,'robust_white_root':bool(min_root>=0.8),'minimum_root_probability_white':min_root,
      'strong_direction_supported':bool(all(strong)),
      'regular_equal_root_rate_ratio_range':[min(ratios),max(ratios)],
      'point_direction':'COLOURED_TO_WHITE_FASTER_POINT_ESTIMATE',
      'fine_state_conditional_test':'NOT_TESTABLE_WITH_CURRENT_INGROUP_BINARY_WHITE_RED_CODING','fine_state_dimension':None,
      'claim_boundary':'Two nuclear-tree treatments are one radiation; profile intervals are conditional on fixed trees.'}


def linoideae(path: Path):
    x=json.loads(path.read_text())
    union=[r for r in x['union_primary_fits'] if r['root_prior']=='equal']; regular=[]
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
      'id':'LINOIDEAE','direction_testable':True,'source_to_tree_reanalysis':True,
      'robust_white_root_testable':True,'robust_white_root':x['ancestral_white_admission']=='ROBUST_WHITE','minimum_root_probability_white':None,
      'strong_direction_supported':bool(any(r['strong'] for r in regular)),
      'regular_union_rate_ratio_range':[min(r['ratio'] for r in regular),max(r['ratio'] for r in regular)],
      'point_direction':'WHITE_TO_NONWHITE_FASTER_IN_REGULAR_UNION_POINT_ESTIMATES',
      'fine_state_conditional_test':'SUPPORTED' if fine_supported else 'NOT_SUPPORTED','fine_state_dimension':'HUE',
      'fine_state_tests':fine['tests'],'fine_state_p_range':fine['p_range'],'fine_state_observed_over_null_range':fine['observed_over_null_range'],
      'claim_boundary':'Tree/source-coding sensitivities are correlated settings within one radiation; hue signal does not identify ecological or molecular cause.'}


def angraecinae(path: Path):
    x=json.loads(path.read_text()); fine=x['conditional_organ_state_signal_across_reconstructions']
    fine_supported=(fine['tests']==6 and fine['all_tests_p_0_0001'] and max(fine['observed_over_null_range'])<1)
    return {
      'id':'ANGRAECINAE','direction_testable':True,'source_to_tree_reanalysis':True,
      'robust_white_root_testable':True,'robust_white_root':x['robust_white_root_gate']=='PASS_IN_BOTH_TREE_RECONSTRUCTIONS',
      'minimum_root_probability_white':x['robust_white_root_min_probability_across_reconstructions'],
      'strong_direction_supported':x['directional_asymmetry_gate']!='FAIL_IN_BOTH_TREE_RECONSTRUCTIONS',
      'point_direction':'WHITE_TO_GREEN_FASTER_POINT_ESTIMATES_BUT_GATE_FAILS','tree_reconstruction_sets':len(x['tree_reconstruction_sets']),
      'fine_state_conditional_test':'SUPPORTED' if fine_supported else 'NOT_SUPPORTED','fine_state_dimension':'FLORAL_ORGAN_CONFIGURATION',
      'fine_state_tests':fine['tests'],'fine_state_p_range':fine['p_range'],'fine_state_observed_over_null_range':fine['observed_over_null_range'],
      'claim_boundary':'Two executed ML reconstruction sets are sensitivities within one radiation; organ signal does not identify ecological or molecular cause.'}


def antirrhineae(path: Path):
    x=json.loads(path.read_text()); mono=x['datasets']['monomorphic']; poly=x['datasets']['polymorphic']
    supported=(x['pre_frozen_gate']=='PASS' and x['third_independent_replication_admitted'] and mono['passing_tests_p_le_0_01_ratio_lt_1']>=18 and poly['passing_tests_p_le_0_01_ratio_lt_1']>=18)
    return {
      'id':'ANTIRRHINEAE','direction_testable':False,'source_to_tree_reanalysis':False,
      'robust_white_root_testable':False,'robust_white_root':None,'minimum_root_probability_white':None,
      'strong_direction_supported':None,'point_direction':'NOT_EVALUATED_IN_THIS_FINE_STATE_GATE',
      'fine_state_conditional_test':'SUPPORTED' if supported else 'NOT_SUPPORTED','fine_state_dimension':'PIGMENT_CLASS',
      'fine_state_primary_tests':20,'fine_state_primary_passing':mono['passing_tests_p_le_0_01_ratio_lt_1'],
      'fine_state_sensitivity_tests':20,'fine_state_sensitivity_passing':poly['passing_tests_p_le_0_01_ratio_lt_1'],
      'fine_state_primary_p_range':mono['p_range'],'fine_state_primary_observed_over_null_range':mono['observed_over_null_range'],
      'fine_state_sensitivity_p_range':poly['p_range'],'fine_state_sensitivity_observed_over_null_range':poly['observed_over_null_range'],
      'source_integrity_status':x['source_integrity_status'],
      'claim_boundary':'Posterior trees are correlated uncertainty within one radiation. Historical ISTA MD5 drift remains explicit; this test does not estimate ancestry or transition rates.'}


def build(hyd:Path,lino:Path,ang:Path,anti:Path):
    systems=[hydrangea(hyd),linoideae(lino),angraecinae(ang),antirrhineae(anti)]
    direction_testable=[s for s in systems if s['direction_testable']]
    directional=[s for s in direction_testable if s['strong_direction_supported']]
    root_testable=[s for s in systems if s['robust_white_root_testable']]
    robust_white=[s for s in root_testable if s['robust_white_root']]
    nested=[s for s in systems if s['fine_state_conditional_test']!='NOT_TESTABLE_WITH_CURRENT_INGROUP_BINARY_WHITE_RED_CODING']
    nested_supported=[s for s in nested if s['fine_state_conditional_test']=='SUPPORTED']
    white_sufficient=all(s['strong_direction_supported'] for s in robust_white) if robust_white else None
    return {
      'version':'v0.2','status':'THREE_RADIATION_DIRECTION_AUDIT_THREE_RADIATION_FINE_STATE_REPLICATION',
      'external_systems_in_decision_layer':len(systems),'systems':systems,
      'direction_rule':{
        'testable_radiations':len(direction_testable),'strong_direction_pass_count':len(directional),
        'universal_white_transition_direction':'NOT_SUPPORTED','point_estimates_are_not_used_as_law':True,
        'interpretation':'The three source-to-tree Mk reanalyses do not yield a shared supported transition-rate direction. Antirrhineae is not added to this denominator because v0.1 there is a nested-state organization test, not a transition-rate reanalysis.'},
      'ancestry_direction_decoupling':{
        'root_testable_radiations':len(root_testable),'robust_white_root_radiations':[s['id'] for s in robust_white],
        'robust_white_root_sufficient_for_supported_direction':white_sufficient,
        'direct_counterexample':'ANGRAECINAE' if any(s['id']=='ANGRAECINAE' and s['robust_white_root'] and not s['strong_direction_supported'] for s in systems) else None,
        'interpretation':'A robust WHITE ancestral state can coexist with failure to support directional rate asymmetry.'},
      'hierarchical_fine_state_rule':{
        'testable_external_radiations':len(nested),'supporting_external_radiations':len(nested_supported),
        'supporting_ids':[s['id'] for s in nested_supported],'dimensions':[s['fine_state_dimension'] for s in nested_supported],
        'status':'REPLICATED_CANDIDATE_3_OF_3_TESTABLE_EXTERNAL_RADIATIONS' if len(nested)==3 and len(nested_supported)==3 else 'NOT_REPLICATED_UNDER_CURRENT_GATE',
        'candidate_rule':'Coarse ancestral/display or pigment state constrains the evolutionary state space without fixing a universal transition direction; phylogenetic organization persists at finer hue, floral-organ, or pigment-class levels after conditioning on the coarse state.',
        'law_status':'STRONGLY_REPLICATED_CANDIDATE_NOT_YET_UNIVERSAL_LAW',
        'next_gate':'Attempt falsification in an additional independent nested-state radiation and test whether the same hierarchy aligns with molecular regulatory-module reuse rather than only visible-state organization.'},
      'paper1_science_changed':False,
      'claim_boundary':'Direction, ancestry and nested-state tests have different admissible denominators. Sensitivity trees, posterior trees, source codings and reconstruction repeats are not counted as independent radiations. Hydrangea lacks a comparable nested fine-state ingroup test in its current WHITE/RED coding.'}


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
    p.add_argument('--antirrhineae',type=Path,default=Path('data/antirrhineae_fine_state_result_v0_1.json'))
    p.add_argument('--out',type=Path,required=True); p.add_argument('--expected',type=Path)
    a=p.parse_args(); result=build(a.hydrangea,a.linoideae,a.angraecinae,a.antirrhineae)
    if a.expected: compare(json.loads(a.expected.read_text()),result)
    a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
