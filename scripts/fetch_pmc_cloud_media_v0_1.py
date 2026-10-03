#!/usr/bin/env python3
"""Retrieve PMC article media from the current PMC Cloud Service.

The legacy PMC OA Web Service and FTP package route were retired in August 2026.
This module resolves article versions from the public pmc-oa-opendata S3 bucket,
selects the published/open-access version when available, downloads media objects,
and verifies the MD5 digest embedded in each metadata URL.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

S3_HTTPS = "https://pmc-oa-opendata.s3.amazonaws.com"
USER_AGENT = "chun-pmc-cloud/0.1 (public-data reproducibility audit)"
PMCID_RE = re.compile(r"^PMC\d+$")


def get_bytes(url: str, timeout: int = 120) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def s3_to_https(url: str) -> tuple[str, str | None]:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "s3" or parsed.netloc != "pmc-oa-opendata":
        raise ValueError(f"unexpected PMC media URL: {url}")
    query = urllib.parse.parse_qs(parsed.query)
    md5 = query.get("md5", [None])[0]
    quoted = urllib.parse.quote(parsed.path.lstrip("/"), safe="/._-")
    return f"{S3_HTTPS}/{quoted}", md5


def list_versions(pmcid: str) -> list[str]:
    if not PMCID_RE.fullmatch(pmcid):
        raise ValueError(f"invalid PMCID: {pmcid}")
    query = urllib.parse.urlencode({
        "list-type": "2",
        "prefix": f"{pmcid}.",
        "delimiter": "/",
    })
    root = ET.fromstring(get_bytes(f"{S3_HTTPS}/?{query}"))
    ns = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}
    prefixes = [
        x.text.rstrip("/")
        for x in root.findall(".//s3:CommonPrefixes/s3:Prefix", ns)
        if x.text
    ]
    def version_key(prefix: str) -> int:
        try:
            return int(prefix.rsplit(".", 1)[1])
        except Exception:
            return -1
    return sorted(set(prefixes), key=version_key)


def fetch_metadata(prefix: str) -> dict:
    url = f"{S3_HTTPS}/metadata/{prefix}.json"
    return json.loads(get_bytes(url).decode("utf-8"))


def choose_version(metadata: list[dict]) -> dict:
    if not metadata:
        raise ValueError("no PMC Cloud metadata candidates")
    eligible = [x for x in metadata if x.get("is_pmc_openaccess") or x.get("is_manuscript")]
    if not eligible:
        eligible = metadata
    published = [x for x in eligible if not x.get("is_manuscript")]
    pool = published or eligible
    return max(pool, key=lambda x: int(x.get("version", 0)))


def fetch_pmc_media(pmcid: str, out_dir: Path, *, include_core: bool = False) -> dict:
    prefixes = list_versions(pmcid)
    if not prefixes:
        raise RuntimeError(f"no PMC Cloud article version found for {pmcid}")
    candidates = [fetch_metadata(p) for p in prefixes]
    meta = choose_version(candidates)
    prefix = f"{meta['pmcid']}.{meta['version']}"
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    sources = list(meta.get("media_urls") or [])
    if include_core:
        sources.extend(
            source
            for source in (meta.get("xml_url"), meta.get("pdf_url"), meta.get("text_url"))
            if source
        )
    for source in sources:
        https_url, expected_md5 = s3_to_https(source)
        name = Path(urllib.parse.urlparse(https_url).path).name
        if not name:
            continue
        data = get_bytes(https_url)
        actual_md5 = hashlib.md5(data).hexdigest()
        if expected_md5 and actual_md5.lower() != expected_md5.lower():
            raise RuntimeError(
                f"PMC Cloud MD5 mismatch for {name}: {actual_md5} != {expected_md5}"
            )
        target = out_dir / name
        target.write_bytes(data)
        rows.append({
            "filename": name,
            "bytes": len(data),
            "md5": actual_md5,
            "source_url": https_url,
        })

    (out_dir / "pmc_cloud_metadata.json").write_text(
        json.dumps(meta, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    with (out_dir / "pmc_cloud_media_manifest.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["filename", "bytes", "md5", "source_url"])
        w.writeheader()
        w.writerows(rows)

    summary = {
        "status": "PMC_CLOUD_MEDIA_FETCHED",
        "transport": "pmc-oa-opendata",
        "pmcid": pmcid,
        "available_prefixes": prefixes,
        "selected_prefix": prefix,
        "is_manuscript": bool(meta.get("is_manuscript")),
        "is_pmc_openaccess": bool(meta.get("is_pmc_openaccess")),
        "license_code": meta.get("license_code"),
        "doi": meta.get("doi"),
        "citation": meta.get("citation"),
        "media_files": len(meta.get("media_urls") or []),
        "downloaded_files": len(rows),
        "include_core": include_core,
        "tabular_media_files": sum(Path(r["filename"]).suffix.lower() in {".xlsx", ".xls", ".csv", ".tsv"} for r in rows),
    }
    (out_dir / "pmc_cloud_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pmcid", required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--require-glob")
    ap.add_argument("--include-core", action="store_true")
    args = ap.parse_args()
    summary = fetch_pmc_media(args.pmcid, args.out_dir, include_core=args.include_core)
    if args.require_glob and not list(args.out_dir.rglob(args.require_glob)):
        raise SystemExit(f"required PMC media pattern not found: {args.require_glob}")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
