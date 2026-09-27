from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts"/"probe_phaidra_abiotic_source_v0_2.py"
spec=importlib.util.spec_from_file_location("probe",SCRIPT)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_extract_pids_from_nested_payload():
    x={"response":{"docs":[{"pid":"o:12"},{"link":"info:fedora/o:13"}]}}
    assert mod.extract_pids(x)==["o:12","o:13"]


def test_relevant_text_detects_environmental_file():
    assert mod.relevant_text("clade_temperature_aridity_uv.csv",None,None,None)
    assert mod.relevant_text(None,"Does the abiotic environment influence the distribution of flower and fruit colors?",None,None)
    assert not mod.relevant_text("unrelated.pdf","unrelated object",None,None)


def test_summarize_payload_collects_related_pids_and_filename():
    payload={
        "pid":"o:9",
        "metadata":{"json-ld":{
            "ebucore:filename":[{"@value":"environment.csv"}],
            "ebucore:hasMimeType":[{"@value":"text/csv"}],
            "dce:title":[{"bf:mainTitle":[{"@value":"Abiotic environment data"}]}],
        }},
        "relations":["info:fedora/o:10","o:11"],
    }
    out=mod.summarize_payload("o:9",payload)
    assert out["filename"]=="environment.csv"
    assert out["mimetype"]=="text/csv"
    assert out["article_or_environment_relevant"] is True
    assert out["related_pids"]==["o:10","o:11"]


def test_search_contract_includes_both_membership_field_names():
    assert "isPartOf" in mod.MEMBERSHIP_FIELDS
    assert "ismemberof" in mod.MEMBERSHIP_FIELDS
    assert "search/select" in mod.SEARCH_PATHS
    assert "solr/select" in mod.SEARCH_PATHS
