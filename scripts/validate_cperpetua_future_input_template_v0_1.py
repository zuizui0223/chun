#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json
from collections import Counter
from pathlib import Path

REQUIRED_COLUMNS=[
'plant_id','season','full_bloom_stage','A','F','C','P','bee_hex_contrast',
'uv_reflectance_300_400','fluorescence_index','anthocyanin_total','flavonol_total',
'carotenoid_total','flavan3ol_total','nectar_volume','sucrose_ratio','temperature_c',
'bird_visitation','bird_effectiveness','bee_visitation','bee_effectiveness','fruit_set','seed_set'
]


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--out-dir',type=Path,required=True);a=ap.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
    with a.input.open(newline='',encoding='utf-8-sig') as f:
        reader=csv.DictReader(f);rows=list(reader);cols=reader.fieldnames
    assert cols==REQUIRED_COLUMNS,(cols,REQUIRED_COLUMNS)
    assert len(rows)==30
    plants=sorted({r['plant_id'] for r in rows});assert plants==[f'P{i:02d}' for i in range(1,16)]
    pairs=Counter((r['plant_id'],r['season']) for r in rows);assert len(pairs)==30 and all(v==1 for v in pairs.values())
    assert all(r['season'] in {'winter','summer'} for r in rows)
    assert all(r['full_bloom_stage']=='full_bloom' for r in rows)
    assert all(sum(r[c].strip()!='' for c in REQUIRED_COLUMNS[3:])==0 for r in rows), 'template must ship with measurement cells blank'
    summary={'analysis':'cperpetua_future_input_template_v0.1','rows':30,'plants':15,'seasons':['summer','winter'],'primary_unit':'plant','measurement_cells_blank':True,'decision':'template structure valid; real-data runner must fail closed until all required primary fields are populated'}
    (a.out_dir/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8');print(json.dumps(summary,indent=2));return 0

if __name__=='__main__':raise SystemExit(main())
