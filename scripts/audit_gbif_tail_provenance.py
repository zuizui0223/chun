#!/usr/bin/env python3
"""Audit provenance and leverage of the coldest occurrence records.

This script is intentionally separate from the ecological model.  It treats the
lowest climatic records as evidence that must pass a provenance gate before a
species-level q05/range-limit statistic is interpreted biologically.

For each taxon it:
- selects the K coldest retained occurrence records;
- quantifies leave-one-record-out change in BIO6 q05;
- flags exact coordinates reused across multiple taxa in the admitted matrix;
- retrieves the current GBIF occurrence record and preserves identification,
  dataset, locality and coordinate metadata needed for manual/range audit.

It does NOT automatically decide whether a record is inside a taxon's native
range.  That judgment needs a declared range source/polygon or taxonomic audit.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import pathlib
import time
from collections import defaultdict

import numpy as np
import requests

GBIF = "https://api.gbif.org/v1"
USER_AGENT = "chun-gbif-tail-provenance/0.1"


def read_csv(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as h:
        return list(csv.DictReader(h))


def write_csv(path: pathlib.Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = list(rows[0])
    with path.open("w", newline="", encoding="utf-8") as h:
        w = csv.DictWriter(h, fieldnames=fields, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)


def get_occurrence(key: str, retries: int = 4) -> dict:
    last = None
    for i in range(retries):
        try:
            r = requests.get(
                f"{GBIF}/occurrence/{key}",
                timeout=60,
                headers={"User-Agent": USER_AGENT},
            )
            r.raise_for_status()
            return r.json()
        except Exception as exc:
            last = exc
            if i + 1 < retries:
                time.sleep(2 ** i)
    return {"_fetch_error": repr(last)}


def q05(vals: list[float]) -> float:
    return float(np.quantile(np.asarray(vals, dtype=float), 0.05))


def clean_text(x: object) -> str:
    if x is None:
        return ""
    if isinstance(x, (list, dict)):
        return json.dumps(x, ensure_ascii=False, sort_keys=True)
    return str(x)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("thermal_points", type=pathlib.Path)
    ap.add_argument("--output", type=pathlib.Path, required=True)
    ap.add_argument("--k", type=int, default=3)
    a = ap.parse_args()

    rows = read_csv(a.thermal_points)
    by_taxon: dict[str, list[dict[str, str]]] = defaultdict(list)
    coord_taxa: dict[tuple[float, float], set[str]] = defaultdict(set)
    for r in rows:
        by_taxon[r["taxon"]].append(r)
        coord = (round(float(r["latitude"]), 6), round(float(r["longitude"]), 6))
        coord_taxa[coord].add(r["taxon"])

    out: list[dict[str, object]] = []
    meta_fields = [
        "scientificName", "acceptedScientificName", "taxonKey", "acceptedTaxonKey",
        "speciesKey", "datasetKey", "datasetTitle", "publishingOrgKey",
        "institutionCode", "collectionCode", "catalogNumber", "occurrenceID",
        "identifiedBy", "identificationQualifier", "typeStatus",
        "coordinateUncertaintyInMeters", "countryCode", "stateProvince",
        "county", "municipality", "locality", "verbatimLocality", "eventDate",
        "year", "basisOfRecord", "establishmentMeans", "degreeOfEstablishment",
        "geodeticDatum", "georeferencedBy", "georeferenceRemarks",
    ]

    for taxon in sorted(by_taxon):
        g = sorted(by_taxon[taxon], key=lambda r: float(r["bio6"]))
        vals = [float(r["bio6"]) for r in g]
        original = q05(vals)
        for rank, r in enumerate(g[: max(1, a.k)], start=1):
            coord = (round(float(r["latitude"]), 6), round(float(r["longitude"]), 6))
            remaining = [float(x["bio6"]) for x in g if x is not r]
            loo = q05(remaining) if remaining else math.nan
            taxa_here = sorted(coord_taxa[coord])
            meta = get_occurrence(str(r["gbif_key"]))
            q = {
                "taxon": taxon,
                "cold_rank": rank,
                "n_species_points": len(g),
                "gbif_key": r["gbif_key"],
                "latitude": r["latitude"],
                "longitude": r["longitude"],
                "bio1": r["bio1"],
                "bio6": r["bio6"],
                "species_bio6_q05": original,
                "loo_bio6_q05": loo,
                "loo_q05_change_C": loo - original,
                "shared_coordinate_taxa_count": len(taxa_here),
                "shared_coordinate_taxa": ";".join(taxa_here),
                "shared_coordinate_flag": "yes" if len(taxa_here) > 1 else "no",
                "gbif_fetch_status": "error" if meta.get("_fetch_error") else "ok",
                "gbif_fetch_error": clean_text(meta.get("_fetch_error", "")),
            }
            for f in meta_fields:
                q[f] = clean_text(meta.get(f, ""))
            out.append(q)
            time.sleep(0.05)

    write_csv(a.output, out)
    print(json.dumps({
        "n_taxa": len(by_taxon),
        "n_audited_records": len(out),
        "n_shared_coordinate_records": sum(r["shared_coordinate_flag"] == "yes" for r in out),
        "output": str(a.output),
    }, indent=2))


if __name__ == "__main__":
    main()
