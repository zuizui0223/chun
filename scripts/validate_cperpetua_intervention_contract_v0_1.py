#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json
from pathlib import Path


def read_csv(p:Path):
    with p.open(newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))


def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('--contract',type=Path,required=True);ap.add_argument('--allocation',type=Path,required=True);ap.add_argument('--out-dir',type=Path,required=True);a=ap.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
    c=read_csv(a.contract);alloc=read_csv(a.allocation)
    gates={r['gate_id']:r for r in c};assert len(gates)==len(c)==6
    assert set(gates)=={'G4X_MANIP_CHECK','G4X_BEE_RESPONSE','G5X_BIRD_WINTER','G5X_BIRD_SEASON','G5X_INSECT_SUMMER','G5X_HAND_CONTEXT'}
    fitness=[r for r in alloc if r['cohort']=='fitness30'];sens=[r for r in alloc if r['cohort']=='sensory_extra']
    assert {r['arm'] for r in fitness}=={'open','bird_exclusion','full_exclusion','hand_cross'}
    assert sum(int(r['flowers_per_plant_per_season']) for r in fitness)==30
    assert all(int(r['n_plants'])==15 and int(r['n_seasons'])==2 for r in alloc)
    assert {r['arm'] for r in sens}=={'active_spectral','vehicle_sham'}
    assert sum(int(r['flowers_per_plant_per_season']) for r in sens)==12
    assert int(next(r for r in fitness if r['arm']=='open')['flowers_per_plant_per_season'])==8
    assert int(next(r for r in fitness if r['arm']=='bird_exclusion')['flowers_per_plant_per_season'])==8
    assert int(next(r for r in fitness if r['arm']=='full_exclusion')['flowers_per_plant_per_season'])==7
    assert int(next(r for r in fitness if r['arm']=='hand_cross')['flowers_per_plant_per_season'])==7
    assert 'difference-in-differences' in gates['G5X_BIRD_SEASON']['decision_rule']
    assert 'manipulation check' in gates['G4X_BEE_RESPONSE']['decision_rule']
    summary={
      'analysis':'cperpetua_intervention_causal_contract_v0.1',
      'n_tagged_plants':15,
      'n_seasons':2,
      'fitness_buds_per_plant_per_season':30,
      'fitness_total_buds':sum(int(r['total_flowers']) for r in fitness),
      'sensory_trial_flowers_per_plant_per_season':12,
      'sensory_total_flowers':sum(int(r['total_flowers']) for r in sens),
      'experimental_gates':sorted(gates),
      'decision':'sensory and pollinator-service causation are tested with separate interventions; manipulation validity is required before outcome interpretation',
      'claim_ceiling':'extant same-population seasonal causal closure only; historical accepted-species transition causation remains outside scope'
    }
    (a.out_dir/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8');print(json.dumps(summary,indent=2));return 0

if __name__=='__main__':raise SystemExit(main())
