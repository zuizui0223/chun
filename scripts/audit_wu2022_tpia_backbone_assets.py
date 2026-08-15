#!/usr/bin/env python3
"""Audit whether Wu et al. 2022 Camellia tips can be reconstructed from public TPIA assemblies.

This is a provenance/crosswalk gate, not a phylogenetic reconstruction. It joins the
publisher Table S1 species names to the live TPIA `selectAllassemblies` catalog and
records which taxa expose downloadable transcriptome assembly ZIPs.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import quote

import requests
from openpyxl import load_workbook


def clean(x):
    return "" if x is None else re.sub(r"\s+", " ", str(x).replace("\xa0", " ").strip())


def norm_taxon(x: str) -> str:
    x = clean(x)
    x = re.sub(r"^C\.\s*", "Camellia ", x)
    x = re.sub(r"\s+", " ", x)
    m = re.search(r"\bCamellia\s+([A-Za-z][A-Za-z-]+)", x, re.I)
    return f"Camellia {m.group(1).lower()}" if m else ""


def extract_table_s1_taxa(xlsx: Path):
    wb = load_workbook(xlsx, read_only=True, data_only=True)
    candidates = []
    for ws in wb.worksheets:
        score = 0
        lname = ws.title.lower().replace(" ", "")
        if "s1" in lname or "table1" in lname: score += 5
        preview = []
        for i, row in enumerate(ws.iter_rows(values_only=True)):
            if i >= 20: break
            vals = [clean(v) for v in row]
            preview.append(vals)
            joined = " ".join(vals).lower()
            if "species" in joined: score += 2
            if "accession" in joined or "bioproject" in joined or "sra" in joined: score += 1
        candidates.append((score, ws, preview))
    candidates.sort(key=lambda z: z[0], reverse=True)
    ws = candidates[0][1]
    rows = list(ws.iter_rows(values_only=True))
    # Locate a header row that contains Species; preserve all columns.
    header_i = None
    for i, row in enumerate(rows[:40]):
        vals = [clean(v) for v in row]
        if any(v.lower() == "species" or "species" in v.lower() for v in vals):
            header_i = i; break
    if header_i is None:
        header_i = 0
    header = [clean(v) or f"col_{j+1}" for j, v in enumerate(rows[header_i])]
    seen = defaultdict(int)
    unique_header = []
    for h in header:
        seen[h] += 1
        unique_header.append(h if seen[h] == 1 else f"{h}_{seen[h]}")
    out_rows = []
    taxa = set()
    for row in rows[header_i + 1:]:
        vals = [clean(v) for v in row]
        if not any(vals): continue
        vals += [""] * (len(unique_header) - len(vals))
        rec = dict(zip(unique_header, vals[:len(unique_header)]))
        found = []
        for v in vals:
            t = norm_taxon(v)
            if t: found.append(t)
        if found:
            rec["_normalized_camellia_taxa"] = ";".join(sorted(set(found)))
            taxa.update(found)
        else:
            rec["_normalized_camellia_taxa"] = ""
        out_rows.append(rec)
    return ws.title, unique_header + ["_normalized_camellia_taxa"], out_rows, sorted(taxa)


def fetch_json(session, url, **kwargs):
    r = session.get(url, timeout=90, **kwargs)
    r.raise_for_status()
    try:
        return r.json()
    except Exception:
        return json.loads(r.text)


def write_csv(path: Path, rows, fields=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    if fields is None:
        fields = sorted({k for r in rows for k in r}) if rows else []
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--supp-xlsx", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--tpia-base", default="https://tpia.teaplants.cn")
    args = ap.parse_args()
    out = args.out_dir; out.mkdir(parents=True, exist_ok=True)

    sheet, fields, s1rows, s1taxa = extract_table_s1_taxa(args.supp_xlsx)
    write_csv(out / "wu2022_table_s1_rows.csv", s1rows, fields)

    sess = requests.Session()
    sess.headers.update({"User-Agent": "Mozilla/5.0 chun-public-backbone-audit/0.1"})
    catalog = fetch_json(sess, args.tpia_base.rstrip("/") + "/selectAllassemblies")
    if isinstance(catalog, dict):
        for key in ("data", "rows", "result"):
            if isinstance(catalog.get(key), list): catalog = catalog[key]; break
    if not isinstance(catalog, list):
        raise SystemExit(f"Unexpected selectAllassemblies payload type: {type(catalog)}")

    catrows = []
    bytax = defaultdict(list)
    for r in catalog:
        name = clean(r.get("name"))
        tax = norm_taxon(name)
        zip_url = ""
        if r.get("hasZipFile"):
            zip_url = args.tpia_base.rstrip("/") + "/web/All_assemblies/Fasta/" + quote(f"{r.get('ID')}_{name}.zip", safe="_")
        row = {k: clean(v) for k, v in r.items()}
        row.update({"normalized_taxon": tax, "assembly_zip_url": zip_url})
        catrows.append(row)
        if tax: bytax[tax].append(row)
    write_csv(out / "tpia_allassemblies_catalog.csv", catrows)

    # Also freeze the public bulk-download catalog for Transcriptome data.
    bulk = fetch_json(sess, args.tpia_base.rstrip("/") + "/selectdownload_data", params={"Type": "Transcriptome data"})
    if isinstance(bulk, dict):
        for key in ("data", "rows", "result"):
            if isinstance(bulk.get(key), list): bulk = bulk[key]; break
    if isinstance(bulk, list): write_csv(out / "tpia_transcriptome_bulk_catalog.csv", [{k: clean(v) for k, v in r.items()} for r in bulk])
    else: (out / "tpia_transcriptome_bulk_raw.json").write_text(json.dumps(bulk, ensure_ascii=False, indent=2) + "\n")

    cross = []
    missing = []
    for tax in s1taxa:
        hits = bytax.get(tax, [])
        if not hits:
            missing.append(tax)
            cross.append({"table_s1_taxon": tax, "tpia_match_count": 0, "tpia_names": "", "zip_match_count": 0, "zip_urls": "", "status": "missing_from_tpia_catalog"})
            continue
        ziphits = [h for h in hits if h.get("assembly_zip_url")]
        cross.append({
            "table_s1_taxon": tax,
            "tpia_match_count": len(hits),
            "tpia_names": ";".join(sorted({h.get("name", "") for h in hits})),
            "zip_match_count": len(ziphits),
            "zip_urls": ";".join(h["assembly_zip_url"] for h in ziphits),
            "status": "downloadable_assembly" if ziphits else "catalog_only_no_zip",
        })
    write_csv(out / "wu2022_tpia_species_crosswalk.csv", cross)

    summary = {
        "source": "Wu et al. 2022 Table S1 + live TPIA2 assembly catalog",
        "doi": "10.1111/tpj.15799",
        "table_s1_sheet": sheet,
        "table_s1_rows": len(s1rows),
        "table_s1_unique_camellia_taxa_detected": len(s1taxa),
        "tpia_catalog_rows": len(catrows),
        "tpia_unique_camellia_taxa": len(bytax),
        "table_s1_taxa_with_tpia_catalog_match": sum(1 for r in cross if int(r["tpia_match_count"]) > 0),
        "table_s1_taxa_with_downloadable_zip": sum(1 for r in cross if int(r["zip_match_count"]) > 0),
        "missing_table_s1_taxa": missing,
        "claim_ceiling": "asset/crosswalk gate only; no topology or transition inference",
    }
    (out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
