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

    with tempfile.TemporaryDirectory(prefix="paper1_v09_docx_") as td:
        base_summary = Path(td) / "docx_v08_summary.json"
        subprocess.run(
            [
                sys.executable,
                "scripts/build_paper1_ajb_docx_v0_8.py",
                "--source", str(a.source),
                "--out", str(a.out),
                "--summary", str(base_summary),
            ],
            check=True,
        )
        inherited = json.loads(base_summary.read_text(encoding="utf-8"))

    summary = {
        **inherited,
        "submission_version": "v0.9",
        "source_markdown": str(a.source),
        "output_docx": str(a.out),
        "source_science_version": "Paper 1 v0.2.2",
        "source_framing_version": "Paper 1 v0.3.2 temporal framing",
        "scientific_results_changed": False,
        "status": "AJB v0.9 DOCX built and structurally audited",
    }
    a.summary.parent.mkdir(parents=True, exist_ok=True)
    a.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
