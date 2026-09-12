#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def read_csv(rel: str):
    with (ROOT/rel).open(newline='',encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def read_json(rel: str):
    return json.loads((ROOT/rel).read_text(encoding='utf-8'))


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()

    tiers=read_csv('data/cross_radiation_pathway_region_tiers_v0_1.csv')
    bench=read_csv('data/cross_clade_mechanistic_recurrence_benchmark_v0_1.csv')
    erica=read_csv('data/erica_white_yellow_mechanisms_v0_1.csv')
    pet=read_json('data/petunieae_prospective_cross_level_v0_1.json')
    ioch=read_json('data/iochrominae_cross_level_bridge_summary_v0_1.json')
    expected=read_json('data/cross_radiation_pathway_region_tier_summary_v0_1.json')

    assert len(tiers)==9, len(tiers)
    assert {r['tier'] for r in tiers}=={'M1_MATCHED_AXIS','M2_HUE_FUNCTIONAL','M3_DEPLETION_FUNCTIONAL'}

    # Source-level checks.
    b={r['benchmark_id']:r for r in bench}
    assert b['IPOMOEA_RED']['shared_count']=='3/3'
    assert b['IOCHROMINAE_A_MINUS']['shared_count']=='4/4'
    assert b['AQUILEGIA_A_MINUS']['strongest_recurrence_level']=='LATE_PATHWAY_EXPRESSION'
    assert b['EPIMEDIUM_A_MINUS']['shared_count']=='4/4'
    assert ioch['hue_maps_to']=='BRANCHING_ENZYME_SUBSPACE'
    assert ioch['intensity_maps_to']=='LATE_PATHWAY_COEXPRESSION_MODULE'

    white=[r for r in erica if r['target_state']=='WHITE']
    yellow=[r for r in erica if r['target_state']=='YELLOW']
    assert len(white)==6 and len(yellow)==2
    white_levels=Counter(r['node_level'] for r in white)
    assert white_levels==Counter({'STRUCTURAL_LATE':5,'TRANS_REGULATOR':1}), white_levels
    assert all(r['focal_node']=='F3_PRIME_H' for r in yellow)

    assert pet['pre_frozen_gate']=='PETUNIEAE_PROSPECTIVE_BRIDGE_MIXED'
    assert pet['pre_frozen_gate_components']=={'amount_axis_pass':False,'coverage_pass':True,'hue_axis_pass':True}
    assert pet['hue_axis']['best_subspace']=='BRANCHING_HUE'
    assert pet['hue_axis']['best_margin_AICc']>2
    assert pet['amount_axis']['best_margin_AICc']<2
    assert pet['amount_axis']['null_model']['AICc'] < pet['amount_axis']['models'][pet['amount_axis']['best_subspace']]['AICc']
    assert pet['source_method_sensitivity_log_amount']['fit']['best_subspace']=='LATE_OUTPUT'

    m1_hue=[r for r in tiers if r['tier']=='M1_MATCHED_AXIS' and r['phenotype_dimension']=='HUE_HYDROXYLATION']
    m1_amount=[r for r in tiers if r['tier']=='M1_MATCHED_AXIS' and r['phenotype_dimension'] in {'PIGMENT_AMOUNT_OR_LOSS','PIGMENT_DEPLETION','PIGMENT_AMOUNT'}]
    expanded_hue=[r for r in tiers if r['phenotype_dimension'] in {'HUE_HYDROXYLATION','HUE_RED_SHIFT'}]
    expanded_loss=[r for r in tiers if r['phenotype_dimension'] in {'PIGMENT_AMOUNT_OR_LOSS','PIGMENT_DEPLETION','PIGMENT_AMOUNT','ANTHOCYANIN_LOSS','ANTHOCYANIN_MINUS_ENDPOINT'}]

    assert len(m1_hue)==3 and all(r['supported_region']=='BRANCHING' and r['region_support_status']=='SUPPORT' for r in m1_hue)
    assert len(m1_amount)==3
    assert sum(r['region_support_status'].startswith('SUPPORT') for r in m1_amount)==2
    assert sum(r['supported_region']=='UNRESOLVED' for r in m1_amount)==1
    assert len(expanded_hue)==4 and all(r['supported_region']=='BRANCHING' for r in expanded_hue)
    assert len(expanded_loss)==5
    assert sum(r['region_support_status'].startswith('SUPPORT') for r in expanded_loss)==4
    assert sum(r['supported_region']=='UNRESOLVED' for r in expanded_loss)==1
    assert not any(r['region_support_status'].startswith('SUPPORT') and r['supported_region'] in {'EARLY','BRANCHING'} for r in expanded_loss)

    summary={
      'version':'v0.1',
      'status':'INTERMEDIATE_PATHWAY_REGION_PREDICTABILITY_SUPPORTED_ACROSS_TIERED_EVIDENCE_WITH_ONE_PROSPECTIVE_HUE_COMPONENT',
      'tier_design':{
        'M1':'matched phenotype-axis to molecular-subspace evidence within a radiation',
        'M2':'independent hue/branching functional stress tests with robust event units',
        'M3':'independent pigment-loss/depletion functional or endpoint stress tests',
        'numeric_pooling':'FORBIDDEN_ACROSS_TIERS'
      },
      'M1_matched_axis':{
        'systems':['IOCHROMINAE','CAPE_ERICA','PETUNIEAE'],
        'hue_branching_support':'3/3 systems',
        'amount_or_depletion_downstream_output_support':'2/3 systems',
        'amount_or_depletion_unresolved':'1/3 systems (Petunieae raw amount)',
        'prospective_components':'Petunieae hue PASS; Petunieae raw amount unresolved; full gate MIXED'
      },
      'expanded_hue_branching':{
        'systems':['IOCHROMINAE','CAPE_ERICA','PETUNIEAE','IPOMOEA'],
        'support':'4/4 systems across M1+M2',
        'independent_functional_stress_test':"Ipomoea F3'H regulatory reduction in 3/3 robust red origins",
        'interpretation':'BRANCHING_HYDROXYLATION_REGION_RECURRENT_ACROSS_MATCHED_AND_EVENT_SPECIFIC_REGIMES'
      },
      'expanded_loss_depletion':{
        'systems':['IOCHROMINAE','CAPE_ERICA','PETUNIEAE','AQUILEGIA','EPIMEDIUM'],
        'downstream_output_or_regulatory_support':'4/5 systems across M1+M3',
        'unresolved':'1/5 systems (Petunieae raw amount)',
        'supported_counterexample_in_early_core_or_hue_branching_region':'0/5',
        'erica_white_detail':'5/6 structural-late focal nodes and 1/6 trans-regulatory bHLH',
        'interpretation':'LOSS_OR_DEPLETION_REPEATEDLY_INVOLVES_DOWNSTREAM_OUTPUT_OR_REGULATORY_REGIONS_BUT_EXACT_NODE_IMPLEMENTATION_IS_HETEROGENEOUS'
      },
      'resolution_inference':'PREDICTABILITY_CONCENTRATES_AT_INTERMEDIATE_BIOCHEMICAL_DIMENSIONS_AND_PATHWAY_REGIONS_RATHER_THAN_AT_SHARED_COARSE_VISIBLE_STATES_OR_COMPLETE_MOLECULAR_PROGRAMMES',
      'critical_boundary':'The M2/M3 expansion is a retrospective hierarchical synthesis created after these source results were known. It is a hypothesis-generating generalization and must be prospectively tested in newly admitted systems before being called a replicated law.',
      'prospective_status':'ONLY_PETUNIEAE_HUE_COMPONENT_PROSPECTIVE_FOR_THIS_ARCHITECTURE',
      'paper1_science_changed':False
    }
    assert summary==expected, (summary,expected)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
