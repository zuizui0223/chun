from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RESULT=ROOT/"results/erica_hoekstra2025_voucher_monophyly_source_gate_v0_1.json"

def test_exact_source_monophyly_rules_do_not_invent_species_clades():
    x=json.loads(RESULT.read_text(encoding="utf-8"))
    assert x["source_original_archive_doi"]=="10.3897/phytokeys.257.139457.suppl3"
    assert x["source_original_md5"]=="d4363c6e604784b58c91d8a1d824a1f1"
    assert len(x["trees"])==3
    assert x["candidate_taxa_any_voucher"]==22
    assert x["unambiguous_unique_tip_taxa"]==11
    assert x["unambiguous_same_colour_pairs"]==20
    assert x["predeclared_min_taxa"]==20
    assert x["predeclared_min_pairs"]==40
    for tree in x["trees"]:
        assert tree["multi"]==11 and tree["single"]==11
        assert tree["monophyly"]=={"False":11}
        assert len(tree["ambiguous_species"])==11
        assert all(z["unmatched_descendants"]>0 for z in tree["ambiguous_species"])

def test_legal_inference_status_is_hold_not_falsification():
    x=json.loads(RESULT.read_text(encoding="utf-8"))
    assert x["status"].startswith("HOLD")
    assert x["new_regulatory_expression_statistic_calculated"] is False
    assert x["independent_replication_admitted"] is False
    assert x["negative_biological_evidence_claimed"] is False
    assert x["full_22_not_admitted_as_single_species_tips"] is True
    assert x["original_camellia_AJB_and_EL_unchanged"] is True
