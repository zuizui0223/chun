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
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def norm_doi(x: str) -> str:
    x = x.strip().lower().rstrip(".,;)")
    return re.sub(r"^https?://(?:dx\.)?doi\.org/", "", x)


def manuscript_dois(text: str) -> set[str]:
    refs = text.split("# LITERATURE CITED", 1)[1].split("# SUPPORTING INFORMATION", 1)[0]
    return {norm_doi(x) for x in re.findall(r"https?://doi\.org/(10\.[^\s]+)", refs, flags=re.I)}


def abstract_words(text: str) -> int:
    block = text.split("## ABSTRACT", 1)[1].split("**Key words:**", 1)[0]
    body = "\n".join(line for line in block.splitlines() if not line.startswith("#"))
    return len(re.findall(r"\b[\w’'-]+\b", body))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    root = a.bundle

    required = [
        "README.md",
        "manuscript/PAPER1_AJB_UPLOAD_V0_8.md",
        "manuscript/PAPER1_AJB_UPLOAD_V0_8.docx",
        *[f"main_figures/Figure_{i}.{ext}" for i in range(1, 7) for ext in ("png", "svg")],
        *[f"appendices/Appendix_S{i}.csv" for i in range(1, 7)],
        "appendices/Appendix_S7.png",
        "appendices/Appendix_S8.png",
        "provenance/paper1_authoritative_results_v0_2_1.csv",
        "provenance/paper1_main_figure_manifest_v0_2_1.csv",
        "provenance/paper1_fig1_observation_contract_v0_2_1.csv",
        "provenance/paper1_reference_registry_v0_2_1.csv",
        "provenance/paper1_reference_registry_v0_4.csv",
        "provenance/paper1_ajb_appendix_mapping_v0_4.csv",
        "provenance/paper1_bibliographic_db_queries_v0_1.csv",
        "provenance/paper1_bibliographic_priority_screen_v0_1.csv",
        "provenance/PAPER1_AJB_MANUSCRIPT_V0_2_1.md",
        "provenance/PAPER1_AJB_MANUSCRIPT_V0_3_1.md",
        "provenance/MICRO_ACCESSIBILITY_V0_2_RESULT.md",
        "provenance/PAPER1_BIBLIOGRAPHIC_DB_SEARCH_2026-08-27.md",
        "provenance/PAPER1_LITERATURE_SATURATION_TEST_2026-08-27.md",
        "provenance/PAPER1_NOVELTY_LITERATURE_AUDIT_2026-08-27.md",
        "provenance/PAPER1_NOVELTY_CORE_ATTACK_ADDENDUM_2026-08-27.md",
        "provenance/science_v0_2_1_build_summary.json",
        "provenance/science_reference_registry_summary.json",
        "provenance/novelty_framing_v0_3_1_summary.json",
        "provenance/reference_registry_v0_4_summary.json",
        "provenance/submission_v0_8_build_summary.json",
        "provenance/submission_reference_registry_summary.json",
        "provenance/docx_v0_8_summary.json",
        "provenance/registry_gate_summary.json",
        "provenance/supplementary_figure_summary.json",
    ]
    missing = [x for x in required if not (root / x).exists()]
    if missing:
        raise SystemExit(f"v0.8 bundle missing required files: {missing}")
    empty = [x for x in required if (root / x).is_file() and (root / x).stat().st_size == 0]
    if empty:
        raise SystemExit(f"v0.8 bundle has empty required files: {empty}")

    manuscript = (root / "manuscript/PAPER1_AJB_UPLOAD_V0_8.md").read_text(encoding="utf-8")
    forbidden = [
        "Draft v0.2", "Draft v0.3", "Draft v0.3.1", "`data/", "`docs/", "`scripts/",
        "GitHub Actions", "ecological Fig. 6", "paper1_authoritative_results_v0_1", "FigS3_legacy_event_falsification",
        "published coverage was A/F/C/P = 8/4/1/3", "anthocyanin-enrichment probability weakened to 0.140625",
    ]
    retained = [x for x in forbidden if x in manuscript]
    if retained:
        raise SystemExit(f"v0.8 manuscript retains stale/internal tokens: {retained}")

    required_claims = [
        "A/F/C/P coverage = 9/4/1/3",
        "coverage was 5/3/1/2",
        "0.00278854",
        "0.046875",
        "10.1007/s10722-025-02606-6",
        "Candidate-free remeasurement fixed exact-signature recurrence at 0.333",
        "pairwise concordance at **0.75**",
        "strict×dominant shared robust event count was therefore zero",
        "The molecular result should not be read as the first demonstration",
        "observation-method dependence itself a new concept",
        "event instability is not itself a new methodological discovery",
        "The ecological value of the present result is an inferential boundary",
    ]
    absent = [x for x in required_claims if x not in manuscript]
    if absent:
        raise SystemExit(f"v0.8 manuscript lost science/framing claims: {absent}")

    words = abstract_words(manuscript)
    if words != 237:
        raise SystemExit(f"AJB v0.8 abstract word-count drift: expected 237, found {words}")
    for label in ["### Premise of the study", "### Methods", "### Key results", "### Conclusions"]:
        if manuscript.count(label) != 1:
            raise SystemExit(f"structured abstract heading drift: {label}")

    placeholders = [
        "[AUTHOR LIST TO ADD AT SUBMISSION]",
        "[AFFILIATIONS TO ADD AT SUBMISSION]",
        "[CORRESPONDING AUTHOR DETAILS TO ADD AT SUBMISSION]",
        "[ACKNOWLEDGMENTS AND FUNDING TO ADD AT SUBMISSION]",
        "[CRediT AUTHOR CONTRIBUTIONS TO ADD AT SUBMISSION]",
        "[ARCHIVE DOI TO ADD AT SUBMISSION]",
    ]
    bad = {x: manuscript.count(x) for x in placeholders if manuscript.count(x) != 1}
    if bad:
        raise SystemExit(f"submission placeholder count drift: {bad}")

    headings = ["# ACKNOWLEDGMENTS", "# AUTHOR CONTRIBUTIONS", "# DATA AVAILABILITY STATEMENT", "# LITERATURE CITED", "# SUPPORTING INFORMATION", "# FIGURE LEGENDS"]
    positions = [manuscript.index(h) for h in headings]
    if positions != sorted(positions):
        raise SystemExit("AJB v0.8 section order drift")
    for i in range(1, 9):
        if f"Appendix S{i}" not in manuscript:
            raise SystemExit(f"manuscript missing Appendix S{i}")

    registry = read_csv(root / "provenance/paper1_reference_registry_v0_4.csv")
    reg_dois = {norm_doi(r["doi"]) for r in registry if r.get("doi", "").strip()}
    ms_dois = manuscript_dois(manuscript)
    if len(registry) != 22 or len(reg_dois) != 22 or reg_dois != ms_dois:
        raise SystemExit(
            f"v0.4 reference contract drift: rows={len(registry)} reg={len(reg_dois)} ms={len(ms_dois)} "
            f"missing={sorted(reg_dois-ms_dois)} extra={sorted(ms_dois-reg_dois)}"
        )

    s1 = read_csv(root / "appendices/Appendix_S1.csv")
    ids = {r.get("result_id", "") for r in s1}
    if "M07_LITERATURE_AXIS_ASCERTAINMENT" not in ids:
        raise SystemExit("Appendix S1 lacks M07 literature-axis ascertainment result")

    docx_summary = json.loads((root / "provenance/docx_v0_8_summary.json").read_text(encoding="utf-8"))
    if not all(docx_summary.get("structural_checks", {}).values()):
        raise SystemExit("DOCX v0.8 structural checks are not all true")
    if (root / "manuscript/PAPER1_AJB_UPLOAD_V0_8.docx").stat().st_size < 20000:
        raise SystemExit("DOCX v0.8 unexpectedly small")

    science_summary = json.loads((root / "provenance/science_v0_2_1_build_summary.json").read_text(encoding="utf-8"))
    if science_summary.get("candidate_free_recurrence_changed") is not False or science_summary.get("macro_results_changed") is not False:
        raise SystemExit("v0.2.1 change-scope boundary drift")

    files = sorted(p for p in root.rglob("*") if p.is_file() and p != a.out)
    entries = [{"path": str(p.relative_to(root)), "bytes": p.stat().st_size, "sha256": sha256(p)} for p in files]
    manifest = {
        "bundle_version": "v0.8-ajb-upload-paper1-v0.2.1-framing-v0.3.1",
        "source_science_version": "Paper 1 v0.2.1",
        "source_framing_version": "Paper 1 v0.3.1",
        "formal_database_search_run": 33039509237,
        "literature_systems": 11,
        "dependence_clusters": 6,
        "cluster_A_enrichment_p": 0.046875,
        "candidate_free_common_systems": 5,
        "candidate_free_recurrence_changed": False,
        "macro_results_changed": False,
        "n_files": len(entries),
        "main_figures": 6,
        "appendices": 8,
        "reference_registry_rows": 22,
        "abstract_word_count": words,
        "docx_present": True,
        "scientific_update_scope": "literature ascertainment only",
        "status": "bundle audit passed",
        "files": entries,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in manifest.items() if k != "files"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
