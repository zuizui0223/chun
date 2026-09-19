from __future__ import annotations

import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"data"/"ruellia51_hidden_memory_prediction_v0_1.json"
BASE=ROOT/"data"/"ruellia51_hplc_resolution_profile_prereg_v0_1.json"
OPP=ROOT/"data"/"ruellia51_opportunity_conditional_prediction_v0_1.json"
HOLD=ROOT/"data"/"ruellia51_tree_provenance_hold_v0_1.json"


def test_hidden_memory_prediction_is_frozen_before_outcomes():
    x=json.loads(P.read_text())
    b=json.loads(BASE.read_text())
    o=json.loads(OPP.read_text())
    h=json.loads(HOLD.read_text())
    assert x["status"]=="FROZEN_BEFORE_RUELLIA51_HPLC_OUTCOME_OPENING"
    assert x["analysis_role"]=="PROSPECTIVE_HELD_OUT_HIERARCHICAL_HIDDEN_MEMORY_TEST"
    assert x["inherits_existing_hierarchy_without_change"] is True
    assert x["opportunity_gate"]=="fine_state_count > coarse_state_count on the frozen common frame"
    assert x["pair_universe"]=="unordered retained-tip pairs sharing the same frozen coarse state"
    assert x["binary_outcome"]=="pair shares the same frozen fine state"
    assert x["score"]=="negative patristic distance"
    assert x["null"]=="permute fine-state labels within each coarse-state group while preserving fine-state counts"
    assert x["permutations"]==9999
    assert x["pass_rule"]=="observed conditional AUC > permutation mean and one-sided permutation p <= 0.05"
    assert x["no_opportunity_status"]=="STRUCTURAL_NO_HIDDEN_MEMORY_TEST"
    assert x["global_tilt_prediction_reference"]=="data/ruellia51_opportunity_conditional_prediction_v0_1.json"
    assert x["global_tilt_result_cannot_rescue_hidden_memory_fail"] is True
    assert b["known_pre_outcome"]["row_level_CHUN_HPLC_presence_patterns_opened_before_freeze"] is False
    assert b["known_pre_outcome"]["CHUN_resolution_AUCs_opened_before_freeze"] is False
    assert h["outcome_firewall"]["six_HPLC_numeric_values_opened"] is False
    assert h["outcome_firewall"]["AUC_computed"] is False
    assert o["held_out_system"]["CHUN_row_level_state_patterns_opened_at_freeze"] is False
    assert x["el_v0_3_science_changed"] is False
    assert x["paper1_science_changed"] is False
