#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json
from pathlib import Path

REQUIRED_IDS = {'IOCH_B1_MACRO_LOSS','IOCH_B2_WHITE_MORPH','IOCH_B3_DFR_MORPH','IOCH_B5_TEMPO'}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--contract', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    with a.contract.open(newline='', encoding='utf-8') as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        raise SystemExit('empty Iochrominae benchmark contract')
    ids = {r['benchmark_id'] for r in rows}
    if not REQUIRED_IDS.issubset(ids):
        raise SystemExit(f'missing required hostile benchmarks: {sorted(REQUIRED_IDS - ids)}')
    required = [r for r in rows if r['required_status'] == 'REQUIRED']
    if len(required) < 4:
        raise SystemExit('at least four Iochrominae hostile benchmarks must remain REQUIRED')
    for r in rows:
        if not r['source_doi'].strip() or not r['forbidden_claim'].strip():
            raise SystemExit(f"{r['benchmark_id']}: missing DOI or forbidden claim")
    morph = next(r for r in rows if r['benchmark_id'] == 'IOCH_B2_WHITE_MORPH')
    if 'non-convergence' not in morph['atlas_test']:
        raise SystemExit('within-population vs fixed-species non-convergence benchmark was weakened')
    tempo = next(r for r in rows if r['benchmark_id'] == 'IOCH_B5_TEMPO')
    if 'time axis' not in tempo['forbidden_claim']:
        raise SystemExit('time-axis novelty boundary was weakened')

    summary = {
        'version': 'v0.1',
        'benchmark_rows': len(rows),
        'required_benchmarks': len(required),
        'within_vs_fixed_prior_art_gate': 'LOCKED',
        'time_axis_generic_novelty_gate': 'FORBIDDEN',
        'iochrominae_role': 'MANDATORY_HOSTILE_BENCHMARK',
        'paper1_science_changed': False,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
