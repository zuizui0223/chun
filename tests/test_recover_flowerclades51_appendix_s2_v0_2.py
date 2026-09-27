from __future__ import annotations

import importlib.util
import io
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts"/"recover_flowerclades51_appendix_s2_v0_2.py"
spec=importlib.util.spec_from_file_location("rec2",SCRIPT)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def minimal_docx()->bytes:
    b=io.BytesIO()
    with zipfile.ZipFile(b,"w") as z:
        z.writestr("[Content_Types].xml",
                   '<Types><Override ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
        z.writestr("word/document.xml",
                   '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body/></w:document>')
    return b.getvalue()


def test_valid_docx_signature_and_members():
    assert mod.valid_docx_bytes(minimal_docx())
    assert not mod.valid_docx_bytes(b"<html>blocked</html>")


def test_static_candidates_include_current_supinfo_routes():
    urls=mod.static_candidate_urls()
    assert any("/doi/suppl/10.1002/ajb2.70146/supinfo/" in u for u in urls)
    assert any("bsapubs.onlinelibrary.wiley.com" in u for u in urls)
    assert any("/action/downloadSupplement?" in u for u in urls)


def test_table_inventory_flags_tokens():
    inv=mod.table_inventory([[["Clade","Mean flower transitions"],["A","12.3"]]])
    assert inv[0]["contains_clade_token"] is True
    assert inv[0]["contains_transition_token"] is True
