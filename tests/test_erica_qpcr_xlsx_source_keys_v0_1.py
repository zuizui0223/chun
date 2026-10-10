from __future__ import annotations
import importlib.util
import io
import pathlib
import sys
import unittest
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
PATH = ROOT / "scripts/audit_erica_qpcr_source_keys_v0_1.py"
spec = importlib.util.spec_from_file_location("erica_source_keys", PATH)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)


def fixture(broken_id=False):
    output = io.BytesIO()
    header = """<row r="1"><c r="A1" t="inlineStr"><is><t>ID_REF</t></is></c>
      <c r="B1" t="inlineStr"><is><t>Value</t></is></c></row>"""
    labels = ["Erica_cameronii_Adult_1_CHS",
              "Erica_cameronii_Juvenile_2_F3'H",
              "Erica_sparmannii_Adult_3_UDP_GST"]
    with zipfile.ZipFile(output, "w") as z:
        z.writestr("[Content_Types].xml", "<Types xmlns='http://schemas.openxmlformats.org/package/2006/content-types'/>")
        sheets = "".join(
            '<sheet name="%s" sheetId="%d" r:id="rId%d"/>' % (name, i, i)
            for i, name in enumerate(["Matrix non-normalized", "Matrix normalized", "Fold Change"], 1)
        )
        z.writestr("xl/workbook.xml",
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            '<sheets>'+sheets+'</sheets></workbook>')
        rels = "".join('<Relationship Id="rId%d" Target="worksheets/sheet%d.xml" '
                       'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet"/>'
                       % (i, i) for i in range(1, 4))
        z.writestr("xl/_rels/workbook.xml.rels",
                   '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   + rels + '</Relationships>')
        for i in range(1, 4):
            rows = [header]
            for rownum, label in enumerate(labels, 2):
                if broken_id and i == 3 and rownum == 2:
                    label = "different_species_Adult_1_CHS"
                rows.append(f'<row r="{rownum}"><c r="A{rownum}" t="inlineStr"><is><t>{label}</t></is></c>'
                            f'<c r="B{rownum}"><v>{rownum}.0</v></c></row>')
            z.writestr("xl/worksheets/sheet%d.xml" % i,
                       '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                       '<sheetData>' + "".join(rows) + '</sheetData></worksheet>')
    return output.getvalue()


class TestSourceKeyAudit(unittest.TestCase):
    def test_key_decomposition_and_no_inference(self):
        result = mod.source_key_audit(fixture())
        self.assertEqual(result["status"], "HOLD_UNRESOLVED_PATHWAY_MEASUREMENTS")
        self.assertEqual(result["quantitative_pathway_measurements"], 3)
        self.assertEqual(result["nonnumeric_reference_control_count"], 0)
        self.assertEqual(result["measurements"], 3)
        self.assertEqual(result["taxon_count_from_measurement_ids"], 2)
        self.assertEqual(result["gene_count_from_measurement_ids"], 3)
        self.assertEqual(result["stages"], {"adult": 2, "juvenile": 1})
        self.assertEqual(result["genes_with_row_counts"]["UDP_GST"], 1)
        self.assertEqual(result["taxon_stage_combinations"], 3)
        self.assertEqual(result["complete_fixed_gene_panel_taxa"], 0)
        self.assertFalse(result["independent_replication_admitted"])
        self.assertTrue(result["no_pigment_species_tree_matched_analysis"])

    def test_require_exact_common_measurement_ids_across_all_three_sheets(self):
        with self.assertRaisesRegex(ValueError, "different ordered measurement IDs"):
            mod.source_key_audit(fixture(broken_id=True))

    def test_unparsable_source_id_must_not_be_silently_removed(self):
        self.assertIsNone(mod.ID_PATTERN.fullmatch("Erica_unknown_random"))
        self.assertIsNotNone(mod.ID_PATTERN.fullmatch("Erica_plukenetii_ssp_breviflora_Intermediate_40_ANS"))

if __name__ == "__main__":
    unittest.main()
