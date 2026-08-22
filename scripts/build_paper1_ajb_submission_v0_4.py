#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def exact_replace(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {n}")
    return text.replace(old, new, 1)


def apply_ajb_style_corrections(text: str) -> tuple[str, list[str]]:
    corrections = [
        (
            "CITE_ORDER_2026",
            "(Lacey, 2026; Berardi et al., 2026)",
            "(Berardi et al., 2026; Lacey, 2026)",
        ),
        (
            "REF_GENG_FIRST7_ETAL",
            "Geng, F., R. Nie, N. Yang, L. Cai, Y. Hu, S. Chen, X. Cheng, Z. Wang, and L. Chen. 2022.",
            "Geng, F., R. Nie, N. Yang, L. Cai, Y. Hu, S. Chen, X. Cheng, et al. 2022.",
        ),
        (
            "REF_JIANG_FIRST7_ETAL",
            "Jiang, H.-D., D.-J. Zeng, H.-Z. Qin, L.-H. Peng, Y.-S. Yang, Z.-Y. Chen, R. Zou, J.-M. Tang, Y.-S. Jiang, Z.-C. Xiong, et al. 2025.",
            "Jiang, H.-D., D.-J. Zeng, H.-Z. Qin, L.-H. Peng, Y.-S. Yang, Z.-Y. Chen, R. Zou, et al. 2025.",
        ),
        (
            "REF_QU_ALL5",
            "Qu, Y., Z. Ou, Q. Q. Yong, X. Yao, et al. 2024.",
            "Qu, Y., Z. Ou, Q. Q. Yong, X. Yao, and J. Luo. 2024.",
        ),
        (
            "REF_ZAN_FIRST7_ETAL",
            "Zan, T., Y.-T. He, M. Zhang, T. Yonezawa, H. Ma, Q.-M. Zhao, W.-Y. Kuo, W.-J. Zhang, and C.-H. Huang. 2023.",
            "Zan, T., Y.-T. He, M. Zhang, T. Yonezawa, H. Ma, Q.-M. Zhao, W.-Y. Kuo, et al. 2023.",
        ),
        (
            "REF_ZHANG2023_FIRST7_ETAL",
            "Zhang, Q., R. A. Folk, Z.-Q. Mo, H. Ye, Z.-Y. Zhang, H. Peng, J.-L. Zhao, S.-X. Yang, and X.-Q. Yu. 2023.",
            "Zhang, Q., R. A. Folk, Z.-Q. Mo, H. Ye, Z.-Y. Zhang, H. Peng, J.-L. Zhao, et al. 2023.",
        ),
        (
            "FLS_CITATION_ORDER",
            "Primary provenance includes Feng et al. (2024), the public F01 PacBio run `SRR22729450`, the *C. nitidissima* T2T genome, and Zhou et al. (2013).",
            "Primary provenance includes Zhou et al. (2013), Feng et al. (2024), the public F01 PacBio run `SRR22729450`, and the *C. nitidissima* T2T genome.",
        ),
    ]
    applied: list[str] = []
    for label, old, new in corrections:
        text = exact_replace(text, old, new, label)
        applied.append(label)
    return text, applied


def sort_literature_cited(text: str) -> tuple[str, int]:
    marker = "# LITERATURE CITED"
    if marker not in text:
        raise SystemExit("cannot locate LITERATURE CITED for final AJB sort")
    before, refs_text = text.split(marker, 1)
    entries = [x.strip() for x in re.split(r"\n\s*\n", refs_text.strip()) if x.strip()]
    if len(entries) < 20:
        raise SystemExit(f"unexpectedly small AJB Literature Cited block: {len(entries)}")

    def first_author_key(entry: str) -> str:
        clean = re.sub(r"[*_`]", "", entry).strip()
        return clean.split(",", 1)[0].casefold()

    entries = sorted(entries, key=lambda x: (first_author_key(x), re.sub(r"[*_`]", "", x).casefold()))
    return before.rstrip() + "\n\n" + marker + "\n\n" + "\n\n".join(entries) + "\n", len(entries)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--v03", type=Path, required=True)
    ap.add_argument("--appendix-map", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    a = ap.parse_args()

    text = a.v03.read_text(encoding="utf-8")
    appendix_rows = read_csv(a.appendix_map)
    if len(appendix_rows) != 9:
        raise SystemExit(f"expected 9 AJB appendices, found {len(appendix_rows)}")

    data_old = (
        "# DATA AVAILABILITY AND REPRODUCIBILITY\n\n"
        "All source datasets used here are public, and the analysis code, frozen derived-data registries, deterministic figure inputs, and reproducibility metadata are assembled in a versioned release for this study [ARCHIVE DOI TO ADD AT SUBMISSION]. The WFO Plant List 2026-06 taxonomy snapshot is independently archived at Zenodo (doi:10.5281/zenodo.20782718). Public nuclear transcriptomic provenance derives from the Wu et al. (2022) sampling and associated public resources; source-specific molecular, taxonomic, colour, and ecological provenance is reported in Supplementary Tables S2–S4."
    )
    legends = "\n".join(
        f"- **{r['appendix_id']}.** {r['title_or_legend']}" for r in appendix_rows
    )
    data_new = (
        "# DATA AVAILABILITY STATEMENT\n\n"
        "All source datasets used here are public, and the analysis code, frozen derived-data registries, deterministic figure inputs, and reproducibility metadata are assembled in a versioned release for this study [ARCHIVE DOI TO ADD AT SUBMISSION]. The WFO Plant List 2026-06 taxonomy snapshot is independently archived at Zenodo (doi:10.5281/zenodo.20782718). Public nuclear transcriptomic provenance derives from the Wu et al. (2022) sampling and associated public resources; source-specific molecular, taxonomic, colour, and ecological provenance is provided in Appendices S2–S4.\n\n"
        "Additional supporting information may be found online in the Supporting Information section at the end of the article.\n\n"
        + legends
    )
    if text.count(data_old) != 1:
        raise SystemExit("could not uniquely locate v0.3 Data Availability block")
    text = text.replace(data_old, data_new, 1)

    replacements = {
        "Supplementary Table S1": "Appendix S1",
        "Supplementary Table S2": "Appendix S2",
        "Supplementary Table S3": "Appendix S3",
        "Supplementary Tables S2–S4": "Appendices S2–S4",
        "Supplementary Tables S5–S6": "Appendices S5–S6",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    supp_marker = "# SUPPLEMENTARY ANALYSIS MAP"
    lit_marker = "# LITERATURE CITED"
    if supp_marker not in text or lit_marker not in text:
        raise SystemExit("cannot locate Supplementary map / Literature Cited boundaries")
    before = text.split(supp_marker, 1)[0].rstrip()
    after = text.split(lit_marker, 1)[1].lstrip()
    text = before + "\n\n" + lit_marker + "\n\n" + after

    text, style_corrections = apply_ajb_style_corrections(text)
    text, reference_count = sort_literature_cited(text)

    forbidden = [
        "Supplementary Table S1", "Supplementary Table S2", "Supplementary Table S3",
        "Supplementary Tables S2–S4", "Supplementary Tables S5–S6",
        "# SUPPLEMENTARY ANALYSIS MAP",
    ]
    for token in forbidden:
        if token in text:
            raise SystemExit(f"AJB upload manuscript retains old Supporting Information token: {token}")
    required = [
        "# DATA AVAILABILITY STATEMENT",
        "Additional supporting information may be found online in the Supporting Information section at the end of the article.",
        "Appendix S1", "Appendix S2", "Appendix S3", "Appendix S4", "Appendix S5",
        "Appendix S6", "Appendix S7", "Appendix S8", "Appendix S9",
    ]
    for token in required:
        if token not in text:
            raise SystemExit(f"AJB upload manuscript missing required token: {token}")

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(text, encoding="utf-8")
    summary = {
        "submission_version": "v0.4",
        "source_version": "v0.3",
        "appendix_count": len(appendix_rows),
        "data_availability_ajb_statement_present": True,
        "supplementary_map_section_removed": True,
        "ajb_style_corrections": style_corrections,
        "literature_cited_entries": reference_count,
        "literature_cited_resorted_after_bibliographic_corrections": True,
        "scientific_results_changed": False,
        "remaining_placeholder": "[ARCHIVE DOI TO ADD AT SUBMISSION]",
    }
    a.summary.parent.mkdir(parents=True, exist_ok=True)
    a.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
