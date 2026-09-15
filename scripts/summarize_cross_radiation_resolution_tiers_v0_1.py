#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_csv(rel: str):
    with (ROOT / rel).open(newline='', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def read_json(rel: str):
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()

    rows = read_csv('data/cross_radiation_resolution_tiers_v0_1.csv')
    bench = {r['benchmark_id']: r for r in read_csv('data/cross_clade_mechanistic_recurrence_benchmark_v0_1.csv')}
    ioch = read_json('data/iochrominae_cross_level_bridge_summary_v0_1.json')
    erica = read_json('data/erica_phenotype_axis_molecular_bridge_summary_v0_1.json')
    pet = read_json('data/petunieae_prospective_cross_level_v0_1.json')

    assert len(rows) == 9, len(rows)
    assert {r['primary_tier'] for r in rows} == {'M1','M2','M3'}
    assert sum(r['primary_tier']=='M1' for r in rows) == 6
    assert sum(r['primary_tier']=='M2' for r in rows) == 1
    assert sum(r['primary_tier']=='M3' for r in rows) == 2

    # Source-backed invariants.
    assert ioch['hue_maps_to'] == 'BRANCHING_ENZYME_SUBSPACE'
    assert ioch['intensity_maps_to'] == 'LATE_PATHWAY_COEXPRESSION_MODULE'
    assert erica['phenotype_axes']['HUE_BRANCH_YELLOW']['branch_hydroxylation_F3_prime_H'] == '2/2'
    assert erica['phenotype_axes']['PIGMENT_DEPLETION_WHITE']['unique_focal_node_classes'] == 4
    assert pet['pre_frozen_gate_components']['hue_axis_pass'] is True
    assert pet['pre_frozen_gate_components']['amount_axis_pass'] is False
    assert pet['hue_axis']['best_margin_AICc'] == 11.60282936
    assert pet['amount_axis']['best_margin_AICc'] == 0.44436806
    assert bench['IPOMOEA_RED']['shared_count'] == '3/3'
    assert bench['AQUILEGIA_A_MINUS']['strongest_recurrence_level'] == 'LATE_PATHWAY_EXPRESSION'
    assert bench['EPIMEDIUM_A_MINUS']['shared_count'] == '4/4'

    hue = [r for r in rows if r['stress_test_family'] == 'HUE_BRANCH']
    loss = [r for r in rows if r['stress_test_family'] == 'LOSS_DEPLETION']
    assert len(hue) == 4
    assert len({r['system'] for r in hue}) == 4
    assert all(r['result_status'] == 'SUPPORT' for r in hue)
    assert all(r['specificity_level'].startswith('NARROW_BRANCHING') for r in hue)
    assert len(loss) == 5
    assert len({r['system'] for r in loss}) == 5

    loss_categories = {
        'broad_late_or_core_support': sum(r['specificity_level'] in {
            'BROAD_LATE_MODULE','RECURRENT_CORE_HETEROGENEOUS_IMPLEMENTATION'
        } for r in loss),
        'heterogeneous_late_and_regulatory': sum(r['specificity_level'] == 'HETEROGENEOUS_LATE_AND_REGULATORY' for r in loss),
        'response_definition_sensitive_primary_fail': sum(r['specificity_level'] == 'RESPONSE_DEFINITION_SENSITIVE' for r in loss),
    }
    assert loss_categories == {
        'broad_late_or_core_support': 3,
        'heterogeneous_late_and_regulatory': 1,
        'response_definition_sensitive_primary_fail': 1,
    }

    m1 = [r for r in rows if r['primary_tier'] == 'M1']
    assert {r['system'] for r in m1} == {'IOCHROMINAE','CAPE_ERICA','PETUNIEAE'}
    assert sum(r['prospective_status']=='PROSPECTIVE' for r in m1) == 2  # two axes, one prospective radiation

    summary = {
        'version': 'v0.1',
        'status': 'DIMENSION_SPECIFIC_ANISOTROPIC_PREDICTABILITY_SUPPORTED_ACROSS_TIERS',
        'scope': {
            'unique_systems': len({r['system'] for r in rows}),
            'evidence_rows': len(rows),
            'M1_matched_axis_systems': 3,
            'M2_hue_branch_functional_systems': 1,
            'M3_loss_depletion_external_systems': 2,
        },
        'M1_matched_axis_result': {
            'systems': ['IOCHROMINAE','CAPE_ERICA','PETUNIEAE'],
            'hue_branching_support': '3/3 systems',
            'fixed_late_output_amount_depletion_support': '1/3 systems',
            'prospective_radiations': ['PETUNIEAE'],
            'petunieae_hue_margin_AICc': pet['hue_axis']['best_margin_AICc'],
            'petunieae_amount_margin_AICc': pet['amount_axis']['best_margin_AICc'],
            'petunieae_full_gate': pet['pre_frozen_gate'],
        },
        'M2_hue_branch_functional_stress': {
            'systems': ['IPOMOEA'],
            'result': '3/3 robust red origins implicate floral F3_PRIME_H regulatory reduction',
            'role': 'INDEPENDENT_EVENT_FUNCTIONAL_SUPPORT_NOT_M1_MATCHED_AXIS_REPLICATION',
        },
        'M3_loss_depletion_stress': {
            'systems': ['AQUILEGIA','EPIMEDIUM'],
            'external_result': 'BOTH_SUPPORT_LATE_OR_CORE_PATHWAY_RECURRENCE_WITHOUT_UNIFORM_COMPLETE_IMPLEMENTATION',
            'combined_loss_depletion_family_systems': 5,
            'combined_localization_categories': loss_categories,
            'interpretation': 'LOSS_DEPLETION_SHOWS_A_BROADER_LATE_OR_CORE_PATHWAY_TENDENCY_BUT_NOT_ONE_NARROW_UNIVERSAL_NODE_OR_COMPLETE_PROGRAMME',
        },
        'integrated_dimension_result': {
            'hue_branch_family': '4/4 systems support narrow branching-node/subspace involvement across matched-radiation and event-functional regimes',
            'loss_depletion_family': '3/5 systems support broad late/core recurrence, 1/5 is heterogeneous across late/regulatory nodes, and 1/5 fails the frozen primary localization',
            'candidate': 'FLOWER_COLOUR_PREDICTABILITY_IS_ANISOTROPIC_BY_PHENOTYPE_DIMENSION_AND_RESOLUTION',
            'interpretation': 'HUE_OR_HYDROXYLATION_CHANGES_SHOW_NARROWER_BRANCH_POINT_PREDICTABILITY_WHILE_PIGMENT_LOSS_OR_DEPLETION_SHOWS_BROADER_MODULE_LEVEL_PREDICTABILITY_WITH_HETEROGENEOUS_EXACT_IMPLEMENTATION',
        },
        'statistical_boundary': 'COUNTS_ARE_DESCRIPTIVE_BY_BIOLOGICAL_SYSTEM; NO_POOLED_P_VALUE_OR_EFFECT_SIZE_ACROSS_HETEROGENEOUS_OBSERVATION_REGIMES',
        'prospective_boundary': 'Only Petunieae was prospectively frozen for the matched M1 two-axis test; Ipomoea, Aquilegia, Epimedium, Iochrominae and Cape Erica are retrospective or external stress tests.',
        'paper1_science_changed': False,
    }

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
