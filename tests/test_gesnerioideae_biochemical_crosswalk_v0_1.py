from __future__ import annotations

import importlib.util
import io
from pathlib import Path

from Bio import Phylo

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts"/"preflight_gesnerioideae_biochemical_crosswalk_v0_1.py"
spec=importlib.util.spec_from_file_location("cw",SCRIPT)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_species_key_uses_first_binomial_only():
    assert mod.species_key("Columnea consanguinea subsp. x")=="columnea_consanguinea"
    assert mod.species_key("  Columnea_consanguinea  ")=="columnea_consanguinea"


def test_tree_tip_prefix_rule_accepts_voucher_suffixes():
    assert mod.tip_matches_key("Columnea_consanguinea_ET_1082_ITS","columnea_consanguinea")
    assert mod.tip_matches_key("Achimenes_admirabilis31","achimenes_admirabilis")
    assert mod.tip_matches_key("Alsobia_punctataP163","alsobia_punctata")
    assert not mod.tip_matches_key("Columnea_consanguineoides_X","columnea_consanguinea")


def test_unique_crosswalk_excludes_unmatched_and_flags_ambiguity():
    source=["A a","B b","C c"]
    tips=["A_a_X","B_b1","B_b2","OUT_x"]
    out=mod.build_crosswalk(source,tips)
    assert out["matched_species"]==1
    assert out["unmatched_source_keys"]==["c_c"]
    assert out["ambiguous_source_keys"]==["b_b"]


def test_identifier_resolver_uses_voucher_before_living_collection():
    cand=["A_a_JLC_6974_ITS","A_a_P246"]
    chosen,field=mod.resolve_candidate_by_source_identifiers(
        cand,{"voucher":"JLC 6974","living_collection_id":"P246"}
    )
    assert chosen=="A_a_JLC_6974_ITS"
    assert field=="voucher"


def test_build_crosswalk_resolves_species_ambiguity_by_source_identifier():
    source=["A a"]
    tips=["A_a_X1","A_a_P230"]
    out=mod.build_crosswalk(
        source,tips,{"a_a":{"voucher":None,"living_collection_id":"P230"}}
    )
    assert out["matched_species"]==1
    assert out["ambiguous_source_keys"]==[]
    assert out["identifier_resolved_species"]==["a_a"]
    assert out["matches"][0]["tree_tip"]=="A_a_P230"


def test_pruned_tree_keeps_exact_matched_tip_set():
    tree=Phylo.read(io.StringIO("((A_a_X:1,B_b1:1):1,C_c_X:1);"),"newick")
    out=mod.pruned_tree(tree,["A_a_X","C_c_X"])
    assert {t.name for t in out.get_terminals()}=={"A_a_X","C_c_X"}
