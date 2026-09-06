#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

EXPECTED_DERIVED = {
    'ABSTRACT_SPECIES': '245',
    'METHODS_TAXONOMY': '245',
    'FIG2_TAXONOMY': '245',
    'SUPPORTING_TABLE_S1': '245',
    'HUE_CATEGORY_COUNTS': '294',
    'WHITE_RED_SET_RESULTS': '292',
    'YELLOW_SET_RESULTS': '292',
    'UV_BINARY_RESULTS': '290',
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--audit', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()

    with a.audit.open(newline='', encoding='utf-8') as fh:
        rows = list(csv.DictReader(fh))
    by = {r['claim_id']: r for r in rows}
    if len(by) != len(rows):
        raise SystemExit('duplicate claim_id')

    for key, expected in EXPECTED_DERIVED.items():
        if key not in by:
            raise SystemExit(f'missing audit claim {key}')
        if by[key]['derived_check'] != expected:
            raise SystemExit(f'{key}: derived count drifted: {by[key]["derived_check"]} != {expected}')

    if by['SUPPORTING_TABLE_S1']['status'] != 'REMOTE_VERIFIED_NOT_INGESTED':
        raise SystemExit('Table S1 must remain remote-verified/not-ingested until binary inspection')
    if by['ATTRACTANT_ORGAN_SCHEMA']['status'] != 'COMPATIBLE_WITH_ATLAS':
        raise SystemExit('organ compatibility gate drifted')

    mismatched = [
        k for k, v in EXPECTED_DERIVED.items()
        if v != '245' and k not in {'ABSTRACT_SPECIES','METHODS_TAXONOMY','FIG2_TAXONOMY','SUPPORTING_TABLE_S1'}
    ]
    if set(mismatched) != {'HUE_CATEGORY_COUNTS','WHITE_RED_SET_RESULTS','YELLOW_SET_RESULTS','UV_BINARY_RESULTS'}:
        raise SystemExit('count-discrepancy set drifted')

    summary = {
        'version': 'v0.1',
        'narrative_primary_species_count': 245,
        'hue_category_sum': 294,
        'white_red_subset_sum': 292,
        'yellow_subset_sum': 292,
        'uv_binary_sum': 290,
        'methods_genera_families': '180/71',
        'figure2_genera_families': '205/76',
        'supporting_table_file': 'PLB-28-201-s001.docx',
        'source_quality_gate': 'HOLD_PENDING_TABLE_S1_BINARY_RECONCILIATION',
        'organ_schema_compatibility': 'PASS',
        'paper1_science_changed': False,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
