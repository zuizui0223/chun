from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts"/"gate_gesnerioideae_biochemical_state_support_v0_1.py"
spec=importlib.util.spec_from_file_location("gate",SCRIPT)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_header_canonicalization_matches_preflight_probe():
    assert mod.canonical_header(" Cyanidin-3-\n  rutinoside ")=="Cyanidin-3- rutinoside"
    assert mod.canonical_header("Delphinidin-\t rhamnose-glucose")=="Delphinidin- rhamnose-glucose"


def test_bit_from_cell_rule():
    assert mod.bit_from_cell(None)==0
    assert mod.bit_from_cell("")==0
    assert mod.bit_from_cell(0)==0
    assert mod.bit_from_cell(0.0)==0
    assert mod.bit_from_cell(0.01)==1


def test_fine_and_coarse_state():
    fs=mod.fine_state([0,1,None]+[0]*10)
    assert len(fs)==13
    assert fs=="0100000000000"
    assert mod.coarse_state(fs)=="PRESENT"
    assert mod.coarse_state("0"*13)=="NONE"


def test_rare_state_filter_uses_same_common_frame():
    rows=[]
    for i in range(5):
        rows.append({"tree_tip":f"a{i}","fine_state":"0"*13,"coarse_state":"NONE"})
    for i in range(6):
        rows.append({"tree_tip":f"b{i}","fine_state":"1"+"0"*12,"coarse_state":"PRESENT"})
    rows.append({"tree_tip":"rare","fine_state":"01"+"0"*11,"coarse_state":"PRESENT"})
    retained,stats=mod.retain_supported_states(rows,rare_min=5)
    assert len(retained)==11
    assert stats["retained_fine_state_count"]==2
    assert stats["retained_coarse_state_count"]==2
