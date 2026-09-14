#!/usr/bin/env python3
import json
from pathlib import Path

P=Path('data/petunieae_biochemical_resolution_profile_prereg_v0_1.json')
x=json.loads(P.read_text())
assert x['status']=='FROZEN_BEFORE_PETUNIEAE_BIOCHEMICAL_RESOLUTION_AUC_COMPUTATION'
assert x['programme_role']=='RETROSPECTIVE_STANDARDIZED_CROSS_REPRESENTATION_TRAINING'
assert x['prospective_label'].startswith('NOT_PROSPECTIVE')
assert x['source_identity']['table_sha256']=='5843d4cd4eb253046f97349fa6bd285ca77e43e7a9c3aaa0e78fae3e8e391edd'
assert x['source_identity']['tree_sha256']=='95b4a688d3d71417b712b37a2b04cdc22a9431be3172d6509def4435f5fd8614'
assert x['source_identity']['processed_rows_before_outgroup_exclusion']==60
assert x['source_identity']['expected_petunieae_taxa_after_outgroup_exclusion']==59
assert x['compound_order']==['Pel_mgg','Cyan_mgg','Peon_mgg','Del_mgg','Pet_mgg','Malv_mgg']
assert x['nested_resolutions']['class_mapping']=={
  'PEL':['Pel_mgg'],'CYA':['Cyan_mgg','Peon_mgg'],'DEL':['Del_mgg','Pet_mgg','Malv_mgg']}
assert x['nested_resolutions']['mapping_is_deterministically_nested'] is True
assert x['common_frame']['fine_state_minimum_tips']==5
assert x['common_frame']['minimum_common_tips']==20
assert x['primary_statistic']['permutations']==9999
assert x['primary_statistic']['seed']==20260913
assert x['decision_rule']['NO_POST_HOC_UPGRADE'] is True
assert x['prior_exposure_boundary']['resolution_profile_AUCs_previously_computed'] is False
assert x['prior_exposure_boundary']['resolution_profile_winner_previously_computed'] is False
assert x['paper1_science_changed'] is False
assert not Path('results/petunieae_biochemical_resolution_profile_v0_1').exists()
print(json.dumps({'status':'PETUNIEAE_BIOCHEMICAL_PROFILE_PREREG_VALID','profile_result_absent':True,'paper1_science_changed':False},indent=2))
