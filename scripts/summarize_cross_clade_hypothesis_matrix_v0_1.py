#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_csv(path: Path):
    with path.open(newline='', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--matrix', type=Path, default=ROOT / 'data/cross_clade_hypothesis_evidence_v0_1.csv')
    ap.add_argument('--registry', type=Path, default=ROOT / 'data/cross_clade_evidence_tier_registry_v0_5.csv')
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()

    rows = read_csv(a.matrix)
    registry = read_csv(a.registry)
    registry_ids = {r['clade_id'] for r in registry}
    assert len(registry_ids) == 18
    assert len(rows) == 33, len(rows)

    hypotheses = [
        'H1_BASELINE_DEPENDENT_TRANSITION_ARCHITECTURE',
        'H2_RETAINED_CAPACITY_REGULATORY_REDEPLOYMENT',
        'H3_HIERARCHICAL_REPEATABILITY',
        'H4_REPRESENTATION_AND_OBSERVATION_RESOLUTION_DEPENDENCE',
        'H5_ACCESSIBILITY_REALIZATION_GAP',
        'H6_ECOLOGICAL_FILTERING_CONDITIONAL_ON_LATENT_PHENOTYPE',
    ]
    assert {r['hypothesis'] for r in rows} == set(hypotheses)

    for r in rows:
        if r['scope'] == 'V0_5_REGISTRY':
            assert r['system'] in registry_ids, r['system']
        else:
            assert r['scope'] == 'POST_V0_5_PROSPECTIVE'
            assert r['system'] == 'PETUNIEAE'

    grouped = defaultdict(list)
    for r in rows:
        grouped[r['hypothesis']].append(r)

    counts = {h: Counter(r['evidence_class'] for r in grouped[h]) for h in hypotheses}
    systems = {h: sorted({r['system'] for r in grouped[h]}) for h in hypotheses}

    assert len(grouped[hypotheses[0]]) == 6
    assert counts[hypotheses[0]] == Counter({'COMPATIBLE_ONLY': 4, 'COUNTEREXAMPLE_TO_STRONGER_FORM': 2})

    assert len(grouped[hypotheses[1]]) == 4
    assert counts[hypotheses[1]] == Counter({'PRIOR_ART_SUPPORT': 2, 'DIRECT_SUPPORT': 1, 'COMPATIBLE_ONLY': 1})

    assert len(grouped[hypotheses[2]]) == 7
    assert counts[hypotheses[2]] == Counter({'DIRECT_SUPPORT': 5, 'PARTIAL_SUPPORT': 2})

    assert len(grouped[hypotheses[3]]) == 7
    assert counts[hypotheses[3]] == Counter({'DIRECT_SUPPORT': 7})
    h4_roles = Counter(r['evidence_role'] for r in grouped[hypotheses[3]])
    assert h4_roles['MACRO_STATE_GRANULARITY'] == 3
    assert h4_roles['PROSPECTIVE_PHENOTYPE_AXIS_LOCALIZATION'] == 1

    assert len(grouped[hypotheses[4]]) == 3
    assert counts[hypotheses[4]] == Counter({'PARTIAL_SUPPORT': 2, 'IDENTIFIABILITY_STRESS': 1})

    assert len(grouped[hypotheses[5]]) == 6
    assert counts[hypotheses[5]] == Counter({'DIRECT_SUPPORT': 4, 'PARTIAL_SUPPORT': 2})

    summary = {
        'version': 'v0.1',
        'status': 'H4_FLAGSHIP_H3_SECONDARY_H1_H5_UNCLOSED',
        'registry_clades': 18,
        'post_registry_systems': ['PETUNIEAE'],
        'evidence_rows': len(rows),
        'hypotheses': {
            'H1': {
                'name': hypotheses[0],
                'systems_with_evidence': len(systems[hypotheses[0]]),
                'evidence_class_counts': dict(counts[hypotheses[0]]),
                'decision': 'STRONGER_ONE_WAY_WHITE_GAIN_FORM_FALSIFIED_BUT_BASELINE_DEPENDENT_RATE_OR_ROUTE_EFFECT_NOT_DIRECTLY_CLOSED',
                'flagship_ready': False,
            },
            'H2': {
                'name': hypotheses[1],
                'systems_with_evidence': len(systems[hypotheses[1]]),
                'evidence_class_counts': dict(counts[hypotheses[1]]),
                'decision': 'SUPPORTED_IN_DIRECT_REGAIN_AND_PRIOR_ART_CONTEXT_BUT_GENERIC_GENETIC_CONTEXT_NOVELTY_PREEMPTED',
                'flagship_ready': False,
            },
            'H3': {
                'name': hypotheses[2],
                'systems_with_evidence': len(systems[hypotheses[2]]),
                'evidence_class_counts': dict(counts[hypotheses[2]]),
                'decision': 'STRONG_CROSS_CLADE_SUPPORT_FOR_HIERARCHICAL_REPEATABILITY_WITH_HETEROGENEOUS_UNITS',
                'flagship_ready': True,
                'role': 'SECONDARY_MECHANISTIC_SPINE',
            },
            'H4': {
                'name': hypotheses[3],
                'systems_with_evidence': len(systems[hypotheses[3]]),
                'evidence_class_counts': dict(counts[hypotheses[3]]),
                'macro_direct_support_systems': ['LINOIDEAE','ANGRAECINAE','ANTIRRHINEAE'],
                'molecular_or_observation_direct_support_systems': ['CAMELLIA','IOCHROMINAE','ERICA_CAPE','PETUNIEAE'],
                'prospective_component': 'PETUNIEAE',
                'decision': 'DIRECT_CROSS_SCALE_SUPPORT_FOR_RESOLUTION_DEPENDENCE_AT_MACRO_STATE_AND_MOLECULAR_AXIS_LEVELS',
                'flagship_ready': True,
                'role': 'PRIMARY_FLAGSHIP_CLAIM',
            },
            'H5': {
                'name': hypotheses[4],
                'systems_with_evidence': len(systems[hypotheses[4]]),
                'evidence_class_counts': dict(counts[hypotheses[4]]),
                'decision': 'PARTIAL_IDENTIFIABILITY_AND_ENDPOINT_EVENT_GAP_ONLY_NO_COMMON_ACCESSIBILITY_REALIZATION_ESTIMATOR',
                'flagship_ready': False,
            },
            'H6': {
                'name': hypotheses[5],
                'systems_with_evidence': len(systems[hypotheses[5]]),
                'evidence_class_counts': dict(counts[hypotheses[5]]),
                'decision': 'MULTISYSTEM_ECOLOGICAL_FILTERING_SUPPORT_BUT_GENERAL_BRANCH_CAUSAL_ASSIGNMENT_REMAINS_OPEN',
                'flagship_ready': False,
                'role': 'ECOLOGICAL_CONTEXT_AND_FUTURE_CAUSAL_LAYER',
            },
        },
        'paper_candidate': {
            'primary': 'H4_REPRESENTATION_AND_OBSERVATION_RESOLUTION_DEPENDENCE',
            'secondary': 'H3_HIERARCHICAL_REPEATABILITY',
            'one_sentence': 'Across independent flower-colour radiations, evolutionary predictability is resolution dependent: fine phylogenetic states and selected biochemical or regulatory dimensions recur more consistently than privileged coarse boundaries, universal directions, or complete molecular implementations.',
            'not_claimed': [
                'universal colour direction',
                'universal causal gene',
                'complete programme replay',
                'pooled recurrence rate across heterogeneous units',
                'branch-specific ecological cause across the atlas',
            ],
        },
        'paper1_science_changed': False,
    }

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
