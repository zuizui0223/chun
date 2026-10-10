#!/usr/bin/env python3
"""Source-only Cape Erica qPCR workbook transport and OOXML sheet inventory.

No biological outcome is calculated. A Figshare private_link is a publicly
published sharing URL in Le Maitre et al. 2019, not an authentication bypass.
Transport failure => SOURCE_HOLD, never an evolutionary hypothesis FAIL.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import pathlib
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
import zipfile

SOURCE_URL = (
    "https://scholardata.sun.ac.za/ndownloader/files/18004067"
    "?private_link=8eb50fa0cf88c0000ed0"
)
SOURCE = {
    "study_doi": "10.3389/fpls.2019.01565",
    "data_doi": "10.25413/sun.9980498",
    "figshare_article_id": 9980498,
    "figshare_file_id": 18004067,
    "metadata_file_format": "XLSX",
    "reported_taxa_species_and_subspecies": 28,
    "reported_resource_size_kb": 87.26,
    "source_role": "independent Cape Erica expression matrix only",
}
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
      "p": "http://schemas.openxmlformats.org/package/2006/relationships"}


def inventory_xlsx(data: bytes) -> dict:
    if not data.startswith(b"PK"):
        raise ValueError("download not a ZIP-based XLSX")
    with zipfile.ZipFile(io.BytesIO(data)) as arc:
        if arc.testzip() is not None:
            raise ValueError("corrupt XLSX ZIP member")
        files = set(arc.namelist())
        if "[Content_Types].xml" not in files or "xl/workbook.xml" not in files:
            raise ValueError("not a spreadsheet workbook")
        wb = ET.fromstring(arc.read("xl/workbook.xml"))
        rels = {}
        if "xl/_rels/workbook.xml.rels" in files:
            root = ET.fromstring(arc.read("xl/_rels/workbook.xml.rels"))
            for rel in root.findall("p:Relationship", NS):
                rels[rel.attrib["Id"]] = rel.attrib["Target"]
        strings = []
        if "xl/sharedStrings.xml" in files:
            root = ET.fromstring(arc.read("xl/sharedStrings.xml"))
            for si in root.findall("m:si", NS):
                strings.append("".join(x.text or "" for x in si.findall(".//m:t", NS)))
        sheets = []
        for sh in wb.findall("m:sheets/m:sheet", NS):
            rel_id = sh.attrib.get("{"+NS["r"]+"}id", "")
            target = rels.get(rel_id, "")
            path = target.lstrip("/") if target.startswith("/") else "xl/" + target
            if path.startswith("xl/xl/"):
                path = path[3:]
            if path not in files:
                raise ValueError("sheet relationship invalid: " + sh.attrib["name"])
            root = ET.fromstring(arc.read(path))
            raw_rows = root.findall("m:sheetData/m:row", NS)
            nonempty = sum(bool(row.findall("m:c", NS)) for row in raw_rows)
            preview = []
            for row in raw_rows[:5]:
                values = []
                for cell in row.findall("m:c", NS)[:14]:
                    value = cell.find("m:v", NS)
                    inline = cell.find("m:is", NS)
                    v = "" if value is None else (value.text or "")
                    if cell.attrib.get("t") == "s" and v:
                        idx = int(v)
                        v = strings[idx] if 0 <= idx < len(strings) else "__SHARED_STRING_INDEX_INVALID__"
                    elif inline is not None:
                        v = "".join(x.text or "" for x in inline.findall(".//m:t", NS))
                    values.append({"ref": cell.attrib.get("r"), "value": v[:100]})
                preview.append(values)
            sheets.append({"name": sh.attrib["name"], "sheet_xml": path,
                           "nonempty_xml_rows": nonempty, "first_five_rows": preview})
    return {"size_bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
            "xlsx_structure": "PASS", "sheets": sheets}


def acquire(*, timeout: int = 25, fetcher=None) -> tuple[dict, bytes | None]:
    result = {"version": "v0.1", "source": SOURCE,
              "status": "HOLD_EXACT_QPCR_WORKBOOK_NOT_RECOVERED",
              "no_biological_outcome_opened": True,
              "new_gene_memory_replicate_admitted": False,
              "trait_tree_expression_joint_source_verified": False,
              "original_submission_artifacts_unchanged": True}
    if fetcher is None:
        fetcher = urllib.request.urlopen
    req = urllib.request.Request(
        SOURCE_URL, headers={"User-Agent": "CHUN-Erica-source-only-preflight/0.1",
                             "Accept": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,*/*"})
    try:
        with fetcher(req, timeout=timeout) as response:
            code = getattr(response, "status", 200)
            result["http_status"] = code
            if code != 200:
                raise ValueError("HTTP " + str(code))
            payload = response.read(2_000_001)
        if len(payload) > 2_000_000:
            raise ValueError("source exceeds 2MB transport ceiling")
        inv = inventory_xlsx(payload)
    except (OSError, ValueError, zipfile.BadZipFile, ET.ParseError,
            urllib.error.URLError) as exc:
        result["transport_or_structure_error"] = type(exc).__name__ + ": " + str(exc)[:350]
        return result, None
    result.update(inv)
    result["status"] = "SOURCE_XLSX_BYTES_RECOVERED_TREE_PIGMENT_JOIN_NOT_YET_ADMITTED"
    return result, payload


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=pathlib.Path, required=True)
    ap.add_argument("--save-xlsx", type=pathlib.Path)
    ap.add_argument("--timeout", type=int, default=25)
    args = ap.parse_args()
    if args.timeout < 1 or args.timeout > 90:
        raise ValueError("invalid transport timeout")
    result, payload = acquire(timeout=args.timeout)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
                        encoding="utf-8")
    if payload is not None and args.save_xlsx is not None:
        args.save_xlsx.parent.mkdir(parents=True, exist_ok=True)
        args.save_xlsx.write_bytes(payload)
    print("ERICA_SOURCE_ONLY_STATUS", result["status"])
    print("ERICA_SHEETS", [(s["name"], s["nonempty_xml_rows"]) for s in result.get("sheets", [])])
    for sh in result.get("sheets", []):
        print("ERICA_SOURCE_FIRST_FIVE_ROWS", sh["name"], json.dumps(sh["first_five_rows"], ensure_ascii=False))
    if "transport_or_structure_error" in result:
        print("SOURCE_HOLD_CAUSE", result["transport_or_structure_error"])
    print("INDEPENDENT_MEMORY_REPLICATION_NOT_TESTED")


if __name__ == "__main__":
    main()
