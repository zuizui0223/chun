#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

REQUIRED = {
    'clade_id','ancestral_baseline','event_structure','molecular_layer','ecology_layer',
    'current_variation','primary_role','white_like_anchor_status','prior_art_risk','key_reference'
}
REQUIRED_CLADES = {
    'CAMELLIA','EPIMEDIUM_DIPHYLLON','PETUNIA_LONG_TUBE_CLADE','ERICA_CAPE',
    'AQUILEGIA','IOCHROMINAE','IPOMOEA_ASTRIPOMOEINAE','ANTIRRHINEAE',
    'HYDRANGEA_CORNIDIA','LINOIDEAE','SILENE_PHYSOLYCHNIS','EUONYMUS',
    'NICOTIANA','LINANTHUS','ACER','DALECHAMPIA'
}
HIGH_PRIOR_ART = {'AQUILEGIA','IOCHROMINAE','IPOMOEA_ASTRIPOMOEINAE','ACER','DALECHAMPIA'}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--registry', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()

    with a.registry.open(newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            raise SystemExit('missing header')
        missing = REQUIRED.difference(reader.fieldnames)
        if missing:
            raise SystemExit(f'missing columns: {sorted(missing)}')
        rows = list(reader)

    ids = [r['clade_id'] for r in rows]
    if len(ids) != len(set(ids)):
        raise SystemExit('duplicate clade_id')
    missing_clades = REQUIRED_CLADES.difference(ids)
    if missing_clades:
        raise SystemExit(f'missing required control/anchor clades: {sorted(missing_clades)}')

    anchors = [r for r in rows if r['white_like_anchor_status'] == 'ANCHOR']
    if [r['clade_id'] for r in anchors] != ['CAMELLIA']:
        raise SystemExit('only Camellia may be a complete anchor at v0.5')

    for r in rows:
        if not r['key_reference'].strip():
            raise SystemExit(f"{r['clade_id']}: missing key_reference")
        if r['clade_id'] in HIGH_PRIOR_ART and r['prior_art_risk'] not in {'HIGH','VERY_HIGH'}:
            raise SystemExit(f"{r['clade_id']}: prior-art risk understated")

    lin = next(r for r in rows if r['clade_id'] == 'LINANTHUS')
    if lin['key_reference'] != '10.1002/ajb2.70005':
        raise SystemExit('Linanthus reference must use the 2025 complete-sampling phylogeny')
    if 'LIKELY_ANCESTRAL' not in lin['ancestral_baseline']:
        raise SystemExit('Linanthus must retain updated ancestral polymorphism framing')

    pet = next(r for r in rows if r['clade_id'] == 'PETUNIA_LONG_TUBE_CLADE')
    if pet['white_like_anchor_status'] != 'PARTIAL_WHITE_LIKE_SUBCLADE':
        raise SystemExit('Petunia must remain a two-regain partial subclade, not a complete anchor')

    hyd = next(r for r in rows if r['clade_id'] == 'HYDRANGEA_CORNIDIA')
    if hyd['primary_role'] != 'TRANSITION_DIRECTION_FALSIFICATION':
        raise SystemExit('Hydrangea directional falsification role drifted')

    roles = Counter(r['primary_role'] for r in rows)
    white_macro = sum(r['white_like_anchor_status'] in {'ANCHOR','MACRO_ONLY','HOLD','PARTIAL_WHITE_LIKE_SUBCLADE'} for r in rows)
    molecular_controls = sum(any(x in r['primary_role'] for x in ('MECHANISTIC','REPEATABILITY','CONVERGENCE','IMPLEMENTATION','POSITIVE_CONTROL')) for r in rows)

    summary = {
        'version': 'v0.5',
        'rows': len(rows),
        'complete_anchor_count': len(anchors),
        'complete_anchor': anchors[0]['clade_id'],
        'second_complete_anchor_gap': 'OPEN',
        'white_like_or_partial_macro_rows': white_macro,
        'molecular_repeatability_control_rows': molecular_controls,
        'unique_primary_roles': len(roles),
        'tiered_architecture_gate': 'PASS',
        'paper1_science_changed': False,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
