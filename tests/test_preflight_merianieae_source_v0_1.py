from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts"/"preflight_merianieae_source_v0_1.py"
spec=importlib.util.spec_from_file_location("m",SCRIPT)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_member_by_suffix_is_folder_specific():
    names=[
      "1_morphospaces_disparity/floraltraits.csv",
      "2_biogeo/Marcelo_Meris.tre",
      "1_morphospaces_disparity/Marcelo_Meris.tre",
    ]
    assert mod.member_by_suffix(names,"1_morphospaces_disparity/floraltraits.csv")=="1_morphospaces_disparity/floraltraits.csv"
    assert mod.member_by_suffix(names,"1_morphospaces_disparity/marcelo_meris.tre")=="1_morphospaces_disparity/Marcelo_Meris.tre"


def test_member_by_suffix_holds_on_ambiguity():
    names=[
      "x/1_morphospaces_disparity/floraltraits.csv",
      "y/1_morphospaces_disparity/floraltraits.csv",
    ]
    try:
        mod.member_by_suffix(names,"1_morphospaces_disparity/floraltraits.csv")
    except RuntimeError as e:
        assert "expected 1 match" in str(e)
    else:
        raise AssertionError("expected RuntimeError")


def test_header_only():
    assert mod.header_only(b"species,x,corolla.colour\nSECRET,SECRET,SECRET\n")==["species","x","corolla.colour"]


def test_tree_metadata_counts_branch_lengths():
    body=b"((A:1,B:1):2,C:3);"
    x=mod.tree_metadata(body)
    assert x["tip_count"]==3
    assert x["duplicate_tip_labels"]==0
    assert x["missing_nonroot_branch_lengths"]==0
