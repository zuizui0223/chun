#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

PREREG = Path('data/flowerclades51_resolution_profile_prereg_v0_1.json')
MAPPING = Path('data/flowerclades51_visible_colour_hierarchy_v0_1.csv')
ERRATUM = Path('data/flowerclades51_source_schema_erratum_v0_1.json')
RESULT_DIR = Path('results/flowerclades51_resolution_profile_v0_1')
PREFLIGHT = Path('data/flowerclades51_source_preflight_receipt_v0_1.json')
CROSSWALK = Path('data/flowerclades51_crosswalk_receipt_v0_1.json')
SOURCE_COPY = Path('data/flowerclades51_final_dataset_v0_1.csv')

p = json.loads(PREREG.read_text(encoding='utf-8'))
assert p['status'] == 'FROZEN_BEFORE_FLOWERCLADES51_SPECIES_LEVEL_FLOWER_COLOR_INGESTION'
assert p['source_article_doi'] == '10.1002/ajb2.70146'
assert p['source_dataset_doi'] == '10.5061/dryad.r4xgxd2sc'
assert p['source_dataset_known_pre_outcome']['reported_clades'] == 51
assert p['source_dataset_known_pre_outcome']['reported_species'] == 2960
assert p['source_dataset_known_pre_outcome']['species_level_flower_color_values_opened_by_chun_before_freeze'] is False
assert p['nested_resolutions']['chemistry_inference_forbidden'] is True
assert p['nested_resolutions']['fruit_color_use_forbidden'] is True
assert p['common_frame']['fine_state_minimum_tips'] == 5
assert p['common_frame']['minimum_common_tips'] == 20
assert p['common_frame']['minimum_states_each_resolution'] == 2
assert p['primary_statistic']['metric'] == 'ROC_AUC'
assert p['primary_statistic']['permutations_per_clade'] == 9999
assert p['primary_statistic']['seed_each_clade'] == 20260913
assert p['training_policy']['biological_replication_unit'] == 'clade'
assert p['training_policy']['minimum_same_estimand_training_radiations_before_quantitative_moderator'] == 5
assert p['training_policy']['moderator_fitting_on_this_pr'] is False
assert p['paper1_science_changed'] is False

with MAPPING.open(newline='', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))
assert len(rows) == 8
expected = {
    'black': ('DARK', 'NONWHITE'),
    'purple': ('COOL', 'NONWHITE'),
    'green': ('COOL', 'NONWHITE'),
    'orange': ('WARM', 'NONWHITE'),
    'pink': ('WARM', 'NONWHITE'),
    'red': ('WARM', 'NONWHITE'),
    'white': ('WHITE', 'WHITE'),
    'yellow': ('WARM', 'NONWHITE'),
}
observed = {r['source_fine_state']: (r['intermediate_state'], r['coarse_state']) for r in rows}
assert observed == expected, observed
intermediate_to_coarse = {}
for r in rows:
    old = intermediate_to_coarse.setdefault(r['intermediate_state'], r['coarse_state'])
    assert old == r['coarse_state']
assert intermediate_to_coarse == {
    'DARK': 'NONWHITE',
    'COOL': 'NONWHITE',
    'WARM': 'NONWHITE',
    'WHITE': 'WHITE',
}

e = json.loads(ERRATUM.read_text(encoding='utf-8'))
assert e['status'] == 'FROZEN_POST_ROW_INGEST_PRE_AUC_SOURCE_SCHEMA_ERRATUM'
assert e['biological_grouping_changed'] is False
assert e['thresholds_changed'] is False
assert e['common_frame_rule_changed'] is False
assert e['permutation_rule_changed'] is False
assert e['AUC_computed_before_erratum_freeze'] is False
assert e['profile_winner_computed_before_erratum_freeze'] is False

# Phase-aware audit: preregistration remains immutable; source-access and identifier/tree
# preflights are now expected because they were merged after the freeze and before AUC.
pre = json.loads(PREFLIGHT.read_text(encoding='utf-8'))
assert pre['status'] == 'HOLD_SOURCE_ACCESS_OUTCOMES_UNOPENED'
cw = json.loads(CROSSWALK.read_text(encoding='utf-8'))
assert cw['status'] == 'FROZEN_BEFORE_FLOWERCLADES51_FLOWER_COLOR_OUTCOME_OPENING'
assert cw['summary']['clades'] == 51
assert cw['summary']['exact_tree_matches'] == 2960
assert cw['outcome_firewall']['AUC_computed'] is False
assert cw['outcome_firewall']['profile_winner_computed'] is False

assert not RESULT_DIR.exists(), 'outcome result directory exists before pre-AUC erratum freeze'
assert not SOURCE_COPY.exists(), 'species-level source copy must not be committed before outcome analysis'

print(json.dumps({
    'status': 'FLOWERCLADES51_PROFILE_PREREG_PLUS_SCHEMA_ERRATUM_VALID',
    'source_categories': len(rows),
    'nested_intermediate_states': sorted(intermediate_to_coarse),
    'crosswalk_exact_matches': cw['summary']['exact_tree_matches'],
    'result_absent': True,
    'schema_erratum_pre_auc': True,
    'moderator_fitted': False,
    'paper1_science_changed': False,
}, indent=2))
