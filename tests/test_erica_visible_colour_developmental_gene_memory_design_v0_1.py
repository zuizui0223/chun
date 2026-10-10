from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "data/erica_predeclared_visible_colour_developmental_gene_memory_design_v0_1.json"
C = ROOT / "data/erica_table2_visible_colour_qpcr_taxon_crosswalk_v0_1.json"


def test_biological_unit_and_all_21_stages_genes_are_frozen():
    d = json.loads(D.read_text(encoding="utf-8"))
    assert d["status"] == "FIXED_BEFORE_ANY_ERICA_TREE_EXPRESSION_OUTCOME_SOURCE_PREVIOUSLY_AVAILABLE"
    genes = d["molecular_features"]["original_genes"]
    stages = d["molecular_features"]["flower_age_stages"]
    assert len(genes) == 7 and len(set(genes)) == 7
    assert stages == ["juvenile", "intermediate", "adult"]
    assert d["primary_test"]["seed"] == 20261010
    assert d["primary_test"]["permutations"] == 9999
    assert d["frame"]["eligible_single_colour_taxon_labels_before_tree_join"] == 27
    assert d["frame"]["upper_bound_within_color_unordered_pairs"] == 117
    assert d["frame"]["one_multimorph_plukenetii_lineage_excluded_from_primary"]


def test_no_automatic_colour_code_or_fuzzy_taxon_matching():
    d = json.loads(D.read_text(encoding="utf-8"))
    c = json.loads(C.read_text(encoding="utf-8"))
    assert len(c["taxa"]) == 30
    assert sum(d["frame"]["original_color_counts"].values()) == 27
    assert d["frame"]["aliases"].startswith("explicit voucher")
    assert d["firewall"]["do_not_recode_red_plus_pink_after_outcome"]
    assert d["firewall"]["do_not_select_stage_genes_or_tip_set_by_test_sign"]
    assert d["source"]["source_pigment_sixbit_values_measured"] is False
    assert d["firewall"]["does_not_reuse_petunieae_sixbit_identity"]


def test_source_tree_unavailability_requires_structural_hold_not_negative_science():
    d = json.loads(D.read_text(encoding="utf-8"))
    assert d["firewall"]["do_not_test_before_source_tree_is_admitted"]
    assert d["frame"]["eligible_joined_tips_at_least"] == 20
    assert d["frame"]["eligible_within_visible_color_pairs_at_least"] == 40
    assert d["frame"]["eligible_distinct_color_states_with_at_least_3_tips"] == 2
    assert "HOLD" in d["primary_test"]["structural_hold_rule"]
    assert "NOT_SUPPORTED" in d["primary_test"]["not_supported_rule"]
    assert d["firewall"]["original_frozen_camellia_ajb_and_el_unchanged"]
