from __future__ import annotations
import importlib.util
import io
import json
import pathlib
import tempfile
import unittest
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
PATH = ROOT / "scripts/preflight_erica_qpcr_xlsx_source_v0_1.py"
spec = importlib.util.spec_from_file_location("erica_qpcr_preflight", PATH)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)


def workbook_bytes() -> bytes:
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        z.writestr("[Content_Types].xml", "<Types xmlns='http://schemas.openxmlformats.org/package/2006/content-types'/>")
        z.writestr("xl/workbook.xml", """<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
          xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
          <sheets><sheet name="Raw" sheetId="1" r:id="rId1"/></sheets></workbook>""")
        z.writestr("xl/_rels/workbook.xml.rels", """<Relationships
          xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
          <Relationship Id="rId1" Target="worksheets/sheet1.xml"
            Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet"/>
          </Relationships>""")
        z.writestr("xl/sharedStrings.xml", """<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
          <si><t>Erica species</t></si></sst>""")
        z.writestr("xl/worksheets/sheet1.xml", """<worksheet
          xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
          <sheetData><row r="1"><c r="A1" t="s"><v>0</v></c><c r="B1"><v>3.14</v></c></row>
          <row r="2"><c r="A2" t="inlineStr"><is><t>Erica test</t></is></c></row></sheetData>
          </worksheet>""")
    return b.getvalue()


class Response:
    status = 200
    def __init__(self, data: bytes):
        self.data = io.BytesIO(data)
    def read(self, size):
        return self.data.read(size)
    def __enter__(self):
        return self
    def __exit__(self, *_):
        return False


class PreflightTest(unittest.TestCase):
    def test_read_sheet_and_shared_string(self):
        data = workbook_bytes()
        d = mod.inventory_xlsx(data)
        self.assertEqual(d["xlsx_structure"], "PASS")
        self.assertEqual(d["sheets"][0]["name"], "Raw")
        self.assertEqual(d["sheets"][0]["nonempty_xml_rows"], 2)
        self.assertEqual(d["sheets"][0]["first_five_rows"][0][0]["value"], "Erica species")
        self.assertEqual(d["sheets"][0]["first_five_rows"][0][1]["value"], "3.14")
        self.assertEqual(d["sheets"][0]["first_five_rows"][1][0]["value"], "Erica test")

    def test_source_success_still_cannot_claim_independent_replication(self):
        d, raw = mod.acquire(fetcher=lambda req, timeout: Response(workbook_bytes()))
        self.assertEqual(d["status"], "SOURCE_XLSX_BYTES_RECOVERED_TREE_PIGMENT_JOIN_NOT_YET_ADMITTED")
        self.assertFalse(d["new_gene_memory_replicate_admitted"])
        self.assertFalse(d["trait_tree_expression_joint_source_verified"])
        self.assertTrue(d["no_biological_outcome_opened"])
        self.assertIsNotNone(raw)

    def test_http_restriction_is_source_hold_never_hypothesis_failure(self):
        class Denied(Response):
            status = 403
        d, raw = mod.acquire(fetcher=lambda req, timeout: Denied(b"Forbidden"))
        self.assertIsNone(raw)
        self.assertTrue(d["status"].startswith("HOLD_"))
        self.assertIn("HTTP 403", d["transport_or_structure_error"])
        self.assertFalse(d["new_gene_memory_replicate_admitted"])

    def test_html_disguised_as_workbook_remains_hold(self):
        d, raw = mod.acquire(fetcher=lambda req, timeout: Response(b"<html>captcha</html>"))
        self.assertIsNone(raw)
        self.assertTrue(d["status"].startswith("HOLD_"))
        self.assertIn("not a ZIP-based XLSX", d["transport_or_structure_error"])

    def test_source_identity_and_audit_scope_are_fixed(self):
        self.assertEqual(mod.SOURCE["figshare_file_id"], 18004067)
        self.assertEqual(mod.SOURCE["reported_taxa_species_and_subspecies"], 28)
        self.assertEqual(mod.SOURCE["data_doi"], "10.25413/sun.9980498")
        self.assertIn("private_link=8eb50fa0cf88c0000ed0", mod.SOURCE_URL)

if __name__ == "__main__":
    unittest.main()
