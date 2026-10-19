from __future__ import annotations
import importlib.util,json
from pathlib import Path
import sys

import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
PATH=ROOT/"scripts/audit_petunieae_functional_module_influence_v0_1.py"
spec=importlib.util.spec_from_file_location("petunieae_function_influence",PATH)
audit=importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(audit)

ORIG=ROOT/"results/petunieae_functional_module_memory_v0_1/result_v0_1.json"
DESIGN=ROOT/"data/petunieae_functional_module_memory_design_v0_1.json"
SOURCE=ROOT/"data/petunieae_nested_regulatory_memory_preregistered_design_v0_1.json"
ADJ=ROOT/"results/petunieae_pigment_adjusted_regulatory_memory_v0_1/result_v0_1.json"


def test_diagnostic_follows_fixed_original_functional_groups_and_not_posthoc_rescue():
    f=json.loads(ORIG.read_text())
    d=json.loads(DESIGN.read_text())
    o=json.loads(SOURCE.read_text())
    mods,indices=audit.module_partition(d,o)
    assert len(mods)==3
    assert [len(x) for x in indices]==[9,4,8]
    assert f["module_results"][0]["p_maxT_familywise"]==0.2709
    assert f["module_results"][1]["p_maxT_familywise"]==0.0162
    assert f["module_results"][2]["p_maxT_familywise"]==0.0007
    assert not f["module_effect_difference_tested"]


def test_previous_21_gene_pigment_adjusted_rho_is_not_changed():
    r=json.loads(ADJ.read_text())
    assert r["abundance_adjusted_rho"]==pytest.approx(0.511199259788796)
    assert r["p_one_sided"]==0.0002
    assert r["decision"]=="RETROSPECTIVE_SUPPORT"
    assert r["does_not_replace_original_k2_prediction_fail"]


def test_no_access_to_source_does_not_create_synthetic_data():
    d=json.loads(DESIGN.read_text())
    o=json.loads(SOURCE.read_text())
    f=json.loads(ORIG.read_text())
    a=json.loads(ADJ.read_text())
    with pytest.raises((FileNotFoundError,ValueError)):
        audit.audit(ROOT/"an_impossible_unverified_Petunieae_source",d,o,f,a)

INFLUENCE=ROOT/"results/petunieae_functional_module_influence_v0_1/summary_v0_1.json"

def test_all_fortyseven_tip_and_six_chemical_code_deletion_summaries_are_frozen():
    result=json.loads(INFLUENCE.read_text())
    assert result["status"]=="POST_OUTCOME_DESCRIPTIVE_MODULE_INFLUENCE_CONFIRMED"
    assert result["source_original_tips"]==47
    assert result["source_original_sixbit_classes"]==6
    assert result["full_source_same_state_pairs"]==183
    summaries=result["module_loo_summaries"]
    assert summaries["leave_one_tip"]["n_total"]==47
    assert summaries["leave_one_tip"]["n_early_above_flavonol_above_late"]==46
    assert summaries["leave_one_fine_state"]["n_total"]==6
    assert summaries["leave_one_fine_state"]["n_early_above_flavonol_above_late"]==6
    for n,module in [(47,summaries["leave_one_tip"]["modules"]),
                     (6,summaries["leave_one_fine_state"]["modules"])]:
        assert all(v["n"]==n and v["positive_count"]==n
                   for v in module.values())
        assert set(module)=={
            "LATE_ANTHOCYANIN_EXECUTION",
            "FLAVONOL_BRANCH_AND_ACTIVATION",
            "EARLY_SHARED_AND_REGULATORY",
        }
    assert result["no_new_p_values"]==0
    assert result["no_independent_biological_replications"]==0
    assert result["cannot_claim_significant_between_module_differences"]
    assert result["not_a_negative_housekeeping_control"]
    assert result["original_output_module_maxT_p_unchanged"]==0.2709
    assert result["original_flavonol_module_maxT_p_unchanged"]==0.0162
    assert result["original_early_shared_module_maxT_p_unchanged"]==0.0007
    assert result["original_frozen_AJB_EL_science_unchanged"]
