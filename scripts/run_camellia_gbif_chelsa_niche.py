#!/usr/bin/env python3
"""Independent Camellia macro-niche screen using GBIF + CHELSA v2.1 COGs.

This is a climate-provider sensitivity path for M8. It deliberately reuses the
same GBIF cleaning/thinning functions and species-level tests as the WorldClim
workflow, but samples official CHELSA v2.1 cloud-optimized GeoTIFFs by HTTP range
requests rather than downloading a global archive.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import pathlib
import time
from collections import Counter

import numpy as np
import rasterio

from run_camellia_gbif_worldclim_niche import (
    exact_label_permutation,
    fetch_occurrences,
    gbif_match,
    keep_occurrence,
    read_csv,
    thin_records,
    write_csv,
)

BIO_VARS = [1, 4, 6, 12, 15]
BASE = "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio"
URLS = {b: f"{BASE}/CHELSA_bio{b}_1981-2010_V.2.1.tif" for b in BIO_VARS}


def decode_value(bio: int, raw: float, scale: float, offset: float) -> float:
    """Decode CHELSA raster storage conservatively.

    Prefer GeoTIFF scale/offset metadata. Historical CHELSA BIO temperature COGs
    are also known to be stored as K*10 in some readers; when metadata is absent,
    a physically impossible raw temperature (>100) triggers 0.1*x - 273.15.
    Non-temperature variables are returned after any metadata scale/offset.
    """
    val = raw * scale + offset
    if bio in (1, 6) and scale == 1.0 and offset == 0.0 and val > 100:
        val = raw * 0.1 - 273.15
    return float(val)


def sample_chelsa(points: list[dict]) -> tuple[list[dict], dict[str, object]]:
    coords = [(float(r["decimalLongitude"]), float(r["decimalLatitude"])) for r in points]
    values: dict[int, list[float | None]] = {}
    metadata: dict[str, object] = {}
    env_opts = {
        "GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR",
        "CPL_VSIL_CURL_ALLOWED_EXTENSIONS": ".tif",
        "GDAL_HTTP_MULTIRANGE": "YES",
        "GDAL_HTTP_MERGE_CONSECUTIVE_RANGES": "YES",
        "CPL_VSIL_CURL_CACHE_SIZE": "20000000",
    }
    with rasterio.Env(**env_opts):
        for b, url in URLS.items():
            with rasterio.open(url) as src:
                scale = float(src.scales[0] if src.scales else 1.0)
                offset = float(src.offsets[0] if src.offsets else 0.0)
                metadata[f"bio{b}"] = {
                    "url": url,
                    "scale": scale,
                    "offset": offset,
                    "dtype": str(src.dtypes[0]),
                    "crs": str(src.crs),
                    "nodata": src.nodata,
                }
                arr: list[float | None] = []
                for v in src.sample(coords, indexes=1, masked=True):
                    x = v[0]
                    if np.ma.is_masked(x):
                        arr.append(None)
                    else:
                        arr.append(decode_value(b, float(x), scale, offset))
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
    return out, metadata


def quant(vals: list[float], p: float) -> float:
    return float(np.nanquantile(np.asarray(vals, dtype=float), p))


def summarize_species(seed: dict[str, str], rows: list[dict]) -> dict[str, object]:
    usable = [r for r in rows if all(r.get(f"bio{b}") not in (None, "") for b in BIO_VARS)]
    out: dict[str, object] = {
        "taxon": seed["taxon"],
        "colour_state": seed["colour_state"],
        "pigment_proxy": seed["pigment_proxy"],
        "analysis_role": seed["analysis_role"],
        "n_climate_points": len(usable),
    }
    for b in BIO_VARS:
        vals = [float(r[f"bio{b}"]) for r in usable]
        if vals:
            out[f"bio{b}_mean"] = float(np.mean(vals))
            out[f"bio{b}_median"] = float(np.median(vals))
            out[f"bio{b}_q05"] = quant(vals, 0.05)
            out[f"bio{b}_q95"] = quant(vals, 0.95)
            out[f"bio{b}_iqr"] = quant(vals, 0.75) - quant(vals, 0.25)
        else:
            for suffix in ("mean", "median", "q05", "q95", "iqr"):
                out[f"bio{b}_{suffix}"] = ""
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--taxa", required=True, type=pathlib.Path)
    ap.add_argument("--out-dir", required=True, type=pathlib.Path)
    ap.add_argument("--gbif-cap-per-country", type=int, default=3000)
    ap.add_argument("--min-points", type=int, default=5)
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    taxa = read_csv(args.taxa)
    matches = []
    audits = []
    point_rows = []
    species_rows = []
    climate_meta: dict[str, object] = {}

    for seed in taxa:
        taxon = seed["taxon"].strip()
        match = gbif_match(taxon)
        matches.append({**seed, **match})
        if not match["usageKey"]:
            audits.append({"taxon": taxon, "status": "no_gbif_match"})
            continue
        key = int(match["usageKey"])
        raw = []
        gbif_total = 0
        for country in [x.strip() for x in seed["native_country_codes"].split(";") if x.strip()]:
            rr, total = fetch_occurrences(key, country, args.gbif_cap_per_country)
            raw.extend(rr); gbif_total += total
        raw = list({str(r.get("key", i)): r for i, r in enumerate(raw)}.values())
        reasons = Counter()
        clean = []
        for r in raw:
            keep, reason = keep_occurrence(r)
            reasons[reason] += 1
            if keep:
                clean.append(r)
        thinned = thin_records(clean)
        if thinned:
            climate, meta = sample_chelsa(thinned)
            climate_meta.update(meta)
        else:
            climate = []
        for r in climate:
            r.update({
                "taxon": taxon,
                "colour_state": seed["colour_state"],
                "pigment_proxy": seed["pigment_proxy"],
            })
            point_rows.append(r)
        audits.append({
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
            species_rows.append(summarize_species(seed, climate))
        print(f"{taxon}: total={gbif_total} fetched={len(raw)} clean={len(clean)} thin={len(thinned)}", flush=True)
        time.sleep(0.12)

    write_csv(args.out_dir / "gbif_taxon_matches.csv", matches)
    write_csv(args.out_dir / "occurrence_filter_audit.csv", audits)
    write_csv(args.out_dir / "thinned_occurrence_chelsa.csv", point_rows)
    write_csv(args.out_dir / "species_climatic_niches.csv", species_rows)
    (args.out_dir / "chelsa_raster_metadata.json").write_text(json.dumps(climate_meta, indent=2) + "\n", encoding="utf-8")

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
                "scope": "species-level exact label permutation; native-country filtered; not phylogenetically corrected",
            })
    write_csv(args.out_dir / "colour_niche_group_tests.csv", tests)

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
                "interpretation": "negative temperature difference means rusticana occupies colder climate despite both species being red/A-state",
            })
    write_csv(args.out_dir / "japonica_rusticana_climate_pair.csv", pair)

    summary = {
        "climate_provider": "CHELSA v2.1 1981-2010 BIO COG",
        "n_taxa_seeded": len(taxa),
        "n_species_admitted": len(species_rows),
        "admitted_by_colour": dict(Counter(r["colour_state"] for r in species_rows)),
        "min_points": args.min_points,
        "claim_ceiling": "direct Camellia species-level colour-niche screen; not phylogenetically corrected or causal",
    }
    (args.out_dir / "analysis_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2), flush=True)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
