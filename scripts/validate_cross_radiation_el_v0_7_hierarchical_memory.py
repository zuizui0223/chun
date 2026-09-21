#!/usr/bin/env python3
from __future__ import annotations
import json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MAN=ROOT/"manuscript"/"CROSS_RADIATION_EVOLUTION_LETTERS_V0_7_HIERARCHICAL_MEMORY_CANDIDATE.md"
GATE=ROOT/"data"/"cross_radiation_evolution_letters_v0_7_hierarchical_memory_gate.json"
VISIBLE=ROOT/"results"/"flowerclades51_hidden_fine_memory_v0_1"/"summary_v0_1.json"
ARCH=ROOT/"results"/"flowerclades51_memory_architecture_v0_1"/"summary_v0_1.json"
PET=ROOT/"results"/"petunieae_hidden_memory_v0_1"/"summary_v0_1.json"
EXT=ROOT/"data"/"cross_radiation_hierarchical_rule_v0_2.json"
RUE=ROOT/"data"/"ruellia51_hidden_memory_prediction_v0_1.json"

TITLE="Flower-color evolutionary memory is hierarchical rather than scale-optimal"

def words(x:str)->int:
    return len(re.findall(r"\b[\w'’-]+\b",x))

def section(text:str,h:str)->str:
    m=re.search(rf"^# {re.escape(h)}\s*$",text,re.M|re.I)
    if not m: return ""
    tail=text[m.end():]
    n=re.search(r"^# ",tail,re.M)
    return tail[:n.start()] if n else tail

def validate_candidate(man_path:Path=MAN,gate_path:Path=GATE)->dict:
    text=man_path.read_text(encoding="utf-8")
    gate=json.loads(gate_path.read_text())
    vis=json.loads(VISIBLE.read_text())
    arch=json.loads(ARCH.read_text())
    pet=json.loads(PET.read_text())
    ext=json.loads(EXT.read_text())
    rue=json.loads(RUE.read_text())

    assert gate["status"]=="HIERARCHICAL_MEMORY_CANDIDATE_PENDING_PROSPECTIVE_RUELLIA"
    assert gate["current_submission_remains"]=="Evolution Letters v0.3"
    assert gate["promotion_allowed_before_ruellia"] is False
    assert gate["ruellia_result_available"] is False
    assert vis["n_clades"]==21 and vis["positive_effect_clades"]==18
    assert abs(vis["median_centered_auc_effect"]-0.02700779596581926)<1e-12
    assert arch["status"]=="FLOWERCLADES51_MEMORY_ARCHITECTURE_EXPLORATORY_RESULT"
    assert abs(arch["variance_share"]["amplitude"]-0.9065164172071694)<1e-12
    assert pet["status"]=="PETUNIEAE_HIERARCHICAL_HIDDEN_MEMORY_RETROSPECTIVE_RESULT"
    assert abs(pet["centered_auc_effect"]-0.18794355717042766)<1e-12
    h=ext["hierarchical_fine_state_rule"]
    assert h["testable_external_radiations"]==3 and h["supporting_external_radiations"]==3
    assert rue["status"]=="FROZEN_BEFORE_RUELLIA51_HPLC_OUTCOME_OPENING"

    assert f"**{TITLE}**" in text
    abstract=section(text,"Abstract")
    intro=section(text,"Introduction")
    methods=section(text,"Methods")
    results=section(text,"Results")
    discussion=section(text,"Discussion")
    refs=section(text,"References")
    assert 180 <= words(abstract) <= 300
    main=words(intro+methods+results+discussion)
    assert main <= 5000
    for token in ["18/21","+0.0270","0.1879","0.0001","90.65%","Ruellia"]:
        assert token in text, token
    assert "post-outcome" in text.lower()
    assert "not a universal" in text.lower() or "not universal" in text.lower()
    assert "10.1111/nph.13576" in refs
    assert "10.1111/evo.13589" in refs
    assert "10.1093/sysbio/syaa036" in refs
    assert "prospective" in discussion.lower() and "ruellia" in discussion.lower()
    assert "current submission remains v0.3" in text.lower()
    return {
      "status":"EL_V0_7_HIERARCHICAL_MEMORY_CANDIDATE_VALID",
      "title":TITLE,
      "abstract_words":words(abstract),
      "main_words":main,
      "visible_hidden_memory_clades":vis["n_clades"],
      "visible_positive_clades":vis["positive_effect_clades"],
      "petunieae_hidden_effect":pet["centered_auc_effect"],
      "external_supporting_radiations":h["supporting_external_radiations"],
      "ruellia_pending":True,
      "current_submission":"Evolution Letters v0.3"
    }

def main():
    out=validate_candidate()
    print(json.dumps(out,indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
