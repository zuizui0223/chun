#!/usr/bin/env python3
"""Study-level directional reproducibility test for the Camellia pollinator filter.

Each independent study cluster contributes exactly one vote. Multiple coefficients
within Li2021JAE are collapsed into one study vote and must all agree with their
predeclared directions. The exact sign-test P value is a diagnostic of directional
consistency under a 0.5 null, not a biological support-rate estimate and not a
correction for publication/ascertainment bias.
"""
from __future__ import annotations
import argparse,csv,json,math
from collections import defaultdict
from pathlib import Path


def read_csv(path: Path):
    with path.open(newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))


def fnum(x):
    s=(x or '').strip();return None if s=='' else float(s)


def exact_upper_sign_p(k:int,n:int)->float:
    return sum(math.comb(n,i) for i in range(k,n+1))/(2**n)


def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('--contract',type=Path,required=True);ap.add_argument('--effects',type=Path,required=True);ap.add_argument('--out-dir',type=Path,required=True);a=ap.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
    contract=read_csv(a.contract);effects={r['effect_id']:r for r in read_csv(a.effects)}
    by_cluster=defaultdict(list)
    for row in contract:
        assert row['effect_id'] in effects, f"missing effect {row['effect_id']}"
        by_cluster[row['cluster_id']].append(row)
    assert len(by_cluster)==7, f"independent study cluster drift: {len(by_cluster)}"

    cluster_rows=[]
    for cluster,rows in sorted(by_cluster.items()):
        component=[]
        for row in rows:
            v=fnum(effects[row['effect_id']].get('effect_value'))
            assert v is not None, f"missing numeric effect_value for {row['effect_id']}"
            expected=row['expected_sign']
            ok=(v>0) if expected=='positive' else (v<0)
            component.append(ok)
        passed=all(component)
        cluster_rows.append({
            'cluster_id':cluster,
            'study_id':rows[0]['study_id'],
            'taxon':rows[0]['taxon'],
            'n_effect_components':len(rows),
            'all_components_expected_direction':passed,
        })

    n=len(cluster_rows);k=sum(bool(r['all_components_expected_direction']) for r in cluster_rows)
    p=exact_upper_sign_p(k,n)
    assert (k,n)==(7,7), f"frozen direction result drift: {k}/{n}"
    assert abs(p-0.0078125)<1e-12

    loo=[]
    for omitted in cluster_rows:
        kept=[r for r in cluster_rows if r['cluster_id']!=omitted['cluster_id']]
        nn=len(kept);kk=sum(bool(r['all_components_expected_direction']) for r in kept)
        pp=exact_upper_sign_p(kk,nn)
        loo.append({'omitted_cluster':omitted['cluster_id'],'expected_direction_clusters':kk,'n_clusters':nn,'one_sided_sign_p':pp})
    assert all(r['expected_direction_clusters']==6 and abs(r['one_sided_sign_p']-0.015625)<1e-12 for r in loo)

    with (a.out_dir/'study_cluster_votes.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(cluster_rows[0]));w.writeheader();w.writerows(cluster_rows)
    with (a.out_dir/'leave_one_study_out.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(loo[0]));w.writeheader();w.writerows(loo)
    summary={
        'analysis':'pollinator_filter_direction_consistency_v0.1',
        'independent_study_clusters':n,
        'expected_direction_clusters':k,
        'one_sided_exact_sign_p':p,
        'leave_one_study_out_all_6_of_6':True,
        'leave_one_study_out_sign_p':0.015625,
        'taxa':sorted({r['taxon'] for r in cluster_rows}),
        'decision':'pollinator-service/reliability direction is reproduced across all seven predeclared independent study clusters and remains directionally complete after any one cluster is removed',
        'claim_ceiling':'directional reproducibility diagnostic only; study ascertainment/publication bias is not estimated, study counts are not biological frequencies, and this does not identify historical flower-colour transition causation',
    }
    (a.out_dir/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8');print(json.dumps(summary,indent=2));return 0

if __name__=='__main__':raise SystemExit(main())
