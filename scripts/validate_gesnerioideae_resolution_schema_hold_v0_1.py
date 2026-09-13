#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

DECISION = Path('data/gesnerioideae_resolution_schema_decision_v0_1.json')
PREREG = Path('data/gesnerioideae_resolution_profile_prereg_v0_1.json')
RESULT = Path('results/gesnerioideae_resolution_profile_v0_1/gesnerioideae_resolution_profile_result_v0_1.json')
RESULT_DIR = RESULT.parent


def main() -> int:
    d = json.loads(DECISION.read_text(encoding='utf-8'))
    p = json.loads(PREREG.read_text(encoding='utf-8'))

    assert p['status'] == 'FROZEN_BEFORE_GESNERIOIDEAE_ROW_LEVEL_OUTCOME_INGESTION'
    assert p['schema_stop_rule'] == 'HOLD_SCHEMA if three nested levels cannot be instantiated without outcome-dependent recoding'
    assert d['status'] == 'HOLD_SCHEMA_SOURCE_AXES_NOT_NESTED'
    assert d['source_doi'] == p['source_doi'] == '10.3389/fpls.2020.604389'
    assert d['upstream_preregistration_status'] == p['status']

    r = d['source_schema_receipt']
    assert r['workflow_run'] == 34738455036
    assert r['artifact_id'] == 10311567109
    assert r['artifact_digest'] == 'sha256:f5e4d31387bd15a4c950875457013f2220aca5b911c889438534297a7ee85a91'
    assert r['workbook'] == 'Table_1.xlsx'
    assert r['workbook_sha256'] == 'a84abf67da0afb8c0bafd4c1251dbcbb6dc48eb286dca788e6e88ce0176ccbc8'
    assert r['worksheet'] == 'FINAL SAMPLE LIST'
    assert r['schema_only'] is True

    axes = d['source_semantic_axes']
    assert axes['intermediate_candidate'] == ['HYD90', 'DEO90', 'DEO+HYD', 'NONE']
    assert axes['fine_candidate'] == 'nine source reflectance/visible-colour groups'

    n = d['nesting_audit']
    assert n['coarse_to_intermediate'].startswith('SEMANTICALLY_NESTED')
    assert n['intermediate_to_fine'] == 'FAIL_CROSS_CUTTING_SOURCE_AXES'
    assert len(n['published_aggregate_counterexamples']) == 2
    assert d['decision'] == 'THREE_NESTED_LEVELS_CANNOT_BE_INSTANTIATED_UNDER_THE_FROZEN_CONTRACT_WITHOUT_POST_FREEZE_RECODING'
    assert d['stop_rule_triggered'] == p['schema_stop_rule']
    assert len(d['forbidden_rescue']) == 4

    f = d['outcome_firewall']
    assert all(v is False for v in f.values())
    assert not RESULT.exists(), f'row-level profile result must not exist after schema HOLD: {RESULT}'
    assert not RESULT_DIR.exists(), f'row-level profile result directory must not exist after schema HOLD: {RESULT_DIR}'

    assert d['biological_interpretation'].startswith('NOT_A_BIOLOGICAL_NEGATIVE')
    assert d['paper1_science_changed'] is False

    print('GESNERIOIDEAE_SCHEMA_HOLD_VALID')
    print('STATUS=HOLD_SCHEMA_SOURCE_AXES_NOT_NESTED')
    print('AUC_COMPUTED=false')
    print('ROW_LEVEL_OUTCOME_OPENED=false')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
