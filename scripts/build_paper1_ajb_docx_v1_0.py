#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


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

    summary = {
        **inherited,
        "submission_version": "v1.0",
        "source_markdown": str(a.source),
        "output_docx": str(a.out),
        "source_science_version": "Paper 1 v0.2.2",
        "source_framing_version": "Paper 1 v0.3.4 event-boundary-safe novelty framing",
        "scientific_results_changed": False,
        "event_boundary_clarified": True,
        "status": "AJB v1.0 DOCX built from framing v0.3.4 and structurally audited",
    }
    a.summary.parent.mkdir(parents=True, exist_ok=True)
    a.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
