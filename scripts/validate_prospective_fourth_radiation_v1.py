#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
selection_path = ROOT / 'analysis' / 'prospective_fourth_radiation_selection_v1.json'
stage_a_prefreeze = ROOT / 'analysis' / 'iris_fine_state_falsification_prefreeze_v1.md'
stage_a_result_path = ROOT / 'analysis' / 'iris_fine_state_falsification_result_v1.json'
stage_b_prefreeze = ROOT / 'analysis' / 'iris_post_endpoint_mechanism_prefreeze_v1.md'

for p in (selection_path, stage_a_prefreeze, stage_a_result_path, stage_b_prefreeze):
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

# Stage B has been frozen, but no canonical Stage-B result may exist yet at this boundary.
assert not (ROOT / 'analysis' / 'iris_post_endpoint_mechanism_result_v1.json').exists()

print('validated: retrospective 3-radiation discovery -> canonical prospective Iris Stage A MIXED -> mechanism-blind Stage B prefreeze')
