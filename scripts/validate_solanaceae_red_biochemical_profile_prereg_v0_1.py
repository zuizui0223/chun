#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / 'data/solanaceae_red_biochemical_resolution_profile_prereg_v0_1.json'
DOC = ROOT / 'docs/SOLANACEAE_RED_BIOCHEMICAL_RESOLUTION_PROFILE_PREREG_V0_1.md'
RESULT = ROOT / 'data/solanaceae_red_biochemical_resolution_profile_result_v0_1.json'

p = json.loads(P.read_text(encoding='utf-8'))
doc = DOC.read_text(encoding='utf-8')

assert p['status'] == 'FROZEN_BEFORE_SOLANACEAE_RED_TABLES1_ROW_LEVEL_OUTCOME_OPENING'
assert p['system'] == 'SOLANACEAE_RED_27'
assert p['prospective_label'] == 'RETROSPECTIVE_STANDARDIZED_CROSS_REPRESENTATION_TRAINING_NOT_PROSPECTIVE'
assert p['source']['primary_pigment_article_doi'] == '10.1093/aobpla/plw013'
assert p['source']['primary_pigment_pmcid'] == 'PMC4804202'
assert p['source']['reported_taxa'] == 27
assert p['source']['supplement_file'] == 'supp_plw013_plw013supp_table1.docx'
assert p['source']['row_level_trait_values_opened_for_this_profile_before_freeze'] is False
assert p['source']['tree_parent_article_doi'] == '10.1111/nph.13576'
assert p['source']['treebase_study_id'] == 'S16617'

assert p['tree_selection']['substitute_tree_allowed'] is False
assert p['tree_selection']['outcome_based_tree_choice_allowed'] is False
assert p['state_variables']['anthocyanidin_branches'] == ['PELARGONIDIN','CYANIDIN','DELPHINIDIN']
assert p['state_variables']['branch_order_by_hydroxylation'] == ['PELARGONIDIN','CYANIDIN','DELPHINIDIN']

nested = p['nested_representations']
assert nested['coarse'] == '(ANY_ANTHOCYANIDIN_PRESENT, CAROTENOID_PRESENT)'
assert 'HIGHEST_HYDROXYLATION_BRANCH_PRESENT' in nested['intermediate']
assert nested['fine'] == '(CAROTENOID_PRESENT, PELARGONIDIN_PRESENT, CYANIDIN_PRESENT, DELPHINIDIN_PRESENT)'
assert 'deterministically maps' in nested['nesting_contract']

frame = p['primary_frame']
assert frame['rare_fine_state_rule'].startswith('exclude every fine state represented by fewer than 5 taxa')
assert frame['minimum_retained_tips'] == 20
assert frame['minimum_states_per_resolution'] == 2
assert frame['hold_if_any_rule_fails'] is True

stat = p['primary_statistic']
assert stat['metric'] == 'ROC_AUC'
assert stat['permutations'] == 9999
assert stat['seed'] == 20260915
assert 'winner-minus-runner-up' in stat['unique_winner_gate']
assert p['post_hoc_rescue_allowed'] is False
assert p['paper1_science_changed'] is False

assert not RESULT.exists(), 'profile result exists before prereg freeze is merged'
for token in [
    '27-species',
    'TreeBASE study `S16617`',
    'Fine therefore maps deterministically to intermediate and coarse',
    'Table S1 row-level pigment values have not been ingested into CHUN for this profile',
    'no profile AUC or permutation p-value exists',
    'Camellia Paper 1 remains unchanged',
]:
    assert token in doc, token

print(json.dumps({
    'status': 'SOLANACEAE_RED_BIOCHEMICAL_PROFILE_PREREG_V0_1_VALID',
    'reported_taxa': 27,
    'treebase_study': 'S16617',
    'row_level_outcomes_opened': False,
    'profile_result_exists': False,
    'minimum_retained_tips': 20,
    'permutations': 9999,
    'paper1_science_changed': False,
}, indent=2))
