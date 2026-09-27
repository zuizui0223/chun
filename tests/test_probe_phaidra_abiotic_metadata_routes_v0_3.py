from __future__ import annotations
import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts"/"probe_phaidra_abiotic_metadata_routes_v0_3.py"
spec=importlib.util.spec_from_file_location("m",SCRIPT)
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

def test_routes_include_metadata_handle_oai_and_frontend():
    labels={x[0] for x in m.routes("o:2098641")}
    assert {"services_metadata","services_jsonld","handle_api","oai_simple","frontend_detail"} <= labels

def test_body_summary_extracts_metadata_only_signals():
    b=b'10.1002/ajb2.70044 o:123 environment.csv'
    x=m.body_summary(b)
    assert x["contains_article_doi"] is True
    assert x["pids"]==["o:123"]
    assert any("environment.csv" in z for z in x["filenames"])
