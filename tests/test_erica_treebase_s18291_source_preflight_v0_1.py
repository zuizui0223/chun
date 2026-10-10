from __future__ import annotations
import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "erica_treebase_preflight",
    ROOT / "scripts/preflight_erica_treebase_s18291_source_v0_1.py",
)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)


class Response:
    def __init__(self, payload, status=200):
        self.payload, self.status = payload, status
    def read(self, _):
        return self.payload
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False


class TreeBasePreflightTests(unittest.TestCase):
    def test_nexus_download_is_source_only_not_admitted_replication(self):
        nexus = b"#NEXUS\nBEGIN TREES;\nTREE a = (Erica_a:1,Erica_b:2);\nEND;\n"
        receipt, payload = mod.audit(fetcher=lambda req, timeout: Response(nexus))
        self.assertEqual(payload, nexus)
        self.assertEqual(receipt["status"],
            "SOURCE_TREE_EXPORT_RECOVERED_TAXON_AND_TREE_SELECTION_NOT_YET_ADMITTED")
        self.assertEqual(receipt["routes"][0]["source_type"], "SOURCE_STUDY_NEXUS_TREE_EXPORT")
        self.assertFalse(receipt["selected_evolutionary_tree"])
        self.assertFalse(receipt["taxon_crosswalk_verified"])
        self.assertFalse(receipt["pigment_gene_memory_test_performed"])
        self.assertFalse(receipt["independent_replication_admitted"])

    def test_html_document_is_not_phylogeny(self):
        receipt, payload = mod.audit(fetcher=lambda req, timeout: Response(b"<html>Not Available</html>"))
        self.assertIsNone(payload)
        self.assertEqual(receipt["status"], "HOLD_TREEBASE_SOURCE_TREE_UNRECOVERED")
        self.assertEqual(len(receipt["routes"]), len(mod.URLS))
        self.assertEqual(receipt["routes"][0]["source_type"], "HTML_NOT_MACHINE_TREE")

    def test_failed_routes_do_not_turn_into_negative_biology(self):
        def no_network(req, timeout):
            raise OSError("host blocked")
        receipt, payload = mod.audit(fetcher=no_network)
        self.assertIsNone(payload)
        self.assertEqual(receipt["status"], "HOLD_TREEBASE_SOURCE_TREE_UNRECOVERED")
        self.assertTrue(all(r["result"] == "HOLD_TRANSPORT" for r in receipt["routes"]))
        self.assertFalse(receipt["independent_replication_admitted"])
        self.assertFalse(receipt["pigment_gene_memory_test_performed"])

    def test_reject_rdf_only_as_tree(self):
        self.assertEqual(mod.classify(b"<?xml version='1.0'?><rdf:RDF></rdf:RDF>"),
                         "METADATA_XML_NOT_CONFIRMED_TREE")

if __name__ == "__main__":
    unittest.main()
