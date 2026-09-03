#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json
from pathlib import Path


def read_csv(p: Path):
    with p.open(newline='',encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def write_csv(p: Path, rows):
    with p.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--models',type=Path,required=True);ap.add_argument('--out-dir',type=Path,required=True);a=ap.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
    rows=[r for r in read_csv(a.models) if r['scope']=='AW_only']
    metrics=['bio1_median','bio6_median','bio6_q05','bio1_iqr']
    out=[];wins=0
    for m in metrics:
        x={r['model']:r for r in rows if r['metric']==m}
        assert {'section','section+colour'}.issubset(x)
        sa=float(x['section']['aic']); sc=float(x['section+colour']['aic'])
        win=sc<sa; wins+=int(win)
        out.append({'metric':m,'section_aic':sa,'section_plus_colour_aic':sc,'delta_add_colour':sc-sa,'adding_colour_improves_aic':win})
    assert wins==0, f'frozen result drift: adding colour improves {wins}/4 metrics'
    summary={'analysis':'history_conditioned_climate_v0.1','scope':'AW_only','n_metrics':4,'section_plus_colour_aic_wins':wins,'decision':'coarse visible colour does not improve any of the four frozen A/W climate models after conditioning on traditional-section history proxy','claim_ceiling':'traditional section is a coarse history proxy, not a substitute for the accepted nuclear tree'}
    write_csv(a.out_dir/'history_conditioned_aic.csv',out)
    (a.out_dir/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
