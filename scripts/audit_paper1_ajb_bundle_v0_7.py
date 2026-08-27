#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def normalize_doi(x: str) -> str:
    x = x.strip().lower().rstrip(".,;)")
    x = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", x)
    return x


def manuscript_dois(text: str) -> set[str]:
    marker = "# LITERATURE CITED"
    if text.count(marker) != 1:
        raise SystemExit("Literature Cited marker missing or duplicated")
    refs = text.split(marker, 1)[1]
    refs = refs.split("# SUPPORTING INFORMATION", 1)[0]
    return {normalize_doi(x) for x in re.findall(r"https?://doi\.org/(10\.[^\s]+)", refs, flags=re.I)}


def abstract_word_count(text: str) -> int:
    block = text.split("## ABSTRACT", 1)[1].split("**Key words:**", 1)[0]
    body = "\n".join(line for line in block.splitlines() if not line.startswith("#"))
    return len(re.findall(r"\b[\w’'-]+\b", body))


def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--bundle", type=Path, required=True); ap.add_argument("--out", type=Path, required=True); a = ap.parse_args()
    root = a.bundle
    required = [
        "README.md",
        "manuscript/PAPER1_AJB_UPLOAD_V0_7.md",
        "manuscript/PAPER1_AJB_UPLOAD_V0_7.docx",
        *[f"main_figures/Figure_{i}.{ext}" for i in range(1, 7) for ext in ("png", "svg")],
        *[f"appendices/Appendix_S{i}.csv" for i in range(1, 7)],
        "appendices/Appendix_S7.png", "appendices/Appendix_S8.png",
        "provenance/paper1_authoritative_results_v0_2.csv",
        "provenance/paper1_main_figure_manifest_v0_2.csv",
        "provenance/paper1_reference_registry_v0_3.csv",
        "provenance/paper1_ajb_appendix_mapping_v0_3.csv",
        "provenance/PAPER1_AJB_MANUSCRIPT_V0_3.md",
        "provenance/PAPER1_NOVELTY_LITERATURE_AUDIT_2026-08-27.md",
        "provenance/PAPER1_NOVELTY_CORE_ATTACK_ADDENDUM_2026-08-27.md",
        "provenance/EVIDENCE_AUDIT_2026-08-26.md",
        "provenance/novelty_framing_summary.json",
        "provenance/reference_registry_summary.json",
        "provenance/submission_v0_7_build_summary.json",
        "provenance/submission_reference_registry_summary.json",
        "provenance/docx_v0_7_summary.json",
        "provenance/registry_gate_summary.json",
        "provenance/supplementary_figure_summary.json",
    ]
    missing = [rel for rel in required if not (root / rel).exists()]
    if missing:
        raise SystemExit(f"bundle missing required files: {missing}")
    tiny = [rel for rel in required if (root / rel).is_file() and (root / rel).stat().st_size == 0]
    if tiny:
        raise SystemExit(f"bundle contains empty required files: {tiny}")

    manuscript = (root / "manuscript/PAPER1_AJB_UPLOAD_V0_7.md").read_text(encoding="utf-8")
    forbidden = ["Draft v0.2", "Draft v0.3", "`data/", "`docs/", "`scripts/", "GitHub Actions", "ecological Fig. 6", "PAPER1_AJB_MANUSCRIPT_V0_1", "paper1_authoritative_results_v0_1", "FigS3_legacy_event_falsification"]
    retained = [x for x in forbidden if x in manuscript]
    if retained:
        raise SystemExit(f"submission manuscript retains stale/internal tokens: {retained}")

    frozen = [
        "Candidate-free remeasurement fixed exact-signature recurrence at 0.333",
        "pairwise concordance at **0.75**",
        "strict×dominant shared robust event count was therefore zero",
        "Repeated flower-colour change in *Camellia* does not imply repetition of one complete A/F/C/P pigment-state package.",
    ]
    novelty = [
        "The molecular result should not be read as the first demonstration",
        "observation-method dependence itself a new concept",
        "event instability is not itself a new methodological discovery",
        "The ecological value of the present result is an inferential boundary",
    ]
    absent = [x for x in frozen + novelty if x not in manuscript]
    if absent:
        raise SystemExit(f"submission manuscript lost frozen/novelty-audit claims: {absent}")

    words = abstract_word_count(manuscript)
    if words > 250:
        raise SystemExit(f"AJB abstract exceeds 250 words: {words}")
    for label in ["### Premise of the study", "### Methods", "### Key results", "### Conclusions"]:
        if manuscript.count(label) != 1:
            raise SystemExit(f"structured abstract heading drift: {label}")

    placeholders = [
        "[AUTHOR LIST TO ADD AT SUBMISSION]", "[AFFILIATIONS TO ADD AT SUBMISSION]",
        "[CORRESPONDING AUTHOR DETAILS TO ADD AT SUBMISSION]", "[ACKNOWLEDGMENTS AND FUNDING TO ADD AT SUBMISSION]",
        "[CRediT AUTHOR CONTRIBUTIONS TO ADD AT SUBMISSION]", "[ARCHIVE DOI TO ADD AT SUBMISSION]",
    ]
    bad = {x: manuscript.count(x) for x in placeholders if manuscript.count(x) != 1}
    if bad:
        raise SystemExit(f"submission placeholder count drift: {bad}")

    headings = ["# ACKNOWLEDGMENTS", "# AUTHOR CONTRIBUTIONS", "# DATA AVAILABILITY STATEMENT", "# LITERATURE CITED", "# SUPPORTING INFORMATION", "# FIGURE LEGENDS"]
    pos = [manuscript.index(x) for x in headings]
    if pos != sorted(pos):
        raise SystemExit(f"AJB section order drift: {list(zip(headings, pos))}")
    for i in range(1, 9):
        if f"Appendix S{i}" not in manuscript:
            raise SystemExit(f"manuscript missing Appendix S{i}")

    registry = read_csv(root / "provenance/paper1_reference_registry_v0_3.csv")
    reg_dois = {normalize_doi(r["doi"]) for r in registry if r.get("doi", "").strip()}
    ms_dois = manuscript_dois(manuscript)
    if len(registry) != 21 or len(reg_dois) != 21 or ms_dois != reg_dois:
        raise SystemExit(f"v0.3 reference contract drift: registry_rows={len(registry)} registry_dois={len(reg_dois)} manuscript_dois={len(ms_dois)} missing={sorted(reg_dois-ms_dois)} extra={sorted(ms_dois-reg_dois)}")

    docx = root / "manuscript/PAPER1_AJB_UPLOAD_V0_7.docx"
    if docx.stat().st_size < 20000:
        raise SystemExit("DOCX unexpectedly small")

    files = sorted(p for p in root.rglob("*") if p.is_file() and p != a.out)
    entries = [{"path": str(p.relative_to(root)), "bytes": p.stat().st_size, "sha256": sha256(p)} for p in files]
    manifest = {
        "bundle_version": "v0.7-ajb-upload-paper1-v0.2-framing-v0.3",
        "source_science_version": "Paper 1 v0.2",
        "source_framing_version": "Paper 1 v0.3",
        "n_files": len(entries), "main_figures": 6, "appendices": 8, "reference_registry_rows": 21,
        "abstract_word_count": words, "docx_present": True, "obsolete_ecological_fig6_absent": True,
        "scientific_results_changed": False, "novelty_audit_date": "2026-08-27", "status": "bundle audit passed", "files": entries,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True); a.out.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in manifest.items() if k != "files"}, indent=2)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
