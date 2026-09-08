#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

MACRO=Path('data/cross_radiation_state_granularity_v0_3.json')
IO=Path('data/iochrominae_cross_level_bridge_summary_v0_1.json')
EPI=Path('data/epimedium_cross_level_endpoint_bridge_summary_v0_1.json')
EXPECTED=Path('data/cross_level_state_granularity_v0_4.json')

macro=json.loads(MACRO.read_text())
io=json.loads(IO.read_text())
epi=json.loads(EPI.read_text())
assert macro['fine_state_replication']['status']=='SUPPORTED_3_OF_3_INDEPENDENT_EXTERNAL_RADIATIONS'
assert macro['direction_result']['strong_direction_pass_count']==0
assert macro['coarse_partition_specificity']['shared_privileged_biological_coarse_boundary']=='NOT_SUPPORTED'
assert io['cross_level_result']=='PHENOTYPE_DIMENSIONS_MAP_TO_DIFFERENT_MOLECULAR_SUBSPACES_WITHIN_ONE_RADIATION'
assert epi['cross_level_result']=='SAME_SOURCE_ENDPOINT_CODE_WITH_RECURRENT_CORE_AND_HETEROGENEOUS_MOLECULAR_IMPLEMENTATION'
assert epi['historical_event_independence']=='FAIL_HOLD_NOT_ESTIMATED'

result={
 'version':'v0.4',
 'status':'MACRO_STATE_GRANULARITY_REPLICATED_CROSS_LEVEL_COMPATIBILITY_PRESENT_MECHANISTIC_REPLICATION_NOT_YET_COMMON_TEST',
 'macro_layer':{
   'fine_state_support':'3/3 independent external radiations',
   'universal_direction':'NOT_SUPPORTED_0_OF_3_STRONG_GATE',
   'shared_privileged_coarse_boundary':'NOT_SUPPORTED',
   'retained_inference':'FLOWER_COLOUR_MACROEVOLUTION_IS_REPRESENTATION_DEPENDENT'},
 'same_radiation_cross_level_bridges':[
   {'id':'IOCHROMINAE','bridge_type':'PHENOTYPE_DIMENSION_TO_MOLECULAR_SUBSPACE',
    'result':io['cross_level_result'],'source_species_scope':io['source_species_scope'],
    'independence_unit':'ONE_RADIATION_SOURCE_DERIVED_MAPPING'},
   {'id':'EPIMEDIUM_SECT_DIPHYLLON','bridge_type':'VISIBLE_ENDPOINT_TO_HIERARCHICAL_MOLECULAR_IMPLEMENTATION',
    'result':epi['cross_level_result'],'macro_molecular_overlap_taxa':epi['macro_molecular_overlap_taxa'],
    'independence_unit':'ONE_RADIATION_TAXON_ENDPOINT_MAPPING_EVENT_IDENTITY_HELD'}],
 'cross_level_bridge_count':2,
 'common_mechanistic_replication_test':'NOT_AVAILABLE_HETEROGENEOUS_BRIDGE_DEFINITIONS',
 'pooled_mechanistic_estimator':'FORBIDDEN',
 'mechanistic_compatibility_inference':'VISIBLE_STATE_RESOLUTION_CAN_HIDE_DISTINCT_MOLECULAR_SUBSPACES_OR_IMPLEMENTATIONS_IN_AT_LEAST_TWO_SAME_RADIATION_CASES',
 'mechanistic_law_status':'COMPATIBILITY_SUPPORTED_NOT_REPLICATED_COMMON_LAW',
 'next_gate':'Admit a second independent radiation under the Iochrominae phenotype-dimension-to-molecular-subspace definition, or preregister a different common cross-level endpoint and apply it prospectively to >=2 independent radiations.',
 'holds':{
   'ANTIRRHINEAE':'MOLECULAR_BRIDGE_FAIL_HOLD_DEPENDENCE_COLLAPSE',
   'EPIMEDIUM_EVENT_LEVEL':'FAIL_HOLD_EVENT_IDENTITY_NOT_ESTIMATED'},
 'paper1_science_changed':False,
 'claim_boundary':'Macro 3/3 replication and two cross-level compatibility cases have different denominators. They do not establish a universal molecular mapping, common event recurrence rate, ecological cause, or mechanistic law.'}
assert result==json.loads(EXPECTED.read_text())
print(json.dumps(result,indent=2))
