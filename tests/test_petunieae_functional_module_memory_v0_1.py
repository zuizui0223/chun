from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
PATH=ROOT/"scripts/analyze_petunieae_functional_module_memory_v0_1.py"
spec=importlib.util.spec_from_file_location("petunieae_module_memory",PATH)
m=importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(m)

DESIGN=ROOT/"data/petunieae_functional_module_memory_design_v0_1.json"
ORIGINAL=ROOT/"data/petunieae_nested_regulatory_memory_preregistered_design_v0_1.json"
ADJUSTED=ROOT/"results/petunieae_pigment_adjusted_regulatory_memory_v0_1/result_v0_1.json"

def load():
    return json.loads(DESIGN.read_text()),json.loads(ORIGINAL.read_text()),json.loads(ADJUSTED.read_text())


def test_functional_annotation_covers_each_of_21_source_genes_once():
    d,o,a=load()
    modules,ind=m.module_partition(d,o)
    assert len(modules)==3 and [len(k) for k in ind]==[9,4,8]
    all_genes=[g for row in modules for g in row["genes"]]
    assert len(set(all_genes))==len(all_genes)==21
    assert set(all_genes)==set(o["primary"]["raw_gene_expression_columns"])
    assert all(len(set(x))==len(x) for x in ind)
    assert a["abundance_adjusted_rho"]==pytest.approx(0.511199259788796)


def test_perturbed_gene_annotation_fails_before_opening_source_outcomes():
    d,o,_=load()
    d["functionally_mapped_nonoverlapping_modules"][0]["genes"][0]="FLS"
    with pytest.raises(ValueError,match="partitioned exactly once"):
        m.module_partition(d,o)


def test_three_modules_keep_original_complete_biochemical_and_gene_frames():
    d,o,adjusted=load()
    assert d["frame"]["retained_species"]==47
    assert d["frame"]["same_fine_state_pairs"]==183
    assert len(d["frame"]["all_21_source_genes"])==21
    assert d["permutation"]["iterations"]==9999
    assert d["permutation"]["seed"]==20261019
    assert d["permutation"]["no_posthoc_selective_gene_reallocation"]
    assert not d["report"]["housekeeping_negative_control_available"]
    assert d["report"]["original_all_gene_p_value_unchanged"]==0.0002
    assert adjusted["decision"]=="RETROSPECTIVE_SUPPORT"
    assert d["report"]["cannot_assume_module_significance_differences_imply_significant_contrast"]


def test_permutation_units_are_full_taxa_and_not_gene_axes_or_pairs():
    d,o,_=load()
    assert "Whole 21-gene residual expression vector" in d["permutation"]["unit"]
    assert "max" in d["permutation"]["familywise_maxT"]
    assert not d["report"]["not_an_independent_biological_radiation"] is False
    assert d["report"]["no_relabel_of_frozen_Petunieae_k2_prediction_FAIL"]
    assert d["report"]["no_change_to_AJB_Camellia_and_EL_frozen_first_submission"]


def test_synthetic_original_response_rankcorr_is_standard_spearman():
    ranks=np.array([1.0,2.0,3.0,4.0,5.0])
    y=np.array([12.0,9.0,5.0,2.0,1.0])
    from scipy.stats import spearmanr
    from analyze_petunieae_pigment_adjusted_regulatory_memory_v0_1 import rankcorr
    assert rankcorr(ranks,y)==pytest.approx(float(spearmanr(ranks,y).statistic),abs=1e-14)

RESULT=ROOT/"results/petunieae_functional_module_memory_v0_1/result_v0_1.json"

def test_real_frozen_three_module_results_and_original_pigment_adjusted_effect():
    result=json.loads(RESULT.read_text(encoding="utf-8"))
    d,_,prior=load()
    assert result["design_status"]==d["status"]
    assert result["n_tips"]==47 and result["n_same_fine_state_pairs"]==183
    assert result["n_original_expression_genes"]==21
    assert result["n_modules"]==3 and result["permutations"]==9999
    assert result["seed"]==20261019
    assert result["original_full_21_gene_adjusted_rho_reproduced"]==pytest.approx(
        prior["abundance_adjusted_rho"],abs=1e-13)
    assert result["original_full_21_gene_p_unchanged"]==0.0002
    modules={x["module_id"]:x for x in result["module_results"]}
    expected={
        "LATE_ANTHOCYANIN_EXECUTION":(9,0.21514622388860405,0.2709,False),
        "FLAVONOL_BRANCH_AND_ACTIVATION":(4,0.3725170195141295,0.0162,True),
        "EARLY_SHARED_AND_REGULATORY":(8,0.45826046500459183,0.0007,True)
    }
    assert set(modules)==set(expected)
    for name,(n,rho,p,pass_module) in expected.items():
        obj=modules[name]
        assert obj["n_genes"]==n
        assert obj["observed_rho"]==pytest.approx(rho,abs=1e-13)
        assert obj["p_maxT_familywise"]==p
        assert obj["retrospective_fwer_signal"] is pass_module
        assert obj["p_nominal"]<=obj["p_maxT_familywise"]
    assert result["module_effect_difference_tested"] is False
    assert result["negative_control_housekeeping_panel_available"] is False
    assert result["original_nearest_two_predictor_still_FAIL"] is True
    assert result["not_an_independent_radiation_replication"] is True
    assert result["original_camellia_AJB_and_EL_science_unchanged"] is True
