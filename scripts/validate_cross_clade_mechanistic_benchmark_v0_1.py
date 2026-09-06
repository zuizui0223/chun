#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


def read_csv(path: Path):
    with path.open(newline='', encoding='utf-8') as fh:
        return list(csv.DictReader(fh))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--benchmark', type=Path, required=True)
    ap.add_argument('--erica', type=Path, required=True)
    ap.add_argument('--petunia', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()

    bench = read_csv(a.benchmark)
    erica = read_csv(a.erica)
    pet = read_csv(a.petunia)

    expected_ids = {
        'CAMELLIA_ANTH_GAIN','CAMELLIA_YELLOW','EPIMEDIUM_A_MINUS','PETUNIA_REGAIN',
        'ERICA_WHITE_YELLOW','AQUILEGIA_A_MINUS','IOCHROMINAE_A_MINUS','IPOMOEA_RED'
    }
    ids = {r['benchmark_id'] for r in bench}
    if ids != expected_ids:
        raise SystemExit(f'benchmark ids drifted: {sorted(ids)}')
    if any(r['pooled_estimator_eligible'] != 'NO' for r in bench):
        raise SystemExit('heterogeneous unit types must not be pooled at v0.1')

    if len(erica) != 8:
        raise SystemExit(f'expected 8 Erica derived taxa, found {len(erica)}')
    node_counts = Counter(r['focal_node'] for r in erica)
    if len(node_counts) != 5 or max(node_counts.values()) != 2:
        raise SystemExit(f'Erica focal-node diversity drifted: {node_counts}')
    reg = sum(r['regulatory_or_coding'].startswith('REGUL') for r in erica)
    coding = sum(r['regulatory_or_coding'] == 'CODING_LOSS' for r in erica)
    if (reg, coding) != (6, 2):
        raise SystemExit(f'Erica regulatory/coding split drifted: {(reg, coding)}')
    groups = {r['comparison_group'] for r in erica}
    if groups != {'B','D','E','F','H','J'}:
        raise SystemExit(f'Erica comparison groups drifted: {groups}')

    if len(pet) != 2:
        raise SystemExit('expected two Petunia regain events')
    if {r['event_independence'] for r in pet} != {'ROBUST_WITHIN_LONG_TUBE_CLADE'}:
        raise SystemExit('Petunia event-independence gate drifted')
    if {r['shared_regulator_class'] for r in pet} != {'R2R3_MYB'}:
        raise SystemExit('Petunia regulator-class recurrence drifted')
    if len({r['regulator_solution'] for r in pet}) != 2:
        raise SystemExit('Petunia implementation heterogeneity missing')
    if {r['mechanistic_complexity'] for r in pet} != {'SIMPLE_SINGLE_MAJOR_RESTORATION','COMPLEX_MULTICOMPONENT_RECRUITMENT'}:
        raise SystemExit('Petunia complexity contrast drifted')

    b = {r['benchmark_id']: r for r in bench}
    if b['IPOMOEA_RED']['shared_count'] != '3/3':
        raise SystemExit('Ipomoea exact-gene positive control drifted')
    if b['IOCHROMINAE_A_MINUS']['shared_count'] != '4/4':
        raise SystemExit('Iochrominae pathway-level control drifted')
    if b['EPIMEDIUM_A_MINUS']['shared_count'] != '4/4':
        raise SystemExit('Epimedium ANS core recurrence drifted')
    if b['PETUNIA_REGAIN']['complete_program_recurrence'] != '0/2':
        raise SystemExit('Petunia whole-implementation contrast drifted')
    if b['ERICA_WHITE_YELLOW']['shared_count'] != '2/8':
        raise SystemExit('Erica causal-node diversity diagnostic drifted')

    summary = {
        'version': 'v0.1',
        'benchmark_rows': len(bench),
        'pooled_estimator': 'FORBIDDEN_HETEROGENEOUS_UNITS',
        'erica_derived_taxa': len(erica),
        'erica_unique_focal_nodes': len(node_counts),
        'erica_max_exact_node_recurrence': '2/8',
        'erica_regulatory_expression_routes': reg,
        'erica_coding_loss_routes': coding,
        'petunia_independent_regains': len(pet),
        'petunia_shared_regulator_class': '2/2 R2R3_MYB',
        'petunia_complete_implementation_recurrence': '0/2',
        'benchmark_gate': 'PASS',
        'interpretation': 'repeatability_level_varies_by_transition_clade_and_observation_regime',
        'paper1_science_changed': False,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
