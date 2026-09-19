from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path

SCRIPT=Path(__file__).resolve().parents[1]/"scripts"/"recheck_rhododendron30_source_access_v0_3.py"
spec=importlib.util.spec_from_file_location("rhodorecheck",SCRIPT)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_tree_payload_requires_exact_sha_and_newick_shape():
    body=b"(A:0.1,B:0.2);\n"
    digest=hashlib.sha256(body).hexdigest()
    ok=mod.validate_tree_payload(body,"text/plain",digest)
    assert ok["digest_match"] is True
    assert ok["treeish_payload"] is True
    bad=mod.validate_tree_payload(b"<html>blocked</html>","text/html",digest)
    assert bad["digest_match"] is False
    assert bad["treeish_payload"] is False


def test_dryad_candidate_urls_include_api_and_stash_routes():
    urls=mod.dryad_candidate_urls(1853438,{})
    assert "https://datadryad.org/api/v2/files/1853438/download" in urls
    assert "https://datadryad.org/stash/downloads/file_stream/1853438" in urls


def test_status_pass_requires_both_trait_and_tree_and_crosswalk():
    assert mod.decide_status(True,True,23)=="SOURCE_ACCESS_AND_CROSSWALK_PASS_CHEMISTRY_STILL_UNOPENED"
    assert mod.decide_status(False,True,23)=="HOLD_SOURCE_ACCESS_STILL_BLOCKED_OUTCOMES_UNOPENED"
    assert mod.decide_status(True,False,23)=="HOLD_SOURCE_ACCESS_STILL_BLOCKED_OUTCOMES_UNOPENED"
    assert mod.decide_status(True,True,19)=="HOLD_CROSSWALK_OR_TREE_COVERAGE_OUTCOMES_UNOPENED"
