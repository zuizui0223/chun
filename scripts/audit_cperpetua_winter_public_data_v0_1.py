#!/usr/bin/env python3
"""Fail-closed audit of the public-data gap for winter mature flowers of Camellia perpetua.

The purpose is not to prove that no unpublished dataset exists. It asks a narrower,
reproducible question: among the explicitly screened open/public resources in the
frozen registry, is there an eligible winter mature-flower molecular or spectral
anchor comparable to the admitted summer flower datasets and the seasonal ecology
study?
"""
from __future__ import annotations
import argparse,csv,json
from pathlib import Path


def read_csv(path: Path):
    with path.open(newline='',encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('--screen',type=Path,required=True);ap.add_argument('--out-dir',type=Path,required=True);a=ap.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
    rows=read_csv(a.screen)
    ids=[r['record_id'] for r in rows];assert len(ids)==len(set(ids)), 'duplicate record_id'
    assert len(rows)>=7, 'screen unexpectedly small'

    summer=[r for r in rows if r['decision'] in {'admit_summer_flower_anchor','admit_independent_summer_flower_anchor'}]
    winter=[r for r in rows if 'winter' in r['season_or_month'].lower() and r['decision'].startswith('admit_') and r['record_id']!='JIANG2025_SEASONAL_ECOLOGY']
    ecology=[r for r in rows if r['decision']=='admit_ecology_anchor']
    metadata=[r for r in rows if r['decision']=='admit_metadata_no_winter']
    negative=[r for r in rows if r['decision']=='no_eligible_winter_petal_dataset_found']
    off_target=[r for r in rows if r['decision']=='context_not_petal_state']

    assert len(summer)>=2, 'expected >=2 independent summer floral molecular anchors'
    assert len(ecology)==1 and ecology[0]['record_id']=='JIANG2025_SEASONAL_ECOLOGY'
    assert len(metadata)>=1
    assert len(negative)==1
    assert len(off_target)>=2
    assert len(winter)==0, f'eligible winter molecular/spectral anchor unexpectedly present: {[r["record_id"] for r in winter]}'

    eligible_winter=[]
    for r in rows:
        tissue=r['tissue_or_material'].lower();scope=r['molecular_scope'].lower();season=r['season_or_month'].lower()
        mature_flower=any(x in tissue for x in ('flower','petal')) and 'bud' not in tissue and 'leaf' not in tissue
        molecular=any(x in scope for x in ('rna-seq','transcript','metabol','flavonoid','spectra','spectral','pigment'))
        if 'winter' in season and mature_flower and molecular and r['decision'] not in {'admit_ecology_anchor','no_eligible_winter_petal_dataset_found'}:
            eligible_winter.append(r['record_id'])
    assert not eligible_winter

    summary={
      'analysis':'cperpetua_winter_public_data_screen_v0.1',
      'screened_records':len(rows),
      'summer_mature_flower_molecular_anchors':len(summer),
      'summer_anchor_ids':[r['record_id'] for r in summer],
      'seasonal_ecology_anchors':len(ecology),
      'metadata_resources_without_winter_label':len(metadata),
      'seasonal_or_annual_molecular_context_not_mature_petal':len(off_target),
      'eligible_winter_mature_flower_molecular_or_spectral_anchors':0,
      'decision':'no eligible open/public winter mature-flower molecular or spectral anchor was recovered in the frozen screen; the public-data causal bridge remains open at the winter floral-state step',
      'next_decisive_measurement':'same GBG population: winter vs summer mature flowers measured for CHUN A/F/C/P or RNA-seq, pigment/metabolite chemistry, and UV-visible/fluorescence alongside pollinator effectiveness and fruit/seed fitness',
      'claim_ceiling':'open/public indexed evidence saturation for the frozen query set; not proof that unpublished, inaccessible, or non-indexed data do not exist'
    }
    (a.out_dir/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    with (a.out_dir/'screen_decisions.csv').open('w',newline='',encoding='utf-8') as f:
        fields=['record_id','season_or_month','tissue_or_material','molecular_scope','decision'];w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows([{k:r[k] for k in fields} for r in rows])
    print(json.dumps(summary,indent=2,ensure_ascii=False));return 0

if __name__=='__main__':raise SystemExit(main())
