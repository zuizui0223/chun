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
NS_PKG="http://schemas.openxmlformats.org/package/2006/relationships"


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


def sheet_structure(body:bytes,rows=(1,2,3,4))->dict:
    with zipfile.ZipFile(io.BytesIO(body)) as z:
        path=first_sheet_xml_path(z)
        root=ET.fromstring(z.read(path))
        sheet_data=root.find(q(NS_MAIN,"sheetData"))
        by_row={}
        for row in sheet_data.findall(q(NS_MAIN,"row")):
            r=int(row.attrib["r"])
            if r not in rows:
                continue
            cells=[]
            for cell in row.findall(q(NS_MAIN,"c")):
                cells.append({
                    "ref":cell.attrib.get("r"),
                    "style_id":int(cell.attrib.get("s","0")),
                    "cell_type":cell.attrib.get("t"),
                    "has_formula":cell.find(q(NS_MAIN,"f")) is not None,
                    "has_value_slot":cell.find(q(NS_MAIN,"v")) is not None or cell.find(q(NS_MAIN,"is")) is not None,
                })
            by_row[str(r)]={"row":r,"cell_count":len(cells),"cells":cells}
        merge=root.find(q(NS_MAIN,"mergeCells"))
        merged=[x.attrib.get("ref") for x in list(merge)] if merge is not None else []

    for r in rows:
        by_row.setdefault(str(r),{"row":r,"cell_count":0,"cells":[]})

    r1=by_row["1"]["cell_count"]
    r2=by_row["2"]["cell_count"]
    r3=by_row["3"]["cell_count"]
    row3_candidate=bool(r3>=2 and r1<=1 and r2<=1)
    return {
        "worksheet_xml_path":path,
        "rows":by_row,
        "merged_ranges":merged,
        "row3_header_candidate_by_structure":row3_candidate,
        "candidate_rule":"row3 has >=2 stored cells while rows1-2 each have <=1 stored cell; no shared-string or inline-string text is decoded",
    }


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    a.out.parent.mkdir(parents=True,exist_ok=True)

    body,url=preflight.recover_trait_source()
    structure=sheet_structure(body)
    status=(
        "NG2018_ROW3_SCHEMA_OPENING_PREDECLARED"
        if structure["row3_header_candidate_by_structure"]
        else "HOLD_NG2018_ROW3_NOT_STRUCTURALLY_IDENTIFIED_AS_HEADER"
    )
    out={
        "version":"v0.1",
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
            "OPEN_ROW3_VALUES_AS_SCHEMA_ONLY"
            if status=="NG2018_ROW3_SCHEMA_OPENING_PREDECLARED"
            else "STOP_HOLD"
        ),
    }
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
