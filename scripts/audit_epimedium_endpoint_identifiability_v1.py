#!/usr/bin/env python3
"""Post-endpoint validity audit for Epimedium.

This does not replace or alter the prospectively frozen classifier. It asks a
separate methodological question: did the frozen conditional-permutation
endpoint have any ability to vary under its own null on the frozen topology?
"""
from __future__ import annotations

import csv
import io
import json
from collections import Counter, defaultdict
from pathlib import Path

from Bio import Phylo

ADMISSION = Path('analysis/epimedium_fine_state_admission_v1.json')
ACCESS = Path('analysis/_generated/epimedium_fine_state_access_v1')
ENDPOINT = Path('analysis/_generated/epimedium_fine_state_falsification_v1/result.json')
OUT = Path('analysis/_generated/epimedium_endpoint_identifiability_v1')
INF = 10**9


def parse_ott(label):
    import re
    m = re.search(r'(?:ott)?(\d+)$', str(label or '').strip("'"))
    return int(m.group(1)) if m else None


def load_tree(adm):
    tr = Phylo.read(io.StringIO((ACCESS/'opentree_raw.nwk').read_text()), 'newick')
    by = {int(x['ott_id']): x['taxon'] for x in adm['taxa']}
    for tip in tr.get_terminals():
        tip.name = by[parse_ott(tip.name)]
    return tr


def sankoff(tree, mapping, alphabet):
    states = list(alphabet)
    dp = {}
    for clade in tree.find_clades(order='postorder'):
        if clade.is_terminal():
            if clade.name in mapping:
                obs = mapping[clade.name]
                dp[id(clade)] = [0 if s == obs else INF for s in states]
            else:
                dp[id(clade)] = [0]*len(states)
        else:
            vals = []
            for i, _ in enumerate(states):
                total = 0
                for child in clade.clades:
                    cc = dp[id(child)]
                    total += min(cc[j] + (0 if i == j else 1) for j in range(len(states)))
                vals.append(total)
            dp[id(clade)] = vals
    return min(dp[id(tree.root)])


def deterministic_extremes(rows, coarse):
    """Generate topology-blind deterministic rearrangements within coarse groups."""
    groups = defaultdict(list)
    base = {r['taxon']: r['joint'] for r in rows}
    for r in rows:
        groups[r[coarse]].append(r['taxon'])
    out = []
    for mode in ('reverse','rotate1','sorted_labels','reverse_labels'):
        m = dict(base)
        for g in sorted(groups):
            names = sorted(groups[g])
            vals = [base[n] for n in names]
            if mode == 'reverse':
                vals = list(reversed(vals))
            elif mode == 'rotate1':
                vals = vals[1:]+vals[:1] if vals else vals
            elif mode == 'sorted_labels':
                vals = sorted(vals)
            elif mode == 'reverse_labels':
                vals = sorted(vals, reverse=True)
            for n,v in zip(names, vals):
                m[n] = v
        out.append((mode,m))
    return out


def tree_resolution(tree):
    internal = [c for c in tree.get_nonterminals()]
    child_counts = Counter(len(c.clades) for c in internal)
    return {
        'n_tips': len(tree.get_terminals()),
        'n_internal_nodes': len(internal),
        'internal_child_count_distribution': dict(sorted(child_counts.items())),
        'n_binary_internal': child_counts.get(2,0),
        'n_polytomous_internal_gt2': sum(v for k,v in child_counts.items() if k>2),
        'max_internal_degree': max(child_counts) if child_counts else 0,
    }


def audit_subset(tree, rows, name):
    alphabet = tuple(sorted({r['joint'] for r in rows}))
    base = {r['taxon']: r['joint'] for r in rows}
    obs = sankoff(tree, base, alphabet)
    result = {'subset': name, 'n': len(rows), 'observed': obs, 'directions': {}}
    for coarse in ('sepal','spur'):
        scores = []
        arrangements = []
        for mode,m in deterministic_extremes(rows, coarse):
            s = sankoff(tree,m,alphabet)
            scores.append(s)
            arrangements.append({'mode':mode,'score':s})
        result['directions'][coarse] = {
            'deterministic_rearrangements': arrangements,
            'score_min': min(scores),
            'score_max': max(scores),
            'score_varies': len(set(scores))>1,
        }
    return result


def main():
    adm = json.loads(ADMISSION.read_text())
    endpoint = json.loads(ENDPOINT.read_text())
    tree = load_tree(adm)
    rows = list(adm['taxa'])

    # Rebuild sensitivity subsets exactly as frozen, without reading endpoint scores.
    xwalk = list(csv.DictReader((ACCESS/'source_rebuild'/'s9_s1_s4_crosswalk.csv').open()))
    elig = {r['taxon_normalized'] for r in xwalk
            if (r['join_status']=='EXACT_ID_AND_TAXON' or r['join_status'].startswith('EXPLICIT_'))
            and str(r['s4_code_agreement']).lower()=='true'}
    s9 = [r for r in rows if r['taxon'] in elig]

    src = list(csv.DictReader((ACCESS/'source_rebuild'/'source_taxon_summary.csv').open()))
    counts = {r['taxon_normalized']: int(r['source_rows']) for r in src}
    ranked = sorted([r['taxon'] for r in rows], key=lambda n:(-counts[n],n))
    rem = set(ranked[:5])
    del5 = [r for r in rows if r['taxon'] not in rem]

    audits = [audit_subset(tree, rows, 'primary36'), audit_subset(tree,s9,'S9'), audit_subset(tree,del5,'delete5')]
    endpoint_nulls = {
        'primary_sepal': [endpoint['primary']['sepal_conditioned']['null_min'], endpoint['primary']['sepal_conditioned']['null_max']],
        'primary_spur': [endpoint['primary']['spur_conditioned']['null_min'], endpoint['primary']['spur_conditioned']['null_max']],
        'S9_sepal': [endpoint['sensitivities']['S1_source_S9_ingroup']['sepal_conditioned']['null_min'], endpoint['sensitivities']['S1_source_S9_ingroup']['sepal_conditioned']['null_max']],
        'S9_spur': [endpoint['sensitivities']['S1_source_S9_ingroup']['spur_conditioned']['null_min'], endpoint['sensitivities']['S1_source_S9_ingroup']['spur_conditioned']['null_max']],
        'delete5_sepal': [endpoint['sensitivities']['S2_delete_five_largest_source_row_taxa']['sepal_conditioned']['null_min'], endpoint['sensitivities']['S2_delete_five_largest_source_row_taxa']['sepal_conditioned']['null_max']],
        'delete5_spur': [endpoint['sensitivities']['S2_delete_five_largest_source_row_taxa']['spur_conditioned']['null_min'], endpoint['sensitivities']['S2_delete_five_largest_source_row_taxa']['spur_conditioned']['null_max']],
    }
    all_null_degenerate = all(a==b for a,b in endpoint_nulls.values())
    all_deterministic_invariant = all(not d['score_varies'] for a in audits for d in a['directions'].values())
    validity = 'NON_IDENTIFIABLE_DEGENERATE_NULL' if all_null_degenerate and all_deterministic_invariant else 'VARIATION_PRESENT'
    out = {
        'analysis_id':'epimedium_endpoint_identifiability_v1',
        'prospective_classifier_preserved': endpoint['classification'],
        'tree_resolution': tree_resolution(tree),
        'endpoint_null_ranges': endpoint_nulls,
        'all_endpoint_nulls_degenerate': all_null_degenerate,
        'deterministic_rearrangement_audits': audits,
        'all_tested_rearrangements_score_invariant': all_deterministic_invariant,
        'validity_classification': validity,
        'counts_as_biological_refutation': False if validity=='NON_IDENTIFIABLE_DEGENERATE_NULL' else None,
        'reason': 'A conditional randomization test whose statistic is invariant over its admissible rearrangement space cannot distinguish phylogenetic organization from the frozen null. The prospective classifier is retained as an audit artifact but is not promoted to a biological counterexample when the endpoint has zero randomization support.' if validity=='NON_IDENTIFIABLE_DEGENERATE_NULL' else 'At least one admissible rearrangement changes the score; inspect further before biological interpretation.'
    }
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'result.json').write_text(json.dumps(out,indent=2)+'\n')
    print('EPIMEDIUM_IDENTIFIABILITY='+json.dumps(out,separators=(',',':')))

if __name__=='__main__':
    main()
