from __future__ import annotations
import importlib.util,json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
sp=importlib.util.spec_from_file_location(
    "erica_2025_voucher_clades",
    ROOT/"scripts/audit_erica_hoekstra2025_voucher_monophyly_v0_1.py")
m=importlib.util.module_from_spec(sp)
assert sp and sp.loader
sp.loader.exec_module(m)
REF=json.loads((ROOT/"data/erica_table2_visible_colour_qpcr_taxon_crosswalk_v0_1.json").read_text())

class SourceMonophylyTests(unittest.TestCase):
    def test_only_categorical_source_names_are_matched_without_synonyms(self):
        hits=m.match_names({"abietina_abi_ANA","cameronii_ANA","haematocodon_MP1033","random_fake_ID"},REF)
        by={s:keys for s,colour,keys in hits}
        self.assertEqual(len(hits),27)
        self.assertEqual(by["Erica_abietina"],["abietina_abi_ANA"])
        self.assertEqual(by["Erica_cameronii"],["cameronii_ANA"])
        self.assertEqual(by["Erica_hematocodon"],["haematocodon_MP1033"])
        self.assertFalse(by["Erica_sparmanii"])

    def test_corrupted_archive_not_accepted(self):
        with self.assertRaisesRegex(ValueError,"MD5"):
            m.inspect(b"not the observed original 2025 archive",REF)

    def test_polymorphic_plukenetii_colour_morphs_not_placed_on_tree_as_events(self):
        hits=m.match_names({"plukenetii_plukenetii_MP","plukenetii_breviflora_MP"},REF)
        self.assertNotIn("Erica_plukenetii_plukenetii",[x[0] for x in hits])
        self.assertEqual(len(hits),27)

if __name__=="__main__":unittest.main()
