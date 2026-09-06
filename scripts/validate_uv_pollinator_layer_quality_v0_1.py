#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--manifest', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()

    with a.manifest.open(newline='', encoding='utf-8') as fh:
        rows = {r['metric']: r for r in csv.DictReader(fh)}

    def iv(name: str, field: str = 'derived_value') -> int:
        value = rows[name][field]
        if value == '':
            raise SystemExit(f'{name}: empty {field}')
        return int(float(value))

    declared = iv('DECLARED_SPECIES_N')
    white_red = iv('WHITE_RED_RED') + iv('WHITE_RED_WHITE') + iv('WHITE_RED_OTHER')
    yellow = iv('YELLOW_YELLOW') + iv('YELLOW_OTHER')
    uv = iv('UV_MINUS') + iv('UV_PLUS')
    methods_taxonomy = (iv('METHODS_GENERA'), iv('METHODS_FAMILIES'))
    fig_taxonomy = (iv('FIG2_GENERA'), iv('FIG2_FAMILIES'))

    if declared != 245:
        raise SystemExit('declared species count drift')
    if white_red != iv('WHITE_RED_SUM') or white_red == declared:
        raise SystemExit('white-red discrepancy not reproduced')
    if yellow != iv('YELLOW_SUM') or yellow == declared:
        raise SystemExit('yellow discrepancy not reproduced')
    if uv != iv('UV_BINARY_SUM') or uv == declared:
        raise SystemExit('UV discrepancy not reproduced')
    if methods_taxonomy == fig_taxonomy:
        raise SystemExit('taxonomy-count conflict unexpectedly absent')
    if iv('SUPPLEMENT_BINARY_INGESTED') != 0:
        raise SystemExit('supplement cannot be marked ingested in v0.1')
    if iv('ECOLOGY_TIER_ADMISSION') != 0:
        raise SystemExit('ecology layer must remain HOLD until row reconciliation')

    summary = {
        'version': 'v0.1',
        'declared_species_n': declared,
        'white_red_count_sum': white_red,
        'yellow_count_sum': yellow,
        'uv_binary_count_sum': uv,
        'methods_genera_families': methods_taxonomy,
        'figure2_genera_families': fig_taxonomy,
        'count_conflict_gate': 'PASS_CONFLICT_REPRODUCED',
        'supplement_ingestion_gate': 'HOLD',
        'ecology_tier_admission': 'HOLD_COUNT_RECONCILIATION_REQUIRED',
        'paper1_science_changed': False,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
