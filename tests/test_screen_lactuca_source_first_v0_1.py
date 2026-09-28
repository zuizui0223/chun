from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts"/"screen_lactuca_source_first_v0_1.py"
spec=importlib.util.spec_from_file_location("l",SCRIPT)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def test_mapping_contract_from_author_line():
    body=b'# 0 = white, 1 = light yellow, 2 = yellow, 3 = strong yellow, 4 = light purple, 5 = purple, 6 = pink\n'
    x=mod.script_contract(body)
    assert x["mapping_ok"] is True
    assert "0 = white" in x["mapping_line"]

def test_expected_mapping_is_frozen():
    assert mod.EXPECTED_MAPPING["0"]=="white"
    assert mod.EXPECTED_MAPPING["4"]=="light purple"
    assert mod.EXPECTED_MAPPING["6"]=="pink"
