from __future__ import annotations

import importlib.util
import io
import json
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts"/"recover_rhododendron30_wiley_supplements_v0_5.py"
spec=importlib.util.spec_from_file_location("rec",SCRIPT)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def office_bytes(kind:str)->bytes:
    b=io.BytesIO()
    with zipfile.ZipFile(b,"w") as z:
        z.writestr("[Content_Types].xml","x")
        if kind=="xlsx":
            z.writestr("xl/workbook.xml","x")
        else:
            z.writestr("word/document.xml","x")
    return b.getvalue()


def test_valid_office_distinguishes_xlsx_docx():
    x=office_bytes("xlsx")
    d=office_bytes("docx")
    assert mod.valid_office(x,"xlsx")
    assert not mod.valid_office(x,"docx")
    assert mod.valid_office(d,"docx")
    assert not mod.valid_office(d,"xlsx")


def test_extract_filename_urls_from_html_and_text():
    fn="plb12649-sup-0001-TableS1-S2.xlsx"
    body=(
        f'<a href="/action/downloadSupplement?file={fn}">x</a> '
        f'https://cdn.example/{fn}'
    ).encode()
    out=mod.extract_filename_urls(body,fn,"https://onlinelibrary.wiley.com/doi/x")
    assert any(u.startswith("https://onlinelibrary.wiley.com/action/") for u in out)
    assert any(u.startswith("https://cdn.example/") for u in out)


def test_parse_cdx_and_archive_candidates():
    body=json.dumps([
        ["timestamp","original","statuscode","mimetype","digest","length"],
        ["20200102030405","https://x/y.xlsx","200","application/octet-stream","ABC","123"]
    ]).encode()
    rows=mod.parse_cdx(body)
    assert rows[0]["timestamp"]=="20200102030405"
    urls=mod.archive_candidates(rows)
    assert urls==["https://web.archive.org/web/20200102030405id_/https://x/y.xlsx"]


def test_direct_candidates_cover_legacy_and_static_routes():
    urls=mod.direct_candidates("plb12649-sup-0001-TableS1-S2.xlsx")
    assert any("action/downloadSupplement" in u for u in urls)
    assert any("pb-assets/assets/14388677" in u for u in urls)
