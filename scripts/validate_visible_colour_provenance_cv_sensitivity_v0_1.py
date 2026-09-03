#!/usr/bin/env python3
"""Test whether the out-of-sample A/W climate null depends on provenance correction.

Runs the same species- and section-holdout prediction under three frozen scenarios:
original country-only values, minimal removal of two shared extreme coordinates,
and the strict Tuberculatae section-envelope sensitivity.
"""
from __future__ import annotations
import argparse,csv,json,math
from pathlib import Path
from validate_visible_colour_out_of_sample_v0_1 import (
    METRICS, read_csv, write_csv, norm_section, predict_rows, summarize
)


def prepare(base, sens, scenario):
    rows=[dict(r) for r in base]
    taxa={r['taxon'] for r in rows}
    if {'Camellia kissi','Camellia kissii'}.issubset(taxa):
        rows=[r for r in rows if r['taxon']!='Camellia kissi']
    if scenario!='original_country_only_filter':
        corr={r['taxon']:r for r in sens if r['scenario']==scenario}
        assert set(corr)=={'Camellia rhytidocarpa','Camellia tuberculata'}
        by={r['taxon']:r for r in rows}
        for taxon,c in corr.items():
            by[taxon]['n_points']=c['n_points']
            for m in METRICS: by[taxon][m]=c[m]
    for r in rows: r['section_norm']=norm_section(r['section'])
    aw=[r for r in rows if r['colour_state'] in {'A','W'}]
    assert len(aw)==48
    return aw


def run_cv(data, scenario):
    summaries=[]
    sections=sorted({r['section_norm'] for r in data})
    for metric in METRICS:
        pred=[]
        for i,held in enumerate(data):
            train=[r for j,r in enumerate(data) if j!=i]
            pred.extend(predict_rows(train,[held],metric))
        s=summarize('leave_one_species_out',metric,pred);s['scenario']=scenario;summaries.append(s)

        pred=[]
        for sec in sections:
            test=[r for r in data if r['section_norm']==sec]
            train=[r for r in data if r['section_norm']!=sec]
            pred.extend(predict_rows(train,test,metric))
        s=summarize('leave_one_section_out',metric,pred);s['scenario']=scenario;summaries.append(s)
    return summaries


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--species',type=Path,required=True);ap.add_argument('--provenance',type=Path,required=True);ap.add_argument('--out-dir',type=Path,required=True);a=ap.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
    base=read_csv(a.species);sens=read_csv(a.provenance)
    scenarios=['original_country_only_filter','minimal_remove_two_shared_extreme_coordinates','strict_section_envelope_22.54_30.96N_103.83_111.76E']
    rows=[]
    for sc in scenarios: rows.extend(run_cv(prepare(base,sens,sc),sc))
    wins=sum(bool(r['colour_improves_rmse']) for r in rows)
    assert len(rows)==24 and wins==0, f'provenance sensitivity drift: colour improves {wins}/24 comparisons'
    grouped=[]
    for sc in scenarios:
        for mode in ['leave_one_species_out','leave_one_section_out']:
            z=[r for r in rows if r['scenario']==sc and r['mode']==mode]
            ratio=math.exp(sum(math.log(float(r['colour_to_null_rmse_ratio'])) for r in z)/len(z))
            grouped.append({'scenario':sc,'mode':mode,'colour_RMSE_wins':sum(bool(r['colour_improves_rmse']) for r in z),'n_metrics':len(z),'geometric_mean_colour_to_null_RMSE_ratio':ratio})
    summary={'analysis':'visible_colour_provenance_cv_sensitivity_v0.1','n_scenarios':3,'n_modes':2,'n_metrics':4,'total_comparisons':24,'colour_RMSE_wins':wins,'decision':'the out-of-sample visible-colour climate null is invariant to original, minimally corrected, and strict Tuberculatae provenance scenarios','claim_ceiling':'predictive sensitivity only; does not test flowering-window mediation or historical branch causation'}
    write_csv(a.out_dir/'scenario_metric_summary.csv',rows)
    write_csv(a.out_dir/'scenario_mode_summary.csv',grouped)
    (a.out_dir/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))
    return 0

if __name__=='__main__': raise SystemExit(main())
