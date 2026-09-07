"""Offline tests for nominal-state audit and actual ingested source data."""
import importlib.util
import json
import math
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('epi', ROOT/'scripts/analyze_epimedium_organ_states_v0_1.py')
epi = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(epi)


class NominalUnitTests(unittest.TestCase):
    def test_taxon_normalization_is_not_taxonomy_inference(self):
        self.assertEqual(epi.taxon_name('E.  acuminatum JS48'), 'Epimedium acuminatum')
        self.assertEqual(epi.taxon_name('E. epstenii'), 'Epimedium epstenii')
        with self.assertRaises(ValueError):
            epi.taxon_name('unknown')

    def test_nonfunctional_mapping_detected_both_ways(self):
        r = epi.nominal_summary([('a','x'),('a','y'),('b','y')])
        self.assertFalse(r['sepal_sufficient_for_spur'])
        self.assertFalse(r['spur_sufficient_for_sepal'])

    def test_functional_mapping_detected(self):
        r = epi.nominal_summary([('a','x'),('a','x'),('b','y')])
        self.assertTrue(r['sepal_sufficient_for_spur'])
        self.assertTrue(r['spur_sufficient_for_sepal'])
        self.assertAlmostEqual(r['spur_given_sepal_bits'], 0)

    def test_independent_renaming_of_codes_preserves_results(self):
        a = epi.nominal_summary([('0','1'),('0','2'),('1','2'),('3','4')])
        b = epi.nominal_summary([('w','s'),('w','r'),('v','r'),('u','q')])
        for key in ('entropy_joint_bits','mutual_information_bits','spur_given_sepal_bits','sepal_given_spur_bits'):
            self.assertAlmostEqual(a[key], b[key])

    def test_empty_data_rejected(self):
        with self.assertRaises(ValueError):
            epi.nominal_summary([])


class ActualSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = ROOT/'data/atlas_epimedium_ingested_v0_1'
        if not cls.source.is_dir():
            raise RuntimeError('actual source data required; tests cannot silently skip')
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = Path(cls.tmp.name)
        cls.result = epi.run(cls.source, cls.out)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_actual_units_and_weights(self):
        r = self.result
        self.assertEqual((r['source_measurement_rows'],r['organ_long_rows']), (699,1398))
        self.assertEqual((r['source_taxon_groups'],r['named_source_taxa'],r['source_strata']), (42,41,53))
        self.assertEqual(r['primary_equal_taxon_weight']['n_source_taxa'],41)

    def test_joint_state_information_is_not_single_hue(self):
        r = self.result['primary_equal_taxon_weight']
        self.assertEqual((r['sepal_categories'],r['spur_categories'],r['joint_categories']), (4,5,7))
        self.assertAlmostEqual(r['spur_given_sepal_bits'],0.6598654612803192)
        self.assertAlmostEqual(r['sepal_given_spur_bits'],0.9472688726387011)
        self.assertFalse(r['sepal_sufficient_for_spur'])
        self.assertFalse(r['spur_sufficient_for_sepal'])

    def test_source_crosswalk_keeps_mismatch_visible(self):
        r = self.result
        self.assertEqual((r['s9_total_data_rows'],r['s9_ingroup_data_rows']), (35,34))
        self.assertTrue(r['article_vs_s9_count_discrepancy'])
        self.assertEqual((r['s9_exact_id_matches'],r['s9_explicit_id_corrections'],r['s9_s4_state_agreements']), (33,1,34))
        self.assertEqual((r['molecular_taxa_in_s1'],r['molecular_taxa_in_s4'],r['molecular_taxa_in_s9']), (7,6,5))

    def test_no_false_population_or_event_claim(self):
        r = self.result
        self.assertEqual(r['within_taxon_variable_codes'],0)
        self.assertIn('NOT_IDENTIFIABLE',r['population_polymorphism_inference'])
        self.assertEqual(r['historical_event_analysis'],'NOT_RUN')
        self.assertFalse(r['paper1_science_changed'])

    def test_unknown_taxon_sensitivity(self):
        r = self.result['sensitivity_include_unidentified']
        self.assertEqual(r['n_source_taxa'],42)
        self.assertEqual(r['joint_categories'],7)
        self.assertFalse(r['sepal_sufficient_for_spur'])
        self.assertFalse(r['spur_sufficient_for_sepal'])

    def test_csv_changes_without_raw_changes_are_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td)
            shutil.copy2(self.source/'Table_1.xlsx',src/'Table_1.xlsx')
            text = (self.source/'Table_1_sheet4.csv').read_text()
            (src/'Table_1_sheet4.csv').write_text(text.replace('E. acuminatum','E. invented',1))
            with self.assertRaisesRegex(ValueError,'CSV/XML cell mismatch'):
                epi.verify_positional_export(src,4)

    def test_source_change_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            src=Path(td)
            (src/'Table_1.xlsx').write_bytes(b'not the frozen workbook')
            with self.assertRaisesRegex(ValueError,'SHA256'):
                epi.run(src,src/'out')


if __name__ == '__main__':
    unittest.main()
