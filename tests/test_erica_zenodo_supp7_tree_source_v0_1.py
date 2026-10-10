from __future__ import annotations
import importlib.util
import io
import json
from pathlib import Path
import unittest
import zipfile

PATH = Path(__file__).resolve().parents[1] / "scripts/audit_erica_zenodo_supp7_tree_source_v0_1.py"
spec = importlib.util.spec_from_file_location("zenodo_erica_tree", PATH)
m = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(m)


def zip_data():
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        z.writestr("raw/erica_combined.nex", "#NEXUS\nBEGIN TREES; TREE x=(a:1,b:1); END;")
        z.writestr("README.txt", "Source 2024")
    return b.getvalue()


class Response:
    status = 200
    def __init__(self, data):
        self.data = io.BytesIO(data)
    def read(self, count):
        return self.data.read(count)
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass


class TestZenodo(unittest.TestCase):
    def test_id_doi_and_single_zip_admission(self):
        meta = {"id": m.RECORD_ID, "doi": m.EXPECTED_DOI,
                "files": [{"key": "tree.zip", "size": len(zip_data()),
                           "links": {"self": "https://zenodo.org/api/records/12730704/files/tree.zip/content"}}]}
        f, url = m.source_metadata(meta)
        self.assertEqual(f["key"], "tree.zip")
        self.assertEqual(url.split("/")[-1], "content")
        mapping = {m.RECORD_API: json.dumps(meta).encode(), url: zip_data()}
        def fake(req, timeout):
            return Response(mapping[req.full_url])
        result, raw = m.run(urlopen=fake)
        self.assertEqual(raw, zip_data())
        self.assertEqual(result["status"], "PASS_ZENODO_SOURCE_ZIP_INVENTORY_ONLY_NOT_TREE_JOIN")
        self.assertFalse(result["is_original_2016_tree"])
        self.assertFalse(result["independent_replication_admitted"])
        self.assertEqual(len(result["members"]), 2)

    def test_html_and_wrong_record_fail(self):
        d = {"id": 999, "doi": m.EXPECTED_DOI, "files": []}
        with self.assertRaisesRegex(ValueError, "incorrect Zenodo"):
            m.source_metadata(d)
        result, raw = m.run(urlopen=lambda req, timeout: Response(b"<html>blocked</html>"))
        self.assertIsNone(raw)
        self.assertTrue(result["status"].startswith("HOLD"))
        self.assertFalse(result["expression_tree_taxon_join_verified"])

    def test_external_download_url_denied(self):
        d = {"id": m.RECORD_ID, "doi": m.EXPECTED_DOI,
             "files": [{"key": "a.zip", "links": {"self": "https://wrong.example/a.zip"}}]}
        with self.assertRaisesRegex(ValueError, "untrusted"):
            m.source_metadata(d)

if __name__ == "__main__":
    unittest.main()
