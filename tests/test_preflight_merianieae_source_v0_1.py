from __future__ import annotations

import importlib.util
import io
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts"/"preflight_merianieae_source_v0_1.py"
spec=importlib.util.spec_from_file_location("m",SCRIPT)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_member_candidates_casefold_basename():
    names=["a/floraltraits.csv","b/FLORALTRAITS.CSV","x/other.csv"]
    assert mod.member_candidates(names,"floraltraits.csv")==["a/floraltraits.csv","b/FLORALTRAITS.CSV"]


def test_identical_duplicate_members_are_allowed():
    b=io.BytesIO()
    with zipfile.ZipFile(b,"w") as z:
        z.writestr("a/floraltraits.csv","species,x,corolla.colour\n")
        z.writestr("b/floraltraits.csv","species,x,corolla.colour\n")
    with zipfile.ZipFile(io.BytesIO(b.getvalue())) as z:
        p,body,copies=mod.choose_identical_members(z,["a/floraltraits.csv","b/floraltraits.csv"],"trait")
    assert p=="a/floraltraits.csv"
    assert len(copies)==2
    assert mod.header_only(body)==["species","x","corolla.colour"]


def test_nonidentical_duplicate_members_hold():
    b=io.BytesIO()
    with zipfile.ZipFile(b,"w") as z:
        z.writestr("a/floraltraits.csv","species,x,corolla.colour\n")
        z.writestr("b/floraltraits.csv","species,x,colour\n")
    with zipfile.ZipFile(io.BytesIO(b.getvalue())) as z:
        try:
            mod.choose_identical_members(z,["a/floraltraits.csv","b/floraltraits.csv"],"trait")
        except RuntimeError as e:
            assert "non-identical" in str(e)
        else:
            raise AssertionError("expected RuntimeError")


def test_tree_metadata_counts_branch_lengths():
    body=b"((A:1,B:1):2,C:3);"
    x=mod.tree_metadata(body)
    assert x["tip_count"]==3
    assert x["duplicate_tip_labels"]==0
    assert x["missing_nonroot_branch_lengths"]==0
