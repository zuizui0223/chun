#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def read_csv(rel):
    with (ROOT/rel).open(newline='',encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def read_json(rel):
    return json.loads((ROOT/rel).read_text(encoding='utf-8'))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    rows=read_csv('data/ruellia_post_freeze_resolution_validation_v0_1.csv')
    pre=read_json('data/cross_radiation_pathway_region_tier_summary_v0_1.json')
    expected=read_json('data/ruellia_post_freeze_resolution_result_v0_1.json')

    assert len(rows)==4
    r={x['row_id']:x for x in rows}
    assert r['RUELLIA_PANEL']['n_taxa']=='10'
    assert r['RUELLIA_PURPLE_TO_RED']['pathway_region']=='BRANCHING_HYDROXYLATION'
    assert r['RUELLIA_PURPLE_TO_RED']['classification']=='HUE_BRANCHING_SUPPORT'
    assert r['RUELLIA_RED_TO_PURPLE']['classification']=='HUE_BRANCHING_SUPPORT_PUTATIVE'
    assert r['RUELLIA_YELLOW_LOSS']['n_taxa']=='3'
    assert r['RUELLIA_YELLOW_LOSS']['pathway_region']=='EARLY_PLUS_LATE_PLUS_REGULATORY'
    assert r['RUELLIA_YELLOW_LOSS']['classification']=='DEPLETION_MIXED_REGION_COUNTEREXAMPLE'
    assert {x['source_doi'] for x in rows}=={'10.1186/s12862-021-01955-x'}

    assert pre['expanded_hue_branching']['support']=='4/4 systems across M1+M2'
    assert pre['expanded_loss_depletion']['downstream_output_or_regulatory_support']=='4/5 systems across M1+M3'
    assert pre['expanded_loss_depletion']['unresolved'].startswith('1/5')

    result={
      'version':'v0.1',
      'source_doi':'10.1186/s12862-021-01955-x',
      'validation_timing':'EXTERNAL_SOURCE_READ_AFTER_INTERMEDIATE_PATHWAY_REGION_RULE_WAS_FROZEN_ON_MAIN_BUT_RUELLIA_WAS_NOT_TARGET_PREREGISTERED',
      'classification':'HUE_PASS_DEPLETION_MIXED',
      'panel':{
        'species':10,'purple':4,'red':3,'yellow':3,
        'formal_colour_ASR_by_source':False,
        'source_transition_status':'POTENTIAL_TRANSITIONS_FROM_10_TIP_PHYLOGENY'
      },
      'hue_component':{
        'classification':'SUPPORT_BRANCHING_HYDROXYLATION',
        'source_mechanism':"F3_prime_5_prime_H coding/regulatory loss in purple-to-red context and putative reactivation in red-to-purple context",
        'pathway_region':'BRANCHING_HYDROXYLATION','event_count_promoted':False
      },
      'depletion_component':{
        'classification':'MIXED_EARLY_LATE_REGULATORY_COUNTEREXAMPLE_TO_OUTPUT_SIDE_ONLY',
        'yellow_taxa':3,'F3H_downregulated_taxa':2,'ANS_downregulated_taxa':3,
        'source_interpretation':'coordinated structural-gene downregulation likely involving regulatory change',
        'pathway_regions':['EARLY_CORE','LATE_OUTPUT','REGULATORY'],'event_count_promoted':False
      },
      'cross_system_update':{
        'hue_branching_system_support_after_Ruellia':'5/5 systems',
        'loss_depletion_output_side_support_after_Ruellia':'4/6 systems',
        'loss_depletion_unresolved_after_Ruellia':'1/6 systems (Petunieae raw amount)',
        'loss_depletion_mixed_early_late_counterexample_after_Ruellia':'1/6 systems (Ruellia)'
      },
      'interpretation':'The post-freeze external source strengthens the hue-to-branching pattern while falsifying an output-side-only formulation for pigment loss/depletion. Loss/depletion is better described as recurrently regulatory/downstream-biased but mechanistically broader than hue shifts.',
      'prospective_status':'NOT_PROSPECTIVE_TARGET_SELECTION',
      'paper1_science_changed':False
    }
    assert result==expected,(result,expected)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
