from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
P=ROOT/"scripts/audit_petunieae_module_gene_count_and_chemistry_v0_1.py"
spec=importlib.util.spec_from_file_location("petunieae_size_chemistry_diagnostic",P)
m=importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(m)

FILES=[
    "data/petunieae_module_gene_count_and_chemistry_diagnostic_design_v0_1.json",
    "data/petunieae_functional_module_memory_design_v0_1.json",
    "data/petunieae_nested_regulatory_memory_preregistered_design_v0_1.json",
    "results/petunieae_functional_module_memory_v0_1/result_v0_1.json",
    "results/petunieae_pigment_adjusted_regulatory_memory_v0_1/result_v0_1.json",
]

def inputs():
    return [json.loads((ROOT/f).read_text(encoding="utf-8")) for f in FILES]


def test_fixed_module_sizes_and_exhaustive_panel_cardinalities():
    d,modules,original,prior,adjusted=inputs()
    groups,indices=m.module_partition(modules,original)
    assert [len(g) for g in indices]==[9,4,8]
    assert [len(set(g)) for g in indices]==[9,4,8]
    assert sorted(g for group in groups for g in group["genes"])==sorted(
        original["primary"]["raw_gene_expression_columns"])
    assert d["status"]=="POST_OUTCOME_DESCRIPTIVE_MODULE_FEATURE_COUNT_AND_CHEMISTRY_DECOMPOSITION"
    assert "C(9,4)=126" in d["calculation"]["fixed_four_gene_panels"]
    assert "C(9,8)=9" in d["calculation"]["fixed_eight_gene_panels"]
    assert prior["module_results"][0]["p_maxT_familywise"]==0.2709
    assert prior["module_results"][1]["p_maxT_familywise"]==0.0162
    assert prior["module_results"][2]["p_maxT_familywise"]==0.0007
    assert adjusted["abundance_adjusted_rho"]==pytest.approx(0.511199259788796)


def test_descriptive_distribution_is_not_a_p_value_or_independent_tip_test():
    r=m.describe([0.1,0.3,-0.2,0.4,0.2])
    assert r["n_gene_panels"]==5
    assert r["positive_count"]==4
    assert r["median_rho"]==pytest.approx(0.2)
    assert r["min_rho"]==-0.2
    assert r["max_rho"]==0.4
    assert r["panel_values_not_independent_tests"]
    with pytest.raises(ValueError,match="nonfinite"):
        m.describe([np.nan,0.4])
    with pytest.raises(ValueError,match="nonfinite"):
        m.describe([])


def test_do_not_reclassify_original_positive_or_nonpositive_function_modules():
    d,modules,original,prior,adjusted=inputs()
    gate=d["guardrails"]
    assert gate["preserve_late_output_maxT_not_supported"]
    assert gate["preserve_flavonol_and_early_original_maxT_positive"]
    assert gate["no_claim_true_hypothesis_early_module_more_than_late_module_from_significance_difference"]
    assert gate["no_transcriptome_housekeeping_negative_control"]
    assert gate["no_change_Camellia_AJB_or_EL_v03"]
    assert d["calculation"]["no_new_permutations"]
    assert d["calculation"]["no_p_values"]
    assert prior["module_effect_difference_tested"] is False
    assert adjusted["decision"]=="RETROSPECTIVE_SUPPORT"


def test_bad_unverified_original_source_cannot_create_gene_results():
    design,modules,original,prior,adjusted=inputs()
    with pytest.raises((ValueError,FileNotFoundError)):
        m.audit(ROOT/"this_is_not_a_verified_phyloCCA_data_source",
                design,modules,original,prior,adjusted)
