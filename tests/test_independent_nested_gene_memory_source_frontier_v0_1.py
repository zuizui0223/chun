from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTIER = ROOT / "data/independent_nested_gene_memory_source_frontier_v0_1.json"


def test_independent_expression_bridge_remains_unreplicated() -> None:
    d = json.loads(FRONTIER.read_text(encoding="utf-8"))
    assert d["status"].startswith("INDEPENDENT_MATCHED_RADIATION_SOURCE_PREFLIGHT")
    assert d["admission_status"]["independently_replicated_petunieae_exact_sixbit_conditional_21gene_test"] is False
    assert d["admission_status"]["numeric_new_radiations_admitted"] == 0
    assert d["admission_status"]["no_figure_digitization_as_raw_numeric_source"] is True
    assert d["admission_status"]["no_post_hoc_state_binning"] is True


def test_iochrominae_publications_and_tree_objects_cannot_be_conflated() -> None:
    d = json.loads(FRONTIER.read_text(encoding="utf-8"))
    by = {x["id"]: x for x in d["candidates"]}
    q = by["IOCHROMINAE_LARTER2018_QPCR"]
    dev = by["IOCHROMINAE_LARTER2019_DVDY"]
    assert q["source_paper_doi"] == "10.1093/molbev/msy117"
    assert q["original_analysis_tree_doi"] == "10.3732/ajb.1500163"
    assert q["original_tree_data_doi"] == "10.5061/dryad.0732g"
    assert q["distinct_2018_shape_tree"]["doi"] == "10.5061/dryad.5jn7b"
    assert q["numeric_species_by_gene_expression_table_verified"] is False
    assert q["species_level_tree_raw_bytes_verified"] is False
    assert q["numeric_species_by_pigment_identity_verified"] is False
    assert q["current_status"].startswith("HOLD_")
    assert dev["source_data_doi"] == "10.5061/dryad.p5dq84v"
    assert dev["current_status"].startswith("HOLD_")
    assert dev["required_archive"]["md5"] == "76b46e384fb7c9bf1ef3fbd7d1e5d2f0"
    assert "do not change the frozen exact-profile denominator" in dev["use_policy"]


def test_no_other_candidate_is_falsely_promoted() -> None:
    d = json.loads(FRONTIER.read_text(encoding="utf-8"))
    assert len(d["candidates"]) == 7
    assert all(x.get("current_status",x.get("status","")).startswith(("HOLD_","PIGMENT_","INDEPENDENT_","SMALL_"))
               for x in d["candidates"])


def test_original_iochrominae_tree_http401_is_source_access_hold_not_negative_result():
    receipt=json.loads((ROOT/"data/iochrominae_2015_exact_tree_transport_receipt_v0_1.json").read_text(encoding="utf-8"))
    gate=json.loads((ROOT/"data/iochrominae_2015_published_tree_archive_identity_gate_v0_1.json").read_text(encoding="utf-8"))
    assert receipt["source_doi"] == gate["source_doi"] == "10.5061/dryad.0732g"
    assert receipt["file"] == gate["filename"]
    assert receipt["expected_md5"] == gate["expected_md5"]
    assert receipt["metadata_source_confirmed"] is True
    assert receipt["source_archive_bytes_recovered"] is False
    assert receipt["additional_replicate_admitted"] is False
    assert len(receipt["attempts"]) == 2
    assert all(x["result"] == "HTTP_401_UNAUTHORIZED" for x in receipt["attempts"])
    assert receipt["expression_2018_28taxa_qpcr_numeric_table_recovered"] is False
    assert receipt["phylogenetic_tree_members_examined"] is False
    assert receipt["changed_frozen_science"] is False


def test_epimedium_not_qualified_as_an_independent_same_tip_gene_memory_replication():
    d=json.loads(FRONTIER.read_text(encoding="utf-8"))
    by={x["id"]:x for x in d["candidates"]}
    epi=by["EPIMEDIUM_MI2023_EIGHT_ACCESSIONS"]
    assert epi["source_paper_doi"]=="10.3389/fpls.2023.1133616"
    assert epi["qPCR_accession_n"]==8
    assert epi["qpcr_pathway_gene_n"]==12
    assert epi["qPCR_to_tree_accession_crosswalk_verified"] is False
    assert epi["exact_molecular_sample_tree_source_match"] is False
    assert epi["replicate_admitted"] is False
    assert epi["current_status"].startswith("HOLD_")
    assert {"Epimedium acuminatum","Epimedium leptorrhizum"} <= set(epi["known_polymorphism_in_molecular_A_plus_taxa"])


def test_iochroma_2025_backcross_samples_are_not_independent_species_tips():
    d=json.loads(FRONTIER.read_text(encoding="utf-8"))
    by={x["id"]:x for x in d["candidates"]}
    w=by["IOCHROMA_WHEELER2025_SIX_SPECIES"]
    assert w["source_paper_doi"]=="10.1093/g3journal/jkaf230"
    assert w["source_data_doi"]=="10.17605/OSF.IO/J5M8F"
    assert w["comparative_rnaseq_n"]==6
    assert w["within_species_backcross_individuals"]==24
    assert w["replicate_admitted"] is False
    assert w["current_status"].startswith("SMALL_")
