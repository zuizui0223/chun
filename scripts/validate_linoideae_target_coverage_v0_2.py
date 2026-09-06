#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--contract', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()

    with a.contract.open(newline='', encoding='utf-8') as fh:
        rows = {r['metric']: r for r in csv.DictReader(fh)}

    def fv(name: str) -> float:
        try:
            return float(rows[name]['value'])
        except KeyError as e:
            raise SystemExit(f'missing metric: {name}') from e
        except ValueError as e:
            raise SystemExit(f'invalid numeric value: {name}') from e

    tips = int(fv('LINOIDEAE_PHYLOGENY_SPECIES'))
    coloured = int(fv('LINOIDEAE_COLOUR_RECORDED_SPECIES'))
    missing = int(fv('EXPECTED_UNCOLOURED_LINOIDEAE_TIPS'))
    raw_cov = fv('RAW_MAX_COLOUR_COVERAGE')
    min_cov = fv('ATLAS_MIN_PROVENANCE_COVERAGE')
    min_rows = int(fv('ATLAS_MIN_PROVENANCE_COMPLETE_ROWS'))
    outgroups = int(fv('OUTGROUP_SPECIES_IN_PHYLOGENETIC_ANALYSIS'))
    states = int(fv('ALLOWED_TERMINAL_COLOUR_STATES'))
    row_policy = int(fv('MATRIX_ROW_POLICY'))

    if tips != 113:
        raise SystemExit('Linoideae target-tip denominator drift')
    if coloured != 112:
        raise SystemExit('source-study colour count drift')
    if tips - coloured != missing or missing != 1:
        raise SystemExit('113/112 missing-tip relationship not preserved')
    expected_cov = coloured / tips
    if not math.isclose(raw_cov, expected_cov, rel_tol=0, abs_tol=1e-10):
        raise SystemExit('raw coverage fraction mismatch')
    if not math.isclose(min_cov, 0.80, rel_tol=0, abs_tol=1e-12):
        raise SystemExit('coverage threshold drift')
    if min_rows != math.ceil(tips * min_cov) or min_rows != 91:
        raise SystemExit('minimum provenance-complete row count mismatch')
    if outgroups != 3:
        raise SystemExit('outgroup count drift')
    if states != 6:
        raise SystemExit('terminal state-count drift')
    if row_policy != tips:
        raise SystemExit('matrix row policy must retain all 113 target tips')

    notes = rows['MATRIX_ROW_POLICY']['notes'].upper()
    if 'UNKNOWN' not in notes or 'NEVER DROPPED' not in notes:
        raise SystemExit('explicit UNKNOWN retention rule missing')

    summary = {
        'version': 'v0.2',
        'linoideae_target_tips': tips,
        'source_colour_species': coloured,
        'expected_source_uncoloured_tips': missing,
        'raw_source_colour_coverage': expected_cov,
        'minimum_provenance_complete_rows': min_rows,
        'denominator_gate': 'PASS',
        'unknown_retention_gate': 'PASS',
        'ancestral_state_reconstruction_gate': 'BLOCKED_PENDING_113_TIP_MATRIX',
        'paper1_science_changed': False,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
