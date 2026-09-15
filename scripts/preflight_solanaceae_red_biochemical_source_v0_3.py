#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import io
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V2 = ROOT / "scripts/preflight_solanaceae_red_biochemical_source_v0_2.py"

spec = importlib.util.spec_from_file_location("solanaceae_preflight_v02", V2)
if spec is None or spec.loader is None:
    raise RuntimeError("could not load v0.2 preflight module")
v2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v2)
base = v2.base


def inspect_docx_identifiers(docx_bytes: bytes, expected_name: str) -> dict:
    if not v2.is_docx(docx_bytes):
        raise RuntimeError("supplement payload is not a valid DOCX")
    with zipfile.ZipFile(io.BytesIO(docx_bytes)) as zf:
        root = ET.fromstring(zf.read("word/document.xml"))

    tables = [x for x in root.iter() if base.local_name(x.tag) == "tbl"]
    structural = []
    grouped = {}
    for ti, tbl in enumerate(tables):
        trs = [x for x in list(tbl) if base.local_name(x.tag) == "tr"]
        rows = [[base.text_content(tc) for tc in list(tr) if base.local_name(tc.tag) == "tc"] for tr in trs]
        structural.append({
            "table_index": ti,
            "rows": len(rows),
            "max_columns": max((len(r) for r in rows), default=0),
        })
        for hi, header in enumerate(rows[:5]):
            for ci, cell in enumerate(header):
                normalized_header = re.sub(r"\s+", " ", cell.strip().lower())
                if normalized_header not in {"species", "taxon", "study species", "species name"}:
                    continue
                vals = []
                for row in rows[hi + 1:]:
                    if ci < len(row):
                        species = base.norm_species(row[ci])
                        if species:
                            vals.append(species)
                if len(set(vals)) < 20:
                    continue
                key = (ti, ci)
                candidate = {
                    "table_index": ti,
                    "header_row_index": hi,
                    "species_column_index": ci,
                    "header": header,
                    "values": vals,
                    "unique_count": len(set(vals)),
                }
                previous = grouped.get(key)
                if previous is None or candidate["unique_count"] > previous["unique_count"] or (
                    candidate["unique_count"] == previous["unique_count"]
                    and candidate["header_row_index"] < previous["header_row_index"]
                ):
                    grouped[key] = candidate

    candidates = sorted(
        grouped.values(),
        key=lambda c: (c["table_index"], c["species_column_index"], c["header_row_index"]),
    )
    if not candidates:
        raise RuntimeError("no >=20-species identifier table/column found")

    species_sets = [set(c["values"]) for c in candidates]
    reference = species_sets[0]
    if any(s != reference for s in species_sets[1:]):
        diagnostics = [
            {
                "table_index": c["table_index"],
                "header_row_index": c["header_row_index"],
                "species_column_index": c["species_column_index"],
                "unique_species": len(s),
                "missing_vs_first": len(reference - s),
                "extra_vs_first": len(s - reference),
            }
            for c, s in zip(candidates, species_sets)
        ]
        raise RuntimeError(
            "multiple >=20-species identifier tables do not share one identical species universe: "
            f"{diagnostics}"
        )

    selected = candidates[0]
    uniq = sorted(reference)
    return {
        "expected_filename": expected_name,
        "docx_bytes": len(docx_bytes),
        "docx_sha256": base.sha256_bytes(docx_bytes),
        "table_count": len(tables),
        "table_structure": structural,
        "selected_table_index": selected["table_index"],
        "selected_header_row_index": selected["header_row_index"],
        "selected_species_column_index": selected["species_column_index"],
        "selected_header": selected["header"],
        "species_rows_parsed": len(selected["values"]),
        "unique_normalized_species": len(uniq),
        "normalized_species": uniq,
        "species_identifier_table_count": len(candidates),
        "species_identifier_table_indices": [c["table_index"] for c in candidates],
        "identical_species_universe_across_candidate_tables": True,
        "duplicate_header_candidates_collapsed": True,
        "outcome_columns_emitted": False,
        "outcome_data_rows_emitted": False,
    }


base.inspect_docx_identifiers = inspect_docx_identifiers

if __name__ == "__main__":
    raise SystemExit(base.main())
