#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import urllib.request
from collections import Counter
from pathlib import Path

import pandas as pd

TRAIT_URL = "https://pmc-oa-opendata.s3.amazonaws.com/PMC7588356.1/Table_1.xlsx"
ACCESSION_URL = "https://pmc-oa-opendata.s3.amazonaws.com/PMC7588356.1/Data_Sheet_1.csv"
TRAIT_SHA256 = "183ef5231c48e782b0ea69a7aa5605d40c892dd91d9d9b2d259ed7b65d230072"
ACCESSION_SHA256 = "942d684256eb4527d02b274d9da374c8cc5585a190ef20a9058c231460a4ad71"
UA = "chun-iris-postfreeze-ingest/0.1"


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def clean(x: object) -> str:
    if pd.isna(x):
        return ""
    return re.sub(r"\s+", " ", str(x)).strip()


def value_counts(s: pd.Series) -> dict[str, int]:
    c = Counter(clean(x) for x in s)
    return dict(sorted(c.items(), key=lambda kv: (-kv[1], kv[0])))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    trait_b = fetch(TRAIT_URL)
    acc_b = fetch(ACCESSION_URL)
    if sha256(trait_b) != TRAIT_SHA256:
        raise SystemExit("Iris trait source SHA drifted")
    if sha256(acc_b) != ACCESSION_SHA256:
        raise SystemExit("Iris accession source SHA drifted")

    traits = pd.read_excel(io.BytesIO(trait_b), sheet_name="Source of data", engine="openpyxl")
    traits.columns = [clean(c) for c in traits.columns]
    required = {"Species", "Colour", "Pigment", "Bic"}
    if not required.issubset(traits.columns):
        raise SystemExit(f"trait columns drifted: {traits.columns.tolist()}")

    # Post-freeze outcome ingestion: category levels and counts are now allowed to be inspected.
    trait_summary = {
        "rows": int(len(traits)),
        "nonempty_species": int(sum(bool(clean(x)) for x in traits["Species"])),
        "columns": traits.columns.tolist(),
        "colour_counts": value_counts(traits["Colour"]),
        "pigment_counts": value_counts(traits["Pigment"]),
        "bicolour_counts": value_counts(traits["Bic"]),
        "species_first_12": [clean(x) for x in traits["Species"].head(12)],
        "raw_triplets_first_12": [
            {
                "species": clean(row["Species"]),
                "colour": clean(row["Colour"]),
                "pigment": clean(row["Pigment"]),
                "bicolour": clean(row["Bic"]),
            }
            for _, row in traits.head(12).iterrows()
        ],
    }

    text = acc_b.decode("utf-8-sig", errors="strict")
    semicolon_rows = list(csv.reader(io.StringIO(text), delimiter=";"))
    comma_rows = list(csv.reader(io.StringIO(text), delimiter=","))
    width_counts_semicolon = Counter(len(r) for r in semicolon_rows)
    width_counts_comma = Counter(len(r) for r in comma_rows)
    # The source file begins with a title line; retain only structural samples here.
    accession_summary = {
        "text_first_line": text.splitlines()[0] if text.splitlines() else "",
        "semicolon_width_counts": dict(sorted(width_counts_semicolon.items())),
        "comma_width_counts": dict(sorted(width_counts_comma.items())),
        "semicolon_first_12_rows": [[clean(x) for x in r] for r in semicolon_rows[:12]],
        "line_count": len(text.splitlines()),
    }

    out = {
        "version": "v0.1",
        "status": "POST_FREEZE_ROW_LEVEL_INGESTION_DIAGNOSTIC",
        "freeze_contract": "data/intermediate_resolution_rule_prereg_v0_1.json",
        "source_sha256": {"traits": TRAIT_SHA256, "accessions": ACCESSION_SHA256},
        "traits": trait_summary,
        "accessions": accession_summary,
        "auc_computed": False,
        "decision_computed": False,
        "paper1_science_changed": False,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
