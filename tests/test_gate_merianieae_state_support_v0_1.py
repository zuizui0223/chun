from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts"/"gate_merianieae_state_support_v0_1.py"
spec=importlib.util.spec_from_file_location("m",SCRIPT)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_state_frame_filters_rare_and_builds_white_nonwhite(tmp_path):
    trait=tmp_path/"t.csv"
    rows=["species,x,corolla.colour"]
    # 5 white, 5 red, 5 pink, 1 blue
    for state,n in [("white",5),("red",5),("pink",5),("blue",1)]:
        for i in range(n):
            rows.append(f"S{state}{i},T{state}{i},{state}")
    trait.write_text("\n".join(rows)+"\n")
    matches=[]
    rownum=2
    for state,n in [("white",5),("red",5),("pink",5),("blue",1)]:
        for i in range(n):
            matches.append({"source_row":rownum,"source_x":f"T{state}{i}","tree_tip":f"T{state}{i}","species":f"S{state}{i}"})
            rownum+=1
    cw=tmp_path/"cw.json"
    cw.write_text(json.dumps({"status":"MERIANIEAE_IDENTIFIER_CROSSWALK_FROZEN_COROLLA_COLOUR_UNOPENED","matched_count":16,"matches":matches}))
    x=mod.build_state_frame(trait,cw)
    assert x["rare_fine_states_excluded"]=={"blue":1}
    assert x["fine_state_counts"]=={"pink":5,"red":5,"white":5}
    assert x["coarse_state_counts"]=={"NONWHITE":10,"WHITE":5}
    assert x["compression_opportunity"] is False  # 15 tips is below frozen 20-tip frame
