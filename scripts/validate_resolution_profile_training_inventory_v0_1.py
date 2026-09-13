#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

INV=Path('data/resolution_profile_training_inventory_v0_1.csv')
SUMMARY=Path('data/resolution_profile_training_inventory_summary_v0_1.json')
IRIS=Path('results/iris_intermediate_resolution_v0_1/iris_intermediate_resolution_result_v0_1.json')
GES=Path('data/gesnerioideae_resolution_schema_decision_v0_1.json')
GES_PREREG=Path('data/gesnerioideae_resolution_profile_prereg_v0_1.json')
HIER=Path('data/cross_radiation_hierarchical_rule_v0_2.json')


def read_csv(path: Path):
    with path.open(newline='',encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def main() -> int:
    rows=read_csv(INV)
    summary=json.loads(SUMMARY.read_text())
    iris=json.loads(IRIS.read_text())
    ges=json.loads(GES.read_text())
    gp=json.loads(GES_PREREG.read_text())
    hier=json.loads(HIER.read_text())

    assert len(rows)==5
    by={r['radiation']:r for r in rows}
    assert set(by)=={'IRIS','GESNERIOIDEAE','LINOIDEAE','ANGRAECINAE','ANTIRRHINEAE'}

    exact='PAIRWISE_SAME_STATE_ROC_AUC_COARSE_INTERMEDIATE_FINE_JOINT_9999_PERMUTATION'
    exact_rows=[r for r in rows if r['estimand']==exact]
    assert {r['radiation'] for r in exact_rows}=={'IRIS','GESNERIOIDEAE'}
    training=[r for r in exact_rows if r['same_estimand_training_eligible']=='true']
    assert len(training)==1 and training[0]['radiation']=='IRIS'

    # Iris is a valid exact-estimand outcome even though the preregistered universal rule failed.
    assert iris['terminal_decision']=='FAIL'
    assert iris['observed']['AUC_coarse'] < 0.5
    assert iris['observed']['AUC_intermediate'] < 0.5
    assert iris['observed']['AUC_fine'] < 0.5

    # Gesnerioideae was stopped before any target outcome and cannot train the moderator.
    assert gp['moderator_policy']['minimum_same_estimand_training_radiations_before_quantitative_moderator']==5
    assert ges['status']=='HOLD_SCHEMA_SOURCE_AXES_NOT_NESTED'
    assert ges['outcome_firewall']['coarse_intermediate_fine_AUC_computed'] is False
    assert ges['outcome_firewall']['resolution_winner_computed'] is False
    assert by['GESNERIOIDEAE']['same_estimand_training_eligible']=='false'

    # Discovery radiations are positive conditional-hierarchy evidence, not interchangeable profile outcomes.
    assert hier['hierarchical_fine_state_replication']['testable_external_radiations']==3
    assert hier['hierarchical_fine_state_replication']['supporting_external_radiations']==3
    for rid in ['LINOIDEAE','ANGRAECINAE','ANTIRRHINEAE']:
        assert by[rid]['estimand']=='CONDITIONAL_FINE_STATE_PHYLOGENETIC_ORGANIZATION'
        assert by[rid]['same_estimand_training_eligible']=='false'

    assert summary['same_estimand_training_n']==1
    assert summary['moderator_policy']['minimum_same_estimand_training_radiations']==5
    assert summary['moderator_policy']['fit_any_quantitative_moderator_now'] is False
    assert summary['moderator_policy']['use_discovery_conditional_results_as_training_outcomes'] is False
    assert summary['failure_mode_separation']=={
        'IRIS':'VALID_ESTIMAND_TERMINAL_PROSPECTIVE_FAIL',
        'GESNERIOIDEAE':'PRE_OUTCOME_SCHEMA_HOLD_NOT_A_BIOLOGICAL_NEGATIVE',
    }
    assert summary['paper1_science_changed'] is False

    print('RESOLUTION_PROFILE_TRAINING_INVENTORY_VALID')
    print('SAME_ESTIMAND_TRAINING_N=1')
    print('QUANTITATIVE_MODERATOR_FIT=false')
    return 0


if __name__=='__main__':
    raise SystemExit(main())
