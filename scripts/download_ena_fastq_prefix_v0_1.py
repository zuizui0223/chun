#!/usr/bin/env python3
"""Stream a paired FASTQ prefix for one SRA run from ENA over HTTPS.

The route is intentionally independent of any expression or colour outcome.
ENA run metadata resolves the archived paired FASTQ payloads; each gzip stream is
read only until the preregistered number of read pairs has been written locally.
Full-file MD5 values are recorded for provenance but cannot be validated against
a deliberately truncated prefix.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import io
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

ENA_API = "https://www.ebi.ac.uk/ena/portal/api/filereport"
USER_AGENT = "chun-candidate-free-rnaseq/0.1"


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


def https_fastq_urls(row: dict[str, str]) -> list[str]:
    values = [x.strip() for x in (row.get("fastq_ftp") or "").split(";") if x.strip()]
    if len(values) != 2:
        raise SystemExit(f"expected exactly two paired ENA FASTQ payloads, got {values}")
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


def stream_prefix(url: str, out_path: Path, max_records: int, mate: int, attempts: int = 3) -> int:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    last: Exception | None = None
    for attempt in range(1, attempts + 1):
        tmp = out_path.with_suffix(out_path.suffix + ".part")
        tmp.unlink(missing_ok=True)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=120) as response:
                encoding = (response.headers.get("Content-Encoding") or "").lower()
                if url.endswith(".gz") and encoding not in {"gzip", "x-gzip"}:
                    binary = gzip.GzipFile(fileobj=response, mode="rb")
                else:
                    binary = response
                with io.TextIOWrapper(binary, encoding="utf-8", newline="") as src, tmp.open(
                    "w", encoding="utf-8", newline=""
                ) as dst:
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
        except Exception as exc:  # pragma: no cover - exercised by network CI
            last = exc
            tmp.unlink(missing_ok=True)
            if attempt < attempts:
                time.sleep(2 * attempt)
    raise RuntimeError(f"mate {mate}: failed to stream {url} after {attempts} attempts: {last}")


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
    args.metadata_out.parent.mkdir(parents=True, exist_ok=True)
    args.metadata_out.write_text(metadata_text, encoding="utf-8")

    n1 = stream_prefix(urls[0], args.out_r1, args.max_spots, mate=1)
    n2 = stream_prefix(urls[1], args.out_r2, args.max_spots, mate=2)
    if n1 != n2:
        raise SystemExit(f"mates yielded different prefix sizes: R1={n1}, R2={n2}")
    n_pairs = validate_pairs(args.out_r1, args.out_r2)
    if n_pairs != n1:
        raise SystemExit(f"pair validation count differs from stream count: {n_pairs} != {n1}")

    full_md5 = [x for x in (row.get("fastq_md5") or "").split(";") if x]
    full_bytes = [x for x in (row.get("fastq_bytes") or "").split(";") if x]
    summary = {
        "status": "ready",
        "run": args.run,
        "route": "ENA_https_fastq_prefix",
        "library_layout": row.get("library_layout"),
        "requested_max_pairs": args.max_spots,
        "actual_pairs": n_pairs,
        "source_urls": urls,
        "source_full_file_md5": full_md5,
        "source_full_file_bytes": full_bytes,
        "local_r1_bytes": args.out_r1.stat().st_size,
        "local_r2_bytes": args.out_r2.stat().st_size,
        "integrity_note": "FASTQ structure and pair IDs validated on the streamed prefix; archive MD5 values describe full remote files and are not compared to truncated local prefixes.",
    }
    args.summary_out.parent.mkdir(parents=True, exist_ok=True)
    args.summary_out.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
