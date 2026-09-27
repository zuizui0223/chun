from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts"/"probe_phaidra_abiotic_source_v0_2.py"
spec=importlib.util.spec_from_file_location("probe2",SCRIPT)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_root_info_pid_extraction_excludes_root():
    payload={"pid":"o:2098641","haspart":["o:11","o:12"],"nested":{"member":"o:13"}}
    assert mod.pids_from_root_info(payload,"o:2098641")==["o:11","o:12","o:13"]


def test_choose_source_requires_exactly_one_relevant_root():
    roots=[
      {"pid":"o:1","provenance":"a","root_object":None,
       "members":[{"pid":"o:11","candidate_environment_or_code":True,"filename":"env.csv"}]},
      {"pid":"o:2","provenance":"b","root_object":None,"members":[]},
    ]
    out=mod.choose_source(roots)
    assert out["pid"]=="o:1"
    assert out["relevant_member_count"]==1


def test_choose_source_holds_when_two_roots_qualify():
    roots=[
      {"pid":"o:1","provenance":"a","root_object":{"candidate_environment_or_code":True},"members":[]},
      {"pid":"o:2","provenance":"b","root_object":{"candidate_environment_or_code":True},"members":[]},
    ]
    assert mod.choose_source(roots) is None
