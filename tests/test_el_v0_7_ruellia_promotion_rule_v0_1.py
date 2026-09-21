from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RULE=ROOT/"data"/"el_v0_7_ruellia_promotion_rule_v0_1.json"
RUE=ROOT/"data"/"ruellia51_hidden_memory_prediction_v0_1.json"
GATE=ROOT/"data"/"cross_radiation_evolution_letters_v0_7_hierarchical_memory_gate.json"

def test_promotion_rule_is_frozen_before_ruellia_outcome():
    x=json.loads(RULE.read_text())
    r=json.loads(RUE.read_text())
    g=json.loads(GATE.read_text())
    assert x["status"]=="FROZEN_BEFORE_RUELLIA51_HIDDEN_MEMORY_OUTCOME"
    assert r["status"]=="FROZEN_BEFORE_RUELLIA51_HPLC_OUTCOME_OPENING"
    assert g["ruellia_result_available"] is False
    assert x["current_submission_before_outcome"]=="Evolution Letters v0.3"
    assert x["candidate_under_test"]=="Evolution Letters v0.7 hierarchical memory"

def test_only_hidden_memory_pass_can_unlock_promotion():
    x=json.loads(RULE.read_text())
    assert x["primary_gate"]["pass_label"]=="PROSPECTIVE_HIDDEN_MEMORY_CONFIRMED"
    assert x["independence_rule"]["promotion_primary"]=="within-coarse hidden-memory test"
    assert "Do not promote v0.7" in x["fail_gate"]["consequence"]
    assert "do not promote v0.7" in x["structural_gate"]["consequence"].lower()
    assert "v0.7 remains a non-current candidate" in x["hold_gate"]["consequence"]

def test_post_outcome_rescue_is_forbidden():
    x=json.loads(RULE.read_text())
    p=" ".join(x["prohibited_after_outcome"]).lower()
    assert "switching to global tilt" in p
    assert "changing the fine-state support threshold" in p
    assert "prospective fail" in p
    assert x["el_v0_3_science_changed"] is False
    assert x["paper1_science_changed"] is False
