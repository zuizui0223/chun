#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

PREREG = Path('data/gesnerioideae_resolution_profile_prereg_v0_1.json')
RESULT = Path('results/gesnerioideae_resolution_profile_v0_1/gesnerioideae_resolution_profile_result_v0_1.json')
RESULT_DIR = RESULT.parent


def main() -> int:
    x = json.loads(PREREG.read_text(encoding='utf-8'))
    assert x['status'] == 'FROZEN_BEFORE_GESNERIOIDEAE_ROW_LEVEL_OUTCOME_INGESTION'
    assert x['source_doi'] == '10.3389/fpls.2020.604389'
    assert x['prospective_label'] == 'ANALYSIS_PROSPECTIVE_NOT_LITERATURE_BLINDED'
    assert x['candidate_role'] == 'FIFTH_RADIATION_SAME_ESTIMAND_PROFILE_REPLICATION_AND_TRAINING_EXPANSION'

    s = x['primary_statistic']
    assert s['metric'] == 'ROC_AUC'
    assert s['permutations'] == 9999
    assert s['seed'] == 20260913
    assert x['common_frame']['fine_state_minimum_tips'] == 5
    assert x['common_frame']['exclude_rare_fine_state_from_common_frame'] is True
    assert x['common_frame']['outcome_improving_exclusions_forbidden'] is True

    d = x['decision_rule']
    assert set(d) == {
        'PROFILE_SIGNALLED_COARSE',
        'PROFILE_SIGNALLED_INTERMEDIATE',
        'PROFILE_SIGNALLED_FINE',
        'PROFILE_SIGNALLED_TIED',
        'PROFILE_NO_PHYLOGENETIC_SIGNAL',
        'NO_POST_HOC_UPGRADE',
    }
    assert d['NO_POST_HOC_UPGRADE'] is True

    m = x['moderator_policy']
    assert m['fit_multivariable_model_now'] is False
    assert m['minimum_same_estimand_training_radiations_before_quantitative_moderator'] == 5
    assert m['max_predictors_at_n5'] == 1
    assert m['require_outcome_independent_target_predictor'] is True
    assert m['require_leave_one_radiation_out_improvement_over_intercept_baseline'] is True

    # Hard pre-outcome firewall: neither the terminal result nor its result directory may exist on the prereg branch.
    assert not RESULT.exists(), f'prospective result already exists before prereg freeze: {RESULT}'
    assert not RESULT_DIR.exists(), f'prospective result directory already exists before prereg freeze: {RESULT_DIR}'

    print('GESNERIOIDEAE_RESOLUTION_PROFILE_PREREG_VALID')
    print('OUTCOME_FIREWALL=CLOSED')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
