#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json
from pathlib import Path


def read_csv(path: Path):
    with path.open(newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))


def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('--audit',type=Path,required=True);ap.add_argument('--out-dir',type=Path,required=True);a=ap.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
    rows=read_csv(a.audit);assert len(rows)==2
    by={r['source_id']:r for r in rows};assert set(by)=={'ZHU2024','DENG2025'}
    z=by['ZHU2024'];d=by['DENG2025']
    assert z['year']=='2022' and d['year']=='2023'
    assert z['CHUN_P_direction']=='down'
    assert z['full_AFCP_remeasurable']=='yes'
    assert d['CHUN_P_direction']=='not_directly_estimated'
    assert d['full_AFCP_remeasurable']=='no'
    down=int(d['late_stage_catechin_down_count']);total=int(d['late_stage_catechin_total'])
    assert (down,total)==(4,4)
    assert d['replication_status']=='partial_P_like_chemical_replication'
    summary={
        'analysis':'cperpetua_summer_replication_audit_v0.1',
        'independent_summer_studies':2,
        'years':[2022,2023],
        'candidate_free_P_direction':'down',
        'independent_late_stage_galloylated_catechins_down':down,
        'independent_late_stage_galloylated_catechins_total':total,
        'late_stage_direction_fraction':down/total,
        'full_AFCP_signature_independently_replicated':False,
        'P_like_functional_chemistry_partial_replication':True,
        'decision':'Independent 2023 chemistry supports a late-bloom decline in the flavan-3-ol/galloylated-catechin branch compatible with the 2022 candidate-free P-down direction, but does not independently reproduce the full A/F/C/P signature.',
        'claim_ceiling':'cross-study partial functional replication only; galloylated catechin abundance is not identical to the CHUN P module and cannot replace winter mature-flower measurements'
    }
    (a.out_dir/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2,ensure_ascii=False));return 0

if __name__=='__main__':raise SystemExit(main())
