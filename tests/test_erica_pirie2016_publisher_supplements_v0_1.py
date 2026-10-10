from __future__ import annotations
import importlib.util,io,pathlib,unittest,zipfile
p=pathlib.Path(__file__).resolve().parents[1]/"scripts/audit_erica_pirie2016_publisher_supplements_v0_1.py"
spec=importlib.util.spec_from_file_location("pirie_2016_supp",p)
m=importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(m)

def data():
    f=io.BytesIO()
    with zipfile.ZipFile(f,"w") as z:
        z.writestr("Figure_S1a.pdf","fake graph, no numeric tree")
        z.writestr("trees/example.nex","#NEXUS\nBEGIN TREES;TREE x=(a:1,b:1);END;")
    return f.getvalue()

class Response:
    status=200
    def __init__(self,bytes):self.data=io.BytesIO(bytes)
    def read(self,n):return self.data.read(n)
    def __enter__(self):return self
    def __exit__(self,*a):return False

class TestPublisher(unittest.TestCase):
    def test_explicit_raw_tree_detection_never_promotes_phylogeny(self):
        result,z=m.run(urlopen=lambda req,timeout:Response(data()))
        self.assertEqual(len(z),2)
        self.assertTrue(result["original_2016_treebase_S18291_unchanged_HOLD"])
        self.assertFalse(result["new_phylogenetic_tree_admitted"])
        self.assertTrue(result["no_species_tip_or_branch_distance_computed"])
        self.assertFalse(result["new_regulatory_memory_replicate"])
        self.assertEqual(result["source_archives"]["MOESM2_Figure_S1"]["explicit_tree_file_candidates"],["trees/example.nex"])
    def test_html_is_hold_not_new_biology(self):
        r,z=m.run(urlopen=lambda req,timeout:Response(b"<html>Not zip</html>"))
        self.assertFalse(z)
        self.assertEqual(r["status"],"HOLD_ORIGINAL_SUPPLEMENT_MACHINE_TREE_UNVERIFIED")
        self.assertFalse(r["new_regulatory_memory_replicate"])

if __name__=="__main__":
    unittest.main()
