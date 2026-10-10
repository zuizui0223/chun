from __future__ import annotations
import importlib.util
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
GATE=ROOT/"data/iochrominae_2015_published_tree_archive_identity_gate_v0_1.json"
SCRIPT=ROOT/"scripts/recover_iochrominae_2015_exact_tree_archive_v0_1.py"
spec=importlib.util.spec_from_file_location("original_tree_transport",SCRIPT)
mod=importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)

def test_frozen_original_tree_digest_and_public_origin():
    d=json.loads(GATE.read_text(encoding="utf-8"))
    assert d["status"]=="ORIGINAL_2015_TREE_ARCHIVE_IDENTITY_FROZEN_BEFORE_BYTES"
    assert d["source_doi"]=="10.5061/dryad.0732g"
    assert d["dryad_version_id"]==3567
    assert d["filename"]=="ModeandTempoFlColor.zip"
    assert d["expected_size_bytes"]==686186
    assert d["expected_md5"]=="78957f5320749f5c022de78e8ad1ab32"
    assert d["independent_replication_status"]=="HOLD"

def test_wrong_checksum_is_fail_closed_without_opening_tree(monkeypatch,tmp_path):
    g=json.loads(GATE.read_text(encoding="utf-8"))
    data={"_embedded":{"stash:files":[{
        "path":g["filename"],"size":g["expected_size_bytes"],
        "digest":g["expected_md5"],
        "_links":{"self":{"href":"/api/v2/files/9876"}}
    }]}}
    monkeypatch.setattr(mod,"get_json",lambda *args,**kwargs:data)
    monkeypatch.setattr(mod,"downloaded",lambda *args,**kwargs:b"wrong bytes")
    r=mod.inspect_transport(g,tmp_path)
    assert r["status"].startswith("HOLD_")
    assert r["exact_file"] is None
    assert not (tmp_path/g["filename"]).exists()
    assert r["tree_members_opened"] is False
    assert r["qpcr_outcomes_opened"] is False

def test_admit_only_exact_verbatim_archive_bytes(monkeypatch,tmp_path):
    # A synthetic short-archive test; never reads a real biological tree.
    raw=b"ARBITRARY SOURCE DATA"
    g={
        "source_doi":"10.5061/dryad.test","public_api_source":"https://datadryad.org/api/v2/versions/1/files",
        "filename":"synthetic.zip","expected_size_bytes":len(raw),
        "expected_md5":hashlib.md5(raw).hexdigest()
    }
    metadata={"_embedded":{"stash:files":[{
        "path":g["filename"],"size":len(raw),"digest":g["expected_md5"],
        "_links":{"self":{"href":"/api/v2/files/123"}}
    }]}}
    monkeypatch.setattr(mod,"get_json",lambda *args,**kwargs:metadata)
    monkeypatch.setattr(mod,"downloaded",lambda *args,**kwargs:raw)
    r=mod.inspect_transport(g,tmp_path)
    assert r["status"]=="ORIGINAL_TREE_ARCHIVE_EXACT_BYTES_VERIFIED_SOURCE_PREFLIGHT_ONLY"
    assert r["exact_file"]["md5"]==g["expected_md5"]
    assert r["tree_members_opened"] is False
    assert r["independent_replication_pass"] is False
