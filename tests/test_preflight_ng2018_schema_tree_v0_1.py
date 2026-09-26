from __future__ import annotations

import importlib.util
import io
from pathlib import Path

from openpyxl import Workbook

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts"/"preflight_ng2018_schema_tree_v0_1.py"
spec=importlib.util.spec_from_file_location("preflight",SCRIPT)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_workbook_header_metadata_reads_header_only():
    wb=Workbook()
    ws=wb.active
    ws.title="Table S1"
    ws.append(["Species","Pelargonidin","Cyanidin","Delphinidin"])
    ws.append(["SHOULD_NOT_BE_INTERPRETED",1,2,3])
    b=io.BytesIO()
    wb.save(b)
    out=mod.workbook_header_metadata(b.getvalue())
    assert out["sheet_count"]==1
    assert out["sheets"][0]["header"]==["Species","Pelargonidin","Cyanidin","Delphinidin"]


def test_tree_metadata_selects_unique_tree():
    body=b'''<?xml version="1.0"?>
    <nex:nexml xmlns:nex="http://www.nexml.org/2009">
      <nex:trees>
        <nex:tree id="tree1" label="MCC tree">
          <nex:node id="n1"/><nex:node id="n2"/><nex:node id="n3"/>
          <nex:edge source="n1" target="n2"/><nex:edge source="n1" target="n3"/>
        </nex:tree>
      </nex:trees>
    </nex:nexml>'''
    out=mod.tree_metadata(body)
    assert out["tree_count"]==1
    assert out["selected_tree_id"]=="tree1"
    assert out["selected_tree_terminal_node_count"]==2


def test_tree_metadata_holds_when_multiple_unlabelled_trees():
    body=b'''<?xml version="1.0"?>
    <nex:nexml xmlns:nex="http://www.nexml.org/2009">
      <nex:trees>
        <nex:tree id="a"><nex:node id="a1"/></nex:tree>
        <nex:tree id="b"><nex:node id="b1"/></nex:tree>
      </nex:trees>
    </nex:nexml>'''
    out=mod.tree_metadata(body)
    assert out["tree_count"]==2
    assert out["selected_tree_id"] is None
    assert out["selection_status"]=="HOLD_TREE_SELECTION_AMBIGUOUS_PRE_TRAIT"
