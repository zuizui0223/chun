from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts"/"recover_iochrominae_preservation_mirrors_v0_4.py"
spec=importlib.util.spec_from_file_location("rec",SCRIPT)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_exact_requires_both_size_and_md5():
    body=b"abc"
    spec={"size":3,"md5":"900150983cd24fb0d6963f7d28e17f72"}
    assert mod.exact(body,spec)
    assert not mod.exact(body+b"x",spec)
    assert not mod.exact(body,{"size":3,"md5":"0"*32})


def test_parse_cdx_and_archive_bounds():
    body=json.dumps([
        ["timestamp","original","statuscode","mimetype","digest","length"],
        ["20190101000000","https://x/file","200","application/octet-stream","A","10"],
        ["20200101000000","https://x/file","200","application/octet-stream","B","10"],
        ["20240101000000","https://x/file","200","application/octet-stream","C","10"],
    ]).encode()
    rows=mod.parse_cdx(body)
    assert mod.archive_urls(rows)==[
        "https://web.archive.org/web/20190101000000id_/https://x/file",
        "https://web.archive.org/web/20240101000000id_/https://x/file",
    ]


def test_dryad_direct_urls_cover_api_and_stash():
    urls=mod.dryad_direct_urls(mod.OBJECTS["archive"])
    assert any("/api/v2/files/108456/download" in u for u in urls)
    assert any("/stash/downloads/file_stream/108456" in u for u in urls)


def test_zenodo_queries_include_doi_filename_and_digest():
    spec=mod.OBJECTS["readme"]
    qs=mod.zenodo_queries(spec)
    assert mod.DOI in qs
    assert any(spec["filename"] in q for q in qs)
    assert spec["md5"] in qs
