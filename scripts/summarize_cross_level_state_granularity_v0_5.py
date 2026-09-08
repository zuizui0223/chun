#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

V4=json.loads(Path('data/cross_level_state_granularity_v0_4.json').read_text())
IO=json.loads(Path('data/iochrominae_cross_level_bridge_summary_v0_1.json').read_text())
ERICA=json.loads(Path('data/erica_phenotype_axis_molecular_bridge_summary_v0_1.json').read_text())
EPI=json.loads(Path('data/epimedium_cross_level_endpoint_bridge_summary_v0_1.json').read_text())
EXPECTED=json.loads(Path('data/cross_level_state_granularity_v0_5.json').read_text())

assert V4['macro_layer']['fine_state_support']=='3/3 independent external radiations'
assert IO['cross_level_result']=='PHENOTYPE_DIMENSIONS_MAP_TO_DIFFERENT_MOLECULAR_SUBSPACES_WITHIN_ONE_RADIATION'
assert ERICA['alignment_to_iochrominae']=='RETROSPECTIVE_INDEPENDENT_ALIGNMENT_AT_PHENOTYPE_AXIS_TO_MOLECULAR_SUBSPACE_LEVEL'
assert EPI['cross_level_result']=='SAME_SOURCE_ENDPOINT_CODE_WITH_RECURRENT_CORE_AND_HETEROGENEOUS_MOLECULAR_IMPLEMENTATION'

result={
 'version':'v0.5',
 'status':'MACRO_REPLICATION_PLUS_TWO_RADIATION_RETROSPECTIVE_PHENOTYPE_AXIS_MOLECULAR_ALIGNMENT_WITH_COMPLEMENTARY_EPIMEDIUM_ENDPOINT_BRIDGE',
 'macro_state_granularity':{
   'fine_state_replication':'3/3 independent external radiations',
   'universal_direction':'NOT_SUPPORTED',
   'privileged_coarse_boundary':'NOT_SUPPORTED'},
 'matched_high_level_cross_level_definition':{
   'definition':'VISIBLE_PHENOTYPE_AXIS_TO_MOLECULAR_SUBSPACE_WITHIN_ONE_RADIATION',
   'independent_radiations':['IOCHROMINAE','CAPE_ERICA'],
   'radiation_count':2,
   'IOCHROMINAE_result':IO['cross_level_result'],
   'CAPE_ERICA_result':ERICA['cross_level_result'],
   'alignment_status':'RETROSPECTIVE_ALIGNMENT_IN_TWO_INDEPENDENT_RADIATIONS',
   'prospective_replication_count':0,
   'law_status':'NOT_PROSPECTIVELY_REPLICATED'},
 'complementary_endpoint_bridge':{
   'id':'EPIMEDIUM_SECT_DIPHYLLON',
   'result':EPI['cross_level_result'],
   'role':'COMPATIBILITY_ONLY_DIFFERENT_BRIDGE_DEFINITION',
   'historical_event_status':EPI['historical_event_independence']},
 'retained_cross_level_inference':'DIFFERENT_VISIBLE_PHENOTYPE_DIMENSIONS_OR_ENDPOINT_RESOLUTIONS_CAN_MAP_TO_DIFFERENT_MOLECULAR_SUBSPACES_OR_IMPLEMENTATIONS_WITHIN_RADIATIONS',
 'mechanistic_generalization_status':'TWO_RADIATION_RETROSPECTIVE_ALIGNMENT_PLUS_ONE_COMPLEMENTARY_CASE_NOT_A_UNIVERSAL_LAW',
 'next_gate':'Preregister the phenotype-axis-to-molecular-subspace test before inspecting mechanism distributions in a newly admitted independent radiation that contains both pigment-depletion and hue-shift contrasts.',
 'pooled_estimator':'FORBIDDEN_HETEROGENEOUS_UNITS',
 'paper1_science_changed':False,
 'claim_boundary':'The macro result is replicated; the cross-level phenotype-axis alignment is retrospective in two systems and therefore still needs prospective external validation.'}
assert result==EXPECTED,(result,EXPECTED)
print(json.dumps(result,indent=2))
