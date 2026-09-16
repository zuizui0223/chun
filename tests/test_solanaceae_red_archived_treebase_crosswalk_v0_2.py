#!/usr/bin/env python3
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "verify_solanaceae_red_archived_treebase_crosswalk_v0_2.py"

spec = importlib.util.spec_from_file_location("sol_archived_treebase", SCRIPT)
if spec is None or spec.loader is None:
    raise RuntimeError(f"missing production verifier: {SCRIPT}")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class ArchivedTreebaseCrosswalkTests(unittest.TestCase):
    def test_tree_serialization_normalization_is_exact_not_fuzzy(self):
        self.assertEqual(mod.normalize_tree_tip("Brugmansia_sanguinea"), "brugmansia_sanguinea")
        self.assertEqual(mod.normalize_source_species("Brugmansia sanguinea"), "brugmansia_sanguinea")
        self.assertEqual(mod.normalize_tree_tip("Cestrum_newellii"), "cestrum_newellii")
        self.assertEqual(mod.normalize_source_species("Cestrum newelli"), "cestrum_newelli")
        self.assertNotEqual(mod.normalize_tree_tip("Cestrum_newellii"), mod.normalize_source_species("Cestrum newelli"))

    def test_crosswalk_leaves_nonidentical_names_unmatched(self):
        source = ["Brugmansia sanguinea", "Cestrum newelli", "Cestrum sp nov"]
        tips = ["Brugmansia_sanguinea", "Cestrum_newellii", "Cestrum_SpNov"]
        result = mod.exact_crosswalk(source, tips)
        self.assertEqual(result["exact_match_count"], 1)
        self.assertEqual(result["source_unmatched"], ["Cestrum newelli", "Cestrum sp nov"])
        self.assertFalse(result["fuzzy_or_synonym_repair_used"])

    def test_gate_requires_source_identity_tree_integrity_and_twenty_matches(self):
        good = mod.classify_gate(
            source_identity_supported=True,
            archived_tree_object_count=1,
            terminal_count=1344,
            duplicate_normalized_tips=0,
            nonroot_branches_missing_length=0,
            exact_match_count=25,
        )
        self.assertEqual(good, "PASS_ARCHIVED_TREEBASE_S16617_OBJECT_CROSSWALK_FROZEN")
        self.assertTrue(mod.classify_gate(True, 1, 1344, 0, 0, 19).startswith("HOLD_"))
        self.assertTrue(mod.classify_gate(True, 2, 1344, 0, 0, 25).startswith("HOLD_"))
        self.assertTrue(mod.classify_gate(True, 1, 1344, 1, 0, 25).startswith("HOLD_"))
        self.assertTrue(mod.classify_gate(True, 1, 1344, 0, 1, 25).startswith("HOLD_"))

    def test_stable_acquisition_summary_ignores_outer_zip_digest(self):
        acquisition = {
            "oa_package": {"selected_method": None},
            "europe_pmc": {
                "selected_method": "europe_pmc_supplementaryFiles",
                "selected_url": "https://example.test/supplementaryFiles",
                "selected_member": "supp_plw013_plw013supp_table1.docx",
                "attempts": [
                    {"method": "europe_pmc_supplementaryFiles", "sha256": "volatile-outer-zip"},
                    {
                        "method": "europe_pmc_member",
                        "member": "supp_plw013_plw013supp_table1.docx",
                        "bytes": 118778,
                        "sha256": mod.EXPECTED_SUPPLEMENT_SHA256,
                        "is_docx": True,
                    },
                ],
            },
        }
        summary = mod.stable_acquisition_summary(acquisition)
        self.assertEqual(summary["selected_method"], "europe_pmc_supplementaryFiles")
        self.assertEqual(summary["selected_member"], "supp_plw013_plw013supp_table1.docx")
        self.assertEqual(summary["member_bytes"], 118778)
        self.assertEqual(summary["member_sha256"], mod.EXPECTED_SUPPLEMENT_SHA256)
        self.assertNotIn("volatile-outer-zip", repr(summary))


if __name__ == "__main__":
    unittest.main()
