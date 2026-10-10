#!/usr/bin/env python3
"""Retrospective, pre-declared nested biochemical/regulatory memory test.

Only run on SHA-verified Wheeler et al 2023 Petunieae frozen OSF source.
Do not interpret conditional expression phylogenetic structure as molecular causation.
"""
from __future__ import annotations
import argparse
import collections
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from Bio import Phylo
from scipy.stats import rankdata


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def zscale_log(values: np.ndarray, multiplier: float) -> tuple[np.ndarray, list[str]]:
    raw = np.asarray(values, dtype=float)
    if not np.isfinite(raw).all() or np.any(raw < 0):
        raise ValueError('non-finite or negative source measurement')
    x = np.log1p(multiplier * raw)
    mean = x.mean(axis=0)
    sd = x.std(axis=0, ddof=0)
    zeros = [str(j) for j in np.flatnonzero(sd == 0)]
    z = np.zeros_like(x)
    good = sd != 0
    z[:, good] = (x[:, good] - mean[good]) / sd[good]
    return z, zeros


def fine_sixbit(df: pd.DataFrame, cols: list[str]) -> list[str]:
    x = df[cols].to_numpy(dtype=float)
    if not np.isfinite(x).all() or np.any(x < 0):
        raise ValueError('bad pigment profile')
    return [''.join('1' if v > 0 else '0' for v in row) for row in x]


def within_state_pairs(states: list[str]) -> tuple[np.ndarray, np.ndarray]:
    ii, jj = np.triu_indices(len(states), 1)
    s = np.asarray(states)
    mask = s[ii] == s[jj]
    return ii[mask], jj[mask]


def spearman_precomputed(x_ranks: np.ndarray, y: np.ndarray) -> float:
    ry = rankdata(y, method='average')
    xd = x_ranks - np.mean(x_ranks)
    yd = ry - np.mean(ry)
    denom = np.sqrt(float(np.dot(xd, xd) * np.dot(yd, yd)))
    if denom == 0:
        return float('nan')
    return float(np.dot(xd, yd) / denom)


def conditional_memory(
    distances: np.ndarray,
    vectors: np.ndarray,
    fine: list[str],
    *,
    permutations: int,
    seed: int,
    leave_one_out: bool = False,
) -> dict:
    ii, jj = within_state_pairs(fine)
    if len(ii) < 10:
        raise ValueError('insufficient same-fine pairs')
    x = np.asarray(vectors, dtype=float)
    if x.shape[0] != len(fine) or distances.shape != (len(fine), len(fine)):
        raise ValueError('tip/measurement misalignment')
    d = distances[ii, jj]
    dx = rankdata(d, method='average')

    def observed_stat(vectors: np.ndarray) -> float:
        y = np.sqrt(np.mean((vectors[ii] - vectors[jj]) ** 2, axis=1))
        return spearman_precomputed(dx, y)

    observed = observed_stat(x)
    if not np.isfinite(observed):
        raise ValueError('undefined correlation')

    rng = np.random.default_rng(seed)
    labels = np.asarray(fine)
    groups = [np.flatnonzero(labels == c) for c in sorted(set(fine))]
    null = np.empty(permutations, dtype=float)
    for b in range(permutations):
        p = np.arange(len(fine))
        for group in groups:
            p[group] = rng.permutation(group)
        null[b] = observed_stat(x[p])
    if not np.isfinite(null).all():
        raise ValueError('undefined null statistic')
    answer = {
        'same_fine_unordered_pairs': int(len(ii)),
        'rho': observed,
        'null_mean_rho': float(null.mean()),
        'null_q025': float(np.quantile(null, .025)),
        'null_q975': float(np.quantile(null, .975)),
        'p_one_sided': float((1 + np.count_nonzero(null >= observed)) / (permutations + 1)),
        'n_permutations': permutations,
        'random_seed': seed,
    }
    if leave_one_out:
        loo = []
        for excluded in range(len(fine)):
            keep = np.arange(len(fine)) != excluded
            dk = distances[np.ix_(keep, keep)]
            fk = np.asarray(fine)[keep]
            xk = x[keep]
            a, b = within_state_pairs(fk.tolist())
            y = np.sqrt(np.mean((xk[a] - xk[b]) ** 2, axis=1))
            loo.append(spearman_precomputed(rankdata(dk[a, b], method='average'), y))
        answer['leave_one_tip_out'] = {
            'n': len(loo),
            'positive_count': sum(v > 0 for v in loo),
            'min_rho': float(min(loo)),
            'median_rho': float(np.median(loo)),
            'max_rho': float(max(loo)),
        }
    return answer


def analyze(source: Path, design_path: Path, permutations_override: int | None = None) -> dict:
    design = json.loads(design_path.read_text(encoding='utf-8'))
    spec = design['source']
    table = source / spec['processed_csv_path']
    treefile = source / spec['tree_path']
    script = source / 'processed/phyloCCA__phyloCCA_expression_HPLC-with-flavs-final.r'
    expected = [(table, 'processed_csv_sha256'), (treefile, 'tree_sha256'), (script, 'source_script_sha256')]
    for path, key in expected:
        if not path.is_file() or sha256(path) != spec[key]:
            raise ValueError(f'frozen identity mismatch: {key}')
    manifest = json.loads((source / 'source_manifest.json').read_text(encoding='utf-8'))
    if manifest['authoritative_prefix'] != 'phyloCCA' or manifest['required_duplicate_identity'] != 'PASS_PHYLOCCA_PHYLOPCA_CSV_AND_TREE_OSF_METADATA_IDENTICAL':
        raise ValueError('source manifest identity drift')
    df = pd.read_csv(table)
    if len(df) != design['frame']['source_rows'] or df['key_0'].duplicated().any():
        raise ValueError('source row count or identity drift')
    if int((df['key_0'] == design['frame']['source_outgroup']).sum()) != 1:
        raise ValueError('outgroup missing')
    tree = Phylo.read(str(treefile), 'newick')
    tips = [t.name for t in tree.get_terminals()]
    if len(tips) != 60 or set(tips) != set(df['key_0']):
        raise ValueError('tree/source key mismatch')
    df = df.set_index('key_0').loc[[t for t in tips if t != 'BROW']]
    six = design['frame']['fine_six_compounds_order']
    fine = fine_sixbit(df, six)
    counts = collections.Counter(fine)
    admitted = [i for i, s in enumerate(fine) if counts[s] >= 5]
    df = df.iloc[admitted]
    fine = [fine[i] for i in admitted]
    counts = collections.Counter(fine)
    if len(fine) != 47 or len(counts) != 6:
        raise ValueError(f'rare fine state gate failed {len(fine)} tips, {len(counts)} fine codes')
    coarse = collections.Counter('1' if '1' in code else '0' for code in fine)
    if dict(sorted(coarse.items())) != design['frame']['coarse_counts_expected']:
        raise ValueError(f'coarse gate drift {coarse}')
    labels = list(df.index)
    n = len(labels)
    ii, jj = within_state_pairs(fine)
    if len(ii) != design['frame']['same_fine_unordered_pairs_expected']:
        raise ValueError(f'same-state pair support drift {len(ii)}')
    distance = np.zeros((n, n), dtype=float)
    terminals = {t.name: t for t in tree.get_terminals()}
    for i in range(n):
        for j in range(i + 1, n):
            d = float(tree.distance(terminals[labels[i]], terminals[labels[j]]))
            distance[i, j] = distance[j, i] = d
    if np.any(distance[ii, jj] <= 0):
        raise ValueError('nonpositive tree distances')
    genes = design['primary']['raw_gene_expression_columns']
    expr, expr_zero = zscale_log(df[genes].to_numpy(dtype=float), 1.0)
    pigment, pig_zero = zscale_log(df[design['secondary']['pigment_columns']].to_numpy(dtype=float), 100.0)
    pri = design['primary']
    permutations = pri['permutations'] if permutations_override is None else permutations_override
    primary = conditional_memory(
        distance, expr, fine, permutations=permutations, seed=pri['random_seed'],
        leave_one_out=True
    )
    secondary = conditional_memory(
        distance, pigment, fine, permutations=permutations,
        seed=design['secondary']['statistic_seed'] if 'statistic_seed' in design['secondary'] else 20261009,
        leave_one_out=False
    )
    supported = primary['rho'] > 0 and primary['p_one_sided'] <= 0.05
    return {
        'version': 'v0.1',
        'analysis_role': 'RETROSPECTIVE_PREDECLARED_TEST_PETUNIEAE_ONE_RADIATION',
        'design_commit': '91b10bede74ead47953b7a838adf64d95c59b7ed',
        'source_hash_verified': True,
        'source_article_doi': spec['article_doi'],
        'retained_tips': n,
        'fine_state_counts': dict(sorted(counts.items())),
        'coarse_state_counts': dict(sorted(coarse.items())),
        'expression_feature_count': len(genes),
        'pigment_feature_count': len(design['secondary']['pigment_columns']),
        'zero_variance_expression_columns': [genes[int(i)] for i in expr_zero],
        'zero_variance_pigment_columns': [design['secondary']['pigment_columns'][int(i)] for i in pig_zero],
        'primary_conditional_expression_memory': {
            **primary, 'status': 'POSITIVE_EXPLORATORY' if supported else 'NOT_SUPPORTED'
        },
        'secondary_conditional_pigment_concentration_memory': secondary,
        'interpretation_boundary': [
            'Retrospective source, one radiation; not independent prospective replication',
            'Same fine code refers to six-anthocyanidin presence bits, not identical pigment concentration or exact visible flower hue',
            'Whole-vector within-fine taxon permutations preserve expression covariance but assume exchangeability within fine code under no conditional phylogenetic structure',
            'A positive result is phylogenetic organization of expression within an identical pigment-presence class, not proof that a molecular implementation caused color memory decay',
            'Secondary pigment magnitude result is exploratory; raw rho difference between expression and pigments is not a tested difference in memory rates',
            'Original AJB and EL scientific freezes are unchanged',
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--design', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--permutations', type=int, default=None)
    a = p.parse_args()
    result = analyze(a.source, a.design, a.permutations)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
