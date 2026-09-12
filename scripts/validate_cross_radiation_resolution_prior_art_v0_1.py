#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def read_csv(path: Path):
    with path.open(newline='', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--matrix',type=Path,required=True)
    ap.add_argument('--decision',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    rows=read_csv(a.matrix)
    decision=json.loads(a.decision.read_text(encoding='utf-8'))

    prior=[r for r in rows if r['paper_id']!='CURRENT_SYNTHESIS']
    current=[r for r in rows if r['paper_id']=='CURRENT_SYNTHESIS']
    assert len(prior)==10, len(prior)
    assert len(current)==1
    assert len({r['doi'] for r in prior})==10

    # Existing literature must pre-empt every generic component used in the current synthesis.
    assert any(r['transition_type_or_direction_dependence']=='YES' for r in prior)
    assert any(r['same_visible_endpoint_alternate_mechanisms']=='YES' for r in prior)
    assert any(r['phenotype_axis_to_molecular_mapping']=='YES' for r in prior)
    assert any(r['state_representation_or_recoding']=='YES' for r in prior)

    # None of the representative priors is coded as the same integrated empirical test.
    assert not any(r['cross_radiation_macro_plus_molecular_resolution_test']=='YES' for r in prior)
    assert current[0]['cross_radiation_macro_plus_molecular_resolution_test']=='YES'
    assert current[0]['prospective_external_component']=='PARTIAL'

    assert decision['audit_type']=='TARGETED_REPRESENTATIVE_PRIOR_ART_AUDIT_NOT_SYSTEMATIC_REVIEW'
    assert decision['prior_art_rows']==10
    assert decision['current_candidate_row']==1
    assert decision['direct_prior_match_to_integrated_candidate_found'] is False
    assert decision['priority_status']=='NO_FIRST_CLAIM_TARGETED_AUDIT_ONLY'
    assert 'CROSS_RADIATION_ALIGNMENT' in decision['novelty_candidate']
    assert all('FIRST' in x or 'UNIVERSAL' in x for x in decision['forbidden_wording'])
    assert decision['paper1_science_changed'] is False

    summary={
        'version':'v0.1',
        'audit_type':decision['audit_type'],
        'representative_prior_rows':len(prior),
        'generic_transition_dependence_preempted':True,
        'generic_same_endpoint_alternate_mechanism_preempted':True,
        'single_radiation_axis_mapping_preempted':True,
        'generic_state_recoding_effect_preempted':True,
        'representative_direct_integrated_match_found':False,
        'novelty_candidate':decision['novelty_candidate'],
        'priority_status':decision['priority_status'],
        'paper1_science_changed':False,
        'status':'PASS_WITHOUT_PRIORITY_CLAIM'
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
