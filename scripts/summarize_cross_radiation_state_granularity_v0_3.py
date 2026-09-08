#!/usr/bin/env python3
"""Derive the v0.3 cross-radiation state-granularity result.

Inputs are the merged v0.2 decision layer and the pre-frozen exhaustive
partition-specificity control. This script does not re-count sensitivity
settings as biological replications and does not infer ecology or mechanism.
"""
from __future__ import annotations
import argparse,json,math
from pathlib import Path


def build(v2_path:Path,specificity_path:Path):
    v2=json.loads(v2_path.read_text())
    sp=json.loads(specificity_path.read_text())
    if v2['direction_rule']['testable_radiations']!=3 or v2['direction_rule']['strong_direction_pass_count']!=0:
        raise ValueError('v0.2 direction denominator/result changed')
    fine=v2['hierarchical_fine_state_rule']
    if fine['testable_external_radiations']!=3 or fine['supporting_external_radiations']!=3:
        raise ValueError('v0.2 3/3 fine-state result changed')
    if sp['cross_radiation']['status']!='GENERIC_FINE_STATE_ORGANIZATION_MORE_LIKELY':
        raise ValueError('specificity decision changed')
    classes={r['radiation']:r['classification'] for r in sp['radiations']}
    if list(classes.values()).count('BIOLOGICAL_PARTITION_NOT_ENRICHED')<2:
        raise ValueError('pre-frozen rejection criterion no longer met')
    if any(v=='BIOLOGICAL_PARTITION_ENRICHED' for v in classes.values()):
        raise ValueError('unexpected enriched biological partition')
    return {
      'version':'v0.3',
      'status':'THREE_RADIATION_FINE_STATE_REPLICATION_WITHOUT_SHARED_PRIVILEGED_COARSE_BOUNDARY',
      'inputs':{
        'cross_radiation_v0_2':str(v2_path),
        'hierarchy_specificity_v0_1':str(specificity_path)},
      'direction_result':{
        'testable_radiations':v2['direction_rule']['testable_radiations'],
        'strong_direction_pass_count':v2['direction_rule']['strong_direction_pass_count'],
        'universal_transition_direction':'NOT_SUPPORTED',
        'retained_counterexample':v2['ancestry_direction_decoupling']['direct_counterexample']},
      'fine_state_replication':{
        'testable_external_radiations':fine['testable_external_radiations'],
        'supporting_external_radiations':fine['supporting_external_radiations'],
        'supporting_ids':fine['supporting_ids'],
        'dimensions':fine['dimensions'],
        'status':'SUPPORTED_3_OF_3_INDEPENDENT_EXTERNAL_RADIATIONS'},
      'coarse_partition_specificity':{
        'status':sp['cross_radiation']['status'],
        'radiation_classifications':classes,
        'enriched_radiations':sp['cross_radiation']['enriched_radiations'],
        'not_enriched_radiations':sp['cross_radiation']['not_enriched_radiations'],
        'intermediate_radiations':sp['cross_radiation']['intermediate_radiations'],
        'shared_privileged_biological_coarse_boundary':'NOT_SUPPORTED'},
      'revised_cross_radiation_inference':{
        'state_representation_result':'FINE_STATE_ORGANIZATION_REPLICATED_BUT_PRESELECTED_COARSE_BOUNDARIES_NOT_PRIVILEGED',
        'candidate_rule':'Flower-colour macroevolution is representation-dependent: fine-state phylogenetic organization recurs across independent radiations, but no tested biological coarse boundary is consistently privileged and coarse coding does not determine a universal transition direction.',
        'superseded_stronger_wording':'Coarse ancestral/display or pigment state constrains the evolutionary state space.',
        'supersession_reason':'Exhaustive alternative-partition controls classify Linoideae and Antirrhineae biological coarse partitions as NOT_ENRICHED and Angraecinae as INTERMEDIATE; none is ENRICHED.',
        'law_status':'REPLICATED_REPRESENTATION_PATTERN_NOT_UNIVERSAL_CAUSAL_LAW',
        'next_gate':'Test whether recurrent fine-state organization aligns with independently resolved molecular pathway or regulatory-module axes, and prospectively test any newly proposed coarse partition in an external radiation.'},
      'paper1_science_changed':False,
      'claim_boundary':'The 3/3 result concerns fine-state phylogenetic organization. It does not establish a privileged universal colour partition, transition direction, ancestral state, ecological cause, molecular mechanism, or dated rate.'}


def compare(a,b,path='root'):
    if type(a) is not type(b): raise ValueError(path+': type mismatch')
    if isinstance(a,dict):
        if set(a)!=set(b): raise ValueError(path+': key mismatch')
        for k in a: compare(a[k],b[k],path+'.'+k)
    elif isinstance(a,list):
        if len(a)!=len(b): raise ValueError(path+': length mismatch')
        for i,(x,y) in enumerate(zip(a,b)): compare(x,y,f'{path}[{i}]')
    elif isinstance(a,float):
        if not math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-12): raise ValueError(f'{path}: numeric drift')
    elif a!=b: raise ValueError(f'{path}: {a!r} != {b!r}')


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--v2',type=Path,default=Path('data/cross_radiation_hierarchical_rule_v0_2.json'))
    p.add_argument('--specificity',type=Path,default=Path('data/hierarchy_partition_specificity_summary_v0_1.json'))
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--expected',type=Path)
    a=p.parse_args();result=build(a.v2,a.specificity)
    if a.expected: compare(json.loads(a.expected.read_text()),result)
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__': main()
