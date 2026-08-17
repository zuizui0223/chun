#!/usr/bin/env python3
"""Normalize GWH GFF3 local IDs to public Accession IDs for cross-assembly work.

GWH files often store prediction-local identifiers in `ID`/`Parent` and stable
public accessions in `Accession`/`Parent_Accession`/`Protein_Accession`. This
script preserves every original attribute while overriding the operational
ID/Parent/protein_id fields with the stable accession when available.
"""
from __future__ import annotations

import argparse
from collections import OrderedDict
from pathlib import Path
from urllib.parse import unquote


def parse_attrs(text: str) -> OrderedDict[str, str]:
    attrs: OrderedDict[str, str] = OrderedDict()
    for raw in text.strip().strip(";").split(";"):
        item = raw.strip()
        if not item:
            continue
        if "=" in item:
            key, value = item.split("=", 1)
            attrs[key] = value
        elif " " in item:
            key, value = item.split(None, 1)
            attrs[key] = value.strip('"')
    return attrs


def render_attrs(attrs: OrderedDict[str, str]) -> str:
    return ";".join(f"{key}={value}" for key, value in attrs.items())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)

    feature_rows = 0
    accession_ids = 0
    accession_parents = 0
    protein_accessions = 0
    with args.input.open(encoding="utf-8", errors="replace") as source, args.output.open("w", encoding="utf-8") as target:
        for line in source:
            if line.startswith("#") or not line.strip():
                target.write(line)
                continue
            fields = line.rstrip("\n").split("\t")
            if len(fields) < 9:
                target.write(line)
                continue
            feature_rows += 1
            feature_type = fields[2].lower()
            attrs = parse_attrs(fields[8])
            accession = unquote(attrs.get("Accession", ""))
            parent_accession = unquote(attrs.get("Parent_Accession", ""))
            protein_accession = unquote(attrs.get("Protein_Accession", ""))

            if accession and (feature_type == "gene" or feature_type in {"mrna", "transcript", "rna", "lnc_rna", "ncrna"} or "transcript" in feature_type):
                attrs["Original_ID"] = attrs.get("ID", "")
                attrs["ID"] = accession
                accession_ids += 1
            if parent_accession:
                attrs["Original_Parent"] = attrs.get("Parent", "")
                attrs["Parent"] = parent_accession
                accession_parents += 1
            if protein_accession:
                attrs["protein_id"] = protein_accession
                protein_accessions += 1
            fields[8] = render_attrs(attrs)
            target.write("\t".join(fields) + "\n")

    print(
        {
            "feature_rows": feature_rows,
            "stable_accession_ids": accession_ids,
            "stable_accession_parents": accession_parents,
            "protein_accessions": protein_accessions,
            "decision": "normalized GFF uses public GWH accession IDs while preserving original local IDs",
        }
    )
    if accession_ids == 0 or accession_parents == 0:
        raise SystemExit("No stable GWH accession relationships were normalized")


if __name__ == "__main__":
    main()
