from __future__ import annotations

import importlib.util
import io
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


def test_structure_finds_first_multi_cell_boundary_after_preamble():
    body=workbook_bytes([
        ["title"],
        ["explanation"],
        ["another explanation"],
        ["header1","header2"],
        ["data1","data2"],
    ])
    out=mod.sheet_structure(body)
    assert out["first_multi_value_cell_row"]==4
    assert out["all_preceding_rows_single_or_empty"] is True
    assert out["predeclared_header_candidate_row"]==4


def test_structure_holds_without_multi_cell_boundary():
    body=workbook_bytes([
        ["title"],
        ["explanation"],
        ["only one"],
    ])
    out=mod.sheet_structure(body)
    assert out["first_multi_value_cell_row"] is None
    assert out["predeclared_header_candidate_row"] is None


def test_structure_does_not_decode_cell_text_anywhere():
    body=workbook_bytes([
        ["SECRET_TITLE"],
        ["SECRET_EXPLANATION"],
        ["SECRET_MORE"],
        ["SECRET_HEADER_A","SECRET_HEADER_B"],
        ["SECRET_DATA_A","SECRET_DATA_B"],
    ])
    out=mod.sheet_structure(body)
    text=repr(out)
    for secret in [
        "SECRET_TITLE","SECRET_EXPLANATION","SECRET_MORE",
        "SECRET_HEADER_A","SECRET_HEADER_B","SECRET_DATA_A","SECRET_DATA_B"
    ]:
        assert secret not in text
