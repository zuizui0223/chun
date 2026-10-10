from __future__ import annotations
import importlib.util
import io
import json
from pathlib import Path
import unittest
import zipfile

P=Path(__file__).resolve().parents[1]/"scripts/preflight_erica_2025_uct_phylogenomics_v0_1.py"
s=importlib.util.spec_from_file_location("erica25",P)
m=importlib.util.module_from_spec(s)
assert s and s.loader
s.loader.exec_module(m)


class Response:
    status=200
    def __init__(self,data):self.b=io.BytesIO(data)
    def read(self,n):return self.b.read(n)
    def __enter__(self):return self
    def __exit__(self,*_):return False


def archive():
    b=io.BytesIO()
    with zipfile.ZipFile(b,"w") as z:
        z.writestr("trees/erica.nwk","(Erica_abietina:0.1,Erica_viscaria:0.3);")
        z.writestr("README.txt","observed species only")
    return b.getvalue()


class TestErica2025(unittest.TestCase):
    def metadata(self):
        raw=archive()
        return {"id":m.ARTICLE_ID,"doi":m.DOI,"title":"Erica trees",
                "files":[{"name":"phylogenetic_trees.zip","id":11,"size":len(raw),
                    "computed_md5":__import__("hashlib").md5(raw).hexdigest(),
                    "download_url":"https://ndownloader.figshare.com/files/11"}]}
    def test_valid_metadata_and_tree_archive_not_replication(self):
        metadata=self.metadata()
        url=metadata["files"][0]["download_url"]
        response={m.API:json.dumps(metadata).encode(),url:archive()}
        r,data=m.run(urlopen=lambda req,timeout:Response(response[req.full_url]))
        self.assertEqual(r["status"],"PASS_2025_SOURCE_BYTES_INVENTORY_NO_TREE_TIP_JOIN")
        self.assertEqual(len(data),1)
        self.assertEqual(r["recovered_files"][0]["zip_members"][0]["filename"],"trees/erica.nwk")
        self.assertFalse(r["selected_phylogeny"])
        self.assertFalse(r["independent_memory_test_performed"])
        self.assertFalse(r["same_taxa_expression_tree_join_verified"])
    def test_mismatched_article_or_missing_doi_rejected(self):
        article=self.metadata()
        article["id"]=27134207
        with self.assertRaisesRegex(ValueError,"different Figshare"):
            m.candidates(article)
        article=self.metadata()
        article["doi"]="10.1000/different"
        with self.assertRaisesRegex(ValueError,"DOI"):
            m.candidates(article)
    def test_wrong_external_file_url_not_downloaded(self):
        article=self.metadata()
        article["files"][0]["download_url"]="https://wrong.example/a.zip"
        files=m.candidates(article)
        self.assertFalse(files[0]["bounded_safe_download"])
    def test_nonzip_fails_structural_gate(self):
        with self.assertRaisesRegex(ValueError,"not ZIP"):
            m.zip_members(b"<html>Access denied</html>")
    def test_network_failure_is_hold_not_scientific_negative(self):
        def fail(req,timeout):raise TimeoutError("network")
        r,files=m.run(urlopen=fail)
        self.assertTrue(r["status"].startswith("HOLD"))
        self.assertFalse(files)
        self.assertFalse(r["independent_memory_test_performed"])

if __name__=="__main__":
    unittest.main()
