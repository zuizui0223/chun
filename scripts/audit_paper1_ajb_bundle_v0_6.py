#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    root = a.bundle

    required = [
        "README.md",
        "manuscript/PAPER1_AJB_UPLOAD_V0_6.md",
        "main_figures/Figure_1.png", "main_figures/Figure_1.svg",
        "main_figures/Figure_2.png", "main_figures/Figure_2.svg",
        "main_figures/Figure_3.png", "main_figures/Figure_3.svg",
        "main_figures/Figure_4.png", "main_figures/Figure_4.svg",
        "main_figures/Figure_5.png", "main_figures/Figure_5.svg",
        "main_figures/Figure_6.png", "main_figures/Figure_6.svg",
        *[f"appendices/Appendix_S{i}.csv" for i in range(1, 7)],
        "appendices/Appendix_S7.png",
        "appendices/Appendix_S8.png",
        "provenance/paper1_authoritative_results_v0_2.csv",
        "provenance/paper1_main_figure_manifest_v0_2.csv",
        "provenance/paper1_reference_registry_v0_2.csv",
        "provenance/paper1_ajb_appendix_mapping_v0_3.csv",
        "provenance/submission_v0_6_build_summary.json",
        "provenance/registry_gate_summary.json",
        "provenance/supplementary_figure_summary.json",
    ]
    missing = [rel for rel in required if not (root / rel).exists()]
    if missing:
        raise SystemExit(f"bundle missing required files: {missing}")

    tiny = [rel for rel in required if (root / rel).is_file() and (root / rel).stat().st_size == 0]
    if tiny:
        raise SystemExit(f"bundle contains empty required files: {tiny}")

    manuscript = (root / "manuscript/PAPER1_AJB_UPLOAD_V0_6.md").read_text(encoding="utf-8")
    forbidden = [
        "Draft v0.2",
        "`data/", "`docs/", "`scripts/",
        "GitHub Actions",
        "ecological Fig. 6",
        "PAPER1_AJB_MANUSCRIPT_V0_1",
        "paper1_authoritative_results_v0_1",
        "FigS3_legacy_event_falsification",
    ]
    retained = [token for token in forbidden if token in manuscript]
    if retained:
        raise SystemExit(f"submission manuscript retains stale/internal tokens: {retained}")

    required_claims = [
        "candidate-free exact-signature recurrence at 0.333",
        "pairwise concordance at 0.75",
        "strict×dominant shared robust event count was therefore zero",
        "Repeated flower-colour change in *Camellia* does not imply repetition of one complete A/F/C/P pigment-state package.",
    ]
    absent_claims = [token for token in required_claims if token not in manuscript]
    if absent_claims:
        raise SystemExit(f"submission manuscript lost frozen v0.2 claims: {absent_claims}")

    if manuscript.count("[ARCHIVE DOI TO ADD AT SUBMISSION]") != 1:
        raise SystemExit("submission manuscript must contain exactly one archive DOI placeholder")
    for i in range(1, 9):
        if f"Appendix S{i}" not in manuscript:
            raise SystemExit(f"manuscript missing Appendix S{i} legend/reference")

    files = sorted(p for p in root.rglob("*") if p.is_file() and p != a.out)
    entries = [
        {
            "path": str(p.relative_to(root)),
            "bytes": p.stat().st_size,
            "sha256": sha256(p),
        }
        for p in files
    ]
    manifest = {
        "bundle_version": "v0.6-ajb-upload-paper1-v0.2",
        "source_science_version": "Paper 1 v0.2",
        "n_files": len(entries),
        "main_figures": 6,
        "appendices": 8,
        "obsolete_ecological_fig6_absent": True,
        "legacy_v0_1_registry_absent_from_submission_contract": True,
        "archive_doi_placeholders": 1,
        "status": "bundle audit passed",
        "files": entries,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in manifest.items() if k != "files"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
