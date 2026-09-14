#!/usr/bin/env python3
import csv,json
from pathlib import Path
P=Path('data/rhododendron30_biochemical_resolution_profile_prereg_v0_1.json')
M=Path('data/rhododendron30_biochemical_resolution_mapping_v0_1.csv')
R=Path('results/rhododendron30_biochemical_resolution_profile_v0_1')
p=json.loads(P.read_text())
assert p['status']=='FROZEN_BEFORE_RHODODENDRON30_ROW_LEVEL_ANTHOCYANIN_OUTCOME_INGESTION'
assert p['source_article_doi']=='10.1111/plb.12649'
assert p['source_phylogeny_doi']=='10.5061/dryad.8cz8w9grq'
assert p['primary_tree_file']=='1_WP_RAxML.tre'
assert p['known_pre_outcome']['reported_species']==30
assert p['known_pre_outcome']['row_level_CHUN_compound_values_opened_before_freeze'] is False
assert p['nested_resolutions']['continuous_concentration_magnitude_ignored'] is True
assert p['nested_resolutions']['visible_colour_and_CIELAB_ignored'] is True
assert p['common_frame']['fine_state_minimum_tips']==5
assert p['common_frame']['minimum_common_tips']==20
assert p['primary_statistic']['permutations']==9999
assert p['primary_statistic']['seed']==20260913
assert p['decision_rule']['NO_POST_HOC_UPGRADE'] is True
assert p['training_policy']['moderator_fitting_on_this_pr'] is False
rows=list(csv.DictReader(M.open()))
assert len(rows)==7
classes={r['aglycone_class'] for r in rows}
assert classes=={'CY','DP','MV'}
assert sum(r['aglycone_class']=='CY' for r in rows)==4
assert sum(r['aglycone_class']=='DP' for r in rows)==2
assert sum(r['aglycone_class']=='MV' for r in rows)==1
assert not R.exists(), 'result exists before prereg freeze'
print(json.dumps({'status':'RHODODENDRON30_BIOCHEMICAL_PROFILE_PREREG_VALID','compounds':7,'classes':sorted(classes),'result_absent':True},indent=2))
