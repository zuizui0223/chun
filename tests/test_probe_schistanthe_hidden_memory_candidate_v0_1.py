from __future__ import annotations
import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts"/"probe_schistanthe_hidden_memory_candidate_v0_1.py"
spec=importlib.util.spec_from_file_location("p",SCRIPT)
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

def test_candidate_file_names_are_fixed():
    assert mod.COLOR_FILE=="Vireya_RADsamples_tiplabels_ingroup_color_clade.xls"
    assert mod.TREE_FILE=="VireyaRADd10m5c91R1_0717_Rdref_min4_raxml_treePLCIs.mean.newick"

def test_fine_to_coarse_rule_is_outcome_independent():
    assert mod.coarse_from_source_color("white")=="WHITE"
    assert mod.coarse_from_source_color(" red ")=="NONWHITE"
    assert mod.coarse_from_source_color("") is None
