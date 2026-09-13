#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import urllib.request
from pathlib import Path

import pandas as pd

TRAIT_URL = "https://pmc-oa-opendata.s3.amazonaws.com/PMC7588356.1/Table_1.xlsx"
ACCESSION_URL = "https://pmc-oa-opendata.s3.amazonaws.com/PMC7588356.1/Data_Sheet_1.csv"
TRAIT_SHA256 = "183ef5231c48e782b0ea69a7aa5605d40c892dd91d9d9b2d259ed7b65d230072"
ACCESSION_SHA256 = "942d684256eb4527d02b274d9da374c8cc5585a190ef20a9058c231460a4ad71"
UA = "chun-iris-source-crosswalk-validator/0.1"


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def clean(x: object) -> str:
    if pd.isna(x):
        return ""
    return re.sub(r"\s+", " ", str(x)).strip()


def accession_rows(data: bytes) -> list[str]:
    rows = list(csv.reader(io.StringIO(data.decode("utf-8-sig")), delimiter=";"))
    assert rows[1] == ["organism", "matK", "trnL", "ndhF", "trnK", "rbcL", "ITS"]
    return [clean(r[0]) for r in rows[2:] if r and clean(r[0])]


def binomial_key(raw: str) -> str:
    """Source-only join key; infraspecific ranks collapse to the source binomial unless explicitly overridden."""
    s = clean(raw).lower().replace("×", "x").replace("_", " ")
    s = re.sub(r"\b(subsp|subs|ssp|var|cf)\.?\b", " ", s)
    s = re.sub(r"\b(l|mill|auct)\.?\b", " ", s)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    toks = s.split()
    if not toks:
        return ""
    if toks[0].startswith("irisx") and len(toks[0]) > 5:
        return "iris " + toks[0][5:]
    if toks[0] == "iris" and len(toks) > 1:
        if toks[1] == "x" and len(toks) > 2:
            return "iris " + toks[2]
        return "iris " + toks[1]
    return " ".join(toks[:2])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--crosswalk", type=Path, default=Path("data/iris_source_taxon_crosswalk_v0_1.csv"))
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    trait_b = fetch(TRAIT_URL)
    acc_b = fetch(ACCESSION_URL)
    assert hashlib.sha256(trait_b).hexdigest() == TRAIT_SHA256
    assert hashlib.sha256(acc_b).hexdigest() == ACCESSION_SHA256

    traits = pd.read_excel(io.BytesIO(trait_b), sheet_name="Source of data", engine="openpyxl")
    # Deliberately consume Species only. Colour/Pigment/Bic are not read here.
    trait_labels = [clean(x) for x in traits["Species"] if clean(x)]
    acc_labels = accession_rows(acc_b)

    with args.crosswalk.open(newline="", encoding="utf-8-sig") as f:
        cw_rows = list(csv.DictReader(f))
    assert len(cw_rows) == 5
    assert all(r["status"] == "ADMITTED" for r in cw_rows)
    explicit = {r["trait_source_label"]: r["accession_source_label"] for r in cw_rows}
    assert len(explicit) == 5
    assert set(explicit).issubset(set(trait_labels))
    assert set(explicit.values()).issubset(set(acc_labels))

    # Remove explicitly claimed accession rows before generic binomial matching. This is
    # necessary for Iris spuria subsp. sogdiana -> Iris_sogdiana, while the other
    # Iris spuria trait row must remain available for Iris_spuria subsp. spuria.
    reserved_accessions = set(explicit.values())
    acc_by_key: dict[str, list[str]] = {}
    for a in acc_labels:
        if a in reserved_accessions:
            continue
        acc_by_key.setdefault(binomial_key(a), []).append(a)

    mapped: dict[str, str] = {}
    ambiguous: dict[str, list[str]] = {}
    missing: list[str] = []
    for t in trait_labels:
        if t in explicit:
            mapped[t] = explicit[t]
            continue
        candidates = acc_by_key.get(binomial_key(t), [])
        if len(candidates) == 1:
            mapped[t] = candidates[0]
        elif len(candidates) > 1:
            ambiguous[t] = candidates
        else:
            missing.append(t)

    mapped_accessions = list(mapped.values())
    duplicates = sorted({a for a in mapped_accessions if mapped_accessions.count(a) > 1})
    unmatched_accessions = sorted(set(acc_labels) - set(mapped_accessions))

    if missing or ambiguous or duplicates:
        raise SystemExit(
            f"crosswalk not one-to-one: missing={missing}, ambiguous={ambiguous}, duplicate_accessions={duplicates}"
        )
    if len(mapped) != 226 or len(set(mapped_accessions)) != 226:
        raise SystemExit(f"expected 226 one-to-one mapped trait rows; got {len(mapped)} / {len(set(mapped_accessions))}")
    expected_unmatched = ["Iris_cedretii", "Iris_darwasica"]
    if unmatched_accessions != expected_unmatched:
        raise SystemExit(f"unexpected accession-only rows after crosswalk: {unmatched_accessions}")

    out = {
        "version": "v0.1",
        "status": "IRIS_SOURCE_TAXON_CROSSWALK_VALID",
        "trait_rows": len(trait_labels),
        "accession_rows": len(acc_labels),
        "explicit_crosswalk_rows": len(cw_rows),
        "mapped_trait_rows": len(mapped),
        "mapped_distinct_accession_rows": len(set(mapped_accessions)),
        "unmatched_accession_rows": unmatched_accessions,
        "iris_darwasica_role": "SOURCE_SPECIFIC_EXCLUSION_NO_TRAIT_ROW",
        "iris_cedretii_role": "TREE_ONLY_NO_TRAIT_ROW",
        "generic_join_rule": "BINOMIAL_KEY_AFTER_EXPLICIT_SOURCE_LABEL_OVERRIDES",
        "trait_columns_read": ["Species"],
        "trait_values_inspected": False,
        "auc_computed": False,
        "decision_computed": False,
        "paper1_science_changed": False,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
