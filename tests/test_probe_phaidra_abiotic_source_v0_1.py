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
