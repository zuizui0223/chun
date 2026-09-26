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


def test_static_supplement_candidates_cover_oup_cdn_and_wiley_legacy():
    urls=mod.static_supplement_candidates()
    assert any("oup.silverchair-cdn.com/oup/backfile/" in u for u in urls)
    assert any("onlinelibrary.wiley.com/action/downloadSupplement" in u for u in urls)
    assert any("evo13589-sup-0002-TableS1.xlsx" in u for u in urls)


def test_treebase_candidate_endpoints_include_http_and_https_phylows():
    urls=mod.treebase_candidate_urls("S23063")
    assert any(u.startswith("https://purl.org/phylo/treebase/phylows/study/") and "format=nexml" in u for u in urls)
    assert any(u.startswith("http://purl.org/phylo/treebase/phylows/study/") and "format=nexus" in u for u in urls)


def test_treebase_candidates_include_official_download_a_study_route():
    urls=mod.treebase_candidate_urls("S23063")
    assert any("search/downloadAStudy.html?id=23063&format=nexml" in u for u in urls)
    assert any("search/downloadAStudy.html?id=23063&format=nexus" in u for u in urls)


def test_extract_treebase_download_urls_from_summary_html():
    body=b'<a href="/treebase-web/search/downloadAStudy.html?id=23063&format=nexus">Nexus</a><a href="x">Other</a>'
    urls=mod.extract_treebase_download_urls(body,"https://treebase.org/treebase-web/search/study/summary.html?id=23063")
    assert urls==["https://treebase.org/treebase-web/search/downloadAStudy.html?id=23063&format=nexus"]


def test_xlsx_signature_rejects_html():
    assert mod.xlsxish(b"PK\x03\x04abc")
    assert not mod.xlsxish(b"<html>blocked</html>")


def test_treebase_payload_accepts_nexus_and_xml_not_html():
    assert mod.treebase_payload(b"#NEXUS\nbegin trees;")
    assert mod.treebase_payload(b"<?xml version='1.0'?><nex:nexml/>")
    assert not mod.treebase_payload(b"<html>blocked</html>")
