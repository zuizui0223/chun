from __future__ import annotations
import importlib.util
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
SPEC=importlib.util.spec_from_file_location(
  "petunieae_state_coverage",ROOT/"scripts/audit_petunieae_fine_pigment_state_retention_v0_1.py"
)
mod=importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(mod)

RESULT=ROOT/"results/petunieae_fine_pigment_state_retention_v0_1/coverage_v0_1.json"
REG=ROOT/"results/petunieae_nested_regulatory_memory_v0_1/result_v0_1.json"

def test_exact_retained_sixbit_partition_is_only_three_variable_components():
    r=json.loads(RESULT.read_text(encoding="utf-8"))
    assert (r["unfiltered_ingroup_tips"],r["retained_tips"],r["excluded_tips"])==(59,47,12)
    assert (r["fine_states_unfiltered"],r["fine_states_retained"])==(15,6)
    assert r["retained_constant_zero_anthocyanidin_compounds"]==[
        "Pel_mgg","Cyan_mgg","Peon_mgg"
    ]
    assert r["retained_variable_anthocyanidin_compounds"]==[
        "Del_mgg","Pet_mgg","Malv_mgg"
    ]
    assert r["retained_compound_positive_tips"]=={
        "Pel_mgg":0,"Cyan_mgg":0,"Peon_mgg":0,
        "Del_mgg":29,"Pet_mgg":31,"Malv_mgg":19
    }
    assert r["excluded_compound_positive_tips"]["Pel_mgg"]==7
    assert r["excluded_compound_positive_tips"]["Cyan_mgg"]==4
    assert r["excluded_compound_positive_tips"]["Peon_mgg"]==6
    assert r["three_bit_reduction_preserves_fine_partition"] is True
    assert len(r["unfiltered_sixbit_state_counts"])==15
    assert sum(r["unfiltered_sixbit_state_counts"].values())==59
    assert sum(r["retained_sixbit_state_counts"].values())==47
    assert all(s.startswith("000") for s in r["retained_sixbit_state_counts"])

def test_pigment_coverage_does_not_modify_primary_result_or_permutation_cohort():
    r=json.loads(RESULT.read_text(encoding="utf-8"))
    reg=json.loads(REG.read_text(encoding="utf-8"))
    assert reg["retained_tips"]==r["retained_tips"]==47
    assert reg["fine_state_counts"]==r["retained_sixbit_state_counts"]
    assert reg["primary_conditional_expression_memory"]["same_fine_unordered_pairs"]==183
    assert reg["primary_conditional_expression_memory"]["p_one_sided"]==0.0001
    assert reg["primary_conditional_expression_memory"]["rho"]>0
    assert r["primary_cohort_or_result_changed"] is False
    assert r["all_rare_branch_positive_removed"] is True
    assert r["source_verified"] is True

def test_auditor_states_distinguish_assay_from_supported_dimension():
    import pandas as pd
    df=pd.DataFrame({
       "Pel_mgg":[0,0,0,0],
       "Cyan_mgg":[0,0,0,0],
       "Peon_mgg":[0,0,0,0],
       "Del_mgg":[0,2,0,4],
       "Pet_mgg":[1,0,0,1],
       "Malv_mgg":[0,0,0,1]
    })
    assert mod.fine_sixbit(df,list(df.columns))==[
       "000010","000100","000000","000111"
    ]
