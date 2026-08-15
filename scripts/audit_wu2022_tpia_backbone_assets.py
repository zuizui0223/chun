#!/usr/bin/env python3
"""Audit whether Wu et al. 2022 Camellia data can seed a public nuclear backbone.

This is a provenance/crosswalk gate, not a phylogenetic reconstruction. It joins
public taxon evidence from PRJNA665925 RunInfo and, when available, publisher
Table S1 to the live TPIA `selectAllassemblies` catalog and records which taxa
expose downloadable transcriptome assembly ZIPs.
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
        for i, row in enumerate(ws.iter_rows(values_only=True)):
            if i >= 20: break
            vals = [clean(v) for v in row]
            joined = " ".join(vals).lower()
            if "species" in joined: score += 2
            if "accession" in joined or "bioproject" in joined or "sra" in joined: score += 1
        candidates.append((score, ws))
    candidates.sort(key=lambda z: z[0], reverse=True)
    ws = candidates[0][1]
    rows = list(ws.iter_rows(values_only=True))
    header_i = None
    for i, row in enumerate(rows[:40]):
        vals = [clean(v) for v in row]
        if any(v.lower() == "species" or "species" in v.lower() for v in vals):
            header_i = i; break
    if header_i is None: header_i = 0
    header = [clean(v) or f"col_{j+1}" for j, v in enumerate(rows[header_i])]
    seen = defaultdict(int); unique_header = []
    for h in header:
        seen[h] += 1
        unique_header.append(h if seen[h] == 1 else f"{h}_{seen[h]}")
    out_rows = []; taxa = set()
    for row in rows[header_i + 1:]:
        vals = [clean(v) for v in row]
        if not any(vals): continue
        vals += [""] * (len(unique_header) - len(vals))
        rec = dict(zip(unique_header, vals[:len(unique_header)]))
        found = sorted({t for v in vals if (t := norm_taxon(v))})
        rec["_normalized_camellia_taxa"] = ";".join(found)
        taxa.update(found); out_rows.append(rec)
    return ws.title, unique_header + ["_normalized_camellia_taxa"], out_rows, sorted(taxa)


def extract_sra_taxa(path: Path):
    with path.open(newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    taxa = set(); out = []
    for r in rows:
        sci = clean(r.get("ScientificName") or r.get("scientific_name") or r.get("Organism"))
        tax = norm_taxon(sci)
        if tax: taxa.add(tax)
        out.append({
            "Run": clean(r.get("Run")),
            "BioSample": clean(r.get("BioSample")),
            "ScientificName": sci,
            "normalized_taxon": tax,
            "BioProject": clean(r.get("BioProject")),
            "LibraryStrategy": clean(r.get("LibraryStrategy")),
        })
    return out, sorted(taxa)


def fetch_json(session, url, **kwargs):
    r = session.get(url, timeout=90, **kwargs)
    r.raise_for_status()
    try: return r.json()
    except Exception: return json.loads(r.text)


def write_csv(path: Path, rows, fields=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    if fields is None: fields = sorted({k for r in rows for k in r}) if rows else []
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--supp-xlsx", type=Path)
    ap.add_argument("--sra-runinfo", type=Path)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--tpia-base", default="https://tpia.teaplants.cn")
    args = ap.parse_args()
    if not args.supp_xlsx and not args.sra_runinfo:
        raise SystemExit("Provide --supp-xlsx and/or --sra-runinfo")
    out = args.out_dir; out.mkdir(parents=True, exist_ok=True)

    source_taxa = set(); source_parts = []
    table_sheet = None; table_rows_n = 0
    if args.supp_xlsx and args.supp_xlsx.exists():
        sheet, fields, rows, taxa = extract_table_s1_taxa(args.supp_xlsx)
        write_csv(out / "wu2022_table_s1_rows.csv", rows, fields)
        source_taxa.update(taxa); source_parts.append("publisher_Table_S1")
        table_sheet = sheet; table_rows_n = len(rows)
    sra_rows_n = 0; sra_taxa_n = 0
    if args.sra_runinfo and args.sra_runinfo.exists():
        rows, taxa = extract_sra_taxa(args.sra_runinfo)
        write_csv(out / "prjna665925_run_taxa.csv", rows)
        source_taxa.update(taxa); source_parts.append("PRJNA665925_RunInfo")
        sra_rows_n = len(rows); sra_taxa_n = len(taxa)
    source_taxa = sorted(source_taxa)

    sess = requests.Session(); sess.headers.update({"User-Agent": "Mozilla/5.0 chun-public-backbone-audit/0.2"})
    catalog = fetch_json(sess, args.tpia_base.rstrip("/") + "/selectAllassemblies")
    if isinstance(catalog, dict):
        for key in ("data", "rows", "result"):
            if isinstance(catalog.get(key), list): catalog = catalog[key]; break
    if not isinstance(catalog, list): raise SystemExit(f"Unexpected selectAllassemblies payload type: {type(catalog)}")

    catrows = []; bytax = defaultdict(list)
    for r in catalog:
        name = clean(r.get("name")); tax = norm_taxon(name); zip_url = ""
        if r.get("hasZipFile"):
            zip_url = args.tpia_base.rstrip("/") + "/web/All_assemblies/Fasta/" + quote(f"{r.get('ID')}_{name}.zip", safe="_")
        row = {k: clean(v) for k, v in r.items()}
        row.update({"normalized_taxon": tax, "assembly_zip_url": zip_url})
        catrows.append(row)
        if tax: bytax[tax].append(row)
    write_csv(out / "tpia_allassemblies_catalog.csv", catrows)

    bulk = fetch_json(sess, args.tpia_base.rstrip("/") + "/selectdownload_data", params={"Type": "Transcriptome data"})
    if isinstance(bulk, dict):
        for key in ("data", "rows", "result"):
            if isinstance(bulk.get(key), list): bulk = bulk[key]; break
    if isinstance(bulk, list): write_csv(out / "tpia_transcriptome_bulk_catalog.csv", [{k: clean(v) for k, v in r.items()} for r in bulk])
    else: (out / "tpia_transcriptome_bulk_raw.json").write_text(json.dumps(bulk, ensure_ascii=False, indent=2) + "\n")

    cross = []; missing = []
    for tax in source_taxa:
        hits = bytax.get(tax, []); ziphits = [h for h in hits if h.get("assembly_zip_url")]
        if not hits: missing.append(tax)
        cross.append({
            "source_taxon": tax,
            "tpia_match_count": len(hits),
            "tpia_names": ";".join(sorted({h.get("name", "") for h in hits})),
            "zip_match_count": len(ziphits),
            "zip_urls": ";".join(h["assembly_zip_url"] for h in ziphits),
            "status": "downloadable_assembly" if ziphits else ("catalog_only_no_zip" if hits else "missing_from_tpia_catalog"),
        })
    write_csv(out / "wu2022_tpia_species_crosswalk.csv", cross)

    summary = {
        "source": "+".join(source_parts),
        "doi": "10.1111/tpj.15799",
        "publisher_table_s1_recovered": bool(args.supp_xlsx and args.supp_xlsx.exists()),
        "table_s1_sheet": table_sheet,
        "table_s1_rows": table_rows_n,
        "sra_runinfo_rows": sra_rows_n,
        "sra_unique_camellia_taxa": sra_taxa_n,
        "source_unique_camellia_taxa": len(source_taxa),
        "tpia_catalog_rows": len(catrows),
        "tpia_unique_camellia_taxa": len(bytax),
        "source_taxa_with_tpia_catalog_match": sum(1 for r in cross if int(r["tpia_match_count"]) > 0),
        "source_taxa_with_downloadable_zip": sum(1 for r in cross if int(r["zip_match_count"]) > 0),
        "missing_source_taxa": missing,
        "claim_ceiling": "asset/crosswalk gate only; species-level reconstruction may omit duplicated cultivated-tea tips; no topology or transition inference",
    }
    (out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))

if __name__ == "__main__": main()
