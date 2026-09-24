from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts"/"probe_ng2018_solanaceae_sources_v0_1.py"
spec=importlib.util.spec_from_file_location("probe",SCRIPT)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_extract_supplement_urls_filters_target():
    html=b'<a href="https://cdn.example/evo13589-sup-0002-tables1.xlsx?x=1">Table S1</a><a href="x">other</a>'
    urls=mod.extract_supplement_urls(html)
    assert urls==["https://cdn.example/evo13589-sup-0002-tables1.xlsx?x=1"]


def test_treebase_candidate_endpoints_include_nexml():
    urls=mod.treebase_candidate_urls("S23063")
    assert any("phylows" in u and "nexml" in u.lower() for u in urls)


def test_xlsx_signature_rejects_html():
    assert mod.xlsxish(b"PK\x03\x04abc")
    assert not mod.xlsxish(b"<html>blocked</html>")
