from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
spec=importlib.util.spec_from_file_location("crosswalk",ROOT/"scripts/audit_erica_table2_visible_colour_crosswalk_v0_1.py")
m=importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(m)
DATA=json.loads((ROOT/"data/erica_table2_visible_colour_qpcr_taxon_crosswalk_v0_1.json").read_text())


def sample_q():
    return {"status":"SOURCE_KEYS_ADMITTED_FOR_SCHEMA_ONLY",
            "taxa_with_row_counts":{r["qpcr_label"]:24 for r in DATA["taxa"]},
            "quantitative_pathway_measurements":630,
            "quantitative_pathway_genes":["ANS","CHI","CHS","DFR","F3'H","F3H","UDP3-O-GST"],
            "taxon_stage_combinations":90}


class TestTable2(unittest.TestCase):
    def test_source_only_support(self):
        r=m.crosswalk(DATA,sample_q())
        self.assertEqual(r["raw_qpcr_id_labels"],30)
        self.assertEqual(r["lineage_labels_after_collapsing_colour_morphs"],28)
        self.assertEqual(r["single_visible_colour_lineages"],27)
        self.assertEqual(r["raw_table2_colour_counts"],
                         {"pink":7,"red":15,"white":6,"yellow":2})
        self.assertEqual(r["single_colour_lineage_counts"],
                         {"pink":6,"red":14,"white":5,"yellow":2})
        self.assertEqual(r["total_theoretical_pairs_before_tree_join"],117)
        self.assertEqual(r["theoretical_within_visible_colour_pairs_before_tree_join"],
                         {"pink":15,"red":91,"white":10,"yellow":1})
        self.assertTrue(r["no_true_phylogenetic_pair_count_computed"])
        self.assertTrue(r["no_sixbit_or_full_anthocyanidin_pigment_profile_measured"])
        self.assertTrue(r["no_cross_radiation_regulatory_memory_test"])

    def test_exact_key_gate(self):
        q=sample_q()
        q["taxa_with_row_counts"].pop("Erica_cameronii")
        with self.assertRaisesRegex(ValueError,"exactly cover"):
            m.crosswalk(DATA,q)

    def test_morphs_not_three_species(self):
        modified=json.loads(json.dumps(DATA))
        for x in modified["taxa"]:
            if x["qpcr_label"]=="Erica_plukenetii_plukenetii_red":
                x["collapsed_species_lineage"]="Erica_NEW_fake_species"
        with self.assertRaisesRegex(ValueError,"lineage count"):
            m.crosswalk(modified,sample_q())

    def test_unverified_quantitative_panel_is_hold(self):
        q=sample_q()
        q["quantitative_pathway_measurements"]=629
        with self.assertRaisesRegex(ValueError,"incomplete"):
            m.crosswalk(DATA,q)

if __name__=="__main__":
    unittest.main()
