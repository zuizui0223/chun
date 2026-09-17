#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_cross_radiation_el_submission_metadata_v0_1.py"

spec = importlib.util.spec_from_file_location("el_metadata", SCRIPT)
if spec is None or spec.loader is None:
    raise RuntimeError(f"missing production validator: {SCRIPT}")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def base_metadata():
    return {
        "schema_version": "v0.1",
        "paper_title": "No universal scale of predictability in flower-color evolution",
        "phase1_author_identity": {
            "authors": [],
            "affiliations": [],
            "corresponding_author": {"author_name": None, "email": None, "postal_address": None, "orcid": None},
        },
        "phase2_declarations": {
            "acknowledgments": None,
            "funding_status": None,
            "funding_sources": [],
            "credit_roles": [],
            "conflict_of_interest": "The authors declare no conflicts of interest.",
        },
        "phase3_archive": {"archive_doi": None, "archive_version": None, "archive_url": None},
        "governance": {
            "do_not_infer_missing_human_metadata": True,
            "science_status": "SCIENCE_AND_JOURNAL_FORMAT_READY_METADATA_HOLD",
            "submission_route": "Evolution Letters v0.2",
            "current_state": "AWAITING_PHASE1_AUTHOR_IDENTITY",
        },
    }


def complete_phase1(x):
    x["phase1_author_identity"] = {
        "authors": [{"name": "A. Author", "affiliation_ids": ["aff1"], "orcid": "0000-0000-0000-0001"}],
        "affiliations": [{"id": "aff1", "institution": "Example University", "address": "City, Country"}],
        "corresponding_author": {
            "author_name": "A. Author",
            "email": "a@example.org",
            "postal_address": "City, Country",
            "orcid": "0000-0000-0000-0001",
        },
    }


class ElSubmissionMetadataTests(unittest.TestCase):
    def test_empty_scaffold_stops_at_phase1(self):
        x = base_metadata()
        s = mod.validate_metadata(x)
        self.assertEqual(s["current_state"], "AWAITING_PHASE1_AUTHOR_IDENTITY")
        self.assertFalse(s["ready_for_final_bundle"])
        self.assertIn("final author list/order", s["phase1_missing"])

    def test_completed_phase1_advances_to_declarations(self):
        x = base_metadata()
        complete_phase1(x)
        x["governance"]["current_state"] = "AWAITING_PHASE2_DECLARATIONS"
        s = mod.validate_metadata(x)
        self.assertEqual(s["current_state"], "AWAITING_PHASE2_DECLARATIONS")
        self.assertTrue(s["phase1_complete"])
        self.assertFalse(s["phase2_complete"])

    def test_completed_declarations_advance_to_archive(self):
        x = base_metadata()
        complete_phase1(x)
        x["phase2_declarations"].update({
            "acknowledgments": "None.",
            "funding_status": "none",
            "funding_sources": [],
            "credit_roles": [{"author_name": "A. Author", "roles": ["Conceptualization", "Formal analysis", "Writing – original draft"]}],
        })
        x["governance"]["current_state"] = "AWAITING_PHASE3_ARCHIVE_DOI"
        s = mod.validate_metadata(x)
        self.assertEqual(s["current_state"], "AWAITING_PHASE3_ARCHIVE_DOI")
        self.assertTrue(s["phase2_complete"])

    def test_complete_metadata_is_ready(self):
        x = base_metadata()
        complete_phase1(x)
        x["phase2_declarations"].update({
            "acknowledgments": "None.",
            "funding_status": "none",
            "funding_sources": [],
            "credit_roles": [{"author_name": "A. Author", "roles": ["Conceptualization", "Formal analysis", "Writing – original draft"]}],
        })
        x["phase3_archive"] = {"archive_doi": "10.5281/zenodo.1234567", "archive_version": "v0.2", "archive_url": "https://doi.org/10.5281/zenodo.1234567"}
        x["governance"]["current_state"] = "READY_FOR_FINAL_BUNDLE"
        s = mod.validate_metadata(x)
        self.assertTrue(s["ready_for_final_bundle"])
        self.assertEqual(s["current_state"], "READY_FOR_FINAL_BUNDLE")

    def test_missing_human_metadata_must_not_be_inferred(self):
        x = base_metadata()
        x["governance"]["do_not_infer_missing_human_metadata"] = False
        with self.assertRaises(ValueError):
            mod.validate_metadata(x)


if __name__ == "__main__":
    unittest.main()
