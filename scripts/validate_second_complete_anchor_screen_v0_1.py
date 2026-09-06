#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

REQUIRED = {
    'candidate','white_like_baseline','three_or_more_robust_events',
    'three_or_more_matched_molecular_event_contrasts','current_polymorphism','ecology_layer',
    'event_confidence','molecular_match','verdict','primary_failure','reopen_condition','key_reference'
}
EXPECTED = {
    'EPIMEDIUM_DIPHYLLON','ANTIRRHINEAE','PETUNIA_LONG_TUBE','SILENE_PHYSOLYCHNIS',
    'LINOIDEAE','HYDRANGEA_CORNIDIA','ANGRAECINAE','POLYGONATUM_VERTICILLATA',
    'JASMINUM_INDIA','NICOTIANA_SECTIONAL','LINANTHUS','ERICA_CAPE'
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--screen', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()

    with a.screen.open(newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            raise SystemExit('missing header')
        missing = REQUIRED.difference(reader.fieldnames)
        if missing:
            raise SystemExit(f'missing columns: {sorted(missing)}')
        rows = list(reader)

    ids = {r['candidate'] for r in rows}
    if ids != EXPECTED:
        raise SystemExit(f'candidate set drifted: missing={sorted(EXPECTED-ids)} extra={sorted(ids-EXPECTED)}')
    if len(rows) != len(ids):
        raise SystemExit('duplicate candidate rows')
    if any(r['verdict'] == 'PASS' for r in rows):
        raise SystemExit('v0.1 screen must not contain a complete second-anchor PASS')
    for r in rows:
        if not r['primary_failure'].strip() or not r['reopen_condition'].strip() or not r['key_reference'].strip():
            raise SystemExit(f"{r['candidate']}: missing failure/reopen/reference field")

    pet = next(r for r in rows if r['candidate'] == 'PETUNIA_LONG_TUBE')
    if pet['three_or_more_robust_events'] != 'NO' or pet['verdict'] != 'FAIL_PARTIAL':
        raise SystemExit('Petunia must remain a two-event partial regain control')
    epi = next(r for r in rows if r['candidate'] == 'EPIMEDIUM_DIPHYLLON')
    if epi['three_or_more_robust_events'] != 'NO' or epi['verdict'] != 'FAIL_HOLD':
        raise SystemExit('Epimedium event-independence hold drifted')
    ant = next(r for r in rows if r['candidate'] == 'ANTIRRHINEAE')
    if ant['three_or_more_matched_molecular_event_contrasts'] != 'NO':
        raise SystemExit('Antirrhineae molecular independent-system failure drifted')
    lin = next(r for r in rows if r['candidate'] == 'LINANTHUS')
    if lin['verdict'] != 'FAIL_WRONG_BASELINE':
        raise SystemExit('Linanthus must remain a wrong-baseline control under recent phylogenomics')
    erica = next(r for r in rows if r['candidate'] == 'ERICA_CAPE')
    if erica['three_or_more_robust_events'] != 'YES' or erica['three_or_more_matched_molecular_event_contrasts'] != 'YES' or erica['verdict'] != 'FAIL_WRONG_BASELINE':
        raise SystemExit('Erica should demonstrate that strong event+molecular evidence can fail only the white-baseline criterion')

    verdicts = Counter(r['verdict'] for r in rows)
    white_candidates = sum(r['white_like_baseline'] in {'YES','YES_OR_ORGAN_SPECIFIC','YES_OR_LIKELY','PROVISIONAL_YES','DERIVED_COLORLESS_SUBCLADE','SOME_WHITE_ANCESTRAL_NODES','PINK_WHITE_CONTEXT'} for r in rows)
    robust_event_candidates = sum(r['three_or_more_robust_events'] in {'YES','YES_OR_LIKELY','YES_SPECTRAL'} for r in rows)
    molecular_event_candidates = sum(r['three_or_more_matched_molecular_event_contrasts'] == 'YES' for r in rows)

    summary = {
        'version': 'v0.1',
        'screened_candidates': len(rows),
        'complete_second_anchor_passes': 0,
        'white_like_or_partial_candidates': white_candidates,
        'candidates_with_three_plus_robust_events': robust_event_candidates,
        'candidates_with_three_plus_matched_molecular_event_contrasts': molecular_event_candidates,
        'verdict_counts': dict(verdicts),
        'broad_discovery_screen': 'CLOSED_UNTIL_REOPEN_CONDITION',
        'next_strategy': 'EVIDENCE_TIER_ATLAS_AND_ORIGINAL_TRAIT_RECONSTRUCTION',
        'paper1_science_changed': False,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
