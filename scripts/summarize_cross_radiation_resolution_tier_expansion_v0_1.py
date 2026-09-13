#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def rows(path: Path):
    with path.open(newline='', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--ledger', type=Path, default=ROOT / 'data/cross_radiation_resolution_tier_expansion_v0_1.csv')
    ap.add_argument('--benchmark', type=Path, default=ROOT / 'data/cross_clade_mechanistic_recurrence_benchmark_v0_1.csv')
    ap.add_argument('--petunieae', type=Path, default=ROOT / 'data/petunieae_prospective_cross_level_v0_1.json')
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()

    ledger = rows(a.ledger)
    benchmark = {r['benchmark_id']: r for r in rows(a.benchmark)}
    pet = json.loads(a.petunieae.read_text(encoding='utf-8'))

    assert len(ledger) == 10, len(ledger)
    assert {r['tier'] for r in ledger} == {'M1','M2','M3','M4'}

    m1 = [r for r in ledger if r['tier'] == 'M1']
    assert len(m1) == 6
    systems = {'IOCHROMINAE','CAPE_ERICA','PETUNIEAE'}
    assert {r['system'] for r in m1} == systems
    for s in systems:
        sr = [r for r in m1 if r['system'] == s]
        assert len(sr) == 2
        assert {r['phenotype_dimension'] for r in sr} == {'HUE_OR_HYDROXYLATION','PIGMENT_AMOUNT_OR_DEPLETION'}

    hue = [r for r in m1 if r['phenotype_dimension'] == 'HUE_OR_HYDROXYLATION']
    amount = [r for r in m1 if r['phenotype_dimension'] == 'PIGMENT_AMOUNT_OR_DEPLETION']
    assert len(hue) == len(amount) == 3
    assert sum(r['specificity_class'] == 'BRANCH_SPECIFIC_OR_FINER' for r in hue) == 3
    assert sum(r['specificity_class'] == 'BRANCH_SPECIFIC_OR_FINER' for r in amount) == 0
    assert sum(r['specificity_class'] == 'MODULE_OR_CORE' for r in amount) == 1
    assert sum(r['specificity_class'] == 'DIVERSE_OR_PRIMARY_FAIL' for r in amount) == 2

    assert pet['pre_frozen_gate'] == 'PETUNIEAE_PROSPECTIVE_BRIDGE_MIXED'
    assert pet['pre_frozen_gate_components']['hue_axis_pass'] is True
    assert pet['pre_frozen_gate_components']['amount_axis_pass'] is False
    assert abs(pet['hue_axis']['best_margin_AICc'] - 11.60282936) < 1e-8
    assert abs(pet['amount_axis']['best_margin_AICc'] - 0.44436806) < 1e-8

    m2 = [r for r in ledger if r['tier'] == 'M2']
    m3 = [r for r in ledger if r['tier'] == 'M3']
    m4 = [r for r in ledger if r['tier'] == 'M4']
    assert len(m2) == 1 and m2[0]['system'] == 'IPOMOEA'
    assert m2[0]['specificity_class'] == 'BRANCH_SPECIFIC_OR_FINER'
    assert benchmark['IPOMOEA_RED']['shared_count'] == '3/3'

    assert {r['system'] for r in m3} == {'AQUILEGIA','EPIMEDIUM'}
    assert all(r['specificity_class'] == 'MODULE_OR_CORE' for r in m3)
    assert benchmark['EPIMEDIUM_A_MINUS']['shared_count'] == '4/4'
    assert benchmark['AQUILEGIA_A_MINUS']['strongest_recurrence_level'] == 'LATE_PATHWAY_EXPRESSION'

    assert len(m4) == 1 and m4[0]['system'] == 'PETUNIA'
    assert benchmark['PETUNIA_REGAIN']['shared_count'] == '2/2'
    assert benchmark['PETUNIA_REGAIN']['complete_program_recurrence'] == '0/2'

    summary = {
        'version': 'v0.1',
        'status': 'PAIRED_SPECIFICITY_ASYMMETRY_SURVIVES_EXTERNAL_TIER_STRESS',
        'primary_paired_M1': {
            'systems': ['IOCHROMINAE','CAPE_ERICA','PETUNIEAE'],
            'hue_branch_specific_or_finer': '3/3',
            'amount_or_depletion_branch_specific_or_finer': '0/3',
            'amount_or_depletion_module_or_core': '1/3',
            'amount_or_depletion_diverse_or_primary_fail': '2/3',
            'prospective_component': 'PETUNIEAE_HUE_PASS_AMOUNT_FAIL',
            'petunieae_hue_margin_AICc': pet['hue_axis']['best_margin_AICc'],
            'petunieae_amount_margin_AICc': pet['amount_axis']['best_margin_AICc'],
        },
        'external_stress': {
            'M2_hue_branching': {
                'system': 'IPOMOEA',
                'result': 'EXACT_GENE_REGULATORY_F3_PRIME_H_IN_3_OF_3_ROBUST_RED_ORIGINS',
                'alignment': 'SUPPORTS_FINE_BRANCH_SPECIFIC_LOCALIZATION_OUTSIDE_M1',
            },
            'M3_depletion_or_loss': {
                'systems': ['AQUILEGIA','EPIMEDIUM'],
                'results': [
                    'AQUILEGIA_LATE_PATHWAY_EXPRESSION_RECURRENCE_WITHOUT_UNIVERSAL_EXACT_REGULATOR',
                    'EPIMEDIUM_ANS_CORE_4_OF_4_WITH_BROADER_IMPLEMENTATION_HETEROGENEITY',
                ],
                'alignment': 'SUPPORTS_RECURRENCE_AT_COARSER_MODULE_OR_CORE_LEVEL_OUTSIDE_M1',
            },
            'M4_regain': {
                'system': 'PETUNIA',
                'result': 'R2R3_MYB_REGULATOR_CLASS_2_OF_2_WITH_COMPLETE_IMPLEMENTATION_0_OF_2',
                'alignment': 'SUPPORTS_HIERARCHICAL_REPEATABILITY_NOT_AXIS_SPECIFICITY',
            },
        },
        'revised_inference': 'BOTH_HUE_AND_PIGMENT_LOSS_CAN_REPEAT_BUT_THEIR_MOST_STABLE_REPEATABILITY_OCCURS_AT_DIFFERENT_MECHANISTIC_RESOLUTIONS',
        'specificity_candidate': 'HUE_OR_HYDROXYLATION_CAN_RECUR_AT_BRANCHING_ENZYME_OR_EXACT_REGULATORY_LEVEL_WHEREAS_PIGMENT_DEPLETION_OR_LOSS_MORE_OFTEN_RECURS_AT_LATE_PATHWAY_OR_CORE_MODULE_LEVEL_WITH_HETEROGENEOUS_IMPLEMENTATION',
        'superseded_binary_wording': 'HUE_STABLE_WHILE_DEPLETION_UNSTABLE',
        'prospective_status': 'ONE_PAIRED_PROSPECTIVE_SYSTEM_ONLY',
        'numeric_pooling': 'FORBIDDEN_ACROSS_TIERS_AND_OBSERVATION_REGIMES',
        'independence_boundary': 'M1_PAIRED_SYSTEMS_ARE_PRIMARY; M2_M3_ARE_EXTERNAL_QUALITATIVE_STRESS_TESTS_AND_SYSTEM_REUSE_IS_NOT_COUNTED_AS_ADDITIONAL_INDEPENDENT_REPLICATION',
        'claim_boundary': 'The result is a resolution-specificity pattern, not a universal gene rule, not a pooled effect size, and not proof that depletion transitions cannot recur at fine resolution.',
        'paper1_science_changed': False,
    }

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
