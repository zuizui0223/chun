#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
h=json.loads((root/'data/antirrhineae_unconditional_profile_schema_hold_v0_1.json').read_text())
r=json.loads((root/'data/antirrhineae_fine_state_result_v0_1.json').read_text())

assert h['status']=='HOLD_SCHEMA_NO_SOURCE_DEFINED_THREE_LEVEL_NESTING_INTERMEDIATE_FINE_COLLAPSE'
assert h['source_doi']=='10.15479/AT:ISTA:34'
assert h['source_native_face_phenotype_codes']=={
    '0':'UNPIGMENTED','1':'ANTHOCYANIN','2':'YELLOW','3':'DOUBLE_PIGMENTED'
}
assert h['coarse_representation_is_source_supported']=={'UNPIGMENTED':[0],'PIGMENTED':[1,2,3]}
assert h['fine_representation_is_source_supported']=={
    'UNPIGMENTED':[0],'ANTHOCYANIN':[1],'YELLOW':[2],'DOUBLE_PIGMENTED':[3]
}
assert h['intermediate_problem']['source_defined_unique_intermediate_partition'] is False
assert h['unconditional_profile_auc_computed'] is False
assert h['profile_winner_computed'] is False
assert h['counts_as_second_non_visible_exact_profile'] is False
assert h['paper1_science_changed'] is False

mono=r['datasets']['monomorphic']; poly=r['datasets']['polymorphic']
assert mono['exact_joined_tips']==152
assert mono['fine_state_counts']=={'0':21,'1':68,'2':63}
assert poly['exact_joined_tips']==179
assert poly['fine_state_counts']=={'0':29,'1':83,'2':67}
assert int(mono['fine_state_counts'].get('3',0))==0
assert int(poly['fine_state_counts'].get('3',0))==0

# Retain the prior conditional result under its own estimand.
assert r['pre_frozen_gate']=='PASS'
assert r['third_independent_replication_admitted'] is True

print(json.dumps({
  'status':h['status'],
  'primary_exact_tips':mono['exact_joined_tips'],
  'primary_observed_states':mono['fine_state_counts'],
  'sensitivity_exact_tips':poly['exact_joined_tips'],
  'sensitivity_observed_states':poly['fine_state_counts'],
  'unconditional_profile_auc_computed':False,
  'prior_conditional_result_preserved':True,
  'paper1_science_changed':False,
},indent=2))
