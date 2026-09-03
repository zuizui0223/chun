#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,itertools,json,math
from pathlib import Path
import numpy as np


def exact_p(signs: np.ndarray, D: np.ndarray) -> float:
    n=D.shape[0]
    scale=np.sqrt(np.mean(D**2,axis=0))
    scale=np.where(scale==0,1.0,scale)
    obs=np.sum((np.mean(D,axis=0)/scale)**2)
    means=(signs@D)/n
    vals=np.sum((means/scale)**2,axis=1)
    return float(np.mean(vals >= obs-1e-12))


def mu_vector(pattern: str, d: float) -> np.ndarray:
    if pattern=='dense': return np.full(4,d/2.0)
    if pattern=='two_axis': return np.array([d/math.sqrt(2),d/math.sqrt(2),0.0,0.0])
    if pattern=='one_axis': return np.array([d,0.0,0.0,0.0])
    raise ValueError(pattern)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--out-dir',type=Path,required=True)
    ap.add_argument('--reps',type=int,default=500)
    ap.add_argument('--seed',type=int,default=20260903)
    a=ap.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
    n=15;p=4;rho=0.3
    signs=np.asarray(list(itertools.product((-1.0,1.0),repeat=n)),dtype=np.float32)
    assert signs.shape==(32768,15)
    Sigma=np.full((p,p),rho,dtype=float);np.fill_diagonal(Sigma,1.0)
    L=np.linalg.cholesky(Sigma)
    rng=np.random.default_rng(a.seed)
    rows=[]
    for pattern in ('dense','two_axis','one_axis'):
        for d in (0.0,0.5,0.8,1.0,1.2):
            mu=mu_vector(pattern,d);hits=0;ps=[]
            for _ in range(a.reps):
                D=rng.normal(size=(n,p))@L.T+mu
                pv=exact_p(signs,D.astype(np.float32));ps.append(pv);hits+=pv<0.05
            rows.append({
                'pattern':pattern,'multivariate_shift_norm':d,'reps':a.reps,
                'rejection_fraction':hits/a.reps,'median_exact_p':float(np.median(ps))
            })
    nulls=[r for r in rows if float(r['multivariate_shift_norm'])==0.0]
    assert all(0.02 <= float(r['rejection_fraction']) <= 0.09 for r in nulls)
    large=[r for r in rows if float(r['multivariate_shift_norm'])==1.2]
    assert all(float(r['rejection_fraction'])>=0.75 for r in large)
    d08=[r for r in rows if float(r['multivariate_shift_norm'])==0.8]
    assert any(float(r['rejection_fraction'])<0.60 for r in d08)
    with (a.out_dir/'power.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    summary={
        'analysis':'cperpetua_latent_gate_power_v0.1','n_pairs':15,'n_axes':4,
        'exact_sign_assignments':32768,'axis_correlation':rho,'reps_per_cell':a.reps,'seed':a.seed,
        'decision':'the exact omnibus sign-flip gate is calibrated near the nominal false-positive rate, but n=15 has limited power for moderate multivariate seasonal shifts; nonsignificance cannot be treated as equivalence',
        'design_consequence':'reward-only classification requires an independent equivalence/SESOI criterion; otherwise a nonsignificant latent-state result remains unresolved'
    }
    (a.out_dir/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))
    return 0

if __name__=='__main__':raise SystemExit(main())
