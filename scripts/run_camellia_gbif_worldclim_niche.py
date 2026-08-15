#!/usr/bin/env python3
"""Build a conservative Camellia species climatic-niche matrix from GBIF + WorldClim.

Design principles
-----------------
* use only taxon-level wild colour states frozen in data/camellia_macro_niche_taxa_v0_1.csv;
* query GBIF only inside pre-declared native-country filters;
* exclude living specimens, explicit non-native establishment, garden/cultivation text,
  high coordinate uncertainty, duplicates, and records with GBIF geospatial issues;
* spatially thin to one record per 0.1-degree cell;
* extract WorldClim 2.1 10-minute BIO1, BIO4, BIO6, BIO12 and BIO15;
* treat species, not occurrence records, as the units of group comparison;
* report exact permutation tests when sample sizes permit.

This is a preliminary macroecological analysis, not a phylogenetically corrected
causal analysis. It is designed to decide whether a simple visible-colour/cold
association survives a conservative species-level screen before heavier models.
"""

from __future__ import annotations

import argparse
import csv
import itertools
import json
import math
import pathlib
import re
import shutil
import statistics
import time
import zipfile
from collections import Counter
from typing import Iterable

import numpy as np
import requests
import rasterio

GBIF = "https://api.gbif.org/v1"
WORLDCLIM_BIO_10M = "https://geodata.ucdavis.edu/climate/worldclim/2_1/base/wc2.1_10m_bio.zip"
USER_AGENT = "chun-camellia-niche/0.1 (public biodiversity synthesis)"

ALLOWED_BASIS = {
    "PRESERVED_SPECIMEN",
    "MATERIAL_SAMPLE",
    "HUMAN_OBSERVATION",
    "OBSERVATION",
    "MATERIAL_CITATION",
    "OCCURRENCE",
}
NON_NATIVE = {
    "INTRODUCED",
    "NATURALISED",
    "NATURALIZED",
    "INVASIVE",
    "MANAGED",
    "CAPTIVE",
}
CULTIVATION_RE = re.compile(
    r"\b(cultivat(?:ed|ion)|garden|botanic(?:al)?\s+garden|arboretum|nursery|plantation|cultivar)\b",
    re.I,
)
BIO_VARS = [1, 4, 6, 12, 15]


def read_csv(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: pathlib.Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    if fields is None:
        fields = list(rows[0])
    with path.open("w", newline="", encoding="utf-8") as handle:
        w = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)


def get_json(url: str, params=None, retries: int = 5) -> dict:
    last = None
    for attempt in range(retries):
        try:
            r = requests.get(url, params=params, timeout=90, headers={"User-Agent": USER_AGENT})
            r.raise_for_status()
            return r.json()
        except Exception as exc:
            last = exc
            if attempt + 1 < retries:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"request failed: {url} params={params}") from last


def gbif_match(name: str) -> dict:
    data = get_json(f"{GBIF}/species/match", {"name": name, "kingdom": "Plantae"})
    return {
        "query_name": name,
        "usageKey": data.get("usageKey") or data.get("speciesKey") or "",
        "scientificName": data.get("scientificName", ""),
        "canonicalName": data.get("canonicalName", ""),
        "rank": data.get("rank", ""),
        "status": data.get("status", ""),
        "matchType": data.get("matchType", ""),
        "confidence": data.get("confidence", ""),
        "note": data.get("note", ""),
    }


def fetch_occurrences(taxon_key: int, country: str, cap: int) -> tuple[list[dict], int]:
    page = 300
    offset = 0
    rows: list[dict] = []
    total = None
    while len(rows) < cap:
        params = {
            "taxonKey": taxon_key,
            "country": country,
            "hasCoordinate": "true",
            "hasGeospatialIssue": "false",
            "occurrenceStatus": "PRESENT",
            "limit": min(page, cap - len(rows)),
            "offset": offset,
        }
        data = get_json(f"{GBIF}/occurrence/search", params)
        if total is None:
            total = int(data.get("count", 0))
        batch = data.get("results", [])
        rows.extend(batch)
        if data.get("endOfRecords") or not batch:
            break
        offset += len(batch)
        if offset >= min(cap, 100000):
            break
        time.sleep(0.12)
    return rows, int(total or 0)


def record_text(r: dict) -> str:
    fields = [
        "occurrenceRemarks", "habitat", "locality", "verbatimLocality",
        "eventRemarks", "fieldNotes", "identificationRemarks",
    ]
    return " | ".join(str(r.get(k, "") or "") for k in fields)


def keep_occurrence(r: dict) -> tuple[bool, str]:
    basis = str(r.get("basisOfRecord", "") or "").upper()
    if basis and basis not in ALLOWED_BASIS:
        return False, f"basis:{basis}"
    lat, lon = r.get("decimalLatitude"), r.get("decimalLongitude")
    if lat is None or lon is None:
        return False, "missing_coordinate"
    try:
        lat = float(lat); lon = float(lon)
    except Exception:
        return False, "invalid_coordinate"
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return False, "invalid_coordinate"
    uncertainty = r.get("coordinateUncertaintyInMeters")
    if uncertainty not in (None, ""):
        try:
            if float(uncertainty) > 20000:
                return False, "coordinate_uncertainty_gt_20km"
        except Exception:
            pass
    est = str(r.get("establishmentMeans", "") or "").upper().replace(" ", "_")
    deg = str(r.get("degreeOfEstablishment", "") or "").upper().replace(" ", "_")
    if est in NON_NATIVE or deg in NON_NATIVE:
        return False, "explicit_non_native"
    if CULTIVATION_RE.search(record_text(r)):
        return False, "cultivation_text"
    return True, "keep"


def thin_records(records: list[dict], cell_deg: float = 0.1) -> list[dict]:
    # Deterministic one-record-per-cell choice: prefer specimens/material samples,
    # then lower coordinate uncertainty, then GBIF key.
    rank = {
        "PRESERVED_SPECIMEN": 0,
        "MATERIAL_SAMPLE": 1,
        "MATERIAL_CITATION": 2,
        "HUMAN_OBSERVATION": 3,
        "OBSERVATION": 4,
        "OCCURRENCE": 5,
    }
    def score(r: dict):
        basis = str(r.get("basisOfRecord", "") or "").upper()
        try:
            unc = float(r.get("coordinateUncertaintyInMeters") or 1e20)
        except Exception:
            unc = 1e20
        return (rank.get(basis, 99), unc, str(r.get("key", "")))

    by_cell: dict[tuple[int, int], dict] = {}
    for r in records:
        lat = float(r["decimalLatitude"]); lon = float(r["decimalLongitude"])
        cell = (math.floor((lat + 90) / cell_deg), math.floor((lon + 180) / cell_deg))
        cur = by_cell.get(cell)
        if cur is None or score(r) < score(cur):
            by_cell[cell] = r
    return list(by_cell.values())


def download_worldclim(out_dir: pathlib.Path) -> dict[int, pathlib.Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    zpath = out_dir / "wc2.1_10m_bio.zip"
    if not zpath.exists():
        with requests.get(WORLDCLIM_BIO_10M, timeout=180, headers={"User-Agent": USER_AGENT}, stream=True) as r:
            r.raise_for_status()
            with zpath.open("wb") as f:
                shutil.copyfileobj(r.raw, f)
    with zipfile.ZipFile(zpath) as z:
        existing = {p.name for p in out_dir.glob("*.tif")}
        for name in z.namelist():
            if name.endswith(".tif") and pathlib.Path(name).name not in existing:
                z.extract(name, out_dir)
    paths = {}
    for b in BIO_VARS:
        matches = list(out_dir.rglob(f"wc2.1_10m_bio_{b}.tif"))
        if len(matches) != 1:
            raise RuntimeError(f"WorldClim BIO{b}: expected one raster, found {matches}")
        paths[b] = matches[0]
    return paths


def sample_climate(points: list[dict], rasters: dict[int, pathlib.Path]) -> list[dict]:
    coords = [(float(r["decimalLongitude"]), float(r["decimalLatitude"])) for r in points]
    values: dict[int, list[float | None]] = {}
    for b, path in rasters.items():
        with rasterio.open(path) as src:
            arr = []
            for val in src.sample(coords, indexes=1, masked=True):
                x = val[0]
                if np.ma.is_masked(x):
                    arr.append(None)
                else:
                    arr.append(float(x))
            values[b] = arr
    out = []
    for i, r in enumerate(points):
        row = {
            "gbif_key": r.get("key", ""),
            "decimalLatitude": r.get("decimalLatitude", ""),
            "decimalLongitude": r.get("decimalLongitude", ""),
            "basisOfRecord": r.get("basisOfRecord", ""),
            "year": r.get("year", ""),
            "countryCode": r.get("countryCode", ""),
        }
        for b in BIO_VARS:
            row[f"bio{b}"] = values[b][i]
        out.append(row)
    return out


def temperature_scale(rows: list[dict]) -> float:
    vals = [abs(float(r["bio1"])) for r in rows if r.get("bio1") not in (None, "")]
    if not vals:
        return 1.0
    # WorldClim distributions are normally in degrees C; guard against an
    # archive/version using tenths of degrees without hard-coding it silently.
    med = float(np.nanmedian(vals))
    return 0.1 if med > 80 else 1.0


def q(v: Iterable[float], p: float) -> float:
    a = np.asarray(list(v), dtype=float)
    return float(np.nanquantile(a, p))


def summarize_species(taxon: str, colour: str, pigment: str, rows: list[dict], scale: float) -> dict[str, object]:
    usable = [r for r in rows if all(r.get(f"bio{b}") not in (None, "") for b in BIO_VARS)]
    out: dict[str, object] = {
        "taxon": taxon,
        "colour_state": colour,
        "pigment_proxy": pigment,
        "n_climate_points": len(usable),
        "temperature_scale_applied": scale,
    }
    for b in BIO_VARS:
        vals = [float(r[f"bio{b}"]) for r in usable]
        if b in (1, 6):
            vals = [x * scale for x in vals]
        if vals:
            out[f"bio{b}_mean"] = float(np.mean(vals))
            out[f"bio{b}_median"] = float(np.median(vals))
            out[f"bio{b}_q05"] = q(vals, 0.05)
            out[f"bio{b}_q95"] = q(vals, 0.95)
            out[f"bio{b}_iqr"] = q(vals, 0.75) - q(vals, 0.25)
        else:
            for suffix in ("mean", "median", "q05", "q95", "iqr"):
                out[f"bio{b}_{suffix}"] = ""
    return out


def exact_label_permutation(a: list[float], y: list[float]) -> dict[str, object]:
    vals = np.asarray(a + y, dtype=float)
    na = len(a)
    obs = float(np.mean(a) - np.mean(y))
    ncomb = math.comb(len(vals), na)
    if ncomb > 200000:
        raise RuntimeError("exact permutation space unexpectedly large")
    diffs = []
    inds = range(len(vals))
    for idx in itertools.combinations(inds, na):
        mask = np.zeros(len(vals), dtype=bool)
        mask[list(idx)] = True
        diffs.append(float(np.mean(vals[mask]) - np.mean(vals[~mask])))
    diffs = np.asarray(diffs)
    p2 = float(np.mean(np.abs(diffs) >= abs(obs) - 1e-12))
    p_colder = float(np.mean(diffs <= obs + 1e-12))  # one-sided A more negative/colder
    return {
        "difference_A_minus_Y": obs,
        "exact_two_sided_p": p2,
        "exact_one_sided_p_A_colder": p_colder,
        "n_permutations": int(ncomb),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--taxa", required=True, type=pathlib.Path)
    ap.add_argument("--out-dir", required=True, type=pathlib.Path)
    ap.add_argument("--worldclim-dir", required=True, type=pathlib.Path)
    ap.add_argument("--gbif-cap-per-country", type=int, default=3000)
    ap.add_argument("--min-points", type=int, default=5)
    args = ap.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    taxa = read_csv(args.taxa)
    rasters = download_worldclim(args.worldclim_dir)

    match_rows = []
    audit_rows = []
    all_point_rows = []
    species_rows = []

    for seed in taxa:
        taxon = seed["taxon"].strip()
        match = gbif_match(taxon)
        match_rows.append({**seed, **match})
        if not match["usageKey"]:
            audit_rows.append({"taxon": taxon, "status": "no_gbif_match"})
            continue
        key = int(match["usageKey"])
        raw = []
        gbif_total = 0
        for country in [x.strip() for x in seed["native_country_codes"].split(";") if x.strip()]:
            rr, total = fetch_occurrences(key, country, args.gbif_cap_per_country)
            raw.extend(rr); gbif_total += total
        # Deduplicate GBIF records across country calls.
        uniq = {str(r.get("key", i)): r for i, r in enumerate(raw)}
        raw = list(uniq.values())
        reasons = Counter()
        clean = []
        for r in raw:
            keep, reason = keep_occurrence(r)
            reasons[reason] += 1
            if keep:
                clean.append(r)
        thinned = thin_records(clean)
        climate = sample_climate(thinned, rasters) if thinned else []
        scale = temperature_scale(climate)
        for r in climate:
            r.update({
                "taxon": taxon,
                "colour_state": seed["colour_state"],
                "pigment_proxy": seed["pigment_proxy"],
            })
            if r.get("bio1") not in (None, ""):
                r["bio1"] = float(r["bio1"]) * scale
            if r.get("bio6") not in (None, ""):
                r["bio6"] = float(r["bio6"]) * scale
            all_point_rows.append(r)
        audit_rows.append({
            "taxon": taxon,
            "gbif_taxon_key": key,
            "gbif_total_native_country_query": gbif_total,
            "n_fetched_capped": len(raw),
            "n_clean": len(clean),
            "n_thinned": len(thinned),
            "filter_reasons_json": json.dumps(dict(reasons), sort_keys=True),
            "status": "admit" if len(climate) >= args.min_points else "insufficient_points",
        })
        if len(climate) >= args.min_points:
            species_rows.append(summarize_species(
                taxon, seed["colour_state"], seed["pigment_proxy"], all_point_rows[-len(climate):], 1.0
            ))
        print(f"{taxon}: GBIF total={gbif_total}, fetched={len(raw)}, clean={len(clean)}, thinned={len(thinned)}")
        time.sleep(0.15)

    write_csv(args.out_dir / "gbif_taxon_matches.csv", match_rows)
    write_csv(args.out_dir / "occurrence_filter_audit.csv", audit_rows)
    write_csv(args.out_dir / "thinned_occurrence_climate.csv", all_point_rows)
    write_csv(args.out_dir / "species_climatic_niches.csv", species_rows)

    # Species-level A versus Y test. W remains descriptive unless >=2 taxa.
    admitted = [r for r in species_rows if int(r["n_climate_points"]) >= args.min_points]
    tests = []
    for metric in ["bio1_median", "bio6_median", "bio4_median", "bio12_median", "bio15_median", "bio6_q05", "bio1_iqr"]:
        a = [float(r[metric]) for r in admitted if r["colour_state"] == "A" and r.get(metric) not in (None, "")]
        y = [float(r[metric]) for r in admitted if r["colour_state"] == "Y" and r.get(metric) not in (None, "")]
        if len(a) >= 2 and len(y) >= 2:
            res = exact_label_permutation(a, y)
            tests.append({
                "metric": metric,
                "n_A_species": len(a),
                "n_Y_species": len(y),
                "A_mean_species_value": float(np.mean(a)),
                "Y_mean_species_value": float(np.mean(y)),
                **res,
                "scope": "raw species-level exact label permutation; not phylogenetically corrected",
            })
    write_csv(args.out_dir / "colour_niche_group_tests.csv", tests)

    # Explicit close-pair result for C. japonica vs C. rusticana.
    by_taxon = {r["taxon"]: r for r in species_rows}
    pair = []
    if "Camellia japonica" in by_taxon and "Camellia rusticana" in by_taxon:
        j = by_taxon["Camellia japonica"]; ru = by_taxon["Camellia rusticana"]
        for metric in ["bio1_median", "bio6_median", "bio4_median", "bio12_median", "bio15_median", "bio6_q05"]:
            pair.append({
                "metric": metric,
                "japonica": j[metric],
                "rusticana": ru[metric],
                "rusticana_minus_japonica": float(ru[metric]) - float(j[metric]),
                "interpretation": "negative temperature difference means rusticana colder despite both being red/A-state",
            })
    write_csv(args.out_dir / "japonica_rusticana_climate_pair.csv", pair)

    summary = {
        "n_taxa_seeded": len(taxa),
        "n_species_admitted": len(species_rows),
        "admitted_by_colour": dict(Counter(r["colour_state"] for r in species_rows)),
        "min_points": args.min_points,
        "worldclim": "WorldClim 2.1 10m BIO1/BIO4/BIO6/BIO12/BIO15",
        "gbif_filter": "native-country constrained; PRESENT; coordinates; no geospatial issue; cultivated/non-native/living-specimen/high-uncertainty filtering; 0.1-degree thinning",
        "claim_ceiling": "preliminary species-level colour-niche association and close-pair climate contrast; not causal or phylogenetically corrected",
    }
    (args.out_dir / "analysis_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
