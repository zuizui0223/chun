from __future__ import annotations
import importlib.util
import io
from pathlib import Path
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "erica_later_tree",
    ROOT / "scripts/preflight_erica_2024_tree_bundle_v0_1.py")
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)


def tiny():
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        z.writestr("latest_tree.nex", "#NEXUS\nBEGIN TREES;\nEND;")
        z.writestr("README.txt", "later source")
    return b.getvalue()


class Response:
    def __init__(self, data):
        self.data = data
        self.status = 200
    def read(self, size):
        return self.data[:size]
    def __enter__(self):
        return self
    def __exit__(self, *exc):
        return False


class TestLaterEricaSource(unittest.TestCase):
    def test_zip_inventory_without_phylogeny_selection(self):
        data = tiny()
        r, got = mod.acquire(fetcher=lambda req, timeout: Response(data))
        self.assertEqual(got, data)
        self.assertEqual(r["status"],
                         "LATER_TREE_ZIP_RECOVERED_TREE_AND_TIP_CROSSWALK_UNVERIFIED")
        self.assertEqual(r["source_member_inventory"]["member_count"], 2)
        self.assertEqual(r["source_member_inventory"]["tree_filename_candidates"],
                         ["latest_tree.nex"])
        self.assertEqual(r["selection_of_phylogenetic_tree"], "NOT_PERFORMED")
        self.assertFalse(r["independent_regulatory_memory_replication"])
        self.assertTrue(r["no_imputed_species_admitted"])

    def test_html_200_not_admitted(self):
        r, content = mod.acquire(fetcher=lambda req, timeout: Response(b"<html>blocked</html>"))
        self.assertIsNone(content)
        self.assertEqual(r["status"], "HOLD_LATER_PHYLOGENY_SOURCE_BYTES_UNRECOVERED")
        self.assertEqual(len(r["routes"]), len(mod.URLS))

    def test_source_is_distinct_later_paper(self):
        self.assertEqual(mod.DOI, "10.3897/phytokeys.244.124565.suppl7")
        self.assertTrue(all("124565" in u or "PMC11255470" in u for u in mod.URLS))

if __name__ == "__main__":
    unittest.main()
