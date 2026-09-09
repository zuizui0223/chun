#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
selection_path = ROOT / 'analysis' / 'prospective_fourth_radiation_selection_v1.json'
stage_a_prefreeze = ROOT / 'analysis' / 'iris_fine_state_falsification_prefreeze_v1.md'
stage_a_result_path = ROOT / 'analysis' / 'iris_fine_state_falsification_result_v1.json'
stage_b_prefreeze = ROOT / 'analysis' / 'iris_post_endpoint_mechanism_prefreeze_v1.md'
stage_b_source_screen = ROOT / 'data' / 'iris_post_endpoint_mechanism_source_screen_v1.csv'
stage_b_result_path = ROOT / 'analysis' / 'iris_post_endpoint_mechanism_result_v1.json'

for p in (selection_path, stage_a_prefreeze, stage_a_result_path, stage_b_prefreeze, stage_b_source_screen, stage_b_result_path):
    assert p.exists(), p

selection = json.loads(selection_path.read_text(encoding='utf-8'))
assert selection['status'] == 'CANONICAL_PROSPECTIVE_FOURTH_RADIATION_FIXED'
assert selection['discovery_radiations'] == ['LINOIDEAE', 'ANGRAECINAE', 'ANTIRRHINEAE']
assert selection['prospective_fourth_radiation'] == 'IRIS'
assert selection['selection_basis'] == 'MACRO_PHENOTYPE_TREE_SOURCE_ONLY'
assert selection['mechanism_used_for_selection'] is False
assert selection['phenotype_endpoint_frozen_before_computation'] is True
assert selection['phenotype_prefreeze_commit'] == '6cd82af7733e9dd2a0d8074fd9a7de4163424435'
assert selection['phenotype_classification'] == 'MIXED'
assert selection['mechanism_stage_status_at_selection_freeze'] == 'NOT_OPENED'
for contaminated in ['IOCHROMINAE', 'ERICA', 'EPIMEDIUM', 'AQUILEGIA', 'SILENE']:
    assert contaminated in selection['excluded_from_canonical_prospective_role'], contaminated

stage_a_text = stage_a_prefreeze.read_text(encoding='utf-8')
for marker in [
    'FROZEN BEFORE COMPUTATION OF THE CONDITIONAL FINE-STATE ENDPOINT',
    'Test unit: **Iris**',
    '9,999 conditional permutations',
    'Prohibited post-hoc moves'
]:
    assert marker in stage_a_text, marker

stage_a_result = json.loads(stage_a_result_path.read_text(encoding='utf-8'))
assert stage_a_result['classification'] == 'MIXED'

stage_b_text = stage_b_prefreeze.read_text(encoding='utf-8')
for marker in [
    'FROZEN BEFORE ANY IRIS MECHANISM SEARCH',
    'No Iris molecular/mechanistic source may be selected',
    '`PIGMENT_DEPLOYMENT`',
    '`PIGMENT_CLASS`',
    '`FINE_HUE_BRANCH`',
    '`CAROTENOID_FINE_AXIS`',
    'at least **20 Iris taxa**',
    'at least 5 directly measured taxa in each of two fine states',
    '`PROSPECTIVE_PHENOTYPE_MECHANISM_ALIGNMENT`',
    '`COARSE_ONLY_ALIGNMENT`',
    '`MIXED_MECHANISM_ALIGNMENT`',
    '`HOLD_MECHANISM_OBSERVATION_REGIME`',
    'revise the Stage-A `MIXED` result'
]:
    assert marker in stage_b_text, marker

stage_b_result = json.loads(stage_b_result_path.read_text(encoding='utf-8'))
assert stage_b_result['classification'] == 'HOLD_MECHANISM_OBSERVATION_REGIME'
assert stage_b_result['stage_a_phenotype_classification'] == 'MIXED'
assert stage_b_result['stage_a_changed'] is False
assert stage_b_result['mechanism_search_started_only_after_prefreeze_commit'] is True
assert stage_b_result['source_screen_outcome']['frozen_minimum_n_20_gate'] is False
assert stage_b_result['source_screen_outcome']['comparable_observation_regime_gate'] is False
assert stage_b_result['endpoint_execution']['B1_coarse_molecular_alignment_computed'] is False
assert stage_b_result['endpoint_execution']['B2_residual_fine_state_alignment_computed'] is False
assert stage_b_result['cross_radiation_count_effect'] == 'NONE'
assert stage_b_result['paper1_science_changed'] is False

source_text = stage_b_source_screen.read_text(encoding='utf-8')
for doi in [
    '10.1177/1934578X20937151',
    '10.1016/S0305-1978(97)00008-2',
    '10.1155/2023/7407772',
    '10.1186/s12870-023-04642-9',
    '10.1016/j.plaphy.2024.109355',
    '10.1016/j.phytochem.2018.03.003'
]:
    assert doi in source_text, doi

print('validated: retrospective 3-radiation discovery -> canonical prospective Iris Stage A MIXED -> mechanism-blind Stage B -> HOLD_MECHANISM_OBSERVATION_REGIME without endpoint opening')
