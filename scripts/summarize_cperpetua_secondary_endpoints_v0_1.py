#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json,math
from pathlib import Path

SECONDARY=['uv_reflectance_300_400','fluorescence_index','anthocyanin_total','flavonol_total','carotenoid_total','flavan3ol_total']


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--data',type=Path,required=True);ap.add_argument('--out-dir',type=Path,required=True);a=ap.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
    with a.data.open(newline='',encoding='utf-8-sig') as f:rows=list(csv.DictReader(f))
    assert len(rows)==30
    out=[]
    for endpoint in SECONDARY:
        summer=[float(r[endpoint]) for r in rows if r['season']=='summer'];winter=[float(r[endpoint]) for r in rows if r['season']=='winter']
        assert len(summer)==len(winter)==15 and all(math.isfinite(x) for x in summer+winter)
        sm=sum(summer)/15;wm=sum(winter)/15
        out.append({'endpoint':endpoint,'summer_mean':sm,'winter_mean':wm,'winter_minus_summer':wm-sm,'winter_to_summer_ratio':('' if sm==0 else wm/sm),'role':'secondary_report_only_not_classification_gate'})
    with (a.out_dir/'secondary_seasonal_summary.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
    summary={'analysis':'cperpetua_secondary_endpoints_v0.1','endpoints':SECONDARY,'decision':'all six prespecified UV/fluorescence/chemistry summaries are emitted regardless of primary-gate outcome; none can replace a failed A/F/C/P or bee-hex gate'}
    (a.out_dir/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8');print(json.dumps(summary,indent=2));return 0

if __name__=='__main__':raise SystemExit(main())
