from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/"results/erica_hoekstra2025_source_tree_lexical_and_voucher_support_v0_1.json"

def test_three_source_trees_are_real_but_not_three_replications():
    r=json.loads(PATH.read_text(encoding="utf-8"))
    assert r["source_archive_doi"]=="10.3897/phytokeys.257.139457.suppl3"
    assert r["published_original_zip_md5"]=="d4363c6e604784b58c91d8a1d824a1f1"
    assert len(r["trees"])==3
    assert {t["original_tree_tip_count"] for t in r["trees"]}=={771,749,744}
    assert all(t["unverified_epithet_prefix_taxa"]==22 for t in r["trees"])
    assert all(t["possible_pairs_before_voucher_resolution"]==83 for t in r["trees"])
    assert all(t["unique_candidate_tip_taxa"]==11 for t in r["trees"])
    assert all(t["unique_candidate_tip_possible_pairs"]==20 for t in r["trees"])
    assert all(len(t["ambiguous_multi_voucher_taxa"])==11 for t in r["trees"])
    assert r["original_2016_tree_replaced"] is False
    assert r["inference"]["admitted_independent_replication"] is False
    assert r["inference"]["new_regulatory_memory_rho"] is None
    assert r["inference"]["new_p_value"] is None

def test_strict_source_identity_support_hold_not_false_biological_fail():
    r=json.loads(PATH.read_text(encoding="utf-8"))
    gate=r["strict_unique_tip_gate"]
    assert gate["predeclared_min_taxa"]==20
    assert gate["predeclared_min_same_colour_pairs"]==40
    assert gate["unambiguous_candidate_count"]==11
    assert gate["unambiguous_possible_pairs"]==20
    assert gate["status"].startswith("HOLD_")
    assert all(sum(t["unique_candidate_tip_by_colour"].values())==11 for t in r["trees"])
    assert all(sum(len(v["tip_ids"]) for v in t["ambiguous_multi_voucher_taxa"])>11 for t in r["trees"])
    assert r["inference"]["source_2019_qPCR_not_same_individuals_as_2025_vouchers"]
    assert r["inference"]["original_frozen_AJB_EL_unchanged"]
