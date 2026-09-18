from __future__ import annotations

import importlib.util
import io
import zipfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "recover_flowerclades51_appendix_s2_v0_1.py"
spec = importlib.util.spec_from_file_location("recover", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def synthetic_docx() -> bytes:
    document = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
 <w:body>
  <w:tbl>
   <w:tr><w:tc><w:p><w:r><w:t>Clade</w:t></w:r></w:p></w:tc><w:tc><w:p><w:r><w:t>Flower transitions</w:t></w:r></w:p></w:tc></w:tr>
   <w:tr><w:tc><w:p><w:r><w:t>Ilex</w:t></w:r></w:p></w:tc><w:tc><w:p><w:r><w:t>12.5</w:t></w:r></w:p></w:tc></w:tr>
  </w:tbl>
 </w:body>
</w:document>"""
    content_types = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""
    bio = io.BytesIO()
    with zipfile.ZipFile(bio, "w") as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("word/document.xml", document)
    return bio.getvalue()


def test_valid_docx_bytes_accepts_word_document_zip():
    assert mod.valid_docx_bytes(synthetic_docx())


def test_valid_docx_bytes_rejects_html_interstitial():
    assert not mod.valid_docx_bytes(b"<html><title>Access denied</title></html>")


def test_extract_tables_returns_cell_text_in_order():
    tables = mod.extract_tables_from_docx_bytes(synthetic_docx())
    assert tables == [[["Clade", "Flower transitions"], ["Ilex", "12.5"]]]
