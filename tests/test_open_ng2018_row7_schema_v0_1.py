from __future__ import annotations

import importlib.util
import io
from pathlib import Path

from openpyxl import Workbook

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts"/"open_ng2018_row7_schema_v0_1.py"
spec=importlib.util.spec_from_file_location("row7",SCRIPT)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def workbook_bytes():
    wb=Workbook()
    ws=wb.active
    for x in ["title","explanation1","explanation2","explanation3","explanation4"]:
        ws.append([x])
    ws.append([])
    ws.append(["Species","Source"])
    ws.append(["SECRET_SPECIES","SECRET_SOURCE"])
    b=io.BytesIO()
    wb.save(b)
    return b.getvalue()


def test_row_values_reads_requested_schema_row():
    out=mod.row_values(workbook_bytes(),7)
    assert out==["Species","Source"]


def test_frozen_trait_terms_do_not_treat_source_as_trait():
    header=["Species","Source"]
    norm=[x.lower() for x in header]
    trait=[
        raw for raw,n in zip(header,norm)
        if any(term in n for term in mod.TRAIT_TERMS)
    ]
    assert trait==[]


def test_source_unavailable_receipt_preserves_row7_firewall():
    out=mod.source_unavailable_receipt("exact Table S1 source no longer recoverable")
    assert out["status"]=="HOLD_NG2018_TRAIT_SUPPLEMENT_SOURCE_UNAVAILABLE"
    assert out["header_row_frozen_before_value_opening"]==7
    assert out["header"]==[]
    assert out["rows_8_plus_opened"] is False
    assert out["trait_data_rows_opened"]==0
    assert out["trait_state_frequencies_computed"] is False
    assert out["tree_trait_crosswalk_computed"] is False
    assert out["hidden_memory_auc_computed"] is False
    assert out["next_gate"]=="STOP_HOLD"
