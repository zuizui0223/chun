#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
ident=json.loads((root/'data/resolution_profile_representation_identifiability_v0_1.json').read_text())
pet=json.loads((root/'data/petunieae_biochemical_resolution_profile_result_v0_1.json').read_text())

assert ident['status']=='REPRESENTATION_MODERATOR_NOT_IDENTIFIABLE_SINGLETON_BIOCHEMICAL'
assert ident['exact_profile_completed_total']==30
assert ident['training_composition']=={
    'standardized_visible_colour':28,
    'biochemical_composition':1,
    'mixed_pigment_hue_prospective':1,
}
assert ident['representation_type_model_fit'] is False
assert ident['next_heldout_prediction_frozen'] is False
assert ident['next_gate']=='SECOND_INDEPENDENT_COMPLETED_EXACT_PROFILE_WITH_BIOCHEMICAL_OR_OTHER_NON_VISIBLE_NESTED_REPRESENTATION'
assert ident['paper1_science_changed'] is False

assert pet['status']=='PETUNIEAE_BIOCHEMICAL_RESOLUTION_PROFILE_RESULT'
assert pet['programme_role']=='RETROSPECTIVE_STANDARDIZED_CROSS_REPRESENTATION_TRAINING'
assert pet['do_not_count_as_new_prospective_replication'] is True
assert pet['terminal_class']=='PROFILE_SIGNALLED_FINE'
assert pet['primary_frame']['eligible_tips']==47
assert pet['observed']['AUC_coarse']==0.518925563507132
assert pet['observed']['AUC_intermediate']==0.518925563507132
assert pet['observed']['AUC_fine']==0.6995630849367751
assert pet['p_signal_one_sided']['fine']==0.0001
assert pet['p_winner_gt_runner']==0.0001
assert pet['paper1_science_changed'] is False

inventory=(root/'docs/RESOLUTION_PROFILE_TRAINING_INVENTORY_V0_4.md').read_text()
synthesis=(root/'docs/CROSS_RADIATION_RESOLUTION_SYNTHESIS_V0_4.md').read_text()
for text in (inventory,synthesis):
    assert '30' in text
    assert 'Petunieae' in text
    assert 'PROFILE_SIGNALLED_FINE' in text
assert 'not enough replication of representation classes' in synthesis
assert 'second independent completed biochemical' in synthesis.lower()

print(json.dumps({
    'status':'RESOLUTION_PROFILE_CROSS_REPRESENTATION_STATUS_V0_4_VALID',
    'exact_profile_completed_total':30,
    'visible_colour':28,
    'biochemical':1,
    'mixed':1,
    'petunieae_terminal_class':pet['terminal_class'],
    'representation_moderator_fit':False,
    'paper1_science_changed':False,
},indent=2))
