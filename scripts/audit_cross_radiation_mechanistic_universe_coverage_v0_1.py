#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_csv(path: Path):
    with path.open(newline='', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--registry', type=Path, default=ROOT / 'data/cross_clade_evidence_tier_registry_v0_5.csv')
    ap.add_argument('--benchmark', type=Path, default=ROOT / 'data/cross_clade_mechanistic_recurrence_benchmark_v0_1.csv')
    ap.add_argument('--coverage', type=Path, default=ROOT / 'data/cross_radiation_mechanistic_universe_coverage_v0_1.csv')
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()

    registry = read_csv(a.registry)
    benchmark = read_csv(a.benchmark)
    coverage = read_csv(a.coverage)

    assert len(registry) == 18, len(registry)
    registry_by_id = {r['clade_id']: r for r in registry}
    assert len(registry_by_id) == 18

    v05 = [r for r in coverage if r['registry_scope'] == 'V0_5_REGISTRY']
    post = [r for r in coverage if r['registry_scope'] == 'POST_V0_5_PROSPECTIVE_ADDITION']
    assert len(v05) == 18 and len(post) == 1
    assert {r['clade_id'] for r in v05} == set(registry_by_id)
    assert post[0]['clade_id'] == 'PETUNIEAE'

    # Coverage evidence must reproduce the pre-existing v0.5 molecular-layer wording exactly.
    for r in v05:
        assert r['preexisting_registry_evidence'] == registry_by_id[r['clade_id']]['molecular_layer'], r['clade_id']

    class_counts = Counter(r['coverage_class'] for r in v05)
    expected_counts = {
        'BENCHMARK_ELIGIBLE_INCLUDED': 7,
        'EXCLUDED_DEPENDENCE_COLLAPSE': 1,
        'EXCLUDED_INSUFFICIENT_MATCHED_MOLECULAR_LAYER': 9,
        'EXCLUDED_NETWORK_CONFOUNDED_EVENT_COMPARISON': 1,
    }
    assert dict(class_counts) == expected_counts, class_counts

    eligible = {r['clade_id'] for r in v05 if r['coverage_class'] == 'BENCHMARK_ELIGIBLE_INCLUDED'}
    expected_eligible = {
        'CAMELLIA','EPIMEDIUM_DIPHYLLON','PETUNIA_LONG_TUBE_CLADE','ERICA_CAPE',
        'AQUILEGIA','IOCHROMINAE','IPOMOEA_ASTRIPOMOEINAE'
    }
    assert eligible == expected_eligible
    assert all(r['in_current_mechanistic_benchmark'] == 'YES' for r in v05 if r['clade_id'] in eligible)
    assert all(r['in_current_mechanistic_benchmark'] == 'NO' for r in v05 if r['clade_id'] not in eligible)

    benchmark_clade_to_id = {
        'Camellia': 'CAMELLIA',
        'Epimedium': 'EPIMEDIUM_DIPHYLLON',
        'Petunia': 'PETUNIA_LONG_TUBE_CLADE',
        'Erica': 'ERICA_CAPE',
        'Aquilegia': 'AQUILEGIA',
        'Iochrominae': 'IOCHROMINAE',
        'Ipomoea': 'IPOMOEA_ASTRIPOMOEINAE',
    }
    benchmark_ids = {benchmark_clade_to_id[r['clade']] for r in benchmark}
    assert benchmark_ids == eligible, (benchmark_ids, eligible)

    summary = {
        'version': 'v0.1',
        'status': 'PREEXISTING_MECHANISTIC_UNIVERSE_FULLY_COVERED_BY_BENCHMARK',
        'history': {
            'v0_5_registry_first_commit': '1e69a6494ad9ec7e38b583158bb385ce8bd46296',
            'v0_5_registry_commit_date_utc': '2026-09-06T04:35:37Z',
            'mechanistic_benchmark_first_commit': 'ac15ecfe1b1f390efbcead7683258671372b2bbe',
            'mechanistic_benchmark_commit_date_utc': '2026-09-06T04:38:59Z',
            'current_resolution_tier_expansion_date': '2026-09-13',
            'interpretation': 'SOURCE_UNIVERSE_AND_SEVEN_SYSTEM_BENCHMARK_PREDATE_CURRENT_RESOLUTION_SPECIFICITY_SYNTHESIS',
        },
        'v0_5_registry': {
            'clades_total': 18,
            'benchmark_eligible': 7,
            'benchmark_included': 7,
            'eligible_coverage': '7/7',
            'eligible_ids': sorted(eligible),
            'excluded_total': 11,
            'exclusion_counts': {
                'DEPENDENCE_COLLAPSE': 1,
                'INSUFFICIENT_MATCHED_MOLECULAR_LAYER': 9,
                'NETWORK_CONFOUNDED_EVENT_COMPARISON': 1,
            },
            'eligible_omissions': [],
        },
        'post_registry_addition': {
            'id': 'PETUNIEAE',
            'role': 'PROSPECTIVELY_FROZEN_MATCHED_PHENOTYPE_AXIS_TEST',
            'included_in_M1': True,
            'included_in_v0_5_coverage_denominator': False,
        },
        'selection_bias_result': 'NO_ELIGIBLE_V0_5_MECHANISTIC_CLADE_OMITTED_FROM_BENCHMARK',
        'remaining_selection_boundary': 'THE_V0_5_REGISTRY_IS_A_CURATED_CROSS_CLADE_ATLAS_NOT_A_SYSTEMATIC_CENSUS_OF_ALL_FLOWER_COLOUR_LITERATURE',
        'claim_boundary': 'This audit addresses within-atlas cherry-picking. It does not prove that the atlas itself is globally exhaustive or free of literature-availability bias.',
        'paper1_science_changed': False,
    }

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
