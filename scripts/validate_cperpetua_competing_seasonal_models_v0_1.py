#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json,math
from pathlib import Path


def read_csv(path: Path):
    with path.open(newline='',encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--anchors',type=Path,required=True)
    ap.add_argument('--contract',type=Path,required=True)
    ap.add_argument('--out-dir',type=Path,required=True)
    a=ap.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
    anchors=read_csv(a.anchors);contract=read_csv(a.contract)
    A={r['anchor_id']:r for r in anchors}
    assert len(A)==len(anchors)==7
    expected={
        'CP_NECTAR_VOLUME':453.66/129.14,
        'CP_SUCROSE_RATIO_FULL_BLOOM':49.69/6.99,
        'CP_TOTAL_NECTAR_AMINO_ACIDS':530/1317,
        'CP_BIRD_VISIT':0.58/0.20,
        'CP_APIS_CERANA_VISIT':1.02/4.23,
        'CP_APIS_MELLIFERA_VISIT':0.98/5.26,
        'CP_BIRD_TO_TWO_BEE_RATIO':(0.58/(1.02+0.98))/(0.20/(4.23+5.26)),
    }
    ratio_checks=[]
    for key,val in expected.items():
        stored=float(A[key]['winter_to_summer_ratio'])
        assert abs(stored-val)<1e-8,(key,stored,val)
        ratio_checks.append({'anchor_id':key,'stored_ratio':stored,'recomputed_ratio':val})
    assert expected['CP_NECTAR_VOLUME']>3
    assert expected['CP_SUCROSE_RATIO_FULL_BLOOM']>7
    assert expected['CP_BIRD_VISIT']>1
    assert expected['CP_APIS_CERANA_VISIT']<0.25
    assert expected['CP_APIS_MELLIFERA_VISIT']<0.20
    assert expected['CP_BIRD_TO_TWO_BEE_RATIO']>13

    model_ids={r['model_id'] for r in contract};gate_ids={r['gate_id'] for r in contract}
    assert model_ids=={'M_REWARD_ONLY','M_GENERAL_SEASONAL_PHYSIOLOGY','M_SENSORY_PLUS_REWARD','M_BEHAVIOR_WITHOUT_FITNESS'}
    assert gate_ids=={'G0','G1','G2','G3','G4','G5','G6'}
    assert len(contract)==7
    summary={
        'analysis':'cperpetua_competing_seasonal_models_v0.1',
        'historical_anchor_ratios':{k:v for k,v in expected.items()},
        'bird_to_two_bee_weighting_shift_fold':expected['CP_BIRD_TO_TWO_BEE_RATIO'],
        'contract_gates':sorted(gate_ids),
        'predeclared_classification':{
            'reward_only':'G0 replicated + G1 absent',
            'general_seasonal_physiology':'G1 present but G3/G4 absent',
            'sensory_plus_reward':'G0 + G1 + G3 + G4 + G5',
            'behavior_without_fitness':'G3/G4 present but G5 absent'
        },
        'decision_boundary':'seasonal reward and guild shifts are already large enough that a molecular seasonal shift alone cannot establish sensory mediation; sensory incremental prediction and service-to-fitness gates are required',
        'claim_ceiling':'pre-registration and historical-anchor validation only; no winter petal data exist yet and no historical colour-transition causation is inferred'
    }
    with (a.out_dir/'ratio_checks.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(ratio_checks[0]));w.writeheader();w.writerows(ratio_checks)
    (a.out_dir/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2,ensure_ascii=False))
    return 0

if __name__=='__main__':raise SystemExit(main())
