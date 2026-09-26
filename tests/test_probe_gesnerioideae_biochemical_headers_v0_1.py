from __future__ import annotations

import importlib.util
import io
from pathlib import Path

from openpyxl import Workbook

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts"/"probe_gesnerioideae_biochemical_headers_v0_1.py"
spec=importlib.util.spec_from_file_location("probe",SCRIPT)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def make_xlsx()->bytes:
    wb=Workbook()
    ws=wb.active
    ws.title="FINAL SAMPLE LIST"
    ws.append(["title"])
    ws.append(["notes"])
    ws.append(["Species","Sample","Anthocyanin A","Anthocyanin B","Flower color"])
    ws.append(["X a","s1",1,0,"red"])
    bio=io.BytesIO()
    wb.save(bio)
    return bio.getvalue()


def test_header_only_reads_declared_header_row():
    out=mod.extract_header(make_xlsx(),"FINAL SAMPLE LIST",3)
    assert out==["Species","Sample","Anthocyanin A","Anthocyanin B","Flower color"]


def test_choose_biochemical_columns_excludes_visible_color():
    h=["Species","Sample","Pelargonidin","Cyanidin","Flower color","Reflectance 400"]
    out=mod.biochemical_column_candidates(h)
    assert "Pelargonidin" in out
    assert "Cyanidin" in out
    assert "Flower color" not in out
    assert "Reflectance 400" not in out
