#!/usr/bin/env python3
"""Read exact 2024 Erica supplementary tree ZIP via Zenodo preservation record.

Source admission only. 2024 tree is *not* a surrogate for the exact 2016
TreeBASE tree in the 2019 Erica analysis. No phylogenetic-memory test.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path
import urllib.request
import urllib.parse
import zipfile

RECORD_ID = 12730704
RECORD_API = f"https://zenodo.org/api/records/{RECORD_ID}"
EXPECTED_DOI = "10.3897/phytokeys.244.124565.suppl7"
BYTE_LIMIT = 12_000_000


def inventory(raw: bytes) -> list[dict]:
    if not raw.startswith(b"PK"):
        raise ValueError("download is not a ZIP")
    members = []
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        if z.testzip() is not None:
            raise ValueError("corrupt tree ZIP")
        for f in z.infolist():
            if f.is_dir():
                continue
            if f.file_size > 25_000_000:
                raise ValueError("oversize uncompressed member")
            ext = Path(f.filename).suffix.lower()
            members.append({
                "name": f.filename, "compressed_bytes": f.compress_size,
                "original_bytes": f.file_size,
                "candidate_tree": ext in (".tre", ".tree", ".nwk", ".newick", ".nex", ".nexus", ".phy"),
            })
    return members


def source_metadata(d: dict) -> tuple[dict, str]:
    if str(d.get("id")) != str(RECORD_ID):
        raise ValueError("incorrect Zenodo record identity")
    m = d.get("metadata", {})
    doi_fields = json.dumps({
        "doi": d.get("doi"), "metadata_doi": m.get("doi"),
        "related_identifiers": m.get("related_identifiers", []),
        "alternate_identifiers": m.get("alternate_identifiers", [])
    })
    if EXPECTED_DOI.lower() not in doi_fields.lower():
        raise ValueError("expected dataset DOI not proven by record metadata")
    files = d.get("files", [])
    choices = [f for f in files if f.get("key", "").lower().endswith(".zip")]
    if len(choices) != 1:
        raise ValueError("not exactly one archived supplementary ZIP")
    f = choices[0]
    url = f.get("links", {}).get("self") or f.get("links", {}).get("download")
    if not url or urllib.parse.urlsplit(url).hostname not in ("zenodo.org", "www.zenodo.org"):
        raise ValueError("untrusted/missing archive download link")
    return f, url


def geturl(url, timeout, urlopen=None, limit=BYTE_LIMIT):
    urlopen = urlopen or urllib.request.urlopen
    req = urllib.request.Request(url, headers={
        "User-Agent": "CHUN-Erica-Zenodo-source-admission/0.1",
        "Accept": "application/json,application/zip,application/octet-stream,*/*"})
    with urlopen(req, timeout=timeout) as resp:
        code = getattr(resp, "status", 200)
        if code != 200:
            raise ValueError(f"HTTP {code}")
        data = resp.read(limit + 1)
    if len(data) > limit:
        raise ValueError("response exceeds fixed byte budget")
    return data


def run(timeout=22, urlopen=None) -> tuple[dict, bytes | None]:
    receipt = {
        "version": "v0.1", "zenodo_record_id": RECORD_ID,
        "expected_dataset_doi": EXPECTED_DOI,
        "status": "HOLD_ZENODO_2024_TREE_SOURCE_NOT_ADMITTED",
        "tree_origin": "2024 LATER ALTERNATIVE; NOT 2016 ORIGINAL",
        "is_original_2016_tree": False, "selected_tree": False,
        "expression_tree_taxon_join_verified": False,
        "pigment_identity_join_verified": False,
        "imputed_tip_exclusion_verified": False,
        "new_evolutionary_memory_estimate": False,
        "independent_replication_admitted": False,
        "frozen_submissions_unchanged": True
    }
    try:
        raw_metadata = geturl(RECORD_API, timeout, urlopen, limit=2_000_000)
        metadata = json.loads(raw_metadata)
        f, fileurl = source_metadata(metadata)
        receipt["record_doi"] = metadata.get("doi") or metadata.get("metadata", {}).get("doi")
        receipt["archive_key"] = f.get("key")
        receipt["advertised_size"] = f.get("size")
        receipt["advertised_checksum"] = f.get("checksum")
        raw = geturl(fileurl, timeout, urlopen)
        receipt["actual_bytes"] = len(raw)
        receipt["sha256"] = hashlib.sha256(raw).hexdigest()
        checksum = (f.get("checksum") or "").lower()
        if checksum.startswith("md5:"):
            if hashlib.md5(raw).hexdigest() != checksum.split(":", 1)[1]:
                raise ValueError("Zenodo MD5 does not match downloaded bytes")
        if f.get("size") and len(raw) != f["size"]:
            raise ValueError("Zenodo declared size mismatch")
        receipt["members"] = inventory(raw)
        receipt["status"] = "PASS_ZENODO_SOURCE_ZIP_INVENTORY_ONLY_NOT_TREE_JOIN"
        return receipt, raw
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError,
            zipfile.BadZipFile) as exc:
        receipt["error"] = type(exc).__name__ + ": " + str(exc)[:400]
        return receipt, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--archive", type=Path)
    ap.add_argument("--timeout", type=int, default=22)
    opts = ap.parse_args()
    if not 1 <= opts.timeout <= 45:
        raise ValueError("invalid timeout")
    result, archive = run(opts.timeout)
    opts.out.parent.mkdir(parents=True, exist_ok=True)
    opts.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if archive is not None and opts.archive is not None:
        opts.archive.parent.mkdir(parents=True, exist_ok=True)
        opts.archive.write_bytes(archive)
    print("ERICA_ZENODO_STATUS", result["status"])
    print("ERICA_ZENODO_IDENTITY", result.get("record_doi"), result.get("archive_key"),
          result.get("actual_bytes"), result.get("sha256"))
    for f in result.get("members", []):
        print("ERICA_ZENODO_MEMBER", json.dumps(f))
    if "error" in result:
        print("ERICA_ZENODO_HOLD_CAUSE", result["error"])
    print("NO_NEW_PHYLOGENETIC_MEMORY_RESULT")


if __name__ == "__main__":
    main()
