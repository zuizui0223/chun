#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

REQUIRED = {
    'source_taxon_name','provisional_accepted_taxon','display_organ','visible_state',
    'evidence_status','source_role','source_doi_or_citation','target_tip_match','notes'
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--seed', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()

    with a.seed.open(newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None or not REQUIRED.issubset(reader.fieldnames):
            raise SystemExit('seed schema drift')
        rows = list(reader)

    if len(rows) < 3:
        raise SystemExit('expected at least three explicit seed rows')
    names = [r['source_taxon_name'] for r in rows]
    if len(names) != len(set(names)):
        raise SystemExit('duplicate source taxon')
    for i, r in enumerate(rows, start=2):
        if r['visible_state'] != 'YELLOW':
            raise SystemExit(f'row {i}: current seed is restricted to explicit yellow evidence')
        if r['target_tip_match'] != 'PENDING':
            raise SystemExit(f'row {i}: no seed row may be promoted before 113-tip matching')
        if 'PENDING_TARGET_MATCH' not in r['evidence_status']:
            raise SystemExit(f'row {i}: fail-closed evidence status missing')
        if r['source_role'] != 'ATLAS_ADDITION':
            raise SystemExit(f'row {i}: newer evidence must remain marked ATLAS_ADDITION')

    if not {'Linum guatemalense','Linum mexicanum','Linum orizabae'}.issubset(set(names)):
        raise SystemExit('expected schiedeanum-complex seed taxa missing')

    summary = {
        'version': 'v0.1',
        'seed_rows': len(rows),
        'admitted_terminal_rows': 0,
        'target_tip_match_gate': 'BLOCKED_PENDING_113_TIP_LIST',
        'taxonomy_sensitivity': 'L_mexicanum_vs_L_orizabae',
        'paper1_science_changed': False,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
