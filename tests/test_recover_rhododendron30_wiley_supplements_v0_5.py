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
    x=office_bytes("xlsx"); d=office_bytes("docx")
    assert mod.valid_office(x,"xlsx")
    assert not mod.valid_office(x,"docx")
    assert mod.valid_office(d,"docx")
    assert not mod.valid_office(d,"xlsx")


def test_extract_filename_urls_from_html_and_text():
    fn="plb12649-sup-0001-TableS1-S2.xlsx"
    body=(f'<a href="/action/downloadSupplement?file={fn}">x</a> '
          f'https://cdn.example/{fn}').encode()
    out=mod.extract_filename_urls(body,fn,"https://onlinelibrary.wiley.com/doi/x")
    assert any(u.startswith("https://onlinelibrary.wiley.com/action/") for u in out)
    assert any(u.startswith("https://cdn.example/") for u in out)


def test_parse_cdx_and_bounded_archive_candidates():
    body=json.dumps([
        ["timestamp","original","statuscode","mimetype","digest","length"],
        ["20190101000000","https://x/y.xlsx","200","application/octet-stream","A","123"],
        ["20200102030405","https://x/y.xlsx","200","application/octet-stream","B","123"],
        ["20240102030405","https://x/y.xlsx","200","application/octet-stream","C","123"],
    ]).encode()
    rows=mod.parse_cdx(body)
    urls=mod.bounded_archive_candidates(rows)
    assert urls==[
        "https://web.archive.org/web/20190101000000id_/https://x/y.xlsx",
        "https://web.archive.org/web/20240102030405id_/https://x/y.xlsx",
    ]


def test_direct_candidates_are_bounded_and_include_canonical_route():
    fn="plb12649-sup-0001-TableS1-S2.xlsx"
    urls=mod.direct_candidates(fn)
    assert len(urls)==3
    assert urls[0]==mod.canonical_url(fn)
    assert "action/downloadSupplement" in urls[0]
    assert any("/doi/suppl/" in u for u in urls)
