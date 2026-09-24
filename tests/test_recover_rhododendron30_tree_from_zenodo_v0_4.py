from __future__ import annotations
import hashlib, importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts"/"recover_rhododendron30_tree_from_zenodo_v0_4.py"
spec=importlib.util.spec_from_file_location("r",SCRIPT)
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

def test_exact_match_requires_size_and_sha():
    b=b"(A:1,B:1);\n"
    sha=hashlib.sha256(b).hexdigest()
    assert mod.exact_match(b,len(b),sha)
    assert not mod.exact_match(b,len(b)+1,sha)
    assert not mod.exact_match(b,len(b),"0"*64)

def test_treeish_requires_newick_shape():
    assert mod.treeish(b"(A:1,B:1);\n")
    assert not mod.treeish(b"<html>blocked</html>")
