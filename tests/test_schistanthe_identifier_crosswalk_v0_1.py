from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts"/"preflight_schistanthe_identifier_crosswalk_v0_1.py"
spec=importlib.util.spec_from_file_location("cw",SCRIPT)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_identifier_projection_reads_only_first_column():
    body=b"Tip_Label,Clade_No,Flower_Color,Clade\nA,1,red,X\nB,2,white,Y\n"
    assert mod.project_tip_labels(body)==["A","B"]


def test_crosswalk_requires_exact_unique_labels():
    trait=["A","B","C"]
    tree=["A","B","C","OUT"]
    x=mod.crosswalk_summary(trait,tree)
    assert x["exact_matches"]==3
    assert x["trait_only"]==[]
    assert x["duplicate_trait_labels"]==0
    assert x["duplicate_tree_labels"]==0


def test_crosswalk_reports_unmatched_without_repair():
    x=mod.crosswalk_summary(["A","B"],["A","C"])
    assert x["exact_matches"]==1
    assert x["trait_only"]==["B"]
    assert x["tree_only"]==["C"]
