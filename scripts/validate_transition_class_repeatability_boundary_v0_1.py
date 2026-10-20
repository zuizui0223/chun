#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

REQUIRED_SYSTEMS = {
    'CAMELLIA_ANTHOCYANIN_GAIN',
    'CAMELLIA_YELLOW_DEVELOPMENT',
    'PETUNIA_REGAIN',
    'IOCHROMINAE_LOSS',
    'ERICA_WHITE_YELLOW_DERIVATION',
    'IPOMOEA_RED_SHIFT',
    'AQUILEGIA_ANTHOCYANIN_LOSS',
    'PRIOR_SOBEL_STREISFELD_2013',
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--table', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()

    with a.table.open(newline='', encoding='utf-8') as fh:
        rows = list(csv.DictReader(fh))
    by_id = {r['system']: r for r in rows}
    missing = REQUIRED_SYSTEMS.difference(by_id)
    if missing:
        raise SystemExit(f'missing benchmark systems: {sorted(missing)}')

    prior = by_id['PRIOR_SOBEL_STREISFELD_2013']
    if prior['claim_status'] != 'NOT_NOVEL':
        raise SystemExit('gain-vs-loss mutation-spectrum prior art must remain NOT_NOVEL')

    directions = {r['transition_type'] for r in rows if not r['system'].startswith('PRIOR_')}
    if not {'GAIN','REGAIN','LOSS','HUE_SHIFT'}.issubset(directions):
        raise SystemExit('benchmark must retain multiple transition classes')

    units = {r['unit_of_repeatability'] for r in rows if not r['system'].startswith('PRIOR_')}
    if len(units) < 4:
        raise SystemExit('repeatability hierarchy collapsed to too few biological levels')

    if by_id['PETUNIA_REGAIN']['unit_of_repeatability'] == by_id['CAMELLIA_ANTHOCYANIN_GAIN']['unit_of_repeatability']:
        raise SystemExit('regulator-class and whole-state recurrence must remain distinct')

    summary = {
        'version': 'v0.1',
        'systems': len(rows),
        'transition_classes': sorted(directions),
        'repeatability_units': sorted(units),
        'generic_gain_loss_asymmetry_novelty': 'REJECTED_AS_PRIOR_ART',
        'working_target': 'BIOLOGICAL_LEVEL_OF_REPEATABILITY',
        'global_pooled_recurrence_estimator': 'FORBIDDEN_CURRENTLY',
        'paper1_science_changed': False,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
