#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import io
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V1 = ROOT / "scripts/preflight_solanaceae_red_biochemical_source_v0_1.py"

spec = importlib.util.spec_from_file_location("solanaceae_preflight_v01", V1)
if spec is None or spec.loader is None:
    raise RuntimeError("could not load v0.1 preflight module")
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)


def is_docx(payload: bytes) -> bool:
    if not payload.startswith(b"PK"):
        return False
    try:
        with zipfile.ZipFile(io.BytesIO(payload)) as zf:
            return "word/document.xml" in zf.namelist()
    except zipfile.BadZipFile:
        return False


def inspect_docx_identifiers(docx_bytes: bytes, expected_name: str) -> dict:
    if not is_docx(docx_bytes):
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

    if len(grouped) != 1:
        diagnostics = [
            {
                "table_index": c["table_index"],
                "header_row_index": c["header_row_index"],
                "species_column_index": c["species_column_index"],
                "unique_species": c["unique_count"],
            }
            for c in grouped.values()
        ]
        raise RuntimeError(
            "expected one unique >=20-species table/column after multirow-header collapse; "
            f"found {len(grouped)}: {diagnostics}"
        )

    selected = next(iter(grouped.values()))
    uniq = sorted(set(selected["values"]))
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
        "duplicate_header_candidates_collapsed": True,
        "outcome_columns_emitted": False,
        "outcome_data_rows_emitted": False,
    }


def supplement_from_europe_pmc(pmcid: str, filename: str, out_dir: Path):
    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/supplementaryFiles"
    attempts = []
    try:
        payload, final_url, content_type = base.fetch(url, timeout=120)
        rec = {
            "method": "europe_pmc_supplementaryFiles",
            "url": url,
            "final_url": final_url,
            "content_type": content_type,
            "bytes": len(payload),
            "sha256": base.sha256_bytes(payload),
            "is_zip": payload.startswith(b"PK"),
        }
        if not payload.startswith(b"PK"):
            attempts.append(rec)
            return None, {"attempts": attempts, "selected_method": None}
        with zipfile.ZipFile(io.BytesIO(payload)) as zf:
            matches = [name for name in zf.namelist() if Path(name).name == filename]
            rec["matching_members"] = matches
            attempts.append(rec)
            if len(matches) != 1:
                return None, {"attempts": attempts, "selected_method": None}
            docx = zf.read(matches[0])
        ok = is_docx(docx)
        attempts.append({
            "method": "europe_pmc_member",
            "member": matches[0],
            "bytes": len(docx),
            "sha256": base.sha256_bytes(docx),
            "is_docx": ok,
        })
        if ok:
            (out_dir / filename).write_bytes(docx)
            return docx, {
                "attempts": attempts,
                "selected_method": "europe_pmc_supplementaryFiles",
                "selected_url": url,
                "selected_member": matches[0],
            }
    except Exception as exc:
        attempts.append({
            "method": "europe_pmc_supplementaryFiles",
            "url": url,
            "error": f"{type(exc).__name__}: {exc}",
        })
    return None, {"attempts": attempts, "selected_method": None}


def supplement_from_current_pmc_bin(pmcid: str, filename: str, out_dir: Path):
    urls = [
        f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/bin/{filename}",
        f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/bin/{filename}?download=1",
    ]
    attempts = []
    for url in urls:
        try:
            payload, final_url, content_type = base.fetch(url)
            ok = is_docx(payload)
            attempts.append({
                "method": "current_pmc_bin",
                "url": url,
                "final_url": final_url,
                "content_type": content_type,
                "bytes": len(payload),
                "sha256": base.sha256_bytes(payload),
                "is_docx": ok,
            })
            if ok:
                (out_dir / filename).write_bytes(payload)
                return payload, {
                    "attempts": attempts,
                    "selected_method": "current_pmc_bin",
                    "selected_url": url,
                    "selected_final_url": final_url,
                }
        except Exception as exc:
            attempts.append({
                "method": "current_pmc_bin",
                "url": url,
                "error": f"{type(exc).__name__}: {exc}",
            })
    return None, {"attempts": attempts, "selected_method": None}


def acquire_pmc_supplement(pmcid: str, filename: str, out_dir: Path):
    payload, oa = base.supplement_from_oa_package(pmcid, filename, out_dir)
    if payload is not None:
        return payload, {"oa_package": oa, "europe_pmc": None, "current_pmc_bin": None, "article_fallback": None}

    payload, europe = supplement_from_europe_pmc(pmcid, filename, out_dir)
    if payload is not None:
        return payload, {"oa_package": oa, "europe_pmc": europe, "current_pmc_bin": None, "article_fallback": None}

    payload, current = supplement_from_current_pmc_bin(pmcid, filename, out_dir)
    if payload is not None:
        return payload, {"oa_package": oa, "europe_pmc": europe, "current_pmc_bin": current, "article_fallback": None}

    payload, article = base.supplement_from_article_links(pmcid, filename, out_dir)
    if payload is not None:
        return payload, {"oa_package": oa, "europe_pmc": europe, "current_pmc_bin": current, "article_fallback": article}

    raise RuntimeError(
        "could not recover exact PMC supplement; OA + EuropePMC + current-bin + article attempts="
        + json.dumps({"oa": oa, "europe_pmc": europe, "current_pmc_bin": current, "article": article})
    )


base.inspect_docx_identifiers = inspect_docx_identifiers
base.acquire_pmc_supplement = acquire_pmc_supplement

if __name__ == "__main__":
    raise SystemExit(base.main())
