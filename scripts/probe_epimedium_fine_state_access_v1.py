#!/usr/bin/env python3
"""Signal-free source/topology admission probe for Epimedium fine-state test."""
from __future__ import annotations

import csv
import io
import json
import re
import shutil
from collections import Counter, defaultdict
from pathlib import Path

import requests
from Bio import Phylo

from analyze_epimedium_organ_states_v0_1 import run as build_source

SOURCE = Path('data/atlas_epimedium_ingested_v0_1')
OUT = Path('analysis/_generated/epimedium_fine_state_access_v1')
DERIVED = OUT / 'source_rebuild'
OT = 'https://api.opentreeoflife.org/v3'
UA = 'chun-epimedium-fine-state-access/1.0'


def post(path: str, payload: dict):
    r = requests.post(f'{OT}/{path}', json=payload, headers={'User-Agent': UA}, timeout=120)
    r.raise_for_status()
    return r.json()


def exact_tnrs(names: list[str]):
    data = post('tnrs/match_names', {
        'names': names,
        'do_approximate_matching': False,
        'include_suppressed': False,
    })
    results = data.get('results', [])
    if len(results) != len(names):
        raise SystemExit(f'TNRS cardinality mismatch {len(results)} != {len(names)}')
    out = []
    for q, result in zip(names, results):
        exact = [m for m in result.get('matches', [])
                 if float(m.get('score', 1.0)) >= 0.999999
                 and not bool(m.get('is_approximate_match', False))]
        # Do not rescue synonyms or choose among multiple exact candidates at this stage.
        if len(exact) == 1:
            m = exact[0]; tx = m.get('taxon', {})
            out.append({'query': q, 'status': 'EXACT', 'ott_id': tx.get('ott_id'),
                        'matched_name': tx.get('name', ''), 'is_synonym': bool(m.get('is_synonym', False))})
        else:
            out.append({'query': q, 'status': f'REJECT_{len(exact)}_EXACT_MATCHES', 'ott_id': None,
                        'candidates': [{'ott_id': m.get('taxon', {}).get('ott_id'),
                                        'matched_name': m.get('taxon', {}).get('name', ''),
                                        'is_synonym': bool(m.get('is_synonym', False))}
                                       for m in exact]})
    return out


def main():
    if OUT.exists(): shutil.rmtree(OUT)
    DERIVED.mkdir(parents=True)

    summary = build_source(SOURCE, DERIVED)
    taxon_csv = DERIVED / 'source_taxon_summary.csv'
    rows = list(csv.DictReader(taxon_csv.open(encoding='utf-8')))
    named = [r for r in rows if r['taxon_normalized'] != 'Epimedium sp1']
    if len(named) != 41:
        raise SystemExit(f'expected 41 named source taxa, got {len(named)}')
    if any(str(r['within_source_taxon_code_variation']).casefold() not in {'false','0'} for r in named):
        raise SystemExit('source taxon code variation unexpectedly present')
    joint = Counter(r['joint_codes'] for r in named)
    sepals = Counter(r['sepal_codes'] for r in named)
    spurs = Counter(r['spur_codes'] for r in named)
    if len(joint) != 7 or len(sepals) != 4 or len(spurs) != 5:
        raise SystemExit(f'source state-space drift joint={len(joint)} sepal={len(sepals)} spur={len(spurs)}')

    names = [r['taxon_normalized'] for r in named]
    matches = exact_tnrs(names)
    by_ott = defaultdict(list)
    for m in matches:
        if m['status'] == 'EXACT' and m['ott_id'] is not None:
            by_ott[int(m['ott_id'])].append(m)
    collisions = {oid: xs for oid, xs in by_ott.items() if len(xs) > 1}
    collision_queries = {x['query'] for xs in collisions.values() for x in xs}
    for m in matches:
        if m['query'] in collision_queries:
            m['status'] = 'REJECT_OTT_COLLISION'

    admitted = [m for m in matches if m['status'] == 'EXACT' and m['ott_id'] is not None]
    ids = sorted(int(m['ott_id']) for m in admitted)
    tree_overlap = []
    tree_newick = ''
    if ids:
        sub = post('tree_of_life/induced_subtree', {'ott_ids': ids, 'label_format': 'id'})
        tree_newick = sub.get('newick', '')
        if not tree_newick:
            raise SystemExit('OpenTree returned empty induced subtree')
        tr = Phylo.read(io.StringIO(tree_newick), 'newick')
        for tip in tr.get_terminals():
            label = str(tip.name or '').strip("'")
            mm = re.search(r'(?:ott)?(\d+)$', label)
            if mm: tree_overlap.append(int(mm.group(1)))
    overlap = set(ids) & set(tree_overlap)
    coverage = len(overlap) / len(names)

    # State availability among exactly admitted source taxa only; still no tree signal.
    admitted_queries = {m['query'] for m in admitted if int(m['ott_id']) in overlap}
    admitted_rows = [r for r in named if r['taxon_normalized'] in admitted_queries]
    joint_adm = Counter(r['joint_codes'] for r in admitted_rows)
    sepal_adm = Counter(r['sepal_codes'] for r in admitted_rows)
    spur_adm = Counter(r['spur_codes'] for r in admitted_rows)
    fine_within_sepal = {s: len({r['joint_codes'] for r in admitted_rows if r['sepal_codes'] == s}) for s in sepal_adm}
    fine_within_spur = {s: len({r['joint_codes'] for r in admitted_rows if r['spur_codes'] == s}) for s in spur_adm}

    gates = {
        'source_rebuild_passed': True,
        'exact_tree_n_ge_30': len(overlap) >= 30,
        'exact_tree_coverage_ge_80pct': coverage >= 0.80,
        'joint_states_ge_5': len(joint_adm) >= 5,
        'sepal_has_conditioning_group_n_ge_8_with_ge_2_joint_states': any(sepal_adm[s] >= 8 and fine_within_sepal[s] >= 2 for s in sepal_adm),
        'spur_has_conditioning_group_n_ge_8_with_ge_2_joint_states': any(spur_adm[s] >= 8 and fine_within_spur[s] >= 2 for s in spur_adm),
    }
    result = {
        'source_doi': '10.3389/fpls.2023.1234148',
        'source_workbook_sha256': summary['source_workbook_sha256'],
        'named_source_taxa': 41,
        'source_joint_state_count': len(joint),
        'source_sepal_state_count': len(sepals),
        'source_spur_state_count': len(spurs),
        'tnrs_status_counts': dict(Counter(m['status'] for m in matches)),
        'rejected_queries': [m for m in matches if m['status'] != 'EXACT'],
        'ott_collision_groups': {str(k): [x['query'] for x in v] for k,v in collisions.items()},
        'exact_admitted_before_tree': len(ids),
        'induced_tree_overlap_n': len(overlap),
        'coverage_fraction': coverage,
        'admitted_joint_state_counts': dict(sorted(joint_adm.items())),
        'admitted_sepal_state_counts': dict(sorted(sepal_adm.items())),
        'admitted_spur_state_counts': dict(sorted(spur_adm.items())),
        'fine_states_within_sepal': fine_within_sepal,
        'fine_states_within_spur': fine_within_spur,
        'gates': gates,
        'access_gate': all(gates.values()),
        'endpoint_prefrozen': False,
        'sankoff_computed': False,
        'permutation_test_computed': False,
    }
    (OUT/'result.json').write_text(json.dumps(result, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    (OUT/'tnrs_matches.json').write_text(json.dumps(matches, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    if tree_newick:
        (OUT/'opentree_raw.nwk').write_text(tree_newick+'\n', encoding='utf-8')
    print('EPIMEDIUM_FINE_STATE_ACCESS='+json.dumps(result, ensure_ascii=False))

if __name__ == '__main__': main()
