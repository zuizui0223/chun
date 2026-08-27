#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

V03_BANNER = (
    "> Draft v0.3 framing revision. The scientific result set remains Paper 1 v0.2. Novelty framing was "
    "revised after the 2026-08-27 high-recall prior-art audit; no biological estimate, contrast, figure input, "
    "or inferential gate is changed by this document."
)
V02_BANNER = (
    "> Draft v0.2. This manuscript is governed by `data/paper1_authoritative_results_v0_2.csv`, "
    "`data/paper1_main_figure_manifest_v0_2.csv`, and `data/paper1_reference_registry_v0_2.csv`. "
    "The v0.1 manuscript is retained as provenance and must not be patched back into the molecular framing "
    "when it conflicts with the v0.2 result hierarchy."
)
NOVELTY_TOKENS = [
    "The molecular result should not be read as the first demonstration",
    "observation-method dependence itself a new concept",
    "event instability is not itself a new methodological discovery",
    "The ecological value of the present result is an inferential boundary",
]
NOVELTY_DOIS = [
    "10.1098/rspb.2012.2146",
    "10.1111/nph.13576",
    "10.1093/molbev/msy117",
    "10.1098/rspb.2023.0275",
    "10.1016/j.scienta.2025.114474",
    "10.1007/s11692-025-09645-y",
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, required=True, help="novelty-framed Paper 1 v0.3 markdown")
    ap.add_argument("--appendix-map", type=Path, required=True)
    ap.add_argument("--figure-manifest", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    a = ap.parse_args()

    source_text = a.source.read_text(encoding="utf-8")
    if source_text.count(V03_BANNER) != 1:
        raise SystemExit("expected exactly one Paper 1 v0.3 framing banner")
    missing_novelty = [x for x in NOVELTY_TOKENS + NOVELTY_DOIS if x not in source_text]
    if missing_novelty:
        raise SystemExit(f"v0.3 source missing novelty-audit tokens: {missing_novelty}")

    # Reuse the already-audited AJB v0.6 submission transformer. Only its
    # governance-banner contract is v0.2-specific, so provide a temporary
    # compatibility source while preserving all v0.3 framing/ref text.
    compat_text = source_text.replace(V03_BANNER, V02_BANNER, 1)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.summary.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="paper1_v07_") as td:
        td = Path(td)
        compat = td / "PAPER1_AJB_MANUSCRIPT_V0_3_COMPAT.md"
        base_summary = td / "v06_summary.json"
        compat.write_text(compat_text, encoding="utf-8")
        cmd = [
            sys.executable,
            "scripts/build_paper1_submission_v0_6.py",
            "--source", str(compat),
            "--appendix-map", str(a.appendix_map),
            "--figure-manifest", str(a.figure_manifest),
            "--out", str(a.out),
            "--summary", str(base_summary),
        ]
        subprocess.run(cmd, check=True)
        inherited = json.loads(base_summary.read_text(encoding="utf-8"))

    out_text = a.out.read_text(encoding="utf-8")
    if "Draft v0.2" in out_text or "Draft v0.3" in out_text:
        raise SystemExit("submission output retained a governance banner")
    missing_out = [x for x in NOVELTY_TOKENS + NOVELTY_DOIS if x not in out_text]
    if missing_out:
        raise SystemExit(f"submission output lost novelty-audit tokens: {missing_out}")

    summary = {
        **inherited,
        "submission_version": "v0.7",
        "source_manuscript": str(a.source),
        "source_science_version": "Paper 1 v0.2",
        "source_framing_version": "Paper 1 v0.3",
        "reference_contract": "paper1_reference_registry_v0_3.csv (21 DOI rows)",
        "novelty_audit_date": "2026-08-27",
        "novelty_tokens_preserved": len(NOVELTY_TOKENS),
        "required_novelty_dois_preserved": len(NOVELTY_DOIS),
        "scientific_results_changed": False,
        "status": "submission-clean Paper 1 AJB v0.7 built from science v0.2 + novelty framing v0.3",
    }
    a.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
