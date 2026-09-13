#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

TRAIT_URL = "https://pmc-oa-opendata.s3.amazonaws.com/PMC7588356.1/Table_1.xlsx"
ACCESSION_URL = "https://pmc-oa-opendata.s3.amazonaws.com/PMC7588356.1/Data_Sheet_1.csv"
TRAIT_SHA256 = "183ef5231c48e782b0ea69a7aa5605d40c892dd91d9d9b2d259ed7b65d230072"
ACCESSION_SHA256 = "942d684256eb4527d02b274d9da374c8cc5585a190ef20a9058c231460a4ad71"
LOCI = ["matK", "trnL", "ndhF", "trnK", "rbcL", "ITS"]
UA = "chun-iris-source-join-preflight/0.1"
EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def clean(x: object) -> str:
    if pd.isna(x):
        return ""
    return re.sub(r"\s+", " ", str(x)).strip()


def trait_binomial(raw: str) -> str:
    # Source trait rows start with Iris + epithet; authors follow. Keep the source binomial only.
    s = clean(raw).replace("×", "x")
    m = re.match(r"^(Iris)\s+([^\s]+)", s, flags=re.I)
    if not m:
        return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")
    return f"Iris_{m.group(2)}".replace("-", "_")


def accession_taxon(raw: str) -> str:
    s = clean(raw)
    parts = s.split("_")
    if len(parts) >= 2:
        return f"{parts[0]}_{parts[1]}".replace("-", "_")
    return s.replace("-", "_")


def parse_accession_table(data: bytes) -> list[dict[str, str]]:
    rows = list(csv.reader(io.StringIO(data.decode("utf-8-sig")), delimiter=";"))
    if len(rows) < 3:
        raise SystemExit("accession table unexpectedly short")
    header = [clean(x) for x in rows[1]]
    if header != ["organism", *LOCI]:
        raise SystemExit(f"accession header drifted: {header}")
    out = []
    for r in rows[2:]:
        r = r + [""] * (len(header) - len(r))
        d = dict(zip(header, [clean(x) for x in r[:len(header)]]))
        if d["organism"]:
            out.append(d)
    return out


def normalize_accession(x: str) -> str:
    x = clean(x)
    if not x or x == "-":
        return ""
    return x


def fetch_genbank_xml(accessions: list[str]) -> dict[str, dict[str, object]]:
    if not accessions:
        return {}
    params = urllib.parse.urlencode({
        "db": "nuccore",
        "id": ",".join(accessions),
        "rettype": "gb",
        "retmode": "xml",
    })
    req = urllib.request.Request(EFETCH + "?" + params, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as r:
        raw = r.read()
    root = ET.fromstring(raw)
    out: dict[str, dict[str, object]] = {}
    for gb in root.findall(".//GBSeq"):
        primary = gb.findtext("GBSeq_primary-accession") or ""
        accver = gb.findtext("GBSeq_accession-version") or primary
        length = int(gb.findtext("GBSeq_length") or 0)
        definition = gb.findtext("GBSeq_definition") or ""
        features = []
        for ft in gb.findall("./GBSeq_feature-table/GBFeature"):
            key = ft.findtext("GBFeature_key") or ""
            if key not in {"gene", "CDS", "misc_feature", "misc_RNA", "rRNA", "tRNA"}:
                continue
            quals = {}
            for q in ft.findall("./GBFeature_quals/GBQualifier"):
                name = q.findtext("GBQualifier_name") or ""
                value = q.findtext("GBQualifier_value") or ""
                if name in {"gene", "product", "note"} and value:
                    quals.setdefault(name, []).append(value)
            if quals:
                features.append({"key": key, "quals": quals})
        out[accver] = {
            "primary_accession": primary,
            "length": length,
            "definition": definition,
            "features": features[:20],
        }
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    trait_b = fetch(TRAIT_URL)
    acc_b = fetch(ACCESSION_URL)
    if sha256(trait_b) != TRAIT_SHA256:
        raise SystemExit("trait SHA drift")
    if sha256(acc_b) != ACCESSION_SHA256:
        raise SystemExit("accession SHA drift")

    traits = pd.read_excel(io.BytesIO(trait_b), sheet_name="Source of data", engine="openpyxl")
    traits.columns = [clean(c) for c in traits.columns]
    trait_names = [trait_binomial(x) for x in traits["Species"] if clean(x)]
    trait_set = set(trait_names)

    acc_rows = parse_accession_table(acc_b)
    accession_names = [accession_taxon(r["organism"]) for r in acc_rows]
    accession_set = set(accession_names)
    iris_accession_rows = [r for r in acc_rows if accession_taxon(r["organism"]).startswith("Iris_")]
    non_iris_rows = [r for r in acc_rows if not accession_taxon(r["organism"]).startswith("Iris_")]

    locus_counts = {loc: sum(bool(normalize_accession(r[loc])) for r in acc_rows) for loc in LOCI}
    iris_locus_counts = {loc: sum(bool(normalize_accession(r[loc])) for r in iris_accession_rows) for loc in LOCI}

    assignment: dict[str, list[dict[str, str]]] = defaultdict(list)
    for r in acc_rows:
        tax = accession_taxon(r["organism"])
        for loc in LOCI:
            acc = normalize_accession(r[loc])
            if acc:
                assignment[acc].append({"taxon": tax, "locus": loc})
    cross_locus = {
        acc: vals for acc, vals in assignment.items()
        if len({v["locus"] for v in vals}) > 1
    }
    within_taxon_cross_locus = {
        acc: vals for acc, vals in cross_locus.items()
        if len({v["taxon"] for v in vals}) == 1
    }

    # Probe a deterministic bounded set of duplicated accessions. This diagnoses whether
    # the same source record genuinely spans multiple named loci; it does not use traits.
    probe_accs = sorted(within_taxon_cross_locus)[:12]
    gb = fetch_genbank_xml(probe_accs)

    out = {
        "version": "v0.1",
        "status": "IRIS_SOURCE_JOIN_AND_SEQUENCE_PREFLIGHT_ONLY",
        "source_sha256": {"traits": TRAIT_SHA256, "accessions": ACCESSION_SHA256},
        "trait_rows": len(trait_names),
        "trait_unique_binomials": len(trait_set),
        "accession_organism_rows": len(acc_rows),
        "accession_unique_binomials": len(accession_set),
        "iris_accession_rows": len(iris_accession_rows),
        "non_iris_accession_rows": [r["organism"] for r in non_iris_rows],
        "iris_darwasica_in_traits": "Iris_darwasica" in trait_set,
        "iris_darwasica_in_accessions": "Iris_darwasica" in accession_set,
        "trait_accession_join_count": len(trait_set & accession_set),
        "trait_only_binomials": sorted(trait_set - accession_set),
        "accession_only_binomials": sorted(accession_set - trait_set),
        "locus_availability_all_rows": locus_counts,
        "locus_availability_iris_rows": iris_locus_counts,
        "unique_accessions": len(assignment),
        "cross_locus_duplicate_accessions": len(cross_locus),
        "within_taxon_cross_locus_duplicate_accessions": len(within_taxon_cross_locus),
        "cross_locus_examples": [
            {"accession": acc, "assignments": within_taxon_cross_locus[acc]}
            for acc in sorted(within_taxon_cross_locus)[:20]
        ],
        "duplicate_record_probe": gb,
        "auc_computed": False,
        "trait_state_used_for_tree": False,
        "decision_computed": False,
        "paper1_science_changed": False,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
