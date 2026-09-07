#!/usr/bin/env python3
"""Conditional two-state Mk reanalysis of recovered Cornidia observations.

Trees are independent ML estimates from public nuclear alignments. Branch
lengths are substitutions/site, NOT elapsed years. Expected histories integrate
ancestral states/jumps conditional on each fitted Q and tree, not Q uncertainty.
"""
from __future__ import annotations
import argparse
import copy
import csv
import json
from collections import defaultdict
from pathlib import Path
import numpy as np
from Bio import Phylo
from scipy.linalg import expm
from scipy.optimize import minimize

SEED = 20260907


def transition(a: float, b: float, t: float) -> np.ndarray:
    s = a + b
    off = -np.expm1(-s * t)
    return np.array([[1 - a / s * off, a / s * off],
                     [b / s * off, 1 - b / s * off]])


class BinaryMk:
    def __init__(self, tree, states: dict[str, int]):
        self.tree = tree
        self.nodes = list(tree.find_clades(order='postorder'))
        self.index = {id(n): i for i, n in enumerate(self.nodes)}
        self.children = [[self.index[id(c)] for c in n.clades] for n in self.nodes]
        tips = tree.get_terminals()
        names = [n.name for n in tips]
        if len(names) != len(set(names)) or set(names) != set(states):
            raise ValueError('tree/trait tips must match one-to-one')
        if any(x not in (0, 1) for x in states.values()) or set(states.values()) != {0, 1}:
            raise ValueError('two observed states are required; no invented purple state')
        lengths = [n.branch_length for n in self.nodes[:-1]]
        if any(t is None or not np.isfinite(t) or t < 0 for t in lengths):
            raise ValueError('branch lengths must be finite and nonnegative')
        self.scale = max(tree.depths().values())
        if self.scale <= 0:
            raise ValueError('zero tree depth')
        self.t = np.array([(n.branch_length or 0) / self.scale for n in self.nodes])
        self.t[-1] = 0
        self.leaves = {self.index[id(n)]: states[n.name] for n in tips}
        self.n = len(self.nodes)

    def calculate(self, a: float, b: float, prior: str = 'equal', details=False):
        if a <= 0 or b <= 0 or prior not in ('equal', 'stationary'):
            raise ValueError('positive rates and explicit supported prior required')
        s = a + b
        off = -np.expm1(-s * self.t)
        p = np.empty((self.n, 2, 2))
        p[:, 0, 0] = 1 - a / s * off
        p[:, 0, 1] = a / s * off
        p[:, 1, 0] = b / s * off
        p[:, 1, 1] = 1 - b / s * off
        d = np.ones((self.n, 2))
        msg = np.ones_like(d)
        log_scale = 0.0
        for i in range(self.n):
            if i in self.leaves:
                d[i] = [float(self.leaves[i] == 0), float(self.leaves[i] == 1)]
            else:
                for c in self.children[i]:
                    d[i] *= msg[c]
                z = d[i].sum()
                if z <= 0:
                    return (-np.inf, None) if details else -np.inf
                d[i] /= z
                log_scale += np.log(z)
            msg[i] = p[i] @ d[i]
        pi = np.array([0.5, 0.5]) if prior == 'equal' else np.array([b / s, a / s])
        root_post = pi * d[-1]
        ll = np.log(root_post.sum()) + log_scale
        root_post /= root_post.sum()
        if not details:
            return float(ll)
        outside = np.zeros_like(d)
        outside[-1] = pi
        q = np.array([[-a, a], [b, -b]])
        bases = []
        for i, j in ((0, 1), (1, 0), (0, 0), (1, 1)):
            B = np.zeros((2, 2))
            B[i, j] = q[i, j] if i != j else 1.0
            block = np.zeros((4, 4))
            block[:2, :2] = block[2:, 2:] = q
            block[:2, 2:] = B
            bases.append(block)
        totals = np.zeros(4)
        for i in range(self.n - 1, -1, -1):
            for c in self.children[i]:
                u = outside[i].copy()
                for sibling in self.children[i]:
                    if sibling != c:
                        u *= msg[sibling]
                u /= u.sum()
                denom = u @ p[c] @ d[c]
                for k, block in enumerate(bases):
                    J = expm(block * self.t[c])[:2, 2:]
                    totals[k] += (u @ J @ d[c]) / denom
                outside[c] = u @ p[c]
                outside[c] /= outside[c].sum()
        if not np.isclose(totals[2:].sum(), self.t.sum(), rtol=1e-6, atol=1e-7):
            raise ArithmeticError('posterior occupancy does not conserve branch length')
        return float(ll), dict(root_probability_white=float(root_post[0]),
            expected_white_to_red=float(totals[0]), expected_red_to_white=float(totals[1]),
            expected_white_occupancy_substitutions=float(totals[2]*self.scale),
            expected_red_occupancy_substitutions=float(totals[3]*self.scale),
            histories_conditioned_on='fitted_Q_and_this_tree_no_parameter_posterior')

    def fit(self, model='ER', prior='equal', detailed=True):
        if model not in ('ER', 'ARD'):
            raise ValueError('SYM equals ER for two states')
        dim = 1 if model == 'ER' else 2
        def objective(x):
            rates = np.exp(x)
            return -self.calculate(float(rates[0]), float(rates[-1]), prior)
        starts = [np.full(dim, x) for x in (-2., 0., 2., 4., 7.)]
        if dim == 2:
            starts += [np.array(x) for x in ((-2, 2), (2, -2), (1, 5), (5, 1))]
        runs = [minimize(objective, x, method='L-BFGS-B', bounds=[(-12, 12)]*dim,
                         options={'ftol': 1e-11, 'gtol': 1e-6, 'maxiter': 500}) for x in starts]
        valid = [r for r in runs if r.success and np.isfinite(r.fun)]
        if not valid:
            raise RuntimeError('all optimizations failed')
        best = min(valid, key=lambda x: x.fun)
        rates = np.exp(best.x)
        a, b = float(rates[0]), float(rates[-1])
        ll, stats = self.calculate(a, b, prior, details=True) if detailed else (-float(best.fun), {})
        result = dict(model=model, root_prior=prior, n_tips=len(self.leaves), log_likelihood=ll,
            parameters=dim, AIC=2*dim-2*ll, q_white_to_red=a/self.scale, q_red_to_white=b/self.scale,
            rate_ratio_return_to_gain=b/a, rate_units='per_nuclear_substitution_per_site',
            optimization_bound_hit=bool(np.any(np.abs(best.x) > 11.99)),
            converged_starts=len(valid), starts=len(runs), **stats)
        return result


def ingroup_tree(tree, allowed):
    tree = copy.deepcopy(tree)
    tree.root_with_outgroup(next(n for n in tree.get_terminals() if n.name == 'HY098'))
    mrca = tree.common_ancestor(list(allowed))
    monophyletic = set(n.name for n in mrca.get_terminals()) == set(allowed)
    for tip in list(tree.get_terminals()):
        if tip.name not in allowed:
            tree.prune(tip)
    tree.root.branch_length = 0.0
    return tree, monophyletic


def run(trees: Path, traits: Path, out: Path, balanced: int = 20):
    rows = list(csv.DictReader(traits.open()))
    ingroup = [r for r in rows if r['sampled_clade'] == 'CORNIDIA']
    coding = {'WHITE': 0, 'RED': 1}
    if any(r['visible_state'] not in coding for r in ingroup):
        raise ValueError('unexpected ingroup colour')
    states = {r['accession']: coding[r['visible_state']] for r in ingroup}
    taxa = defaultdict(list)
    for r in ingroup:
        taxa[r['source_taxon']].append(r['accession'])
    out.mkdir(parents=True, exist_ok=True)
    results, sampling = [], []
    for tag in ('short_3161', 'long_3167'):
        tree = Phylo.read(trees / (tag + '.treefile'), 'newick')
        tree, mono = ingroup_tree(tree, states)
        Phylo.write(tree, out / (tag + '_cornidia.nwk'), 'newick')
        model = BinaryMk(tree, states)
        for prior in ('equal', 'stationary'):
            for name in ('ER', 'ARD'):
                r = model.fit(name, prior)
                r.update(alignment=tag, sampling='ALL_ACCESSIONS', cornidia_monophyletic=mono)
                results.append(r)
                print(json.dumps(r), flush=True)
        rng = np.random.default_rng(SEED)
        for draw in range(balanced):
            chosen = sorted(str(rng.choice(taxa[t])) for t in sorted(taxa))
            sub = copy.deepcopy(tree)
            for tip in list(sub.get_terminals()):
                if tip.name not in chosen:
                    sub.prune(tip)
            sub.root.branch_length = 0.0
            mk = BinaryMk(sub, {t: states[t] for t in chosen})
            for name in ('ER', 'ARD'):
                r = mk.fit(name, 'equal', detailed=False)
                r.update(alignment=tag, sampling='ONE_ACCESSION_PER_SOURCE_TAXON', draw=draw,
                         chosen_accessions=';'.join(chosen))
                sampling.append(r)
    allr = results + sampling
    fields = sorted(set().union(*(r.keys() for r in allr)))
    with (out / 'model_fits.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(allr)
    summary = dict(primary_fits=results, balanced_draws=balanced, seed=SEED,
                   observed_ingroup_states=dict((s, sum(r['visible_state']==s for r in ingroup)) for s in coding),
                   cornidia_source_taxa=len(taxa),
                   claim_boundary='conditional independent two-locus reanalysis; not a dated species tree or pooled cross-clade law',
                   paper1_science_changed=False)
    for tag in ('short_3161', 'long_3167'):
        ard = [r for r in sampling if r['alignment']==tag and r['model']=='ARD']
        er = [r for r in sampling if r['alignment']==tag and r['model']=='ER']
        if ard:
            summary[tag+'_balanced'] = dict(
                rate_ratio_quantiles=np.quantile([r['rate_ratio_return_to_gain'] for r in ard],[0,.5,1]).tolist(),
                delta_AIC_ARD_minus_ER_quantiles=np.quantile([a['AIC']-e['AIC'] for a,e in zip(ard,er)],[0,.5,1]).tolist(),
                bound_hit_draws=sum(r['optimization_bound_hit'] for r in ard))
    (out / 'analysis_summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    return summary


if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--trees',type=Path,required=True)
    p.add_argument('--traits',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--balanced',type=int,default=20)
    a=p.parse_args()
    run(a.trees,a.traits,a.out,a.balanced)
