from __future__ import annotations
import importlib.util
import io
import json
from pathlib import Path
import unittest
import zipfile

ROOT=Path(__file__).resolve().parents[1]
p=ROOT/"scripts/audit_erica_hoekstra2025_supp3_tree_crosswalk_v0_1.py"
spec=importlib.util.spec_from_file_location("erica_hoekstra_tree",p)
m=importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(m)
REF=json.loads((ROOT/"data/erica_table2_visible_colour_qpcr_taxon_crosswalk_v0_1.json").read_text())

def fixture():
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,"w") as z:
        z.writestr("trees/Combined.nwk",
                   "(Erica_abietina:0.1,(Erica_viscaria:0.2,Erica_outgroup:0.3):0.4);")
        z.writestr("notes.txt","Example only, must never be admitted")
    return buf.getvalue()

class Response:
    status=200
    def __init__(self,data):self.buf=io.BytesIO(data)
    def read(self,n):return self.buf.read(n)
    def __enter__(self):return self
    def __exit__(self,*args):return False

class TreeCandidateTests(unittest.TestCase):
    def test_source_hash_failure_prevents_tainted_tree(self):
        with self.assertRaisesRegex(ValueError,"MD5"):
            m.source_admission(fixture())

    def test_exact_taxon_tip_overlap_not_broad_genus_matching(self):
        data=fixture()
        names=[{"name":"trees/Combined.nwk","bytes":len("(Erica_abietina:0.1,(Erica_viscaria:0.2,Erica_outgroup:0.3):0.4);"),
                "format":"newick"}]
        audit=m.lexical_tip_overlap(data,names,REF)
        self.assertEqual(len(audit),1)
        found=audit[0]["trees_examined_max_30"][0]
        self.assertEqual(found["tip_count"],3)
        self.assertEqual(found["tip_name_exact_match_count"],2)
        self.assertEqual(found["exact_2019_qpcr_lineage_names"],
                         ["Erica_abietina","Erica_viscaria"])
        self.assertEqual(found["tips_with_branch_lengths"],3)
        self.assertTrue(found["no_sequence_sampling_or_imputation_status_inferred"])

    def test_voucher_prefix_candidates_do_not_silently_apply_synonyms(self):
        tips=["abietina_MP123","cerinthoides_X7","sparmannii_X9",
              "hematocodon_X8","plukenetii_breviflora_X1",
              "an_unrelated_voucher"]
        r=m.voucher_prefix_candidates(tips,REF)
        by={x["source_qpcr_taxon"]:x for x in r["candidate_rows"]}
        assert r["candidate_source_lineages"]==5
        assert r["not_a_voucher_or_sequenced_tip_crosswalk"]
        assert by["Erica_abietina"]["raw_qpcr_epithet_tip_candidates"]==["abietina_MP123"]
        # The published spelling can match independently even when the
        # original qPCR label differs; this must remain tentative.
        assert by["Erica_cerenthoides"]["raw_qpcr_epithet_tip_candidates"]==[]
        assert by["Erica_cerenthoides"]["published_table2_epithet_tip_candidates"]==["cerinthoides_X7"]
        assert by["Erica_sparmanii"]["published_table2_epithet_tip_candidates"]==["sparmannii_X9"]
        assert by["Erica_hematocodon"]["published_table2_epithet_tip_candidates"]==[]
        assert by["Erica_hematocodon"]["raw_qpcr_epithet_tip_candidates"]==["hematocodon_X8"]
        assert r["not_a_final_sample_or_inference_denominator"]

    def test_html_masquerading_as_zip_is_hold(self):
        r,data=m.run(REF,fetcher=lambda req,timeout:Response(b"<html>Blocked</html>"))
        self.assertIsNone(data)
        self.assertEqual(r["status"],"HOLD_ZENODO_TREE_BYTES_UNAVAILABLE")
        self.assertEqual(len(r["routes"]),len(m.SOURCES))
        self.assertFalse(r["independent_gene_memory_replication"])
        self.assertFalse(r["tree_chosen_for_memory_estimator"])

    def test_source_directories_do_not_imply_ancestral_events(self):
        self.assertEqual(m.RECORD_ID,15606575)
        self.assertEqual(m.DOI,"10.3897/phytokeys.257.139457.suppl3")
        self.assertEqual(m.MD5,"d4363c6e604784b58c91d8a1d824a1f1")

if __name__=="__main__":unittest.main()
