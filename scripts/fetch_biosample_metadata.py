#!/usr/bin/env python3
"""Fetch BioSample metadata for SRA RunInfo manifests.

The SRA RunInfo table is intentionally not treated as the complete biological
sample record. This script resolves each BioSample accession through NCBI
E-utilities and stores both a compact sample table and a long attribute table.
It is used to recover provenance such as tissue, developmental stage, voucher,
collection locality, and submitter-provided labels when those fields exist.

No sequence data are downloaded.
"""

from __future__ import annotations

import argparse
import csv
import json
import pathlib
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
USER_AGENT = "chun-flower-colour/0.1 (BioSample provenance audit)"


def request_text(endpoint: str, params: dict[str, str], retries: int = 4) -> str:
    url = f"{EUTILS}/{endpoint}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    last: Exception | None = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                return response.read().decode("utf-8")
        except Exception as exc:  # pragma: no cover - network-dependent
            last = exc
            if attempt + 1 < retries:
                time.sleep(2**attempt)
    raise RuntimeError(f"NCBI request failed after {retries} attempts: {url}") from last


def read_csv(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: pathlib.Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def esearch_biosample(accession: str) -> str:
    payload = request_text(
        "esearch.fcgi",
        {"db": "biosample", "term": accession, "retmode": "json", "retmax": "5"},
    )
    ids = json.loads(payload).get("esearchresult", {}).get("idlist", [])
    if len(ids) != 1:
        raise RuntimeError(f"{accession}: expected one BioSample UID, found {ids}")
    return ids[0]


def efetch_biosample(uid: str) -> ET.Element:
    payload = request_text(
        "efetch.fcgi", {"db": "biosample", "id": uid, "retmode": "xml"}
    )
    return ET.fromstring(payload)


def text_or_empty(node: ET.Element | None) -> str:
    if node is None or node.text is None:
        return ""
    return node.text.strip()


def parse_record(
    root: ET.Element,
    *,
    seed_id: str,
    biosample_accession: str,
    runs: list[str],
) -> tuple[dict[str, str], list[dict[str, str]]]:
    sample = root.find(".//BioSample")
    if sample is None:
        raise RuntimeError(f"{biosample_accession}: BioSample XML lacks BioSample element")

    ids: dict[str, str] = {}
    for node in sample.findall("./Ids/Id"):
        key = node.attrib.get("db", node.attrib.get("db_label", "id"))
        ids[key] = text_or_empty(node)

    organism = sample.find("./Description/Organism")
    title = sample.find("./Description/Title")
    sample_name = ""
    for node in sample.findall("./Ids/Id"):
        if node.attrib.get("db_label") == "Sample name":
            sample_name = text_or_empty(node)
            break

    compact = {
        "seed_id": seed_id,
        "biosample": biosample_accession,
        "runs": ";".join(sorted(runs)),
        "sample_name": sample_name,
        "title": text_or_empty(title),
        "organism_name": organism.attrib.get("taxonomy_name", "") if organism is not None else "",
        "tax_id": organism.attrib.get("taxonomy_id", "") if organism is not None else "",
        "publication_date": sample.attrib.get("publication_date", ""),
        "last_update": sample.attrib.get("last_update", ""),
        "access": sample.attrib.get("access", ""),
        "all_ids_json": json.dumps(ids, sort_keys=True, ensure_ascii=False),
    }

    attributes: list[dict[str, str]] = []
    for attr in sample.findall("./Attributes/Attribute"):
        attributes.append(
            {
                "seed_id": seed_id,
                "biosample": biosample_accession,
                "runs": ";".join(sorted(runs)),
                "sample_name": sample_name,
                "attribute_name": attr.attrib.get("attribute_name", ""),
                "harmonized_name": attr.attrib.get("harmonized_name", ""),
                "display_name": attr.attrib.get("display_name", ""),
                "value": text_or_empty(attr),
            }
        )
    return compact, attributes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest-dir", required=True, type=pathlib.Path)
    parser.add_argument("--out-dir", required=True, type=pathlib.Path)
    args = parser.parse_args()

    by_sample: dict[tuple[str, str], set[str]] = {}
    for manifest in sorted(args.manifest_dir.glob("SEQ*_runinfo.csv")):
        rows = read_csv(manifest)
        for row in rows:
            seed_id = row.get("seed_id", "").strip()
            biosample = row.get("BioSample", "").strip()
            run = row.get("Run", "").strip()
            if not seed_id or not biosample:
                continue
            by_sample.setdefault((seed_id, biosample), set()).add(run)

    if not by_sample:
        raise SystemExit("No BioSample accessions found in RunInfo manifests")

    compact_rows: list[dict[str, str]] = []
    attr_rows: list[dict[str, str]] = []
    for index, ((seed_id, biosample), runs) in enumerate(sorted(by_sample.items())):
        uid = esearch_biosample(biosample)
        root = efetch_biosample(uid)
        compact, attrs = parse_record(
            root,
            seed_id=seed_id,
            biosample_accession=biosample,
            runs=sorted(runs),
        )
        compact_rows.append(compact)
        attr_rows.extend(attrs)
        print(f"{seed_id}: {biosample} -> {len(attrs)} BioSample attributes")
        if index + 1 < len(by_sample):
            time.sleep(0.4)

    write_csv(
        args.out_dir / "biosample_records.csv",
        compact_rows,
        [
            "seed_id",
            "biosample",
            "runs",
            "sample_name",
            "title",
            "organism_name",
            "tax_id",
            "publication_date",
            "last_update",
            "access",
            "all_ids_json",
        ],
    )
    write_csv(
        args.out_dir / "biosample_attributes_long.csv",
        attr_rows,
        [
            "seed_id",
            "biosample",
            "runs",
            "sample_name",
            "attribute_name",
            "harmonized_name",
            "display_name",
            "value",
        ],
    )
    print(
        f"Resolved {len(compact_rows)} BioSamples and {len(attr_rows)} attributes."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
