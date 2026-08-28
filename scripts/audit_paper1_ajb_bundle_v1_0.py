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
        "manuscript/PAPER1_AJB_UPLOAD_V1_0.md",
        "manuscript/PAPER1_AJB_UPLOAD_V1_0.docx",
        "submission/PAPER1_AJB_V1_0_COVER_LETTER_TEMPLATE.md",
        "submission/PAPER1_AJB_V1_0_SUBMISSION_CHECKLIST.md",
        *[f"main_figures/Figure_{i}.{ext}" for i in range(1, 7) for ext in ("png", "svg")],
        *[f"appendices/Appendix_S{i}.csv" for i in range(1, 7)],
        "appendices/Appendix_S7.png",
        "appendices/Appendix_S8.png",
        "provenance/PAPER1_SCIENCE_V0_2_2.md",
        "provenance/PAPER1_NOVELTY_FRAMING_V0_3_4.md",
        "provenance/PAPER1_STATE_IDENTITY_FRAMING_GATE_V0_1.md",
        "provenance/PAPER1_JOURNAL_STRATEGY.md",
        "provenance/paper1_authoritative_results_v0_2_2.csv",
        "provenance/paper1_main_figure_manifest_v0_2_2.csv",
        "provenance/paper1_reference_registry_v0_5.csv",
        "provenance/science_v0_2_2_build_summary.json",
        "provenance/novelty_framing_v0_3_4_summary.json",
        "provenance/submission_v1_0_build_summary.json",
        "provenance/submission_reference_registry_v1_0_summary.json",
        "provenance/docx_v1_0_summary.json",
        "provenance/registry_gate_summary.json",
    ]
    missing = [x for x in required if not (root / x).exists()]
    if missing:
        raise SystemExit(f"v1.0 bundle missing required files: {missing}")
    empty = [x for x in required if (root / x).is_file() and (root / x).stat().st_size == 0]
    if empty:
        raise SystemExit(f"v1.0 bundle has empty required files: {empty}")

    stale_submission_files = [
        "manuscript/PAPER1_AJB_UPLOAD_V0_9.md",
        "manuscript/PAPER1_AJB_UPLOAD_V0_9.docx",
        "provenance/PAPER1_NOVELTY_FRAMING_V0_3_3.md",
        "provenance/novelty_framing_v0_3_3_summary.json",
        "submission/PAPER1_AJB_V0_9_COVER_LETTER_TEMPLATE.md",
        "submission/PAPER1_AJB_V0_9_SUBMISSION_CHECKLIST.md",
    ]
    stale_present = [x for x in stale_submission_files if (root / x).exists()]
    if stale_present:
        raise SystemExit(f"v1.0 bundle retained stale submission/framing files: {stale_present}")

    manuscript = (root / "manuscript/PAPER1_AJB_UPLOAD_V1_0.md").read_text(encoding="utf-8")
    required_claims = [
        "Hierarchical molecular repeatability coexists with local flower-colour conservatism",
        "annotation-driven, outcome-independent quantification within these prespecified modules",
        "not direct macroevolutionary branch events",
        "hierarchical rather than all-or-none",
        "matched inferential audit across scales",
        "not an event-for-event matching of RNA-seq contrasts to reconstructed branches",
        "not a direct observation of independent evolutionary origins",
        "0.333–1.0",
        "0.333–0.5",
        "0.25–1.0",
        "P=0.078125",
        "agreement remained only two",
        "The strict×dominant shared robust event count was therefore zero",
    ]
    absent = [x for x in required_claims if x not in manuscript]
    if absent:
        raise SystemExit(f"v1.0 manuscript lost v0.3.4 boundary/science claims: {absent}")

    forbidden = [
        "Draft v0.2", "Draft v0.3", "Draft v0.3.2", "Draft v0.3.3", "Draft v0.3.4",
        "`data/", "`docs/", "`scripts/", "GitHub Actions",
        "first demonstration that repeated flower colour", "first pathway-level", "first micro-to-macro",
        "anthocyanin-axis ascertainment remained enriched after dependence collapse",
        "ecological Fig. 6",
        "# Standardized remeasurement reveals partial mechanistic replay during repeated flower-colour evolution",
    ]
    retained = [x for x in forbidden if x in manuscript]
    if retained:
        raise SystemExit(f"v1.0 manuscript retains stale/internal/overclaim tokens: {retained}")

    gate = (root / "provenance/PAPER1_STATE_IDENTITY_FRAMING_GATE_V0_1.md").read_text(encoding="utf-8")
    strategy = (root / "provenance/PAPER1_JOURNAL_STRATEGY.md").read_text(encoding="utf-8")
    cover = (root / "submission/PAPER1_AJB_V1_0_COVER_LETTER_TEMPLATE.md").read_text(encoding="utf-8")
    checklist = (root / "submission/PAPER1_AJB_V1_0_SUBMISSION_CHECKLIST.md").read_text(encoding="utf-8")
    companion_contract = {
        "state-identity gate": (
            gate,
            [
                "Decision: wording-only pass",
                "zero have complete defensible A/F/C/P states",
                "does not yield a genuinely new quantified state-resolution result",
                "American Journal of Botany v1.0 route",
            ],
        ),
        "journal strategy": (
            strategy,
            [
                "Primary submission: American Journal of Botany (AJB), v1.0 route",
                "Do not reopen the first-submission decision for *Evolution*",
                "0/53 have complete defensible A/F/C/P states",
                "Resume Issue #85",
            ],
        ),
        "cover letter": (
            cover,
            [
                "Hierarchical molecular repeatability coexists with local flower-colour conservatism",
                "what remains equivalent as molecular observation and historical identification become stricter",
                "not treated as independent macroevolutionary origins",
                "[ARCHIVE DOI TO ADD AT SUBMISSION]",
            ],
        ),
        "submission checklist": (
            checklist,
            [
                "science v0.2.2 + framing v0.3.4 + AJB bundle v1.0",
                "State-identity gate: wording-only; no new quantified result; AJB locked",
                "shared strict-by-dominant robust events = 0",
                "repository runner had no LibreOffice/Word renderer",
                "final visual approval of the metadata-complete Word/submission PDF",
            ],
        ),
    }
    companion_missing = {
        label: [token for token in tokens if token not in text]
        for label, (text, tokens) in companion_contract.items()
        if any(token not in text for token in tokens)
    }
    if companion_missing:
        raise SystemExit(f"v1.0 submission companion contract drift: {companion_missing}")

    words = abstract_words(manuscript)
    if words > 250:
        raise SystemExit(f"AJB v1.0 abstract exceeds 250 words: {words}")
    for label in ["### Premise of the study", "### Methods", "### Key results", "### Conclusions"]:
        if manuscript.count(label) != 1:
            raise SystemExit(f"structured abstract heading drift: {label}")

    registry = read_csv(root / "provenance/paper1_reference_registry_v0_5.csv")
    reg_dois = {norm_doi(r["doi"]) for r in registry if r.get("doi", "").strip()}
    ms_dois = manuscript_dois(manuscript)
    if len(registry) != 25 or len(reg_dois) != 25 or reg_dois != ms_dois:
        raise SystemExit(
            f"v0.5 reference contract drift: rows={len(registry)} reg={len(reg_dois)} ms={len(ms_dois)} "
            f"missing={sorted(reg_dois-ms_dois)} extra={sorted(ms_dois-reg_dois)}"
        )

    s3 = read_csv(root / "appendices/Appendix_S3.csv")
    anth_pair = [r for r in s3 if r["transition_class"] == "anthocyanin_gain" and r["regime"] == "literature" and r["metric"] == "pairwise_axis_concordance"]
    if len(anth_pair) != 1 or abs(float(anth_pair[0]["minimum"]) - 1/3) > 1e-9:
        raise SystemExit("Appendix S3 lacks Luo-updated anthocyanin pairwise lower bound")
    s4 = read_csv(root / "appendices/Appendix_S4.csv")
    anth_overlap = [r for r in s4 if r["transition_class"] == "anthocyanin_gain"]
    if len(anth_overlap) != 1 or anth_overlap[0]["n_comparable_resolved_cells"] != "6" or anth_overlap[0]["n_agree"] != "2":
        raise SystemExit("Appendix S4 lacks Luo-updated 2/6 overlap")

    docx_summary = json.loads((root / "provenance/docx_v1_0_summary.json").read_text(encoding="utf-8"))
    if not all(docx_summary.get("structural_checks", {}).values()):
        raise SystemExit("DOCX v1.0 structural checks are not all true")
    expected_docx_format = {
        "font": "Times New Roman 12 pt body",
        "line_spacing": "double",
        "alignment": "left",
        "margins_inches": 1.0,
        "continuous_line_numbering": True,
        "sequential_page_numbering": True,
    }
    docx_drift = {
        key: {"expected": expected, "actual": docx_summary.get(key)}
        for key, expected in expected_docx_format.items()
        if docx_summary.get(key) != expected
    }
    if docx_drift:
        raise SystemExit(f"DOCX v1.0 formatting contract drift: {docx_drift}")
    if (root / "manuscript/PAPER1_AJB_UPLOAD_V1_0.docx").stat().st_size < 20000:
        raise SystemExit("DOCX v1.0 unexpectedly small")

    science_summary = json.loads((root / "provenance/science_v0_2_2_build_summary.json").read_text(encoding="utf-8"))
    if science_summary.get("candidate_free_recurrence_changed") is not False or science_summary.get("yellow_changed") is not False or science_summary.get("macro_results_changed") is not False:
        raise SystemExit("v0.2.2 change-scope boundary drift")
    framing_summary = json.loads((root / "provenance/novelty_framing_v0_3_4_summary.json").read_text(encoding="utf-8"))
    if framing_summary.get("scientific_estimates_changed") is not False:
        raise SystemExit("v0.3.4 framing altered frozen scientific estimates")
    if framing_summary.get("event_boundary_clarified") is not True or framing_summary.get("candidate_free_definition_clarified") is not True or framing_summary.get("hierarchical_repeatability_headline") is not True:
        raise SystemExit("v0.3.4 framing boundary flags are incomplete")

    submission_summary = json.loads((root / "provenance/submission_v1_0_build_summary.json").read_text(encoding="utf-8"))
    if submission_summary.get("event_boundary_clarified") is not True or submission_summary.get("candidate_free_definition_clarified") is not True:
        raise SystemExit("submission v1.0 did not preserve v0.3.4 boundary flags")

    files = sorted(p for p in root.rglob("*") if p.is_file() and p != a.out)
    entries = [{"path": str(p.relative_to(root)), "bytes": p.stat().st_size, "sha256": sha256(p)} for p in files]
    manifest = {
        "bundle_version": "v1.0-ajb-upload-paper1-v0.2.2-framing-v0.3.4",
        "source_science_version": "Paper 1 v0.2.2",
        "source_framing_version": "Paper 1 v0.3.4 event-boundary-safe novelty framing",
        "novelty_headline": "hierarchical transition-class-dependent molecular repeatability plus separate macro pattern/event identity",
        "state_identity_gate_decision": "wording-only; no new quantified joint state-resolution result",
        "journal_lock": "American Journal of Botany",
        "event_boundary_clarified": True,
        "candidate_free_definition_clarified": True,
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
