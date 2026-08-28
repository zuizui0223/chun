#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def run(*args: str) -> None:
    cmd = [sys.executable, *args]
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True, env={**os.environ, "MPLBACKEND": "Agg"})


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, required=True)
    a = ap.parse_args()
    bundle = a.out_dir

    # Reuse the fully audited v0.9 scientific packaging as the figure/SI base.
    run("scripts/build_paper1_ajb_bundle_v0_9.py", "--out-dir", str(bundle))

    science = bundle / "provenance/PAPER1_SCIENCE_V0_2_2.md"
    framed = bundle / "provenance/PAPER1_NOVELTY_FRAMING_V0_3_4.md"
    run(
        "scripts/build_paper1_novelty_framing_v0_3_4.py",
        "--source", str(science),
        "--out", str(framed),
        "--summary", str(bundle / "provenance/novelty_framing_v0_3_4_summary.json"),
    )
    run(
        "scripts/validate_paper1_reference_registry_v0_5.py",
        "--registry", "data/paper1_reference_registry_v0_5.csv",
        "--manuscript", str(framed),
        "--out", str(bundle / "provenance/novelty_reference_registry_v0_5_summary.json"),
    )

    submission = bundle / "manuscript/PAPER1_AJB_UPLOAD_V1_0.md"
    run(
        "scripts/run_paper1_submission_v1_0.py",
        "--source", str(framed),
        "--appendix-map", "data/paper1_ajb_appendix_mapping_v0_5.csv",
        "--figure-manifest", "data/paper1_main_figure_manifest_v0_2_2.csv",
        "--out", str(submission),
        "--summary", str(bundle / "provenance/submission_v1_0_build_summary.json"),
    )
    run(
        "scripts/validate_paper1_reference_registry_v0_5.py",
        "--registry", "data/paper1_reference_registry_v0_5.csv",
        "--manuscript", str(submission),
        "--out", str(bundle / "provenance/submission_reference_registry_v1_0_summary.json"),
    )
    run(
        "scripts/build_paper1_ajb_docx_v1_0.py",
        "--source", str(submission),
        "--out", str(bundle / "manuscript/PAPER1_AJB_UPLOAD_V1_0.docx"),
        "--summary", str(bundle / "provenance/docx_v1_0_summary.json"),
    )

    # Remove superseded submission-facing v0.9 files while retaining its deeper provenance.
    for rel in [
        "manuscript/PAPER1_AJB_UPLOAD_V0_9.md",
        "manuscript/PAPER1_AJB_UPLOAD_V0_9.docx",
        "provenance/submission_v0_9_build_summary.json",
        "provenance/docx_v0_9_summary.json",
        "provenance/PAPER1_NOVELTY_FRAMING_V0_3_3.md",
        "provenance/novelty_framing_v0_3_3_summary.json",
    ]:
        p = bundle / rel
        if p.exists():
            p.unlink()

    shutil.copy2("docs/PAPER1_AJB_UPLOAD_BUNDLE_V1_0_README.md", bundle / "README.md")
    (bundle / "submission").mkdir(parents=True, exist_ok=True)
    shutil.copy2(
        "docs/PAPER1_AJB_V1_0_COVER_LETTER_TEMPLATE.md",
        bundle / "submission/PAPER1_AJB_V1_0_COVER_LETTER_TEMPLATE.md",
    )
    shutil.copy2(
        "docs/PAPER1_AJB_V1_0_SUBMISSION_CHECKLIST.md",
        bundle / "submission/PAPER1_AJB_V1_0_SUBMISSION_CHECKLIST.md",
    )
    shutil.copy2(
        "docs/PAPER1_STATE_IDENTITY_FRAMING_GATE_V0_1.md",
        bundle / "provenance/PAPER1_STATE_IDENTITY_FRAMING_GATE_V0_1.md",
    )
    shutil.copy2(
        "docs/PAPER1_JOURNAL_STRATEGY.md",
        bundle / "provenance/PAPER1_JOURNAL_STRATEGY.md",
    )

    run(
        "scripts/audit_paper1_ajb_bundle_v1_0.py",
        "--bundle", str(bundle),
        "--out", str(bundle / "BUNDLE_MANIFEST.json"),
    )
    manifest = json.loads((bundle / "BUNDLE_MANIFEST.json").read_text(encoding="utf-8"))
    print(json.dumps({k: v for k, v in manifest.items() if k != "files"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
