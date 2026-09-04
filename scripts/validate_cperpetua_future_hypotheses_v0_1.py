#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json
from pathlib import Path

EXPECTED={
'HCP1':'reward_only',
'HCP2':'cryptic_sensory_reweighting',
'HCP3':'bird_reliability_insurance',
'HCP4':'seasonal_heterochrony',
'HCP5':'modular_ecological_reconfiguration',
'HCP6':'developmental_P_canalization',
}

def read_csv(p:Path):
    with p.open(newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))

def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('--contract',type=Path,required=True);ap.add_argument('--out-dir',type=Path,required=True);a=ap.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
    rows=read_csv(a.contract)
    by={r['hypothesis_id']:r for r in rows}
    assert len(rows)==6 and set(by)==set(EXPECTED)
    for hid,name in EXPECTED.items():
        r=by[hid];assert r['short_name']==name
        for k in ('causal_path','primary_prediction','decisive_test','falsification','role'):assert r[k].strip(),(hid,k)
        assert 'historical' not in r['primary_prediction'].lower(),f'{hid} must remain an extant/future hypothesis'
    assert by['HCP1']['role']=='competing_null'
    assert by['HCP2']['role']=='primary_mechanism'
    assert by['HCP3']['role']=='primary_ecological_filter'
    assert 'summer S1-S5' in by['HCP4']['primary_prediction']
    assert 'independent' in by['HCP5']['primary_prediction'].lower()
    assert 'P-like' in by['HCP6']['primary_prediction']
    summary={
      'analysis':'cperpetua_future_hypotheses_v0.1',
      'n_hypotheses':len(rows),
      'primary_pair':['HCP2','HCP3'],
      'highest_conceptual_novelty':'HCP4',
      'paper1_bridge':'HCP5',
      'competing_null':'HCP1',
      'decision':'future hypotheses are mutually discriminable enough to generate positive, negative, and unresolved outcomes without converting them into current Paper 1 results',
      'claim_ceiling':'future extant-seasonal hypotheses only; no historical accepted-species transition causation'
    }
    (a.out_dir/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');print(json.dumps(summary,indent=2,ensure_ascii=False));return 0

if __name__=='__main__':raise SystemExit(main())
