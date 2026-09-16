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

closed={r['system']:r for r in x['closed_attempts']}
assert set(closed)=={'SOLANACEAE_RED_27'}
sol=closed['SOLANACEAE_RED_27']
assert sol['source_tree_gate']=='PASS_ARCHIVED_TREEBASE_S16617_OBJECT_CROSSWALK_FROZEN'
assert sol['status']=='HOLD_INSUFFICIENT_COMMON_FRAME_OR_STATE_VARIATION'
assert sol['crosswalk_exact_matches']==25
assert sol['eligible_before_rare_filter']==24
assert sol['observed_fine_state_count']==10
assert sol['maximum_observed_fine_state_support']==4
assert sol['frozen_minimum_fine_state_support']==5
assert sol['eligible_tips_after_rare_filter']==0
assert sol['profile_auc_computed'] is False
assert sol['winner_computed'] is False
assert sol['post_hoc_rescue_allowed'] is False
assert sol['counts_as_completed_biochemical_unit'] is False

front={r['system']:r for r in x['candidate_frontier']}
assert set(front)=={'IOCHROMINAE','RUELLIA','RHODODENDRON','ANTIRRHINEAE','CAPE_ERICA'}
io=front['IOCHROMINAE']
assert io['status']=='HOLD_DRYAD_SOURCE_BYTES_STILL_UNAVAILABLE_PROFILE_UNCOMPUTED'
u=io['unlock']
assert u['required_archive_file_id']==108456
assert u['required_archive_size']==3054999
assert u['required_archive_md5']=='76b46e384fb7c9bf1ef3fbd7d1e5d2f0'
assert u['required_readme_file_id']==108458
assert u['required_readme_size']==4072
assert u['required_readme_md5']=='2e4a251725ad4c13975fc09481da302d'
assert front['RUELLIA']['status']=='HOLD_AUTHORITATIVE_2023_TREE_BYTES_OR_EXACT_RECONSTRUCTION_SOURCE_UNAVAILABLE_OUTCOMES_UNOPENED'
assert front['RHODODENDRON']['status']=='HOLD_SOURCE_ACCESS_STILL_BLOCKED_OUTCOMES_UNOPENED'
assert front['ANTIRRHINEAE']['status']=='HOLD_SCHEMA_NO_SOURCE_DEFINED_THREE_LEVEL_NESTING_INTERMEDIATE_FINE_COLLAPSE'
assert all(r['profile_auc_computed'] is False for r in x['candidate_frontier'])
assert x['paper1_science_changed'] is False
print(json.dumps({
    'status':x['status'],
    'next_gate':x['next_gate'],
    'highest_leverage':'IOCHROMINAE',
    'closed_attempt':'SOLANACEAE_RED_27',
    'closed_attempt_status':sol['status'],
    'completed_biochemical_units':rt['biochemical_completed'],
},indent=2))
