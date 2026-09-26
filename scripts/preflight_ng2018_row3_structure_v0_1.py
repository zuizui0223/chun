#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import io
import json
import posixpath
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PREFLIGHT_PATH=ROOT/"scripts"/"preflight_ng2018_schema_tree_v0_1.py"
spec=importlib.util.spec_from_file_location("preflight",PREFLIGHT_PATH)
preflight=importlib.util.module_from_spec(spec)
spec.loader.exec_module(preflight)

NS_MAIN="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS_REL="http://schemas.openxmlformats.org/officeDocument/2006/relationships"


def q(ns:str,tag:str)->str:
    return f"{{{ns}}}{tag}"


def first_sheet_xml_path(z:zipfile.ZipFile)->str:
    wb=ET.fromstring(z.read("xl/workbook.xml"))
    sheets=wb.find(q(NS_MAIN,"sheets"))
    sheet=list(sheets)[0]
    rid=sheet.attrib[q(NS_REL,"id")]
    rels=ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    target=None
    for rel in rels:
        if rel.attrib.get("Id")==rid:
            target=rel.attrib["Target"]
            break
    if target is None:
        raise RuntimeError(f"worksheet relationship {rid} missing")
    if target.startswith("/"):
        return target.lstrip("/")
    return posixpath.normpath(posixpath.join("xl",target))


def sheet_structure(body:bytes)->dict:
    with zipfile.ZipFile(io.BytesIO(body)) as z:
        path=first_sheet_xml_path(z)
        root=ET.fromstring(z.read(path))
        sheet_data=root.find(q(NS_MAIN,"sheetData"))
        summaries=[]
        for row in sheet_data.findall(q(NS_MAIN,"row")):
            r=int(row.attrib["r"])
            cells=[]
            for cell in row.findall(q(NS_MAIN,"c")):
                has_value=cell.find(q(NS_MAIN,"v")) is not None or cell.find(q(NS_MAIN,"is")) is not None
                cells.append({
                    "ref":cell.attrib.get("r"),
                    "style_id":int(cell.attrib.get("s","0")),
                    "cell_type":cell.attrib.get("t"),
                    "has_formula":cell.find(q(NS_MAIN,"f")) is not None,
                    "has_value_slot":has_value,
                })
            summaries.append({
                "row":r,
                "stored_cell_count":len(cells),
                "occupied_cell_count":sum(1 for c in cells if c["has_value_slot"]),
                "style_ids":sorted({c["style_id"] for c in cells}),
                "cell_types":sorted({str(c["cell_type"]) for c in cells}),
            })
        merge=root.find(q(NS_MAIN,"mergeCells"))
        merged=[x.attrib.get("ref") for x in list(merge)] if merge is not None else []

    occupied={x["row"]:x["occupied_cell_count"] for x in summaries}
    multi=[r for r,n in occupied.items() if n>=2]
    first_multi=min(multi) if multi else None
    preceding_single_or_empty=bool(
        first_multi is not None
        and all(occupied.get(r,0)<=1 for r in range(1,first_multi))
    )
    header_candidate=first_multi if preceding_single_or_empty else None
    return {
        "worksheet_xml_path":path,
        "row_structure":summaries,
        "merged_ranges":merged,
        "first_multi_value_cell_row":first_multi,
        "all_preceding_rows_single_or_empty":preceding_single_or_empty,
        "predeclared_header_candidate_row":header_candidate,
        "candidate_rule":"first row with >=2 value-bearing cells after only <=1-value-cell preamble rows; shared-string and inline-string contents are never decoded",
    }


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    a.out.parent.mkdir(parents=True,exist_ok=True)

    body,url=preflight.recover_trait_source()
    structure=sheet_structure(body)
    candidate=structure["predeclared_header_candidate_row"]
    status=(
        "NG2018_SCHEMA_ROW_OPENING_PREDECLARED"
        if candidate is not None
        else "HOLD_NG2018_HEADER_NOT_STRUCTURALLY_IDENTIFIED"
    )
    out={
        "version":"v0.2",
        "status":status,
        "trait_source_url":url,
        "trait_source_sha256":hashlib.sha256(body).hexdigest(),
        "trait_source_bytes":len(body),
        **structure,
        "shared_string_values_opened":False,
        "inline_string_values_opened":False,
        "trait_data_values_opened":False,
        "trait_state_frequencies_computed":False,
        "hidden_memory_auc_computed":False,
        "next_gate":(
            f"OPEN_ROW_{candidate}_VALUES_AS_SCHEMA_ONLY"
            if candidate is not None
            else "STOP_HOLD"
        ),
    }
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
