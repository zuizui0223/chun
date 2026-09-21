from __future__ import annotations
import importlib.util, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts"/"validate_cross_radiation_el_v0_7_hierarchical_memory.py"
MAN=ROOT/"manuscript"/"CROSS_RADIATION_EVOLUTION_LETTERS_V0_7_HIERARCHICAL_MEMORY_CANDIDATE.md"
GATE=ROOT/"data"/"cross_radiation_evolution_letters_v0_7_hierarchical_memory_gate.json"

spec=importlib.util.spec_from_file_location("v07",SCRIPT)
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

def test_candidate_is_not_current_submission_before_ruellia_result():
    x=json.loads(GATE.read_text())
    assert x["status"]=="HIERARCHICAL_MEMORY_CANDIDATE_PENDING_PROSPECTIVE_RUELLIA"
    assert x["current_submission_remains"]=="Evolution Letters v0.3"
    assert x["ruellia_result_available"] is False
    assert x["promotion_allowed_before_ruellia"] is False

def test_candidate_validates_against_frozen_evidence():
    s=mod.validate_candidate(MAN,GATE)
    assert s["status"]=="EL_V0_7_HIERARCHICAL_MEMORY_CANDIDATE_VALID"
    assert s["visible_hidden_memory_clades"]==21
    assert s["visible_positive_clades"]==18
    assert s["petunieae_hidden_effect"]>0.18
    assert s["external_supporting_radiations"]==3
    assert s["ruellia_pending"] is True
