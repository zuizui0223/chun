from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts"/"recover_schistanthe_source_bytes_v0_1.py"
spec=importlib.util.spec_from_file_location("src",SCRIPT)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_exact_sha_requires_size_and_digest():
    b=b"abc"
    assert mod.exact_sha_match(b,3,hashlib.sha256(b).hexdigest())
    assert not mod.exact_sha_match(b,4,hashlib.sha256(b).hexdigest())
    assert not mod.exact_sha_match(b,3,"0"*64)


def test_csv_header_only_does_not_return_data_rows():
    raw=b"tip,species,color\nA,Rhododendron_a,red\nB,Rhododendron_b,white\n"
    h=mod.csv_header_only(raw)
    assert h==["tip","species","color"]
    assert "red" not in h and "white" not in h


def test_identifier_column_candidates_exclude_color():
    h=["tip","species","flower_color","clade"]
    out=mod.identifier_column_candidates(h)
    assert "tip" in out and "species" in out
    assert "flower_color" not in out
