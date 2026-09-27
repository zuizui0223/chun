#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
GATE=ROOT/"data"/"future_hidden_memory_informativeness_gate_v0_1.json"
SCH=ROOT/"results"/"schistanthe_hidden_memory_v0_1"/"result_v0_1.json"
GESINFO=ROOT/"results"/"gesnerioideae_fail_informativeness_v0_1"/"summary_v0_1.json"


def validate()->dict:
    g=json.loads(GATE.read_text())
    s=json.loads(SCH.read_text())
    i=json.loads(GESINFO.read_text())

    assert g["status"]=="FROZEN_FOR_FUTURE_NOT_YET_SELECTED_HIDDEN_MEMORY_SYSTEMS"
    assert g["scope"]["does_not_change_existing_terminal_states"] is True
    assert g["scope"]["does_not_change_ruellia_specific_promotion_rule"] is True
    assert "RUELLIA" in g["scope"]["does_not_apply_retroactively_to"]
    assert "GESNERIOIDEAE" in g["scope"]["does_not_apply_retroactively_to"]

    benchmark=g["informativeness_rule"]["benchmark_centered_effect"]
    assert benchmark==s["centered_auc_effect"]
    assert g["empirical_reference"]["prospective_status"]==s["status"]
    assert g["null_informativeness_calculation"]["permutations"]==9999
    assert g["null_informativeness_calculation"]["seed"]==20260927
    assert g["informativeness_rule"]["hold_terminal"]=="STRUCTURAL_LOW_INFORMATION_HOLD_OBSERVED_AUC_UNOPENED"
    assert g["informativeness_rule"]["hold_is_biological_fail"] is False

    assert g["motivation_receipt"]["gesnerioideae_centered_critical_effect"]==i["one_sided_alpha_0_05_centered_effect_critical"]
    assert g["motivation_receipt"]["schistanthe_reference_effect"]==i["schistanthe_prospective_centered_effect"]
    assert g["motivation_receipt"]["schistanthe_sized_point_effect_crossed_gesnerioideae_critical"] is False
    assert g["motivation_receipt"]["gesnerioideae_prospective_fail_changed"] is False

    assert g["paper1_science_changed"] is False
    assert g["el_v0_3_science_changed"] is False

    return {
        "status":"FUTURE_HIDDEN_MEMORY_INFORMATIVENESS_GATE_VALID",
        "benchmark_centered_effect":benchmark,
        "gesnerioideae_critical_effect":i["one_sided_alpha_0_05_centered_effect_critical"],
        "retroactive_changes":False,
        "paper1_science_changed":False,
        "el_v0_3_science_changed":False,
    }


def main()->int:
    print(json.dumps(validate(),indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
