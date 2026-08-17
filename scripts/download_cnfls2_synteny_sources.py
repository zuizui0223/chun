#!/usr/bin/env python3
"""Download provenance-frozen GWH annotations for the CnFLS2 synteny test.

Transfers are written to temporary files, gzip-validated, and atomically moved
into place. Transient incomplete reads from the public GWH download host are
retried from scratch so network truncation cannot masquerade as data failure.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import time
from pathlib import Path

import requests


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_gzip(path: Path) -> None:
    with path.open("rb") as handle:
        if handle.read(2) != b"\x1f\x8b":
            raise OSError(f"Downloaded file is not gzip: {path}")
    with gzip.open(path, "rb") as handle:
        while handle.read(1024 * 1024):
            pass


def download(session: requests.Session, url: str, path: Path, *, attempts: int = 5) -> dict[str, object]:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".part")
    errors: list[str] = []
    for attempt in range(1, attempts + 1):
        temporary.unlink(missing_ok=True)
        try:
            with session.get(url, stream=True, timeout=(30, 300)) as response:
                response.raise_for_status()
                expected_length = response.headers.get("Content-Length", "")
                with temporary.open("wb") as handle:
                    for block in response.iter_content(1024 * 1024):
                        if block:
                            handle.write(block)
            if expected_length and temporary.stat().st_size != int(expected_length):
                raise OSError(
                    f"incomplete transfer: received {temporary.stat().st_size} of "
                    f"{expected_length} compressed bytes"
                )
            validate_gzip(temporary)
            temporary.replace(path)
            return {
                "url": url,
                "local_path": str(path),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        except (requests.RequestException, OSError, EOFError, gzip.BadGzipFile) as exc:
            errors.append(f"attempt {attempt}/{attempts}: {type(exc).__name__}: {exc}")
            temporary.unlink(missing_ok=True)
            if attempt < attempts:
                time.sleep(min(20, 2**attempt))
    raise RuntimeError(f"Failed to download and validate {url}: {' | '.join(errors)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    with args.sources.open(newline="", encoding="utf-8") as handle:
        sources = list(csv.DictReader(handle))
    if len(sources) != 2:
        raise SystemExit(f"Expected exactly two frozen sources, found {len(sources)}")

    session = requests.Session()
    session.headers["User-Agent"] = "chun-cnfls2-synteny-download/0.2"
    manifest: list[dict[str, object]] = []
    for source in sources:
        role = source["role"]
        for field, suffix in [("ftp_gff", "gff.gz"), ("ftp_protein", "protein.faa.gz")]:
            url = source.get(field, "")
            if not url:
                raise SystemExit(f"Missing {field} for {role}")
            record = download(session, url, args.out_dir / f"{role}.{suffix}")
            record.update(
                {
                    "role": role,
                    "assembly_accession": source["assembly_accession"],
                    "file_class": field,
                    "target_feature": source["target_feature"],
                    "source_basis": source["source_basis"],
                    "claim_boundary": "download/provenance only; no biological comparison inferred",
                }
            )
            manifest.append(record)

    fields = [
        "role",
        "assembly_accession",
        "file_class",
        "url",
        "local_path",
        "bytes",
        "sha256",
        "target_feature",
        "source_basis",
        "claim_boundary",
    ]
    with (args.out_dir / "download_manifest.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(manifest)

    summary = {
        "source_rows": len(sources),
        "downloaded_files": len(manifest),
        "total_compressed_bytes": sum(int(row["bytes"]) for row in manifest),
        "roles": [row["role"] for row in sources],
        "decision": "annotation inputs downloaded and gzip-validated",
        "claim_ceiling": "download and checksum gate only",
    }
    (args.out_dir / "download_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
