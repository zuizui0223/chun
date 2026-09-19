from __future__ import annotations

import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"data"/"ruellia51_opportunity_conditional_prediction_v0_1.json"
BASE=ROOT/"data"/"ruellia51_hplc_resolution_profile_prereg_v0_1.json"
HOLD=ROOT/"data"/"ruellia51_tree_provenance_hold_v0_1.json"


def test_conditional_prediction_is_frozen_before_ruellia_outcomes():
    x=json.loads(P.read_text())
    b=json.loads(BASE.read_text())
    h=json.loads(HOLD.read_text())
    assert x["status"]=="FROZEN_BEFORE_RUELLIA51_HPLC_OUTCOME_OPENING"
    assert x["analysis_role"]=="PROSPECTIVE_HELD_OUT_OPPORTUNITY_REALIZATION_TEST"
    assert x["inherits_existing_hierarchy_without_change"] is True
    assert x["base_preregistration"]=="data/ruellia51_hplc_resolution_profile_prereg_v0_1.json"
    assert x["opportunity_rule"]=="fine_state_count > coarse_state_count on the frozen common frame"
    assert x["prediction_if_opportunity"]["contrast"]=="AUC_fine - AUC_coarse"
    assert x["prediction_if_opportunity"]["direction"]=="positive"
    assert x["prediction_if_opportunity"]["pass_rule"]=="observed contrast > 0 and one-sided joint-permutation p <= 0.05"
    assert x["prediction_if_no_opportunity"]["expected_tilt"]==0
    assert x["prediction_if_no_opportunity"]["biological_success_counted"] is False
    assert x["permutations"]==b["primary_statistic"]["permutations"]==9999
    assert x["seed"]==b["primary_statistic"]["seed"]==20260913
    assert h["outcome_firewall"]["six_HPLC_numeric_values_opened"] is False
    assert h["outcome_firewall"]["AUC_computed"] is False
    assert x["el_v0_3_science_changed"] is False
    assert x["paper1_science_changed"] is False


def test_existing_ruellia_hierarchy_is_untouched():
    b=json.loads(BASE.read_text())
    assert b["nested_resolutions"]["coarse"]=="ANY_ANTHOCYANIDIN_PRESENT versus NONE"
    assert b["nested_resolutions"]["intermediate"]=="three-bit source-pathway-branch presence pattern PEL/CYA/DEL"
    assert b["nested_resolutions"]["fine"]=="six-bit anthocyanidin presence pattern in fixed order Pelargonidin/Cyanidin/Peonidin/Delphinidin/Petunidin/Malvidin"
    assert b["decision_rule"]["NO_POST_HOC_UPGRADE"] is True
