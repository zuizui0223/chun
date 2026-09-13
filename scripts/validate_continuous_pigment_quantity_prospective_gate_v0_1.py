#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def read_csv(path: Path):
    with path.open(newline='', encoding='utf-8-sig') as fh:
        return list(csv.DictReader(fh))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--gate', type=Path, required=True)
    ap.add_argument('--screen', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()

    gate = json.loads(a.gate.read_text(encoding='utf-8'))
    screen = read_csv(a.screen)

    assert gate['version'] == 'v0.1'
    assert gate['status'] == 'FROZEN_BEFORE_FOURTH_RADIATION_CANDIDATE_OUTCOME_INSPECTION'
    assert gate['primary_prediction']['phenotype_dimension'] == 'PIGMENT_QUANTITY_CONTINUOUS'
    assert gate['primary_prediction']['predicted_target_family'] == 'OUTPUT_CONTROL'
    assert gate['primary_prediction']['OUTPUT_CONTROL_members'] == ['LATE_OUTPUT', 'PATHWAY_REGULATION']
    assert gate['primary_prediction']['competing_target_classes'] == ['EARLY_CORE', 'BRANCH_COMPOSITION']

    onto = gate['target_class_ontology']
    assert set(onto) == {'EARLY_CORE', 'BRANCH_COMPOSITION', 'LATE_OUTPUT', 'PATHWAY_REGULATION'}
    assert onto['EARLY_CORE'] == ['CHS', 'CHI', 'F3H']
    assert onto['BRANCH_COMPOSITION'] == ['F3_PRIME_H', 'F3_PRIME_5_H']
    assert 'DFR' in onto['LATE_OUTPUT'] and 'ANS' in onto['LATE_OUTPUT']
    assert onto['PATHWAY_REGULATION'] == ['R2R3_MYB', 'BHLH', 'WD40']

    adm = gate['candidate_admission']
    assert adm['minimum_matched_taxa'] == 20
    assert adm['response_requirements']['minimum_unique_values'] == 10
    assert adm['response_requirements']['maximum_exact_zero_fraction'] == 0.2
    assert adm['response_requirements']['ordinal_colour_scores_forbidden'] is True
    assert adm['response_requirements']['binary_presence_absence_forbidden'] is True
    assert adm['molecular_requirements']['EARLY_CORE_min_genes'] == 2
    assert adm['molecular_requirements']['BRANCH_COMPOSITION_min_genes'] == 1
    assert adm['molecular_requirements']['LATE_OUTPUT_min_genes'] == 2
    assert adm['molecular_requirements']['PATHWAY_REGULATION_min_genes'] == 2
    assert adm['molecular_requirements']['all_four_target_classes_required'] is True
    assert adm['phylogeny_requirements']['branch_length_tree_required'] is True
    assert adm['decisive_target_class_outcome_must_not_be_inspected_before_admission'] is True

    search = gate['candidate_search']
    assert search['maximum_source_publications_screened'] == 20
    assert search['selection_if_multiple_pass'] == [
        'largest_matched_taxon_count',
        'earliest_publication_year',
        'lexicographically_smallest_DOI',
    ]
    forbidden = set(search['outcome_fields_forbidden_before_admission'])
    assert {'best_target_class', 'target_class_AICc', 'target_class_effect_sizes'} <= forbidden

    resp = gate['primary_response_rule']
    assert resp['primary_scale'] == 'RAW_SOURCE_SCALE_Z_STANDARDIZED_WITHIN_RADIATION'
    assert resp['post_outcome_log_sqrt_rank_transform_forbidden_for_primary_gate'] is True
    assert resp['one_predeclared_rank_sensitivity_allowed'] is True
    assert resp['rank_sensitivity_cannot_upgrade_primary_classification'] is True

    model = gate['model_rule']
    assert model['candidate_models'] == ['NULL', 'EARLY_CORE', 'BRANCH_COMPOSITION', 'LATE_OUTPUT', 'PATHWAY_REGULATION']
    assert model['ranking_metric'] == 'AICc'
    assert model['same_taxon_set_for_null_and_all_target_classes'] is True

    classes = gate['classification_rule']
    assert set(classes) == {'PASS', 'MIXED', 'FAIL', 'UNQUALIFIED'}
    assert '>=2 AICc' in classes['PASS']
    assert '>=2 AICc' in classes['FAIL']

    assert len(gate['no_rescue_rule']) == 5
    assert gate['relationship_to_current_programme']['continuous_quantity_status'].startswith('two direct radiation-scale systems only')
    assert gate['relationship_to_current_programme']['paper1_science_changed'] is False

    # Before candidate screening starts the ledger must be empty. This validator deliberately
    # changes state once rows are later added; the frozen gate itself must not be edited.
    if screen:
        if len(screen) > search['maximum_source_publications_screened']:
            raise SystemExit('candidate screen exceeded frozen 20-source cap')
        orders = [int(r['screen_order']) for r in screen]
        if orders != list(range(1, len(screen) + 1)):
            raise SystemExit(f'candidate screen order is not contiguous: {orders}')
        for r in screen:
            if r['decisive_target_outcome_inspected'] not in {'false', 'FALSE', '0', 'False'}:
                raise SystemExit(f"outcome firewall violated for {r['source_doi']}")
        state = 'SCREENING_STARTED_OUTCOME_BLIND'
    else:
        state = 'FROZEN_NO_CANDIDATE_SCREENED'

    summary = {
        'version': 'v0.1',
        'gate_status': gate['status'],
        'candidate_screen_rows': len(screen),
        'current_state': state,
        'primary_dimension': gate['primary_prediction']['phenotype_dimension'],
        'predicted_target_family': gate['primary_prediction']['predicted_target_family'],
        'minimum_matched_taxa': adm['minimum_matched_taxa'],
        'all_four_target_classes_required': adm['molecular_requirements']['all_four_target_classes_required'],
        'raw_response_primary': True,
        'rank_sensitivity_can_upgrade': False,
        'maximum_source_publications_screened': search['maximum_source_publications_screened'],
        'paper1_science_changed': False,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
