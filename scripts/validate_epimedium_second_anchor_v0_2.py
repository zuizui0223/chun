#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json
from pathlib import Path


def read_csv(path: Path):
    with path.open(newline='', encoding='utf-8') as fh:
        return list(csv.DictReader(fh))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--evidence', type=Path, required=True)
    ap.add_argument('--modules', type=Path, required=True)
    ap.add_argument('--gates', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()

    evidence = read_csv(a.evidence)
    modules = read_csv(a.modules)
    gates = read_csv(a.gates)
    if not evidence or not modules or not gates:
        raise SystemExit('empty Epimedium contract input')

    by_id = {r['evidence_id']: r for r in evidence}
    required_evidence = {'EPI_2023_HPLC_QPCR','EPI_2024_CRA014550','EPI_2023_GBS_PHYLOGENY'}
    if not required_evidence.issubset(by_id):
        raise SystemExit('missing required evidence rows')
    if by_id['EPI_2024_CRA014550']['raw_accession'] != 'CRA014550':
        raise SystemExit('CRA014550 accession drift')
    if '2_TO_4' not in by_id['EPI_2023_HPLC_QPCR']['dependence_status']:
        raise SystemExit('historical dependence interval must remain 2-4')

    mandatory = {r['module_id'] for r in modules if r['mandatory'].lower() == 'yes'}
    if mandatory != {'PG','A','F'}:
        raise SystemExit(f'mandatory module drift: {mandatory}')
    y = next((r for r in modules if r['module_id'] == 'Y'), None)
    if y is None or 'CHEMISTRY_UNRESOLVED' not in y['visible_state_rule']:
        raise SystemExit('yellow chemistry must remain unresolved by visible hue alone')

    gate = {r['gate_id']: r for r in gates}
    if gate['EPI_G1_TRANSITION_INDEPENDENCE']['current_status'] != 'NOT_YET_MET':
        raise SystemExit('historical transition gate must remain NOT_YET_MET')
    if gate['EPI_G2_RAW_FLORAL_STATE']['current_status'] != 'REMOTE_DATA_VERIFIED_PENDING_INGESTION':
        raise SystemExit('raw state gate drift')
    if gate['EPI_G5_EXTERNAL_GENERALITY']['current_status'] != 'BLOCKED':
        raise SystemExit('external generality must remain blocked')

    summary = {
        'version': 'v0.2',
        'evidence_rows': len(evidence),
        'mandatory_modules': sorted(mandatory),
        'historical_transition_clusters': '2-4 identified set',
        'historical_transition_gate': 'NOT_YET_MET',
        'raw_flower_accession': 'CRA014550',
        'raw_remeasurement_gate': 'PENDING_INGESTION',
        'external_generality_gate': 'BLOCKED',
        'paper1_science_changed': False,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
