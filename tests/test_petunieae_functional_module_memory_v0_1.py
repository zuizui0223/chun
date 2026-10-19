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
