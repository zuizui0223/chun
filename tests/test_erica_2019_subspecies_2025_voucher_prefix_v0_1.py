from __future__ import annotations
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FILE=ROOT/"scripts/audit_erica_2019_subspecies_to_2025_voucher_prefix_v0_1.py"
spec=importlib.util.spec_from_file_location("erica_subsp2025_source",FILE)
m=importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(m)

CROSS=ROOT/"data/erica_table2_visible_colour_qpcr_taxon_crosswalk_v0_1.json"
PUBLISHED=ROOT/"data/erica_2019_published_subspecies_2025_tree_prefix_contract_v0_1.json"
TREE=ROOT/"results/erica_hoekstra2025_source_tree_lexical_and_voucher_support_v0_1.json"


def inputs():
    return (json.loads(CROSS.read_text(encoding="utf-8")),
            json.loads(PUBLISHED.read_text(encoding="utf-8")),
            json.loads(TREE.read_text(encoding="utf-8")))


def test_all_original_tree_partitions_gain_three_unambiguous_prefixes():
    answer=m.check(*inputs())
    assert answer["status"].startswith("HOLD_PUBLISHED_SUBSPECIES_RESOLVES_3")
    assert answer["prior_one_tip_candidate_taxa"]==11
    assert answer["current_one_tip_candidate_taxa"]==14
    assert answer["prior_one_tip_candidate_pairs"]==20
    assert answer["current_one_tip_candidate_pairs"]==31
    assert len(answer["trees"])==3
    for result in answer["trees"]:
        assert result["matched_taxon_candidates"]==22
        assert result["unique_candidate_taxa"]==14
        assert result["multiple_voucher_taxa"]==8
        assert result["max_same_colour_pairs_one_tip_candidates_not_admitted"]==31
        assert result["unique_by_colour"]=={"pink":5,"red":7,"white":1,"yellow":1}
        assert result["missing_source_taxa"]==[
            "Erica_sparmanii","Erica_plukenetii_breviflora",
            "Erica_mammosa","Erica_filipendula","Erica_annectans",
        ]


def test_published_subspecies_remove_only_unpublished_variants():
    ans=m.check(*inputs())
    expected={
        "Erica_discolor":["discolor_spe_MP1217"],
        "Erica_unicolor":["unicolor_uni_MP1249"],
        "Erica_stagnalis":["stagnalis_sta_MP668"],
    }
    for tree in ans["trees"]:
        indexed={x["qpcr_source_taxon"]:x for x in tree["source_taxa"]}
        for key,allowed in expected.items():
            assert indexed[key]["remaining_tip_candidates"]==allowed
        assert indexed["Erica_coccinea"]["remaining_count"]==3
        assert indexed["Erica_regia"]["remaining_count"]==2
        assert indexed["Erica_abietina"]["remaining_count"]==2
        assert indexed["Erica_viscaria"]["remaining_count"]==4
        assert indexed["Erica_plukenetii_breviflora"]["remaining_count"]==0


def test_source_access_is_not_phylogenetic_memory_admission():
    ans=m.check(*inputs())
    assert ans["original_design_min_taxa"]==20
    assert ans["original_design_min_same_colour_pairs"]==40
    assert ans["source_gate_is_not_the_gene_expression_test"]
    assert ans["no_voucher_or_exact_sample_equivalence_proven"]
    assert ans["no_gene_expression_phylogenetic_rho"]
    assert ans["no_permutation_p_value"]
    assert ans["no_independent_replication_admitted"]
    assert ans["frozen_AJB_EL_unchanged"]


def test_reject_undeclared_autonym_and_missing_original_row():
    d,p,t=inputs()
    p["subspecies_from_published_methods"].append({
       "qpcr_label":"Erica_cameronii","tree_tip_prefix":"cameronii_cam_"})
    try:
        m.check(d,p,t)
        raise AssertionError("undeclared rule was accepted")
    except ValueError as e:
        assert "seven" in str(e)
