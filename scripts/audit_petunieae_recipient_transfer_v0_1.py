#!/usr/bin/env python3
"""Post-outcome recipient coverage; no new predictor, subset selection, or P value.

Independently replays the original fixed 47-tip k=2/class-mean predictions
and matches all three frozen module MSEs before emitting diagnostics.
Recipient omission removes evaluation losses only, not donors or training data.
"""
from __future__ import annotations
import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from Bio import Phylo

GENES = ['CHS','CHI','F3H','F3primeH','F35H','DFR','FLS','ANS','UFGT',
         'AAT','5GT','MTlike','GST','3RT','MYB27','AN11','MYBFL','MYB12',
         'AN1','JAF13','MybsG6']
PIGMENTS = ['Pel_mgg','Cyan_mgg','Peon_mgg','Del_mgg','Pet_mgg','Malv_mgg']
COUNTS = {'000000':6,'000010':6,'000011':6,'000100':10,'000110':6,'000111':13}
MODULES = {
 'LATE_ANTHOCYANIN_EXECUTION':['F35H','DFR','ANS','UFGT','AAT','5GT','MTlike','GST','3RT'],
 'FLAVONOL_BRANCH_AND_ACTIVATION':['F3primeH','FLS','MYBFL','MYB12'],
 'EARLY_SHARED_AND_REGULATORY':['CHS','CHI','F3H','MYB27','AN11','AN1','JAF13','MybsG6']}
HASHES = {
 'processed/phyloCCA__tpm10k-mgg-combined-with-flavs.csv':'5843d4cd4eb253046f97349fa6bd285ca77e43e7a9c3aaa0e78fae3e8e391edd',
 'processed/phyloCCA__11genestre_dated_pruned.tre':'95b4a688d3d71417b712b37a2b04cdc22a9431be3172d6509def4435f5fd8614',
 'processed/phyloCCA__phyloCCA_expression_HPLC-with-flavs-final.r':'abbb43dbec756ca34e9f501b7eb9aaecb7330009b79739b8c1171d9cccce13b8'}
# Frozen PR 427 outputs, not targets to fit or tune. B, nearest-2, random-2.
PRIOR = {
 'LATE_ANTHOCYANIN_EXECUTION':(0.833609089351658,0.9599142113229463,1.0617121361614648),
 'FLAVONOL_BRANCH_AND_ACTIVATION':(0.975529721087243,0.9207666373721116,1.250515200843532),
 'EARLY_SHARED_AND_REGULATORY':(1.5626699365729713,1.7440277415426866,1.8709057582593656)}
TOL = 1e-12


def donor_weights(dist: np.ndarray, states: list[str], names: list[str]):
    n = len(names)
    if (n < 3 or len(set(names)) != n or len(states) != n or
        dist.shape != (n,n) or not np.isfinite(dist).all() or
        not np.allclose(dist,dist.T) or not np.allclose(np.diag(dist),0)):
        raise ValueError('invalid source distance/name frame')
    w0, w1 = np.zeros((n,n)), np.zeros((n,n))
    for i in range(n):
        candidates = [j for j in range(n) if j != i and states[j] == states[i]]
        if len(candidates) < 2:
            raise ValueError('fewer than two same-state donors')
        ordered = sorted(candidates, key=lambda j:(float(dist[i,j]),names[j]))
        w0[i,candidates] = 1/len(candidates)
        w1[i,ordered[:2]] = .5
    return w0,w1


def recipient_losses(x: np.ndarray, w0: np.ndarray, w1: np.ndarray, states: list[str]):
    x = np.asarray(x, dtype=float)
    if x.ndim != 2 or not np.isfinite(x).all() or len(states) != len(x):
        raise ValueError('invalid expression matrix')
    n = len(x)
    if n < 3 or w0.shape != (n,n) or w1.shape != (n,n):
        raise ValueError('invalid weights')
    mu = (x.sum(0)[None,:]-x)/(n-1)
    var = (np.square(x).sum(0)[None,:]-np.square(x))/(n-1)-mu*mu
    var = np.where(var > TOL, var, 1.)
    baseline = np.mean(np.square(w0@x-x)/var,axis=1)
    nearest = np.mean(np.square(w1@x-x)/var,axis=1)
    penalty = np.empty(n)
    for i in range(n):
        donors = [j for j in range(n) if j != i and states[j] == states[i]]
        N = len(donors)
        if N < 2:
            raise ValueError('fewer than two donors')
        penalty[i] = np.mean((N-2)/(2*(N-1))*x[donors].var(0,ddof=0)/var[i])
    random_two = baseline+penalty
    return {'baseline':baseline,'nearest_two':nearest,'random_two':random_two,
            'donor_count_penalty':penalty,'locality_benefit':random_two-nearest}


def summarize_recipients(names, states, baseline, nearest):
    a, b = np.asarray(baseline,dtype=float), np.asarray(nearest,dtype=float)
    n = len(names)
    if (n < 3 or len(set(names)) != n or len(states) != n or
        a.shape != (n,) or b.shape != (n,) or
        not np.isfinite(a).all() or not np.isfinite(b).all() or
        np.any(a < 0) or np.any(b < 0) or a.sum() <= 0):
        raise ValueError('invalid recipient identity or losses')
    delta = a-b
    remain_base = a.sum()-a
    if np.any(remain_base <= 0):
        raise ValueError('zero remaining baseline loss')
    omissions = ((a.sum()-a)-(b.sum()-b))/remain_base
    ranking = sorted(range(n),key=lambda i:(-float(delta[i]),names[i]))
    positive = [i for i in ranking if delta[i] > TOL]
    negatives = sorted((i for i in range(n) if delta[i] < -TOL), key=lambda i:float(delta[i]))
    net = float(delta.sum())
    def details(ids):
        return [{'source_taxon':names[i], 'fine_state':states[i],
                 'baseline_loss':float(a[i]),'nearest_two_loss':float(b[i]),
                 'paired_loss_improvement':float(delta[i])} for i in ids]
    gains = {}
    for k in (1,3):
        chosen = positive[:k]
        if not chosen:
            gains[str(k)] = None
            continue
        gains[str(k)] = {'source_taxa':[names[i] for i in chosen],
                         'share_of_all_positive_improvements':float(delta[chosen].sum()/delta[positive].sum()),
                         'gain_if_recipient_losses_omitted':float((net-delta[chosen].sum())/(a.sum()-a[chosen].sum())),
                         'not_a_revised_primary_result':True}
    return {
        'n_recipients':n, 'pooled_relative_gain':float(net/a.sum()),
        'n_improved_recipients':int((delta > TOL).sum()),
        'n_worse_recipients':int((delta < -TOL).sum()),
        'n_tied_recipients':int((np.abs(delta) <= TOL).sum()),
        'median_paired_loss_improvement':float(np.median(delta)),
        'mean_paired_loss_improvement':float(delta.mean()),
        'positive_after_omitting_one_recipient':int((omissions > TOL).sum()),
        'recipient_omission_gain_min':float(omissions.min()),
        'recipient_omission_gain_max':float(omissions.max()),
        'single_recipient_omissions_reversing_positive_gain':[
            names[i] for i in range(n) if net > TOL and omissions[i] <= TOL],
        'recipient_omission_does_not_refit':True,
        'all_single_recipient_omission_gains':dict(zip(names,map(float,omissions))),
        'largest_positive_contributions':details(positive[:3]),
        'largest_negative_contributions':details(negatives[:3]),
        'positive_contribution_leverage':gains,
        'new_p_values':0, 'independent_recipient_trials_assumed':False}


def load_verified(source: Path):
    for name, expected in HASHES.items():
        if hashlib.sha256((source/name).read_bytes()).hexdigest() != expected:
            raise ValueError('original source SHA256 mismatch: '+name)
    manifest = json.loads((source/'source_manifest.json').read_text())
    if (manifest['authoritative_prefix'] != 'phyloCCA' or
        manifest['required_duplicate_identity'] != 'PASS_PHYLOCCA_PHYLOPCA_CSV_AND_TREE_OSF_METADATA_IDENTICAL'):
        raise ValueError('original manifest identity mismatch')
    df = pd.read_csv(source/list(HASHES)[0])
    tree = Phylo.read(source/list(HASHES)[1], 'newick')
    tips = tree.get_terminals()
    keys = [t.name for t in tips]
    if len(df) != 60 or len(keys) != 60 or set(keys) != set(df.key_0) or df.key_0.duplicated().any():
        raise ValueError('original 60 source keys mismatch')
    df = df.set_index('key_0').loc[[k for k in keys if k != 'BROW']]
    raw = df[PIGMENTS].to_numpy(float)
    if not np.isfinite(raw).all() or (raw < 0).any():
        raise ValueError('invalid pigment values')
    fine = [''.join('1' if v > 0 else '0' for v in r) for r in raw]
    counts = Counter(fine)
    keep = [i for i,f in enumerate(fine) if counts[f] >= 5]
    df = df.iloc[keep]; states = [fine[i] for i in keep]
    if len(df) != 47 or dict(Counter(states)) != COUNTS:
        raise ValueError('original retained cohort changed')
    names = df.index.tolist(); terms = {t.name:t for t in tips}
    dist = np.array([[tree.distance(terms[a],terms[b]) for b in names] for a in names])
    expr = df[GENES].to_numpy(float)
    if not np.isfinite(expr).all() or (expr < 0).any():
        raise ValueError('invalid source expression')
    return names, states, dist, np.log1p(expr)


def run(source: Path):
    names, states, dist, X = load_verified(source)
    w0, w1 = donor_weights(dist,states,names)
    report = {'version':'v0.1', 'status':'POST_OUTCOME_RECIPIENT_COVERAGE_DIAGNOSTIC',
              'source_SHA256_verified':True,'n_taxa':47,'n_source_genes':21,'fixed_k':2,
              'source_article_doi':'10.1098/rspb.2023.0275',
              'source_hashes':HASHES,'new_p_values':0,
              'original_module_locality_P_and_primary_gains_unchanged':True,
              'no_retraining_or_outcome_selected_source_subset':True,
              'no_population_average_gain_confidence_interval':True,
              'no_independent_radiation_or_ecological_causality_claim':True,
              'modules':[]}
    records = []
    for module, genes in MODULES.items():
        cols = [GENES.index(g) for g in genes]
        losses = recipient_losses(X[:,cols],w0,w1,states)
        means = tuple(float(losses[k].mean()) for k in ('baseline','nearest_two','random_two'))
        if not np.allclose(means,PRIOR[module],rtol=0,atol=1e-10):
            raise ValueError('frozen module pooled loss replay mismatch: '+module)
        summary = summarize_recipients(names,states,losses['baseline'],losses['nearest_two'])
        summary.update({'module_id':module,'genes':genes,
                        'baseline_class_mean_MSE':means[0],'nearest_two_MSE':means[1],
                        'exact_random_two_MSE':means[2],
                        'donor_count_penalty_MSE':float(losses['donor_count_penalty'].mean()),
                        'locality_benefit_MSE':float(losses['locality_benefit'].mean())})
        report['modules'].append(summary)
        for i,name in enumerate(names):
            donors = sorted(np.flatnonzero(w1[i]),key=lambda j:(dist[i,j],names[j]))
            all_donors = np.flatnonzero(w0[i])
            record = {'module_id':module,'source_taxon':name,'fine_state':states[i],
                      'same_state_donor_count':len(all_donors),
                      'donor_1':names[donors[0]],'donor_2':names[donors[1]],
                      'mean_selected_donor_distance':float(dist[i,donors].mean()),
                      'mean_all_same_state_donor_distance':float(dist[i,all_donors].mean())}
            record.update({k:float(v[i]) for k,v in losses.items()})
            record['paired_loss_improvement'] = record['baseline']-record['nearest_two']
            records.append(record)
    return report,records


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--out-dir',type=Path,required=True)
    a = p.parse_args()
    report,rows = run(a.source)
    a.out_dir.mkdir(parents=True,exist_ok=True)
    (a.out_dir/'result_v0_1.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    with (a.out_dir/'recipients_v0_1.csv').open('w',newline='') as f:
        w = csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    for m in report['modules']:
        print(json.dumps({k:m[k] for k in ('module_id','pooled_relative_gain','n_improved_recipients',
              'n_worse_recipients','median_paired_loss_improvement','positive_after_omitting_one_recipient',
              'recipient_omission_gain_min','recipient_omission_gain_max',
              'single_recipient_omissions_reversing_positive_gain','donor_count_penalty_MSE','locality_benefit_MSE')},sort_keys=True))

if __name__ == '__main__':
    main()
