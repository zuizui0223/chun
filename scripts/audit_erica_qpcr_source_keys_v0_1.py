#!/usr/bin/env python3
"""Audit *source identity keys*, not a new evolutionary outcome, in Cape Erica qPCR XLSX."""
from __future__ import annotations
import argparse
import collections
import hashlib
import io
import json
import pathlib
import re
import xml.etree.ElementTree as ET
import zipfile

from preflight_erica_qpcr_xlsx_source_v0_1 import NS, inventory_xlsx

ID_PATTERN = re.compile(r"^(?P<taxon>.+?)_(?P<stage>Adult|Juvenile|Intermediate)_(?P<slot>[0-9]+)_(?P<gene>.+)$", re.I)


def extract_rows(data: bytes, path: str) -> list[dict[str, str]]:
    with zipfile.ZipFile(io.BytesIO(data)) as arc:
        shared = []
        if "xl/sharedStrings.xml" in arc.namelist():
            root = ET.fromstring(arc.read("xl/sharedStrings.xml"))
            for item in root.findall("m:si", NS):
                shared.append("".join(el.text or "" for el in item.findall(".//m:t", NS)))
        root = ET.fromstring(arc.read(path))
        all_rows = []
        for row in root.findall("m:sheetData/m:row", NS):
            cells = {}
            for c in row.findall("m:c", NS):
                ref = c.attrib.get("r", "")
                col = re.match(r"[A-Z]+", ref)
                if not col:
                    continue
                value = c.find("m:v", NS)
                inline = c.find("m:is", NS)
                txt = (value.text or "") if value is not None else ""
                if c.attrib.get("t") == "s" and txt:
                    txt = shared[int(txt)]
                elif inline is not None:
                    txt = "".join(x.text or "" for x in inline.findall(".//m:t", NS))
                cells[col.group()] = txt
            if cells:
                all_rows.append(cells)
        return all_rows


def source_key_audit(data: bytes) -> dict:
    wb = inventory_xlsx(data)
    paths = {x["name"]: x["sheet_xml"] for x in wb["sheets"]}
    needed = ["Matrix non-normalized", "Matrix normalized", "Fold Change"]
    if any(k not in paths for k in needed):
        raise ValueError("required three source matrix tabs are missing")
    sheets = {k: extract_rows(data, paths[k]) for k in needed}
    keys = {}
    for name, rows in sheets.items():
        if not rows or rows[0].get("A") != "ID_REF":
            raise ValueError("missing ID_REF header in " + name)
        ids = [r.get("A", "").strip() for r in rows[1:]]
        if not ids or any(not v for v in ids) or len(set(ids)) != len(ids):
            raise ValueError("duplicate/missing expression ID_REF in " + name)
        keys[name] = ids
    if not (keys[needed[0]] == keys[needed[1]] == keys[needed[2]]):
        raise ValueError("matrix sheets have different ordered measurement IDs")
    expressions = sheets["Fold Change"][1:]
    parsed = []
    unparsed = []
    nonnumeric = []
    for r in expressions:
        identifier = r["A"].strip()
        m = ID_PATTERN.fullmatch(identifier)
        if not m:
            unparsed.append(identifier)
        else:
            parsed.append(m.groupdict())
        try:
            value = float(r.get("B", ""))
            if value != value or value == float("inf") or value == -float("inf"):
                raise ValueError("nonfinite")
        except ValueError:
            nonnumeric.append(identifier)
    taxa = collections.Counter(r["taxon"] for r in parsed)
    stages = collections.Counter(r["stage"].lower() for r in parsed)
    genes = collections.Counter(r["gene"] for r in parsed)
    taxa_stage = collections.Counter((r["taxon"], r["stage"].lower()) for r in parsed)
    taxa_gene = collections.Counter((r["taxon"], r["gene"]) for r in parsed)
    axis = sorted(genes)
    per_taxon_genes = {}
    for taxon in sorted(taxa):
        found = {gene for (t, gene), n in taxa_gene.items() if t == taxon}
        per_taxon_genes[taxon] = len(found)
    status = ("SOURCE_KEYS_ADMITTED_FOR_SCHEMA_ONLY"
              if not unparsed and not nonnumeric and len(parsed) == len(expressions)
              else "HOLD_UNRESOLVED_MEASUREMENT_KEYS_OR_NUMERIC_VALUES")
    return {
        "version": "v0.1",
        "status": status,
        "source_data_doi": "10.25413/sun.9980498",
        "xlsx_sha256": hashlib.sha256(data).hexdigest(),
        "source_sheet_rows": {k: len(v) for k, v in sheets.items()},
        "measurements": len(expressions),
        "parsed_measurements": len(parsed),
        "unparsed_measurement_ids": unparsed[:15],
        "nonnumeric_fold_change_ids": nonnumeric[:15],
        "nonnumeric_fold_change_count": len(nonnumeric),
        "unparsed_measurement_count": len(unparsed),
        "taxon_count_from_measurement_ids": len(taxa),
        "taxa_with_row_counts": dict(sorted(taxa.items())),
        "stages": dict(sorted(stages.items())),
        "gene_count_from_measurement_ids": len(genes),
        "genes_with_row_counts": dict(sorted(genes.items())),
        "taxon_stage_combinations": len(taxa_stage),
        "taxon_gene_panel_counts": per_taxon_genes,
        "complete_fixed_gene_panel_taxa": sum(v == len(axis) for v in per_taxon_genes.values()),
        "not_estimate_of_independent_ancestors": True,
        "no_pigment_species_tree_matched_analysis": True,
        "no_phenotype_class_association_test": True,
        "independent_replication_admitted": False,
        "first_submission_science_unchanged": True
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=pathlib.Path, required=True)
    parser.add_argument("--out", type=pathlib.Path, required=True)
    args = parser.parse_args()
    r = source_key_audit(args.source.read_bytes())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(r, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    for k in ["status", "measurements", "taxon_count_from_measurement_ids",
              "gene_count_from_measurement_ids", "stages",
              "taxon_stage_combinations", "complete_fixed_gene_panel_taxa"]:
        print("ERICA_SOURCE_KEY_AUDIT", k, r[k])
    print("ERICA_GENE_PANEL", sorted(r["genes_with_row_counts"]))
    print("ERICA_ALL_TAXA", sorted(r["taxa_with_row_counts"]))
    print("ERICA_UNPARSED", r["unparsed_measurement_ids"])
    print("ERICA_MISSING_OR_NONNUMERIC_FOLD_CHANGE_COUNT", r["nonnumeric_fold_change_count"])
    print("ERICA_MISSING_OR_NONNUMERIC_FOLD_CHANGE_FIRST", r["nonnumeric_fold_change_ids"])
    print("INDEPENDENT_PHYLOGENETIC_MEMORY_NOT_YET_TESTED")


if __name__ == "__main__":
    main()
