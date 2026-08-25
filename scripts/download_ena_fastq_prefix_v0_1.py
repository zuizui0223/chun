#!/usr/bin/env python3
"""Retrieve a paired FASTQ prefix for one SRA run from ENA over HTTPS.

The route is intentionally independent of any expression or colour outcome.
ENA run metadata resolves the archived paired FASTQ payloads. The primary route
streams only the preregistered prefix. If repeated gzip streaming fails because a
remote response terminates before the gzip trailer, that mate falls back to a
complete archive download, verifies ENA byte count and MD5, and extracts the same
prefix locally. Biological thresholds and requested read counts are never changed
by the transport fallback.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

ENA_API = "https://www.ebi.ac.uk/ena/portal/api/filereport"
USER_AGENT = "chun-candidate-free-rnaseq/0.1"
CHUNK_BYTES = 1024 * 1024


def fetch_bytes(url: str, attempts: int = 3, timeout: int = 60) -> bytes:
    last: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return response.read()
        except Exception as exc:  # pragma: no cover - exercised by network CI
            last = exc
            if attempt < attempts:
                time.sleep(2 * attempt)
    raise RuntimeError(f"failed after {attempts} attempts: {url}: {last}")


def ena_metadata(run: str) -> tuple[str, dict[str, str]]:
    query = urllib.parse.urlencode(
        {
            "accession": run,
            "result": "read_run",
            "fields": "run_accession,library_layout,fastq_ftp,fastq_md5,fastq_bytes",
            "format": "tsv",
        }
    )
    url = f"{ENA_API}?{query}"
    text = fetch_bytes(url).decode("utf-8-sig")
    rows = list(csv.DictReader(io.StringIO(text), delimiter="\t"))
    if len(rows) != 1:
        raise SystemExit(f"{run}: expected exactly one ENA read_run row, got {len(rows)}")
    row = rows[0]
    if row.get("run_accession") != run:
        raise SystemExit(f"{run}: ENA returned run_accession={row.get('run_accession')!r}")
    if (row.get("library_layout") or "").upper() != "PAIRED":
        raise SystemExit(f"{run}: paired-end FASTQ required, layout={row.get('library_layout')!r}")
    return text, row


def split_exact_pair(value: str, label: str) -> list[str]:
    parts = [x.strip() for x in (value or "").split(";") if x.strip()]
    if len(parts) != 2:
        raise SystemExit(f"expected exactly two paired {label} values, got {parts}")
    return parts


def https_fastq_urls(row: dict[str, str]) -> list[str]:
    values = split_exact_pair(row.get("fastq_ftp") or "", "ENA FASTQ payload")
    urls = []
    for value in values:
        if value.startswith("ftp://"):
            value = "https://" + value[len("ftp://") :]
        elif value.startswith("ftp."):
            value = "https://" + value
        elif value.startswith("http://"):
            value = "https://" + value[len("http://") :]
        if not value.startswith("https://"):
            raise SystemExit(f"unsupported ENA FASTQ URL: {value}")
        urls.append(value)
    return urls


def read_record(handle: io.TextIOBase, mate: int, record_index: int) -> tuple[str, str, str, str] | None:
    h = handle.readline()
    if h == "":
        return None
    s = handle.readline()
    p = handle.readline()
    q = handle.readline()
    if not s or not p or not q:
        raise RuntimeError(f"mate {mate}: truncated FASTQ record {record_index}")
    if not h.startswith("@"):
        raise RuntimeError(f"mate {mate}: invalid FASTQ header at record {record_index}: {h[:80]!r}")
    if not p.startswith("+"):
        raise RuntimeError(f"mate {mate}: invalid FASTQ separator at record {record_index}: {p[:80]!r}")
    if len(s.rstrip("\r\n")) != len(q.rstrip("\r\n")):
        raise RuntimeError(f"mate {mate}: sequence/quality length mismatch at record {record_index}")
    return h, s, p, q


def copy_fastq_prefix(src: io.TextIOBase, out_path: Path, max_records: int, mate: int) -> int:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = out_path.with_suffix(out_path.suffix + ".part")
    tmp.unlink(missing_ok=True)
    try:
        with tmp.open("w", encoding="utf-8", newline="") as dst:
            n = 0
            while n < max_records:
                record = read_record(src, mate=mate, record_index=n + 1)
                if record is None:
                    break
                dst.writelines(record)
                n += 1
        if n <= 0:
            raise RuntimeError(f"mate {mate}: zero FASTQ records retrieved")
        tmp.replace(out_path)
        return n
    except Exception:
        tmp.unlink(missing_ok=True)
        raise


def stream_prefix(url: str, out_path: Path, max_records: int, mate: int, attempts: int = 3) -> int:
    last: Exception | None = None
    for attempt in range(1, attempts + 1):
        out_path.unlink(missing_ok=True)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=120) as response:
                encoding = (response.headers.get("Content-Encoding") or "").lower()
                if url.endswith(".gz") and encoding not in {"gzip", "x-gzip"}:
                    binary = gzip.GzipFile(fileobj=response, mode="rb")
                else:
                    binary = response
                with io.TextIOWrapper(binary, encoding="utf-8", newline="") as src:
                    return copy_fastq_prefix(src, out_path, max_records, mate)
        except Exception as exc:  # pragma: no cover - exercised by network CI
            last = exc
            out_path.unlink(missing_ok=True)
            if attempt < attempts:
                time.sleep(2 * attempt)
    raise RuntimeError(f"mate {mate}: failed to stream {url} after {attempts} attempts: {last}")


def download_full_verified(
    url: str,
    expected_md5: str,
    expected_bytes: int,
    archive_path: Path,
    mate: int,
    attempts: int = 3,
) -> dict[str, object]:
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    last: Exception | None = None
    for attempt in range(1, attempts + 1):
        archive_path.unlink(missing_ok=True)
        tmp = archive_path.with_suffix(archive_path.suffix + ".part")
        tmp.unlink(missing_ok=True)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            digest = hashlib.md5()
            n_bytes = 0
            with urllib.request.urlopen(req, timeout=180) as response, tmp.open("wb") as dst:
                while True:
                    chunk = response.read(CHUNK_BYTES)
                    if not chunk:
                        break
                    dst.write(chunk)
                    digest.update(chunk)
                    n_bytes += len(chunk)
            observed_md5 = digest.hexdigest()
            if n_bytes != expected_bytes:
                raise RuntimeError(
                    f"mate {mate}: full-download byte mismatch {n_bytes} != {expected_bytes}"
                )
            if observed_md5.lower() != expected_md5.lower():
                raise RuntimeError(
                    f"mate {mate}: full-download MD5 mismatch {observed_md5} != {expected_md5}"
                )
            tmp.replace(archive_path)
            return {
                "verified_full_bytes": n_bytes,
                "verified_full_md5": observed_md5,
                "full_download_attempt": attempt,
            }
        except Exception as exc:  # pragma: no cover - exercised by network CI
            last = exc
            tmp.unlink(missing_ok=True)
            archive_path.unlink(missing_ok=True)
            if attempt < attempts:
                time.sleep(2 * attempt)
    raise RuntimeError(
        f"mate {mate}: failed verified full download after {attempts} attempts: {url}: {last}"
    )


def extract_local_gzip_prefix(archive_path: Path, out_path: Path, max_records: int, mate: int) -> int:
    with gzip.open(archive_path, mode="rt", encoding="utf-8", newline="") as src:
        return copy_fastq_prefix(src, out_path, max_records, mate)


def obtain_prefix(
    url: str,
    out_path: Path,
    max_records: int,
    mate: int,
    expected_md5: str,
    expected_bytes: int,
) -> tuple[int, dict[str, object]]:
    try:
        n = stream_prefix(url, out_path, max_records, mate=mate)
        return n, {"route": "stream_prefix", "stream_failure": None}
    except Exception as stream_exc:
        archive_path = out_path.with_suffix(out_path.suffix + ".source.fastq.gz")
        verified: dict[str, object] = {}
        try:
            verified = download_full_verified(
                url=url,
                expected_md5=expected_md5,
                expected_bytes=expected_bytes,
                archive_path=archive_path,
                mate=mate,
            )
            n = extract_local_gzip_prefix(archive_path, out_path, max_records, mate=mate)
            return n, {
                "route": "verified_full_download_fallback",
                "stream_failure": str(stream_exc),
                **verified,
            }
        finally:
            archive_path.unlink(missing_ok=True)


def normalized_read_id(header: str) -> str:
    token = header[1:].strip().split()[0]
    return re.sub(r"(?:/|_)[12]$", "", token)


def validate_pairs(r1: Path, r2: Path) -> int:
    n = 0
    with r1.open(encoding="utf-8", newline="") as a, r2.open(encoding="utf-8", newline="") as b:
        while True:
            ra = read_record(a, mate=1, record_index=n + 1)
            rb = read_record(b, mate=2, record_index=n + 1)
            if ra is None and rb is None:
                break
            if ra is None or rb is None:
                raise SystemExit(f"paired FASTQ length mismatch after {n} complete pairs")
            if normalized_read_id(ra[0]) != normalized_read_id(rb[0]):
                raise SystemExit(
                    f"paired FASTQ read-id mismatch at pair {n + 1}: "
                    f"{ra[0].strip()!r} != {rb[0].strip()!r}"
                )
            n += 1
    if n <= 0:
        raise SystemExit("no paired FASTQ records validated")
    return n


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--max-spots", type=int, required=True)
    ap.add_argument("--out-r1", type=Path, required=True)
    ap.add_argument("--out-r2", type=Path, required=True)
    ap.add_argument("--metadata-out", type=Path, required=True)
    ap.add_argument("--summary-out", type=Path, required=True)
    args = ap.parse_args()
    if args.max_spots <= 0:
        raise SystemExit("--max-spots must be >0")

    metadata_text, row = ena_metadata(args.run)
    urls = https_fastq_urls(row)
    full_md5 = split_exact_pair(row.get("fastq_md5") or "", "ENA FASTQ MD5")
    full_bytes_text = split_exact_pair(row.get("fastq_bytes") or "", "ENA FASTQ byte-count")
    try:
        full_bytes = [int(x) for x in full_bytes_text]
    except ValueError as exc:
        raise SystemExit(f"invalid ENA fastq_bytes values: {full_bytes_text}") from exc
    if any(x <= 0 for x in full_bytes):
        raise SystemExit(f"non-positive ENA fastq_bytes values: {full_bytes}")

    args.metadata_out.parent.mkdir(parents=True, exist_ok=True)
    args.metadata_out.write_text(metadata_text, encoding="utf-8")

    n1, route1 = obtain_prefix(
        urls[0], args.out_r1, args.max_spots, mate=1,
        expected_md5=full_md5[0], expected_bytes=full_bytes[0],
    )
    n2, route2 = obtain_prefix(
        urls[1], args.out_r2, args.max_spots, mate=2,
        expected_md5=full_md5[1], expected_bytes=full_bytes[1],
    )
    if n1 != n2:
        raise SystemExit(f"mates yielded different prefix sizes: R1={n1}, R2={n2}")
    n_pairs = validate_pairs(args.out_r1, args.out_r2)
    if n_pairs != n1:
        raise SystemExit(f"pair validation count differs from retrieval count: {n_pairs} != {n1}")

    used_fallback = any(x["route"] == "verified_full_download_fallback" for x in (route1, route2))
    summary = {
        "status": "ready",
        "run": args.run,
        "route": "ENA_https_prefix_with_verified_full_fallback" if used_fallback else "ENA_https_fastq_prefix",
        "mate_routes": {"R1": route1, "R2": route2},
        "library_layout": row.get("library_layout"),
        "requested_max_pairs": args.max_spots,
        "actual_pairs": n_pairs,
        "source_urls": urls,
        "source_full_file_md5": full_md5,
        "source_full_file_bytes": full_bytes,
        "local_r1_bytes": args.out_r1.stat().st_size,
        "local_r2_bytes": args.out_r2.stat().st_size,
        "integrity_note": (
            "FASTQ structure and pair IDs are validated on every local prefix. "
            "A mate using fallback is additionally validated against ENA full-file byte count and MD5 before prefix extraction."
        ),
    }
    args.summary_out.parent.mkdir(parents=True, exist_ok=True)
    args.summary_out.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
