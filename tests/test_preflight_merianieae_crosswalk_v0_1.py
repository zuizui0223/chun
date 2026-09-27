from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts"/"preflight_merianieae_crosswalk_v0_1.py"
spec=importlib.util.spec_from_file_location("m",SCRIPT)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_norm_id():
    assert mod.norm_id(" Meriania_speciosa  ")=="meriania speciosa"
    assert mod.norm_id("Meriania   speciosa")=="meriania speciosa"


def test_crosswalk_uses_x_only_and_exact_normalization(tmp_path):
    trait=tmp_path/"t.csv"
    trait.write_text(
      "species,x,corolla.colour\n"
      "Meriania speciosa,Meriania_speciosa,SECRET_RED\n"
      "Meriania maxima,Meriania maxima,SECRET_WHITE\n",
      encoding="utf-8"
    )
    tree=tmp_path/"t.tre"
    tree.write_text("(Meriania_speciosa:1,'Meriania maxima':1,Other_sp:1);\n")
    cw,pruned=mod.build_crosswalk(trait,tree)
    assert cw["matched_count"]==2
    assert cw["unmatched_source_count"]==0
    assert {x["species"] for x in cw["matches"]}=={"Meriania speciosa","Meriania maxima"}
    assert len(pruned.get_terminals())==2
