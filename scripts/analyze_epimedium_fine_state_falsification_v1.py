#!/usr/bin/env python3
"""Execute the prospectively frozen Epimedium organ-joint fine-state endpoint."""
from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import random
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path

from Bio import Phylo

ADMISSION = Path('analysis/epimedium_fine_state_admission_v1.json')
ACCESS = Path('analysis/_generated/epimedium_fine_state_access_v1')
OUT = Path('analysis/_generated/epimedium_fine_state_falsification_v1')
MASTER_SEED = 20260908
N_PERM = 9999
INF = 10**9


def stable_seed(label: str) -> int:
    b = hashlib.sha256(f'{MASTER_SEED}:{label}'.encode()).digest()
    return int.from_bytes(b[:8], 'big', signed=False)


def empirical_quantile(xs: list[int], q: float) -> float:
    s = sorted(xs)
    if not s:
        raise ValueError('empty quantile input')
    pos = q * (len(s) - 1)
    lo = int(math.floor(pos)); hi = int(math.ceil(pos))
    if lo == hi:
        return float(s[lo])
    w = pos - lo
    return float(s[lo] * (1 - w) + s[hi] * w)


def parse_ott(label: str) -> int | None:
    m = re.search(r'(?:ott)?(\d+)$', str(label or '').strip("'"))
    return int(m.group(1)) if m else None


def load_and_verify():
    adm = json.loads(ADMISSION.read_text(encoding='utf-8'))
    cand = json.loads((ACCESS/'admission_candidate.json').read_text(encoding='utf-8'))
    access = json.loads((ACCESS/'result.json').read_text(encoding='utf-8'))
    if not access.get('access_gate'):
        raise SystemExit('HOLD_OBSERVATION_REGIME: regenerated access gate failed')
    if cand['exact_taxa_n'] != adm['exact_admitted_taxa_n']:
        raise SystemExit('HOLD_OBSERVATION_REGIME: admitted n changed')
    if cand['rejected_taxa'] != adm['rejected_taxa']:
        raise SystemExit('HOLD_OBSERVATION_REGIME: rejected taxon set changed')
    if cand['opentree_raw_newick_sha256'] != adm['opentree_raw_newick_sha256']:
        raise SystemExit('HOLD_OBSERVATION_REGIME: OpenTree topology hash changed')
    if cand['state_rows_sha256'] != adm['state_rows_sha256']:
        raise SystemExit('HOLD_OBSERVATION_REGIME: state-row hash changed')
    # Strict equality of frozen taxon-state-OTT records.
    if cand['exact_taxa'] != adm['taxa']:
        raise SystemExit('HOLD_OBSERVATION_REGIME: admitted taxon-state records changed')
    if adm['exact_admitted_taxa_n'] < 30:
        raise SystemExit('HOLD_OBSERVATION_REGIME: n below frozen minimum')
    return adm


def load_tree(adm: dict):
    raw = (ACCESS/'opentree_raw.nwk').read_text(encoding='utf-8')
    tr = Phylo.read(io.StringIO(raw), 'newick')
    ott_to_taxon = {int(x['ott_id']): x['taxon'] for x in adm['taxa']}
    seen = []
    for tip in tr.get_terminals():
        oid = parse_ott(tip.name)
        if oid not in ott_to_taxon:
            raise SystemExit(f'HOLD_OBSERVATION_REGIME: unexpected tree tip {tip.name}')
        tip.name = ott_to_taxon[oid]
        seen.append(tip.name)
    if len(seen) != len(set(seen)) or set(seen) != {x['taxon'] for x in adm['taxa']}:
        raise SystemExit('HOLD_OBSERVATION_REGIME: frozen tree tip identity mismatch')
    return tr


def sankoff_score(tree, mapping: dict[str, str], state_alphabet: tuple[str, ...]) -> int:
    """Unordered unit-cost Sankoff; tips absent from mapping are ambiguous/missing."""
    states = list(state_alphabet)
    dp = {}
    for clade in tree.find_clades(order='postorder'):
        if clade.is_terminal():
            if clade.name in mapping:
                obs = mapping[clade.name]
                if obs not in states:
                    raise ValueError(f'unknown state {obs}')
                dp[id(clade)] = [0 if s == obs else INF for s in states]
            else:
                dp[id(clade)] = [0 for _ in states]
        else:
            costs = []
            for i, s in enumerate(states):
                total = 0
                for child in clade.clades:
                    cc = dp[id(child)]
                    total += min(cc[j] + (0 if i == j else 1) for j in range(len(states)))
                costs.append(total)
            dp[id(clade)] = costs
    return int(min(dp[id(tree.root)]))


def endpoint(tree, rows: list[dict], coarse_key: str, label: str):
    names = [r['taxon'] for r in rows]
    mapping = {r['taxon']: r['joint'] for r in rows}
    alphabet = tuple(sorted({r['joint'] for r in rows}))
    observed = sankoff_score(tree, mapping, alphabet)
    groups = defaultdict(list)
    for r in rows:
        groups[r[coarse_key]].append(r['taxon'])
    base_values = {g: [mapping[n] for n in ns] for g, ns in groups.items()}
    rng = random.Random(stable_seed(label))
    null = []
    for _ in range(N_PERM):
        perm = dict(mapping)
        for g in sorted(groups):
            ns = sorted(groups[g])
            vals = list(base_values[g])
            rng.shuffle(vals)
            for n, v in zip(ns, vals):
                perm[n] = v
        null.append(sankoff_score(tree, perm, alphabet))
    mean = statistics.fmean(null)
    count_lower = sum(v <= observed for v in null)
    p_lower = (1 + count_lower) / (N_PERM + 1)
    ratio = observed / mean if mean else None
    support = bool(p_lower <= 0.01 and ratio is not None and ratio < 1.0)
    return {
        'label': label,
        'coarse_key': coarse_key,
        'n': len(names),
        'fine_state_counts': dict(sorted(Counter(mapping.values()).items())),
        'coarse_state_counts': dict(sorted(Counter(r[coarse_key] for r in rows).items())),
        'observed_changes': observed,
        'null_mean': mean,
        'null_median': statistics.median(null),
        'null_q025': empirical_quantile(null, 0.025),
        'null_q975': empirical_quantile(null, 0.975),
        'observed_over_null_mean': ratio,
        'p_lower': p_lower,
        'support': support,
        'seed': stable_seed(label),
        'n_permutations': N_PERM,
        'null_min': min(null),
        'null_max': max(null),
    }


def s9_subset(adm: dict):
    p = ACCESS/'source_rebuild'/'s9_s1_s4_crosswalk.csv'
    rows = list(csv.DictReader(p.open(encoding='utf-8')))
    eligible = set()
    for r in rows:
        status = r['join_status']
        agree = str(r['s4_code_agreement']).casefold() == 'true'
        if (status == 'EXACT_ID_AND_TAXON' or status.startswith('EXPLICIT_')) and agree:
            eligible.add(r['taxon_normalized'])
    sub = [x for x in adm['taxa'] if x['taxon'] in eligible]
    joint_n = len({x['joint'] for x in sub})
    sepal_ok = any(sum(y['sepal']==s for y in sub) >= 2 and len({y['joint'] for y in sub if y['sepal']==s}) >= 2 for s in {x['sepal'] for x in sub})
    spur_ok = any(sum(y['spur']==s for y in sub) >= 2 and len({y['joint'] for y in sub if y['spur']==s}) >= 2 for s in {x['spur'] for x in sub})
    gates = {'n_ge_25': len(sub)>=25, 'joint_states_ge_5': joint_n>=5,
             'sepal_retains_fine_variation': sepal_ok, 'spur_retains_fine_variation': spur_ok}
    return sub, gates


def largest_measurement_deletion(adm: dict):
    p = ACCESS/'source_rebuild'/'source_taxon_summary.csv'
    rows = list(csv.DictReader(p.open(encoding='utf-8')))
    counts = {r['taxon_normalized']: int(r['source_rows']) for r in rows}
    admitted = [x['taxon'] for x in adm['taxa']]
    ranked = sorted(admitted, key=lambda n: (-counts[n], n))
    removed = ranked[:5]
    keep = [x for x in adm['taxa'] if x['taxon'] not in set(removed)]
    gates = {'n_ge_30': len(keep)>=30, 'joint_states_ge_5': len({x['joint'] for x in keep})>=5}
    return keep, removed, gates


def classify(a: dict, b: dict) -> str:
    if a['support'] and b['support']:
        return 'SUPPORTIVE_ALIGNMENT'
    if a['support'] != b['support']:
        return 'MIXED'
    if (not a['support'] and not b['support'] and
        a['observed_over_null_mean'] >= 1.0 and b['observed_over_null_mean'] >= 1.0):
        return 'REFUTATION'
    return 'ADVERSE_BUT_NOT_REFUTATION'


def main():
    adm = load_and_verify()
    tree = load_tree(adm)
    rows = list(adm['taxa'])
    primary_a = endpoint(tree, rows, 'sepal', 'SEPAL_CONDITIONED')
    primary_b = endpoint(tree, rows, 'spur', 'SPUR_CONDITIONED')
    classification = classify(primary_a, primary_b)

    sub1, gates1 = s9_subset(adm)
    if all(gates1.values()):
        s1 = {
            'status': 'ADMITTED', 'gates': gates1,
            'sepal_conditioned': endpoint(tree, sub1, 'sepal', 'SEPAL_CONDITIONED_S9'),
            'spur_conditioned': endpoint(tree, sub1, 'spur', 'SPUR_CONDITIONED_S9'),
        }
        s1['classification'] = classify(s1['sepal_conditioned'], s1['spur_conditioned'])
    else:
        s1 = {'status': 'NOT_ADMITTED', 'gates': gates1, 'n': len(sub1)}

    sub2, removed2, gates2 = largest_measurement_deletion(adm)
    if all(gates2.values()):
        s2 = {
            'status': 'ADMITTED', 'removed_taxa': removed2, 'gates': gates2,
            'sepal_conditioned': endpoint(tree, sub2, 'sepal', 'SEPAL_CONDITIONED_LARGEST5_DELETE'),
            'spur_conditioned': endpoint(tree, sub2, 'spur', 'SPUR_CONDITIONED_LARGEST5_DELETE'),
        }
        s2['classification'] = classify(s2['sepal_conditioned'], s2['spur_conditioned'])
    else:
        s2 = {'status': 'NOT_ADMITTED', 'removed_taxa': removed2, 'gates': gates2, 'n': len(sub2)}

    result = {
        'analysis_id': 'epimedium_fine_state_falsification_v1',
        'source_doi': '10.3389/fpls.2023.1234148',
        'classification': classification,
        'n': len(rows),
        'fine_state': 'SepalC:SpurC exact nominal source pair',
        'topology_sha256': adm['opentree_raw_newick_sha256'],
        'state_rows_sha256': adm['state_rows_sha256'],
        'primary': {
            'sepal_conditioned': primary_a,
            'spur_conditioned': primary_b,
        },
        'sensitivities': {
            'S1_source_S9_ingroup': s1,
            'S2_delete_five_largest_source_row_taxa': s2,
            'S3_polytomy_resolution': {'status': 'PROHIBITED_BY_PREFREEZE'},
        },
        'paper1_science_changed': False,
        'interpretation_boundary': 'representation-level organ-joint colour organization; not universal hue direction, ancestry, mechanism, or ecology',
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/'result.json').write_text(json.dumps(result, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    print('EPIMEDIUM_FINE_STATE_RESULT='+json.dumps(result, ensure_ascii=False, separators=(',',':')))

if __name__ == '__main__':
    main()
