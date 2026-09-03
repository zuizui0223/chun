#!/usr/bin/env python3
"""Audit whether independent C. perpetua molecular and ecology datasets form a quasi-matched public system.

The audit quantifies spatial/temporal overlap but fails closed on plant/sample identity.
It is designed to distinguish 'same site and period' from 'same biological contrast'.
"""
from __future__ import annotations
import argparse,csv,json,math
from pathlib import Path


def read_csv(p:Path):
    with p.open(newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))


def haversine_m(lat1,lon1,lat2,lon2):
    R=6371000.0
    p1,p2=math.radians(lat1),math.radians(lat2)
    dp=math.radians(lat2-lat1);dl=math.radians(lon2-lon1)
    a=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.atan2(math.sqrt(a),math.sqrt(1-a))


def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('--bridge',type=Path,required=True);ap.add_argument('--out-dir',type=Path,required=True);a=ap.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
    rows=read_csv(a.bridge);by={r['layer']:r for r in rows};assert set(by)=={'molecular','ecology_GBG','ecology_PRV'}
    mol=by['molecular'];gbg=by['ecology_GBG'];prv=by['ecology_PRV']
    d_gbg=haversine_m(float(mol['latitude']),float(mol['longitude']),float(gbg['latitude']),float(gbg['longitude']))
    d_prv=haversine_m(float(mol['latitude']),float(mol['longitude']),float(prv['latitude']),float(prv['longitude']))
    assert 90 < d_gbg < 120, d_gbg
    assert d_prv > 300000, d_prv

    gates=[
        {'gate':'same_taxon','status':'pass','evidence':'Camellia perpetua in both molecular and ecology studies'},
        {'gate':'same_local_site_class','status':'pass','evidence':f'molecular nursery vs GBG coordinates separated by {d_gbg:.1f} m'},
        {'gate':'overlapping_calendar_period','status':'pass','evidence':'molecular sampling June 2022 falls inside ecology observation period 2021-2023'},
        {'gate':'overlapping_season','status':'pass','evidence':'molecular sampling is June/summer peak bloom; ecology explicitly compares summer and winter'},
        {'gate':'similar_plant_age','status':'pass_context_only','evidence':'molecular plants 15 years; ecology GBG plants approximately 15-20 years'},
        {'gate':'same_individual_plants','status':'unresolved','evidence':'sources do not identify molecular replicate trees as the same ecology-observation individuals'},
        {'gate':'same_flower_samples','status':'fail','evidence':'RNA-seq/metabolomics samples and nectar/pollination/fitness observations are not sample-linked'},
        {'gate':'matched_winter_vs_summer_molecular_contrast','status':'fail','evidence':'candidate-free molecular data are June 2022 S1-S5 developmental stages only; no winter petal molecular/spectral samples'},
        {'gate':'event_matched_molecular_to_fitness_chain','status':'fail','evidence':'seasonal ecological change cannot be assigned to a measured seasonal A/F/C/P or spectral change'},
    ]
    with (a.out_dir/'bridge_gates.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(gates[0]));w.writeheader();w.writerows(gates)

    summary={
        'analysis':'cperpetua_site_time_bridge_v0.1',
        'molecular_to_GBG_coordinate_distance_m':d_gbg,
        'molecular_to_PRV_coordinate_distance_km':d_prv/1000,
        'molecular_sampling':'June 2022, summer peak bloom, 3 x 15-year-old plants, S1-S5',
        'ecology_sampling':'GBG and PRV, 2021-2023 study period, summer vs winter nectar/pollinator/reproductive ecology',
        'site_period_bridge_status':'quasi_matched_GBG_site_and_period',
        'exact_sample_bridge_status':'not_identified',
        'seasonal_molecular_bridge_status':'missing_winter_petals',
        'interpretation':'C. perpetua is substantially more matched across public molecular and ecology layers than a taxon-only overlap implies: the molecular nursery and GBG ecology site are ~0.1 km apart and June 2022 is inside the 2021-2023 ecology period. However, current candidate-free A/F/C/P is a summer developmental trajectory, not a winter-vs-summer molecular contrast.',
        'new_testable_prediction':'If flowering-window ecological filtering changes the latent floral signal in C. perpetua, mature-flower petal molecular/pigment/spectral state should differ between winter and summer at GBG; current public data provide summer molecular state but not winter molecular state.',
        'highest_value_missing_data':'winter GBG petal RNA-seq or targeted A/F/C/P expression plus pigment chemistry/reflectance from the same ecology population; ideally paired with nectar, pollinator effectiveness and fruit/seed outcome',
        'claim_ceiling':'same-site/time quasi-match, not same-individual/sample causation; do not infer seasonal molecular change from the June developmental series',
    }
    (a.out_dir/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');print(json.dumps(summary,indent=2,ensure_ascii=False));return 0

if __name__=='__main__':raise SystemExit(main())
