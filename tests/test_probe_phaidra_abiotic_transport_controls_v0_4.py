from __future__ import annotations
import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts"/"probe_phaidra_abiotic_transport_controls_v0_4.py"
spec=importlib.util.spec_from_file_location("m",SCRIPT)
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

def test_handle_urls_are_pid_specific():
    u=m.handle_urls("o:2098641")
    assert any("10.2098641" in x for x in u)

def test_classify_head_requires_identity_metadata():
    assert m.classify_head([{"ok":True,"content_type":"text/html","content_length":None,"content_disposition":None}])["informative"] is False
    assert m.classify_head([{"ok":True,"content_type":"application/zip","content_length":"123","content_disposition":"attachment; filename=x.zip"}])["informative"] is True

def test_controls_are_fixed_public_examples():
    assert m.CONTROL_OBJECT=="o:295002"
    assert m.CONTROL_COLLECTION=="o:295028"
