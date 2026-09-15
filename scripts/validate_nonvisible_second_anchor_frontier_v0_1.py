#!/usr/bin/env python3
import json
from pathlib import Path

p=Path('data/nonvisible_second_anchor_frontier_v0_1.json')
x=json.loads(p.read_text())
assert x['version']=='v0.1'
assert x['status']=='SECOND_NONVISIBLE_EXACT_PROFILE_NOT_YET_IDENTIFIED'
assert x['completed_exact_profile_units']==30
rt=x['representation_training']
assert rt['visible_colour_standardized_clades']==28
assert rt['biochemical_completed']==1
assert rt['biochemical_completed_systems']==['PETUNIEAE']
assert rt['mixed_prospective_completed']==1
assert rt['mixed_prospective_systems']==['IRIS']
assert x['representation_moderator_identifiable'] is False
front={r['system']:r for r in x['candidate_frontier']}
assert set(front)=={'IOCHROMINAE','RUELLIA','RHODODENDRON','ANTIRRHINEAE','CAPE_ERICA'}
io=front['IOCHROMINAE']
assert io['status']=='HOLD_SOURCE_ACCESS_README_AND_ARCHIVE_PROFILE_UNCOMPUTED'
u=io['unlock']
assert u['required_archive_file_id']==108456
assert u['required_archive_size']==3054999
assert u['required_archive_md5']=='76b46e384fb7c9bf1ef3fbd7d1e5d2f0'
assert u['required_readme_file_id']==108458
assert u['required_readme_size']==4072
assert u['required_readme_md5']=='2e4a251725ad4c13975fc09481da302d'
assert front['ANTIRRHINEAE']['status']=='HOLD_SCHEMA_NO_SOURCE_DEFINED_THREE_LEVEL_NESTING_INTERMEDIATE_FINE_COLLAPSE'
assert all(r['profile_auc_computed'] is False for r in x['candidate_frontier'])
assert x['paper1_science_changed'] is False
print(json.dumps({'status':x['status'],'next_gate':x['next_gate'],'highest_leverage':'IOCHROMINAE'},indent=2))
