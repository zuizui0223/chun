#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def figure_legends(rows: list[dict[str, str]]) -> str:
    main = [r for r in rows if r.get("manuscript_status", "").strip() == "main"]
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in main:
        grouped[row["figure_id"].strip()].append(row)
    expected = [f"Fig{i}" for i in range(1, 7)]
    if sorted(grouped) != expected:
        raise SystemExit(f"expected main Fig1..Fig6, found {sorted(grouped)}")
    blocks: list[str] = []
    for i in range(1, 7):
        fid = f"Fig{i}"
        panels = sorted(grouped[fid], key=lambda r: r.get("panel_id", ""))
        parts = []
        for panel in panels:
            pid = panel.get("panel_id", "").strip()
            title = panel.get("panel_title", "").strip().rstrip(".")
            parts.append(f"({pid}) {title}")
        blocks.append(f"**Figure {i}.** " + "; ".join(parts) + ".")
    return "\n\n".join(blocks)


def supporting_information(rows: list[dict[str, str]]) -> str:
    if len(rows) != 8:
        raise SystemExit(f"expected 8 current appendices, found {len(rows)}")
    expected = [f"Appendix S{i}" for i in range(1, 9)]
    observed = [r.get("appendix_id", "").strip() for r in rows]
    if observed != expected:
        raise SystemExit(f"appendix order mismatch: {observed}")
    return "\n".join(
        f"- **{row['appendix_id']}.** {row['title_or_legend'].strip()}"
        for row in rows
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--appendix-map", type=Path, required=True)
    ap.add_argument("--figure-manifest", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    a = ap.parse_args()

    text = a.source.read_text(encoding="utf-8")
    appendix_rows = read_csv(a.appendix_map)
    figure_rows = read_csv(a.figure_manifest)

    expected_title = "# Repeated flower-colour change does not imply repeated pigment-state packages in *Camellia*"
    if not text.startswith(expected_title):
        raise SystemExit("current v0.2 manuscript title contract changed")

    draft_lines = [line for line in text.splitlines() if line.startswith("> Draft v0.2.")]
    if len(draft_lines) != 1:
        raise SystemExit(f"expected one v0.2 governance banner, found {len(draft_lines)}")
    text = text.replace(draft_lines[0] + "\n\n", "", 1)

    old_registry = (
        "The current result set is frozen in `data/paper1_authoritative_results_v0_2.csv`; "
        "Main and Supplement figure roles are frozen in `data/paper1_main_figure_manifest_v0_2.csv`. "
        "Superseded analyses remain in repository history but do not re-enter positive claims."
    )
    new_registry = (
        "The result hierarchy and figure dependencies were frozen before submission. "
        "Analyses superseded by later observation, trait, taxonomy, or topology audits were retained "
        "for reproducibility but were not allowed to re-enter positive claims (Appendix S1)."
    )
    if text.count(old_registry) != 1:
        raise SystemExit("could not uniquely locate internal result-registry sentence")
    text = text.replace(old_registry, new_registry, 1)

    data_marker = "# DATA AVAILABILITY AND REPRODUCIBILITY"
    lit_marker = "# LITERATURE CITED"
    if text.count(data_marker) != 1 or text.count(lit_marker) != 1:
        raise SystemExit("could not uniquely locate data-availability / literature boundaries")
    before = text.split(data_marker, 1)[0].rstrip()
    refs = text.split(lit_marker, 1)[1].lstrip()

    data_block = (
        "# DATA AVAILABILITY STATEMENT\n\n"
        "All source datasets used in this study are public. Analysis code, frozen derived-data "
        "registries, deterministic figure inputs, and reproducibility metadata will be archived as "
        "a versioned release [ARCHIVE DOI TO ADD AT SUBMISSION]. The June 2026 World Flora Online "
        "Plant List snapshot used for taxonomy normalization is independently archived at Zenodo "
        "(doi:10.5281/zenodo.20782718). Public sequence accessions and source-level provenance are "
        "retained in the archived release and Supporting Information.\n\n"
        "# SUPPORTING INFORMATION\n\n"
        + supporting_information(appendix_rows)
        + "\n\n# FIGURE LEGENDS\n\n"
        + figure_legends(figure_rows)
    )
    text = before + "\n\n" + data_block + "\n\n" + lit_marker + "\n\n" + refs

    running = "**Running head:** Modular recurrence and flower-colour realization"
    front = (
        running
        + "\n\n**Authors:** [AUTHOR LIST TO ADD AT SUBMISSION]"
        + "\n\n**Affiliations:** [AFFILIATIONS TO ADD AT SUBMISSION]"
        + "\n\n**Corresponding author:** [CORRESPONDING AUTHOR DETAILS TO ADD AT SUBMISSION]"
    )
    if text.count(running) != 1:
        raise SystemExit("running-head contract changed")
    text = text.replace(running, front, 1)

    forbidden = [
        "Draft v0.2",
        "`data/",
        "`docs/",
        "`scripts/",
        "GitHub Actions",
        "current manuscript consumes",
        "current result set is frozen",
        "ecological Fig. 6",
        "ECOLOGICAL Fig. 6",
    ]
    retained = [token for token in forbidden if token in text]
    if retained:
        raise SystemExit(f"submission output retains internal/stale tokens: {retained}")

    required = [
        "Candidate-free remeasurement fixed exact-signature recurrence at 0.333",
        "pairwise concordance at 0.75",
        "strict×dominant shared robust event count was therefore zero",
        "# DATA AVAILABILITY STATEMENT",
        "# SUPPORTING INFORMATION",
        "# FIGURE LEGENDS",
        "Appendix S8",
        "Figure 6",
        "[ARCHIVE DOI TO ADD AT SUBMISSION]",
    ]
    missing = [token for token in required if token not in text]
    if missing:
        raise SystemExit(f"submission output missing frozen v0.2 tokens: {missing}")
    if text.count("[ARCHIVE DOI TO ADD AT SUBMISSION]") != 1:
        raise SystemExit("expected exactly one archive DOI placeholder")

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(text.rstrip() + "\n", encoding="utf-8")
    summary = {
        "submission_version": "v0.6",
        "source_manuscript": str(a.source),
        "source_science_version": "Paper 1 v0.2",
        "appendix_count": len(appendix_rows),
        "main_figure_count": 6,
        "scientific_results_changed": False,
        "internal_repository_tokens_absent": True,
        "obsolete_ecological_fig6_absent": True,
        "remaining_human_inputs": [
            "author list/order",
            "affiliations",
            "corresponding-author details",
            "contributions/funding/acknowledgments/conflict statement as required",
            "archive DOI",
        ],
        "status": "submission-clean Paper 1 v0.6 manuscript built from current v0.2 source",
    }
    a.summary.parent.mkdir(parents=True, exist_ok=True)
    a.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
