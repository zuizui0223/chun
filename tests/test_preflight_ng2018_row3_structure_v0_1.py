from __future__ import annotations

import importlib.util
import io
import zipfile
from pathlib import Path

from openpyxl import Workbook

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts"/"preflight_ng2018_row3_structure_v0_1.py"
spec=importlib.util.spec_from_file_location("row3",SCRIPT)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def workbook_bytes(rows):
    wb=Workbook()
    ws=wb.active
    for row in rows:
        ws.append(row)
    b=io.BytesIO()
    wb.save(b)
    return b.getvalue()


def test_structure_predeclares_row3_after_two_single_cell_preamble_rows():
    body=workbook_bytes([
        ["title"],
        ["explanation"],
        ["header1","header2"],
        ["data1","data2"],
    ])
    out=mod.sheet_structure(body)
    assert out["rows"]["1"]["cell_count"]==1
    assert out["rows"]["2"]["cell_count"]==1
    assert out["rows"]["3"]["cell_count"]==2
    assert out["row3_header_candidate_by_structure"] is True


def test_structure_holds_when_row3_is_not_two_cell_boundary():
    body=workbook_bytes([
        ["title"],
        ["explanation"],
        ["only one"],
    ])
    out=mod.sheet_structure(body)
    assert out["row3_header_candidate_by_structure"] is False


def test_structure_does_not_decode_cell_text():
    body=workbook_bytes([
        ["SECRET_TITLE"],
        ["SECRET_EXPLANATION"],
        ["SECRET_HEADER_A","SECRET_HEADER_B"],
    ])
    out=mod.sheet_structure(body)
    text=repr(out)
    assert "SECRET_TITLE" not in text
    assert "SECRET_EXPLANATION" not in text
    assert "SECRET_HEADER_A" not in text
    assert "SECRET_HEADER_B" not in text
