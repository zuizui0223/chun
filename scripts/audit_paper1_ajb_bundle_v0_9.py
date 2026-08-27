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
    return re.sub(r"^https?://(?:dx\.)?doi\.org/", "", x.strip().lower().rstrip(".,;)"))


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
        "manuscript/PAPER1_AJB_UPLOAD_V0_9.md",
        "manuscript/PAPER1_AJB_UPLOAD_V0_9.docx",
        *[f"main_figures/Figure_{i}.{ext}" for i in range(1, 7) for ext in ("png", "svg")],
        *[f"appendices/Appendix_S{i}.csv" for i in range(1, 7)],
        "appendices/Appendix_S7.png",
        "appendices/Appendix_S8.png",
        "provenance/paper1_authoritative_results_v0_2_2.csv",
        "provenance/paper1_main_figure_manifest_v0_2_2.csv",
        "provenance/paper1_fig1_observation_contract_v0_2_2.csv",
        "provenance/paper1_reference_registry_v0_2_2.csv",
        "provenance/paper1_reference_registry_v0_5.csv",
        "provenance/paper1_ajb_appendix_mapping_v0_5.csv",
        "provenance/paper1_bibliographic_db_queries_v0_1.csv",
        "provenance/paper1_bibliographic_priority_screen_v0_1.csv",
        "provenance/paper1_citation_chase_seeds_v0_1.csv",
        "provenance/paper1_citation_chase_priority_screen_v0_1.csv",
        "provenance/PAPER1_SCIENCE_V0_2_2.md",
        "provenance/PAPER1_TEMPORAL_FRAMING_V0_3_2.md",
        "provenance/PAPER1_LUO2016_LITERATURE_RECHECK_RESULT.md",
        "provenance/PAPER1_BIBLIOGRAPHIC_DB_SEARCH_2026-08-27.md",
        "provenance/PAPER1_CITATION_CHASE_SCREEN_2026-08-27.md",
        "provenance/PAPER1_LITERATURE_COVERAGE_AUDIT_2026-08-27.md",
        "provenance/PAPER1_NOVELTY_LITERATURE_AUDIT_2026-08-27.md",
        "provenance/PAPER1_NOVELTY_CORE_ATTACK_ADDENDUM_2026-08-27.md",
        "provenance/FLOWER_COLOUR_VARIATION_TEMPORAL_PROGRAM.md",
        "provenance/science_v0_2_2_build_summary.json",
        "provenance/science_reference_registry_summary.json",
        "provenance/temporal_framing_v0_3_2_summary.json",
        "provenance/reference_registry_v0_5_summary.json",
        "provenance/submission_v0_9_build_summary.json",
        "provenance/submission_reference_registry_summary.json",
        "provenance/docx_v0_9_summary.json",
        "provenance/registry_gate_summary.json",
        "provenance/supplementary_figure_summary.json",
    ]
    missing = [x for x in required if not (root / x).exists()]
    if missing:
        raise SystemExit(f"v0.9 bundle missing required files: {missing}")
    empty = [x for x in required if (root / x).is_file() and (root / x).stat().st_size == 0]
    if empty:
        raise SystemExit(f"v0.9 bundle has empty required files: {empty}")

    manuscript = (root / "manuscript/PAPER1_AJB_UPLOAD_V0_9.md").read_text(encoding="utf-8")
    forbidden = [
        "Draft v0.2", "Draft v0.3", "Draft v0.3.2", "`data/", "`docs/", "`scripts/", "GitHub Actions",
        "A/F/C/P coverage = 9/4/1/3", "coverage was 5/3/1/2",
        "anthocyanin-axis ascertainment remained enriched after dependence collapse",
        "published coverage was A/F/C/P = 8/4/1/3", "ecological Fig. 6",
    ]
    retained = [x for x in forbidden if x in manuscript]
    if retained:
        raise SystemExit(f"v0.9 manuscript retains stale/internal tokens: {retained}")

    required_claims = [
        "Repeated generation of flower-colour states does not replay one pigment-state programme",
        "repeated generation with partial mechanistic replay",
        "P=0.078125",
        "0.333–1.0",
        "0.333–0.5",
        "0.25–1.0",
        "10.3389/fpls.2015.01257",
        "10.1016/j.phytochem.2022.113559",
        "10.3732/ajb.1600428",
        "The strict×dominant shared robust event count was therefore zero",
    ]
    absent = [x for x in required_claims if x not in manuscript]
    if absent:
        raise SystemExit(f"v0.9 manuscript lost temporal/science claims: {absent}")

    words = abstract_words(manuscript)
    if words != 221:
        raise SystemExit(f"AJB v0.9 abstract word-count drift: expected 221, found {words}")
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
        raise SystemExit("AJB v0.9 section order drift")
    for i in range(1, 9):
        if f"Appendix S{i}" not in manuscript:
            raise SystemExit(f"manuscript missing Appendix S{i}")

    registry = read_csv(root / "provenance/paper1_reference_registry_v0_5.csv")
    reg_dois = {norm_doi(r["doi"]) for r in registry if r.get("doi", "").strip()}
    ms_dois = manuscript_dois(manuscript)
    if len(registry) != 25 or len(reg_dois) != 25 or reg_dois != ms_dois:
        raise SystemExit(
            f"v0.5 reference contract drift: rows={len(registry)} reg={len(reg_dois)} ms={len(ms_dois)} "
            f"missing={sorted(reg_dois-ms_dois)} extra={sorted(ms_dois-reg_dois)}"
        )

    s1 = read_csv(root / "appendices/Appendix_S1.csv")
    ids = {r.get("result_id", "") for r in s1}
    if "M07_LITERATURE_AXIS_ASCERTAINMENT" not in ids:
        raise SystemExit("Appendix S1 lacks M07")
    s3 = read_csv(root / "appendices/Appendix_S3.csv")
    anth_pair = [r for r in s3 if r["transition_class"] == "anthocyanin_gain" and r["regime"] == "literature" and r["metric"] == "pairwise_axis_concordance"]
    if len(anth_pair) != 1 or abs(float(anth_pair[0]["minimum"]) - 1/3) > 1e-9:
        raise SystemExit("Appendix S3 lacks Luo-updated anthocyanin pairwise lower bound")
    s4 = read_csv(root / "appendices/Appendix_S4.csv")
    anth_overlap = [r for r in s4 if r["transition_class"] == "anthocyanin_gain"]
    if len(anth_overlap) != 1 or anth_overlap[0]["n_comparable_resolved_cells"] != "6" or anth_overlap[0]["n_agree"] != "2":
        raise SystemExit("Appendix S4 lacks Luo-updated 2/6 overlap")

    docx_summary = json.loads((root / "provenance/docx_v0_9_summary.json").read_text(encoding="utf-8"))
    if not all(docx_summary.get("structural_checks", {}).values()):
        raise SystemExit("DOCX v0.9 structural checks are not all true")
    if (root / "manuscript/PAPER1_AJB_UPLOAD_V0_9.docx").stat().st_size < 20000:
        raise SystemExit("DOCX v0.9 unexpectedly small")

    science_summary = json.loads((root / "provenance/science_v0_2_2_build_summary.json").read_text(encoding="utf-8"))
    if science_summary.get("candidate_free_recurrence_changed") is not False or science_summary.get("yellow_changed") is not False or science_summary.get("macro_results_changed") is not False:
        raise SystemExit("v0.2.2 change-scope boundary drift")
    framing_summary = json.loads((root / "provenance/temporal_framing_v0_3_2_summary.json").read_text(encoding="utf-8"))
    if framing_summary.get("scientific_results_changed_by_framing") is not False:
        raise SystemExit("temporal framing changed science flag")

    files = sorted(p for p in root.rglob("*") if p.is_file() and p != a.out)
    entries = [{"path": str(p.relative_to(root)), "bytes": p.stat().st_size, "sha256": sha256(p)} for p in files]
    manifest = {
        "bundle_version": "v0.9-ajb-upload-paper1-v0.2.2-temporal-v0.3.2",
        "source_science_version": "Paper 1 v0.2.2",
        "source_framing_version": "Paper 1 v0.3.2 temporal framing",
        "biological_headline": "repeated generation through evolutionary time and partial mechanistic replay",
        "literature_systems": 12,
        "dependence_clusters": 6,
        "cluster_A_enrichment_p": 0.078125,
        "candidate_free_common_systems": 5,
        "candidate_free_recurrence_changed": False,
        "yellow_changed": False,
        "macro_results_changed": False,
        "n_files": len(entries),
        "main_figures": 6,
        "appendices": 8,
        "reference_registry_rows": 25,
        "abstract_word_count": words,
        "docx_present": True,
        "status": "bundle audit passed",
        "files": entries,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in manifest.items() if k != "files"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
