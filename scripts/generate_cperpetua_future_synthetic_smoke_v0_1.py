#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,math
from pathlib import Path

COLS=['plant_id','season','full_bloom_stage','A','F','C','P','bee_hex_contrast','uv_reflectance_300_400','fluorescence_index','anthocyanin_total','flavonol_total','carotenoid_total','flavan3ol_total','nectar_volume','sucrose_ratio','temperature_c','bird_visitation','bird_effectiveness','bee_visitation','bee_effectiveness','fruit_set','seed_set']


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out-dir',type=Path,required=True);ap.add_argument('--scenario',choices=['sensory_plus_reward','reward_only','latent_unresolved','season_proxy'],required=True);a=ap.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
    rows=[]
    for i in range(1,16):
        x=(i-8)/7;total_service=4.0+0.45*i
        for season in ('summer','winter'):
            w=1 if season=='winter' else 0
            if a.scenario=='sensory_plus_reward':
                A=0.15*x+1.10*w;F=-0.12*x-0.95*w;C=0.10*x+0.85*w;P=-0.08*x-0.80*w
                bee_hex=2.05+0.28*x-0.95*w
            elif a.scenario=='reward_only':
                A=0.15*x;F=-0.12*x;C=0.10*x;P=-0.08*x;bee_hex=1.60+0.25*x
            elif a.scenario=='latent_unresolved':
                A=0.15*x+w*(0.05+0.18*x);F=-0.12*x+w*(-0.04+0.16*x)
                C=0.10*x+w*(0.03-0.18*x);P=-0.08*x+w*(-0.02-0.15*x)
                bee_hex=1.60+0.25*x+w*(0.01+0.16*x)
            else:
                # Adversarial case: both latent state and bee_hex are strongly seasonal,
                # but bee_hex has no incremental relation to pollinator share after season is known.
                A=0.15*x+0.90*w;F=-0.12*x-0.80*w;C=0.10*x+0.70*w;P=-0.08*x-0.65*w
                bee_hex=2.00+0.45*x-0.90*w
            nectar=120+6*((i*5)%7)+300*w;sucrose=7+0.15*((i*3)%5)+42*w;temp=27.0+0.15*((i*2)%5)-14*w
            if a.scenario=='sensory_plus_reward':
                linear=2.7-1.75*bee_hex+0.0012*nectar
                bird_share=1/(1+math.exp(-linear))
            elif a.scenario=='season_proxy':
                bird_share=(0.20 if not w else 0.80)+0.02*(x*x)
            else:
                linear=-2.0+0.0055*nectar-0.04*(temp-20)+0.03*((i*4)%5)
                bird_share=1/(1+math.exp(-linear))
            service=total_service+0.35*w
            bird_vis=bird_share*service;bee_vis=(1-bird_share)*service
            fruit=min(0.95,max(0.02,0.10+0.065*service+0.00025*nectar+0.015*w))
            seed=min(0.95,max(0.02,0.08+0.060*service+0.00020*nectar+0.012*w))
            rows.append({'plant_id':f'P{i:02d}','season':season,'full_bloom_stage':'full_bloom','A':A,'F':F,'C':C,'P':P,'bee_hex_contrast':bee_hex,
                'uv_reflectance_300_400':0.35+0.02*x-0.10*w,'fluorescence_index':1.0+0.05*x-0.20*w,'anthocyanin_total':1.0+A,'flavonol_total':1.5+F,
                'carotenoid_total':2.0+C,'flavan3ol_total':1.3+P,'nectar_volume':nectar,'sucrose_ratio':sucrose,'temperature_c':temp,
                'bird_visitation':bird_vis,'bird_effectiveness':1.0,'bee_visitation':bee_vis,'bee_effectiveness':1.0,'fruit_set':fruit,'seed_set':seed})
    with (a.out_dir/'synthetic.csv').open('w',newline='',encoding='utf-8') as f:
        wr=csv.DictWriter(f,fieldnames=COLS);wr.writeheader();wr.writerows(rows)
    b=0.02 if a.scenario=='latent_unresolved' else 0.20
    bounds=[('A',b),('F',b),('C',b),('P',b),('BEE_HEX',0.02 if a.scenario=='latent_unresolved' else 0.20)]
    with (a.out_dir/'bounds.csv').open('w',newline='',encoding='utf-8') as f:
        wr=csv.DictWriter(f,fieldnames=['axis','bound_abs_raw_units','status','source_note']);wr.writeheader()
        for axis,v in bounds:wr.writerow({'axis':axis,'bound_abs_raw_units':v,'status':'FROZEN_PRE_UNBLIND','source_note':'synthetic smoke-test bound only; never use as biological SESOI'})
    return 0

if __name__=='__main__':raise SystemExit(main())
