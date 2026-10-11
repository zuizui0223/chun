from __future__ import annotations
import importlib.util
import json
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts/audit_erica_2019_qualitative_chemistry_coverage_v0_1.py"
spec=importlib.util.spec_from_file_location("erica_qualitative_chemistry",SCRIPT)
m=importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(m)

FILES=[
    "data/erica_2019_table2_qualitative_chemistry_source_v0_1.json",
    "data/erica_table2_visible_colour_qpcr_taxon_crosswalk_v0_1.json",
    "results/erica_voucher_averaged_developmental_memory_v0_1/result_v0_1.json",
    "results/petunieae_pigment_adjusted_regulatory_memory_v0_1/result_v0_1.json",
]


def source_data():
    return [json.loads((ROOT/file).read_text(encoding="utf-8")) for file in FILES]


def test_2019_original_qualitative_chemical_coverage_and_red_pink_ambiguity():
    result=m.audit(*source_data())
    assert result["source_only_N_2019_measurement_labels"]==30
    assert result["source_only_N_examined_taxa"]==22
    assert result["source_qualitative_production_counts"]=={
        "NORMAL_ANTHOCYANIN":18,
        "PELARGONIDIN_HEXOSE_NOT_CYANIDIN":2,
        "NO_INTERMEDIATES_EXCEPT_QUERCETINS":1,
        "NO_POST_DFR_INTERMEDIATES_KAEMPFEROL_QUERCETIN":1
    }
    assert result["source_qualitative_chemistry_by_visible_colour"]=={
        "red":{"NORMAL_ANTHOCYANIN":12},
        "pink":{"NORMAL_ANTHOCYANIN":6},
        "white":{"NO_INTERMEDIATES_EXCEPT_QUERCETINS":1,
                 "NO_POST_DFR_INTERMEDIATES_KAEMPFEROL_QUERCETIN":1},
        "yellow":{"PELARGONIDIN_HEXOSE_NOT_CYANIDIN":2}
    }
    assert result["same_visible_hue_unordered_taxon_pairs"]==83
    assert result["same_visible_hue_and_same_qualitative_anthocyanin_label_pairs"]==82
    assert result["different_visible_hue_but_same_qualitative_anthocyanin_label_pairs"]==72
    assert result["different_hue_shared_qualitative_categories"]=={
        "NORMAL_ANTHOCYANIN":72
    }


def test_qualitative_normal_is_not_six_component_pigment_chemical_equality():
    result=m.audit(*source_data())
    assert result["normal_category_means_chemical_compounds_identical"] is False
    assert result["numeric_raw_HPLC_compound_matrix_verified"] is False
    assert result["published_UPLC_graph_is_not_an_exact_six_bit_pigment_profile"] is True
    assert result["Petunieae_exact_biochemical_condition_is_not_met"] is True
    assert result["original_erica_NOT_SUPPORTED_retained"] is True
    assert result["original_erica_P"]==0.4988
    assert result["no_new_expression_phylogenetic_memory_statistic"] is True
    assert result["original_Camellia_AJB_EL_unchanged"] is True


def test_exact_30_original_qpcr_ids_required_and_no_fake_chemical_rows():
    d=source_data()
    d[0]["rows"][-1]["qpcr_label"]="Erica_not_original"
    with pytest.raises(ValueError,match="do not match"):
        m.audit(*d)


def test_hypothesis_not_reclassified_from_null_due_to_qualitative_biochemistry():
    d=source_data()
    d[2]["status"]="SUPPORTED_EXPLORATORY_TAXON_NAME_LEVEL"
    with pytest.raises(ValueError,match="NOT_SUPPORTED"):
        m.audit(*d)
