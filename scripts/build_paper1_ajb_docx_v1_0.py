#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile, ZipInfo

from docx import Document

FIXED_CORE_TIME = datetime(2000, 1, 1, 0, 0, 0)
FIXED_ZIP_TIME = (2000, 1, 1, 0, 0, 0)


def normalize_docx_package(path: Path) -> None:
    """Make DOCX metadata and ZIP container timestamps byte-reproducible."""
    doc = Document(path)
    props = doc.core_properties
    props.created = FIXED_CORE_TIME
    props.modified = FIXED_CORE_TIME
    props.last_modified_by = ""
    props.revision = 1
    doc.save(path)

    normalized = path.with_suffix(path.suffix + ".normalized")
    with ZipFile(path, "r") as src, ZipFile(normalized, "w") as dst:
        for member in sorted(src.infolist(), key=lambda x: x.filename):
            data = src.read(member.filename)
            info = ZipInfo(member.filename, date_time=FIXED_ZIP_TIME)
            info.compress_type = member.compress_type
            info.comment = member.comment
            info.extra = b""
            info.create_system = member.create_system
            info.create_version = member.create_version
            info.extract_version = member.extract_version
            info.flag_bits = member.flag_bits
            info.volume = member.volume
            info.internal_attr = member.internal_attr
            info.external_attr = member.external_attr
            if member.compress_type == ZIP_DEFLATED:
                dst.writestr(info, data, compress_type=ZIP_DEFLATED, compresslevel=9)
            elif member.compress_type == ZIP_STORED:
                dst.writestr(info, data, compress_type=ZIP_STORED)
            else:
                dst.writestr(info, data, compress_type=member.compress_type)
    os.replace(normalized, path)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    a = ap.parse_args()

    with tempfile.TemporaryDirectory(prefix="paper1_v10_docx_") as td:
        inherited_summary = Path(td) / "docx_v09_summary.json"
        subprocess.run([
            sys.executable,
            "scripts/build_paper1_ajb_docx_v0_9.py",
            "--source", str(a.source),
            "--out", str(a.out),
            "--summary", str(inherited_summary),
        ], check=True)
        inherited = json.loads(inherited_summary.read_text(encoding="utf-8"))

    normalize_docx_package(a.out)

    summary = {
        **inherited,
        "submission_version": "v1.0",
        "source_markdown": str(a.source),
        "output_docx": str(a.out),
        "bytes": a.out.stat().st_size,
        "source_science_version": "Paper 1 v0.2.2",
        "source_framing_version": "Paper 1 v0.3.4 event-boundary-safe novelty framing",
        "scientific_results_changed": False,
        "event_boundary_clarified": True,
        "reproducible_package_normalized": True,
        "fixed_core_timestamp": "2000-01-01T00:00:00",
        "fixed_zip_timestamp": "2000-01-01T00:00:00",
        "status": "AJB v1.0 DOCX built from framing v0.3.4, structurally audited, and byte-normalized",
    }
    a.summary.parent.mkdir(parents=True, exist_ok=True)
    a.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
