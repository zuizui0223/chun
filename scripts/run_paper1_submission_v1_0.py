#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

MARKER = "<!-- v1.0-compatibility-only: repeated generation with partial mechanistic replay -->"
TITLE = "# Standardized remeasurement reveals partial mechanistic replay during repeated flower-colour evolution in *Camellia*"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--appendix-map", type=Path, required=True)
    ap.add_argument("--figure-manifest", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    a = ap.parse_args()

    text = a.source.read_text(encoding="utf-8")
    if text.count(TITLE) != 1:
        raise SystemExit("v1.0 source title drift")
    if MARKER in text:
        raise SystemExit("v1.0 source unexpectedly contains compatibility marker")
    compat = text.replace(TITLE, TITLE + "\n\n" + MARKER, 1)

    with tempfile.TemporaryDirectory(prefix="paper1_v10_submit_") as td:
        compat_source = Path(td) / "PAPER1_NOVELTY_V033_SUBMISSION_COMPAT.md"
        compat_summary = Path(td) / "submission_summary.json"
        compat_source.write_text(compat, encoding="utf-8")
        subprocess.run([
            sys.executable,
            "scripts/build_paper1_submission_v1_0.py",
            "--source", str(compat_source),
            "--appendix-map", str(a.appendix_map),
            "--figure-manifest", str(a.figure_manifest),
            "--out", str(a.out),
            "--summary", str(compat_summary),
        ], check=True)
        summary = json.loads(compat_summary.read_text(encoding="utf-8"))

    out = a.out.read_text(encoding="utf-8")
    if out.count(MARKER) != 1:
        raise SystemExit(f"v1.0 compatibility marker count drift in output: {out.count(MARKER)}")
    out = out.replace(MARKER + "\n\n", "", 1).replace(MARKER, "", 1)
    if MARKER in out or "repeated generation with partial mechanistic replay" in out:
        raise SystemExit("v1.0 compatibility token leaked into final manuscript")
    a.out.write_text(out.rstrip() + "\n", encoding="utf-8")

    summary.update({
        "source_manuscript": str(a.source),
        "compatibility_marker_removed": True,
        "status": "submission-clean Paper 1 AJB v1.0 built with v0.9 compatibility token removed",
    })
    a.summary.parent.mkdir(parents=True, exist_ok=True)
    a.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
