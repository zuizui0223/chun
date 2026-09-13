#!/usr/bin/env python3
import json
from pathlib import Path

P=Path('data/ruellia51_hplc_resolution_profile_prereg_v0_1.json')
RESULT=Path('results/ruellia51_hplc_resolution_profile_v0_1')
SOURCE_COPY=Path('data/ruellia51_hplc_row_level_v0_1.csv')

x=json.loads(P.read_text())
assert x['status']=='FROZEN_BEFORE_RUELLIA51_ROW_LEVEL_HPLC_STATE_INGESTION'
assert x['source_article_doi']=='10.1002/ajb2.70149'
assert x['source_data_doi']=='10.6084/m9.figshare.30282448'
assert x['known_pre_outcome']['reported_species']==51
assert x['known_pre_outcome']['row_level_CHUN_HPLC_presence_patterns_opened_before_freeze'] is False
assert x['known_pre_outcome']['CHUN_resolution_AUCs_opened_before_freeze'] is False
assert x['known_pre_outcome']['author_defined_pathway_branches']=={
    'PEL':['Pelargonidin'],
    'CYA':['Cyanidin','Peonidin'],
    'DEL':['Delphinidin','Petunidin','Malvidin']}
r=x['nested_resolutions']
assert r['coarse']=='ANY_ANTHOCYANIDIN_PRESENT versus NONE'
assert r['intermediate']=='three-bit source-pathway-branch presence pattern PEL/CYA/DEL'
assert r['fine']=='six-bit anthocyanidin presence pattern in fixed order Pelargonidin/Cyanidin/Peonidin/Delphinidin/Petunidin/Malvidin'
assert r['presence_rule']=='source numeric HPLC concentration > 0 means present; exactly 0 means absent; missing remains missing'
assert r['continuous_concentration_magnitude_ignored'] is True
assert r['visible_hue_ignored'] is True
assert r['mapping_is_deterministically_nested'] is True
assert x['common_frame']['fine_state_minimum_tips']==5
assert x['common_frame']['minimum_common_tips']==20
assert x['common_frame']['minimum_states_each_resolution']==2
assert x['primary_statistic']['metric']=='ROC_AUC'
assert x['primary_statistic']['permutations']==9999
assert x['primary_statistic']['seed']==20260913
assert x['decision_rule']['NO_POST_HOC_UPGRADE'] is True
assert x['relation_to_prior_Ruellia_work']['exchangeable_with_this_profile_outcome'] is False
assert x['moderator_policy']['fit_now'] is False
assert x['moderator_policy']['minimum_same_estimand_radiations']==5
assert x['paper1_science_changed'] is False
assert not RESULT.exists(), 'outcome directory exists before prereg freeze'
assert not SOURCE_COPY.exists(), 'row-level HPLC copy exists before prereg freeze'
print('RUELLIA51_HPLC_RESOLUTION_PROFILE_PREREG_PASS')
