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
    assert len(d["candidates"]) == 5
    assert all(x.get("current_status",x.get("status","")).startswith(("HOLD_","PIGMENT_","INDEPENDENT_","SMALL_"))
               for x in d["candidates"])
