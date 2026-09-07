#!/usr/bin/env python3
"""Retrieve and inventory the frozen Antirrhineae flower-colour source bundle.

Source: Ellis & Field 2016 data object, DOI 10.15479/AT:ISTA:34 (CC0).
The published repository checksum is treated as the admission gate.  The script
fails closed if the downloaded bytes do not match that checksum.
"""
from __future__ import annotations

import argparse
import hashlib
import html.parser
import json
import shutil
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

DOI = "10.15479/AT:ISTA:34"
RECORD_ID = "5550"
FILENAME = "IST-2016-34-v1+1_tellis_flower_colour_data.zip"
EXPECTED_MD5 = "950f85b80427d357bfeff09608ba02e9"
RECORD_URLS = (
    "https://research-explorer.ista.ac.at/record/5550",
    "https://research-explorer-playground.test.ista.ac.at/record/5550",
)


class LinkParser(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag.lower() != "a":
            return
        for k, v in attrs:
            if k.lower() == "href" and v:
                self.hrefs.append(v)


def request_bytes(url: str) -> tuple[bytes, str]:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "chun-antirrhineae-ingestion/0.1 (+https://github.com/zuizui0223/chun)"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read(), resp.geturl()


def candidate_urls() -> list[str]:
    candidates: list[str] = []
    quoted = urllib.parse.quote(FILENAME, safe="+._-")
    for record in RECORD_URLS:
        try:
            html, resolved = request_bytes(record)
        except Exception:
            continue
        parser = LinkParser()
        parser.feed(html.decode("utf-8", errors="replace"))
        for href in parser.hrefs:
            absolute = urllib.parse.urljoin(resolved, href)
            low = urllib.parse.unquote(absolute).lower()
            if FILENAME.lower() in low or ("/record/5550/" in low and ("download" in low or low.endswith(".zip"))):
                candidates.append(absolute)
        base = resolved.split("/record/")[0]
        candidates.extend(
            [
                f"{base}/record/{RECORD_ID}/files/{quoted}?download=1",
                f"{base}/record/{RECORD_ID}/files/{quoted}",
                f"{base}/records/{RECORD_ID}/files/{quoted}?download=1",
                f"{base}/records/{RECORD_ID}/files/{quoted}/content",
            ]
        )
    # Stable de-duplication.
    return list(dict.fromkeys(candidates))


def retrieve_bundle() -> tuple[bytes, str, list[dict]]:
    attempts: list[dict] = []
    for url in candidate_urls():
        try:
            raw, resolved = request_bytes(url)
            md5 = hashlib.md5(raw).hexdigest()
            attempts.append({"url": url, "resolved_url": resolved, "bytes": len(raw), "md5": md5})
            if md5 == EXPECTED_MD5:
                return raw, resolved, attempts
        except Exception as exc:
            attempts.append({"url": url, "error": type(exc).__name__, "message": str(exc)[:300]})
    raise RuntimeError(
        "no retrieved candidate matched the published MD5; attempts=" + json.dumps(attempts, ensure_ascii=False)
    )


def safe_member(name: str) -> bool:
    p = Path(name)
    return not p.is_absolute() and ".." not in p.parts


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()
    out = args.out_dir
    out.mkdir(parents=True, exist_ok=True)

    raw, resolved, attempts = retrieve_bundle()
    bundle = out / FILENAME
    bundle.write_bytes(raw)
    if hashlib.md5(raw).hexdigest() != EXPECTED_MD5:
        raise RuntimeError("published MD5 gate drift")

    extracted = out / "extracted"
    if extracted.exists():
        shutil.rmtree(extracted)
    extracted.mkdir()

    members: list[dict] = []
    with zipfile.ZipFile(bundle) as zf:
        for info in zf.infolist():
            if not safe_member(info.filename):
                raise RuntimeError(f"unsafe archive member: {info.filename}")
            members.append(
                {
                    "name": info.filename,
                    "bytes": info.file_size,
                    "crc32": f"{info.CRC:08x}",
                    "is_dir": info.is_dir(),
                }
            )
            zf.extract(info, extracted)

    files = [m for m in members if not m["is_dir"]]
    lower_names = [m["name"].lower() for m in files]
    colour_candidates = [m["name"] for m in files if any(x in m["name"].lower() for x in ("colour", "color", "trait", "phenotype"))]
    tree_candidates = [m["name"] for m in files if m["name"].lower().endswith((".nex", ".nexus", ".tre", ".tree", ".trees")) or "phylo" in m["name"].lower()]

    manifest = {
        "version": "v0.1",
        "source_doi": DOI,
        "record_id": RECORD_ID,
        "license": "CC0-1.0",
        "filename": FILENAME,
        "published_md5": EXPECTED_MD5,
        "observed_md5": hashlib.md5(raw).hexdigest(),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
        "resolved_download_url": resolved,
        "retrieval_attempts": attempts,
        "archive_members": members,
        "colour_candidate_files": colour_candidates,
        "tree_candidate_files": tree_candidates,
        "has_colour_candidate": bool(colour_candidates),
        "has_tree_candidate": bool(tree_candidates),
        "admission_status": "INGESTED_CHECKSUM_VERIFIED" if colour_candidates and tree_candidates else "INGESTED_NEEDS_CONTENT_MAPPING",
        "paper1_science_changed": False,
    }
    (out / "source_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
