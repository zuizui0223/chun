from __future__ import annotations
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"scripts/preflight_iochrominae_2018_matched_source_metadata_v0_1.py"
D=ROOT/"data/independent_nested_gene_memory_source_frontier_v0_1.json"
spec=importlib.util.spec_from_file_location("source_preflight",P)
mod=importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)

def test_metadata_only_source_identities_are_distinct():
    assert mod.DOIS==("10.5061/dryad.0732g","10.5061/dryad.5jn7b")
    d=json.loads(D.read_text(encoding="utf-8"))
    c={x["id"]:x for x in d["candidates"]}
    assert c["IOCHROMINAE_LARTER2018_QPCR"]["source_paper_doi"]=="10.1093/molbev/msy117"
    assert c["IOCHROMINAE_LARTER2018_QPCR"]["original_tree_data_doi"]==mod.DOIS[0]
    assert c["IOCHROMINAE_LARTER2018_QPCR"]["distinct_2018_shape_tree"]["doi"]==mod.DOIS[1]
    assert c["IOCHROMINAE_LARTER2019_DVDY"]["source_data_doi"] not in mod.DOIS

def test_preflight_never_opens_numeric_outcomes(monkeypatch):
    urls=[]
    def fake(doi,timeout):
        urls.append(doi)
        return {"doi":doi,"resolved":False,"versions":[],"files":[]}
    monkeypatch.setattr(mod,"metadata_one",fake)
    result=mod.preflight()
    assert urls==list(mod.DOIS)
    assert result["direct_replication_completed"] is False
    assert result["no_trait_or_expression_rows_opened"] is True
    assert result["required_numeric_2018_qpcr_species_matrix_verified"] is False
    assert result["required_exact_source_tree_payload_verified"] is False
    assert result["status"].startswith("HOLD_")

def test_metadata_one_fails_closed_on_http_or_schema_error(monkeypatch):
    def fake_get(url, timeout):
        raise ValueError("unexpected metadata response")
    monkeypatch.setattr(mod,"get_json",fake_get)
    report=mod.metadata_one(mod.DOIS[0],timeout=1)
    assert report["resolved"] is False
    assert report["files"]==[]
    assert report["error_type"]=="ValueError"
