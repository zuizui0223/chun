from __future__ import annotations

import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "probe_phaidra_abiotic_source_v0_1.py"
spec = importlib.util.spec_from_file_location("probe", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_extract_pids_handles_nested_api_payload():
    payload = {"members": [{"pid": "o:1"}, {"object": {"pid": "o:2"}}], "noise": "x"}
    assert mod.extract_pids(payload) == ["o:1", "o:2"]


def test_flatten_info_extracts_filename_and_mimetype():
    payload = {
        "metadata": {"json-ld": {
            "ebucore:filename": [{"@value": "climate.csv"}],
            "ebucore:hasMimeType": [{"@value": "text/csv"}],
            "dce:title": [{"bf:mainTitle": [{"@value": "Climate data"}]}]
        }},
        "size": 1234
    }
    out = mod.summarize_info("o:9", payload)
    assert out["pid"] == "o:9"
    assert out["filename"] == "climate.csv"
    assert out["mimetype"] == "text/csv"
    assert out["size"] == 1234


def test_extract_pids_can_exclude_current_root():
    payload = {"members": ["o:2098641", "o:3", "o:4"]}
    assert mod.extract_pids(payload, exclude=("o:2098641",)) == ["o:3", "o:4"]


def test_choose_source_requires_exactly_one_metadata_supported_candidate():
    roots = [
        {"pid":"o:1","provenance":"old","root_object":None,"members":[]},
        {"pid":"o:2","provenance":"new","root_object":{"candidate_environment_or_code":True},"members":[]},
    ]
    assert mod.choose_source(roots)["pid"] == "o:2"
    roots[0]["root_object"]={"candidate_environment_or_code":True}
    assert mod.choose_source(roots) is None
