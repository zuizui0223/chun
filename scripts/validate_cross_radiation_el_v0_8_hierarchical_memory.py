#!/usr/bin/env python3
from __future__ import annotations
import json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MAN=ROOT/"manuscript"/"CROSS_RADIATION_EVOLUTION_LETTERS_V0_8_HIERARCHICAL_MEMORY_SCHISTANTHE_CANDIDATE.md"
GATE=ROOT/"data"/"cross_radiation_evolution_letters_v0_8_hierarchical_memory_gate.json"
VISIBLE=ROOT/"results"/"flowerclades51_hidden_fine_memory_v0_1"/"summary_v0_1.json"
ARCH=ROOT/"results"/"flowerclades51_memory_architecture_v0_1"/"summary_v0_1.json"
PET=ROOT/"results"/"petunieae_hidden_memory_v0_1"/"summary_v0_1.json"
EXT=ROOT/"data"/"cross_radiation_hierarchical_rule_v0_2.json"
SCH=ROOT/"results"/"schistanthe_hidden_memory_v0_1"/"result_v0_1.json"
RUE=ROOT/"data"/"ruellia51_hidden_memory_prediction_v0_1.json"
V07=ROOT/"data"/"cross_radiation_el_v0_7_ruellia_promotion_rule_v0_1.json"
SYN=ROOT/"data"/"hierarchical_evolutionary_memory_synthesis_v0_2.json"

TITLE="Flower-color evolutionary memory is hierarchically retained across phenotype scales"

def words(x:str)->int:
    return len(re.findall(r"\b[\w'’-]+\b",x))

def section(text:str,h:str)->str:
    m=re.search(rf"^# {re.escape(h)}\s*$",text,re.M|re.I)
    if not m:return ""
    tail=text[m.end():]
    n=re.search(r"^# ",tail,re.M)
    return tail[:n.start()] if n else tail

def validate_candidate()->dict:
    text=MAN.read_text(encoding="utf-8")
    gate=json.loads(GATE.read_text())
    vis=json.loads(VISIBLE.read_text())
    arch=json.loads(ARCH.read_text())
    pet=json.loads(PET.read_text())
    ext=json.loads(EXT.read_text())
    sch=json.loads(SCH.read_text())
    rue=json.loads(RUE.read_text())
    v07=json.loads(V07.read_text())
    syn=json.loads(SYN.read_text())

    assert gate["status"]=="HIERARCHICAL_MEMORY_V0_8_CANDIDATE_WITH_PROSPECTIVE_VISIBLE_VALIDATION_BIOCHEMICAL_GATE_PENDING"
    assert gate["current_submission_remains"]=="Evolution Letters v0.3"
    assert gate["prospective_visible_validation_available"] is True
    assert gate["prospective_biochemical_validation_available"] is False
    assert gate["promotion_allowed_before_biochemical_prospective_validation"] is False
    assert gate["v0_7_ruellia_promotion_rule_changed"] is False
    assert v07["promotion_allowed_before_ruellia"] is False

    assert vis["n_clades"]==21 and vis["positive_effect_clades"]==18
    assert abs(vis["median_centered_auc_effect"]-0.02700779596581926)<1e-12
    assert abs(arch["variance_share"]["amplitude"]-0.9065164172071694)<1e-12
    assert abs(pet["centered_auc_effect"]-0.18794355717042766)<1e-12
    h=ext["hierarchical_fine_state_rule"]
    assert h["supporting_external_radiations"]==3
    assert sch["status"]=="PROSPECTIVE_SCHISTANTHE_HIDDEN_MEMORY_PASS"
    assert sch["retained_tips"]==129
    assert abs(sch["centered_auc_effect"]-0.06415799106532227)<1e-12
    assert abs(sch["p_one_sided"]-0.0033)<1e-12
    assert rue["status"]=="FROZEN_BEFORE_RUELLIA51_HPLC_OUTCOME_OPENING"
    assert syn["status"]=="HIERARCHICAL_EVOLUTIONARY_MEMORY_SYNTHESIS_V0_2_READY"

    assert f"**{TITLE}**" in text
    abstract=section(text,"Abstract")
    intro=section(text,"Introduction")
    methods=section(text,"Methods")
    results=section(text,"Results")
    discussion=section(text,"Discussion")
    refs=section(text,"References")
    assert 180<=words(abstract)<=300
    main=words(intro+methods+results+discussion)
    assert main<=5000
    for token in ["18/21","+0.0270","0.1879","0.0001","0.0642","0.0033","90.65%","Schistanthe","Ruellia"]:
        assert token in text, token
    assert "10.1111/nph.18083" in refs
    assert "prospective" in results.lower() and "schistanthe" in results.lower()
    assert "biochemical" in discussion.lower() and "ruellia" in discussion.lower()
    assert "current submission remains v0.3" in text.lower()
    return {
      "status":"EL_V0_8_HIERARCHICAL_MEMORY_SCHISTANTHE_CANDIDATE_VALID",
      "title":TITLE,
      "abstract_words":words(abstract),
      "main_words":main,
      "visible_hidden_memory_clades":21,
      "visible_positive_clades":18,
      "schistanthe_centered_effect":sch["centered_auc_effect"],
      "schistanthe_p":sch["p_one_sided"],
      "petunieae_centered_effect":pet["centered_auc_effect"],
      "external_supporting_radiations":3,
      "ruellia_biochemical_pending":True,
      "current_submission":"Evolution Letters v0.3"
    }

if __name__=="__main__":
    print(json.dumps(validate_candidate(),indent=2))
