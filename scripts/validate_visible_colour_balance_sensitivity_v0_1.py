#!/usr/bin/env python3
"""Balanced-subsample sensitivity for the A/W out-of-sample climate null.

The frozen A/W matrix is imbalanced (A=14, W=34). This script repeatedly
samples 14 W taxa without replacement, combines them with all 14 A taxa, and
recomputes leave-one-species-out null vs colour RMSE for four climate metrics.
It tests whether the predictive null is an artefact of state-count imbalance.
"""
from __future__ import annotations
import argparse,csv,json,math,random
from pathlib import Path
from validate_visible_colour_out_of_sample_v0_1 import METRICS,read_csv,apply_provenance_clean


def quantile(xs, p):
    xs=sorted(xs);pos=(len(xs)-1)*p;lo=int(math.floor(pos));hi=int(math.ceil(pos))
    if lo==hi:return xs[lo]
    w=pos-lo;return xs[lo]*(1-w)+xs[hi]*w


def loso_ratio(rows, metric):
    ys=[float(r[metric]) for r in rows];states=[r['colour_state'] for r in rows];n=len(rows);total=sum(ys)
    null_sse=0.0;colour_sse=0.0
    sums={s:sum(y for y,st in zip(ys,states) if st==s) for s in ('A','W')}
    counts={s:sum(st==s for st in states) for s in ('A','W')}
    for y,st in zip(ys,states):
        pn=(total-y)/(n-1);pc=(sums[st]-y)/(counts[st]-1)
        null_sse+=(y-pn)**2;colour_sse+=(y-pc)**2
    return math.sqrt(colour_sse/n)/math.sqrt(null_sse/n)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--species',type=Path,required=True);ap.add_argument('--provenance',type=Path,required=True);ap.add_argument('--out-dir',type=Path,required=True);ap.add_argument('--reps',type=int,default=10000);ap.add_argument('--seed',type=int,default=20260903);a=ap.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
    rows=apply_provenance_clean(read_csv(a.species),read_csv(a.provenance));aw=[r for r in rows if r['colour_state'] in {'A','W'}]
    A=[r for r in aw if r['colour_state']=='A'];W=[r for r in aw if r['colour_state']=='W'];assert len(A)==14 and len(W)==34
    rng=random.Random(a.seed);ratios={m:[] for m in METRICS};aggregate=[]
    for _ in range(a.reps):
        sample=A+rng.sample(W,len(A));rr=[]
        for m in METRICS:
            x=loso_ratio(sample,m);ratios[m].append(x);rr.append(x)
        aggregate.append(math.exp(sum(math.log(x) for x in rr)/len(rr)))
    rows_out=[]
    for m in METRICS:
        xs=ratios[m]
        rows_out.append({'metric':m,'reps':a.reps,'fraction_colour_improves_rmse':sum(x<1 for x in xs)/a.reps,'median_colour_to_null_rmse_ratio':quantile(xs,0.5),'q05':quantile(xs,0.05),'q95':quantile(xs,0.95)})
    agg={'reps':a.reps,'fraction_aggregate_ratio_lt_1':sum(x<1 for x in aggregate)/a.reps,'median_aggregate_colour_to_null_rmse_ratio':quantile(aggregate,0.5),'q05':quantile(aggregate,0.05),'q95':quantile(aggregate,0.95)}
    assert all(float(r['median_colour_to_null_rmse_ratio'])>1 for r in rows_out)
    assert agg['fraction_aggregate_ratio_lt_1']<0.05
    with (a.out_dir/'metric_summary.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows_out[0]));w.writeheader();w.writerows(rows_out)
    summary={'analysis':'visible_colour_balance_sensitivity_v0.1','A_per_replicate':14,'W_per_replicate':14,'reps':a.reps,'seed':a.seed,'metrics':rows_out,'aggregate':agg,'decision':'state-count imbalance does not rescue coarse visible colour as an out-of-sample annual-climate predictor','claim_ceiling':'balanced resampling sensitivity; species are not treated as phylogenetically independent effect-size replicates'}
    (a.out_dir/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8');print(json.dumps(summary,indent=2));return 0

if __name__=='__main__':raise SystemExit(main())
