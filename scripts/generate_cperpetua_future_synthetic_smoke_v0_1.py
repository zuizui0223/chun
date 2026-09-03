#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,math
from pathlib import Path

COLS=['plant_id','season','full_bloom_stage','A','F','C','P','bee_hex_contrast','uv_reflectance_300_400','fluorescence_index','anthocyanin_total','flavonol_total','carotenoid_total','flavan3ol_total','nectar_volume','sucrose_ratio','temperature_c','bird_visitation','bird_effectiveness','bee_visitation','bee_effectiveness','fruit_set','seed_set']


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out-dir',type=Path,required=True);a=ap.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
    rows=[]
    for i in range(1,16):
        x=(i-8)/7
        total_service=4.0+0.45*i
        for season in ('summer','winter'):
            w=1 if season=='winter' else 0
            # Strong latent shift plus plant variation.
            A=0.15*x+1.10*w;F=-0.12*x-0.95*w;C=0.10*x+0.85*w;P=-0.08*x-0.80*w
            bee_hex=2.05+0.28*x-0.95*w
            nectar=120+6*((i*5)%7)+300*w
            sucrose=7+0.15*((i*3)%5)+42*w
            temp=27.0+0.15*((i*2)%5)-14*w
            # Effective guild share retains plant-level dependence on bee salience beyond reward/temp.
            linear=2.7-1.75*bee_hex+0.0012*nectar
            bird_share=1/(1+math.exp(-linear))
            service=total_service+0.35*w
            bird_vis=bird_share*service;bee_vis=(1-bird_share)*service
            # Fitness has an independent total-service contribution beyond season/reward.
            fruit=min(0.95,max(0.02,0.10+0.065*service+0.00025*nectar+0.015*w))
            seed=min(0.95,max(0.02,0.08+0.060*service+0.00020*nectar+0.012*w))
            rows.append({
                'plant_id':f'P{i:02d}','season':season,'full_bloom_stage':'full_bloom',
                'A':A,'F':F,'C':C,'P':P,'bee_hex_contrast':bee_hex,
                'uv_reflectance_300_400':0.35+0.02*x-0.10*w,'fluorescence_index':1.0+0.05*x-0.20*w,
                'anthocyanin_total':1.0+A,'flavonol_total':1.5+F,'carotenoid_total':2.0+C,'flavan3ol_total':1.3+P,
                'nectar_volume':nectar,'sucrose_ratio':sucrose,'temperature_c':temp,
                'bird_visitation':bird_vis,'bird_effectiveness':1.0,'bee_visitation':bee_vis,'bee_effectiveness':1.0,
                'fruit_set':fruit,'seed_set':seed})
    with (a.out_dir/'synthetic.csv').open('w',newline='',encoding='utf-8') as f:
        wr=csv.DictWriter(f,fieldnames=COLS);wr.writeheader();wr.writerows(rows)
    bounds=[('A',0.20),('F',0.20),('C',0.20),('P',0.20),('BEE_HEX',0.15)]
    with (a.out_dir/'bounds.csv').open('w',newline='',encoding='utf-8') as f:
        wr=csv.DictWriter(f,fieldnames=['axis','bound_abs_raw_units','status','source_note']);wr.writeheader()
        for axis,b in bounds:wr.writerow({'axis':axis,'bound_abs_raw_units':b,'status':'FROZEN_PRE_UNBLIND','source_note':'synthetic smoke-test bound only; never use as biological SESOI'})
    return 0

if __name__=='__main__':raise SystemExit(main())
