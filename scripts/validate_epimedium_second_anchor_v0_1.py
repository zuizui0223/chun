#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--panel', type=Path, required=True)
    ap.add_argument('--dependence', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()

    with a.panel.open(newline='', encoding='utf-8') as fh:
        panel = list(csv.DictReader(fh))
    with a.dependence.open(newline='', encoding='utf-8') as fh:
        dep = list(csv.DictReader(fh))

    if len(panel) != 8:
        raise SystemExit(f'expected 8 panel taxa, found {len(panel)}')
    if len({r['taxon_accepted'] for r in panel}) != 8:
        raise SystemExit('accepted taxa are not unique')
    if not any(r['taxon_raw'] == 'Epimedium epstenii' and r['taxon_accepted'] == 'Epimedium epsteinii' for r in panel):
        raise SystemExit('E. epstenii -> E. epsteinii crosswalk missing')

    aminus = [r for r in panel if r['A_status'] == 'A_MINUS']
    aplus = [r for r in panel if r['A_status'] == 'A_PLUS']
    if len(aminus) != 4 or len(aplus) != 4:
        raise SystemExit('panel must retain 4 A-minus and 4 A-plus species')
    if any(r['hplc_anthocyanin'] != 'NOT_DETECTED' for r in aminus):
        raise SystemExit('all A-minus species must retain HPLC NOT_DETECTED state')
    if any(r['ANS_state'] != 'LOW' for r in aminus):
        raise SystemExit('ANS shared-core gate failed')

    dfr_low = sum(r['DFR_state'] == 'LOW' for r in aminus)
    chs_low = sum(r['CHS_state'] in {'CHS1_LOW', 'CHS2_LOW'} for r in aminus)
    fls_div = sum(r['FLS_state'] == 'INCREASED_WITH_LOW_DFR' for r in aminus)
    if (dfr_low, chs_low, fls_div) != (3, 2, 2):
        raise SystemExit(f'molecular qualitative counts drifted: {(dfr_low, chs_low, fls_div)}')

    broad = []
    copy_aware = []
    for r in aminus:
        chs_any = 'LOW' if r['CHS_state'] in {'CHS1_LOW', 'CHS2_LOW'} else 'NOT_LOW'
        fls = 'DIVERSION_HIGH' if r['FLS_state'] == 'INCREASED_WITH_LOW_DFR' else 'OTHER'
        broad.append((r['ANS_state'], r['DFR_state'], chs_any, fls))
        copy_aware.append((r['ANS_state'], r['DFR_state'], r['CHS_state'], fls))
    max_broad = max(Counter(broad).values())
    max_copy = max(Counter(copy_aware).values())
    if max_broad != 2 or max_copy != 1:
        raise SystemExit(f'signature recurrence diagnostic drifted: broad={max_broad}, copy={max_copy}')

    dep_minus = [r for r in dep if r['A_status'] == 'A_MINUS']
    if len(dep_minus) != 4:
        raise SystemExit('dependence table must contain four A-minus taxa')
    if any(r['robust_event_independence'] != 'UNRESOLVED' for r in dep_minus):
        raise SystemExit('historical event independence must remain unresolved at v0.1')

    summary = {
        'version': 'v0.1',
        'panel_taxa': 8,
        'A_minus_taxa': 4,
        'A_plus_taxa': 4,
        'A_minus_anthocyanin_not_detected': 4,
        'ANS_low': 4,
        'DFR_low': dfr_low,
        'CHS_copy_specific_low': chs_low,
        'FLS_diversion_high': fls_div,
        'max_broad_signature_recurrence': f'{max_broad}/4',
        'max_copy_aware_signature_recurrence': f'{max_copy}/4',
        'observation_regime': 'COMMON_12_GENE_CANDIDATE_PANEL',
        'mechanistic_common_panel_gate': 'PASS',
        'historical_event_independence_gate': 'FAIL_HOLD',
        'paper1_science_changed': False,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
