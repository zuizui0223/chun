#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

TITLE = "Flexible molecular routes coexist with locally conserved flower colours in *Camellia*"
HEADINGS = ["Premise of the study", "Methods", "Key results", "Conclusions"]


def count_words(text: str) -> int:
    clean = re.sub(r"[*_`]", "", text)
    return len(re.findall(r"\b[\w/–—-]+\b", clean, flags=re.UNICODE))


def abstract_body(text: str) -> str:
    block = text.split("## ABSTRACT", 1)[1].split("**Key words:**", 1)[0]
    pieces = []
    for i, h in enumerate(HEADINGS):
        marker = f"### {h}"
        if marker not in block:
            raise SystemExit(f"missing AJB abstract heading: {h}")
        after = block.split(marker, 1)[1]
        if i + 1 < len(HEADINGS):
            nxt = f"### {HEADINGS[i + 1]}"
            pieces.append(after.split(nxt, 1)[0])
        else:
            pieces.append(after)
    return " ".join(pieces)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manuscript", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    text = a.manuscript.read_text(encoding="utf-8")

    if not text.startswith(f"# {TITLE}\n"):
        raise SystemExit("frozen title mismatch")
    words = count_words(abstract_body(text))
    if words > 250:
        raise SystemExit(f"AJB abstract exceeds 250 words: {words}")

    required_sections = [
        "# INTRODUCTION", "# MATERIALS AND METHODS", "# RESULTS", "# DISCUSSION",
        "# CONCLUSIONS", "# DATA AVAILABILITY AND REPRODUCIBILITY", "# FIGURE LEGENDS",
        "# SUPPLEMENTARY ANALYSIS MAP", "# LITERATURE CITED",
    ]
    for s in required_sections:
        if s not in text:
            raise SystemExit(f"missing submission section: {s}")

    required_claims = [
        "normalized RF = 0.08",
        "strict *P* = 0.00116",
        "dominant *P* = 0.000080",
        "strict × dominant cross-scenario accepted branch count was therefore zero",
        "public hard-state data do not identify *which* accepted-species branch",
        "geometric mean RR was **3.53**",
        "geometric mean was **2.42**",
        "**5/5** in the expected direction",
        "Five studies across four taxa",
        "reproductive-service filtering",
    ]
    for x in required_claims:
        if x not in text:
            raise SystemExit(f"missing current manuscript claim/value: {x}")
    if "46/50 nontrivial splits" not in text and "46 of 50 nontrivial splits" not in text:
        raise SystemExit("missing topology concordance value")

    forbidden = [
        "Draft v0",
        "# OPEN ITEMS",
        "`data/", "`docs/", "`scripts/", "GitHub Actions", "PR #", "PR#",
        "we demonstrate that the Camellia ancestor was white",
        "pollinators drove genus-level flower-colour evolution",
        "three robust W→A branches provide",
        "red-specific bird syndrome",
    ]
    lower = text.casefold()
    for x in forbidden:
        if x.casefold() in lower:
            raise SystemExit(f"submission manuscript retains forbidden/internal token: {x}")

    if text.count("[ARCHIVE DOI TO ADD AT SUBMISSION]") != 1:
        raise SystemExit("submission manuscript must contain exactly one archive DOI placeholder")
    for token in ["Supplementary Table S1", "Supplementary Table S2", "Supplementary Table S3", "Supplementary Tables S5–S6", "Supplementary Figures S1–S3"]:
        if token not in text:
            raise SystemExit(f"missing formal Supplementary reference: {token}")

    for citation in ["Liu et al., 2025", "Xie et al., 2013", "Yuan et al., 2025", "Kunitake et al., 2004", "Sun et al., 2017"]:
        if citation not in text:
            raise SystemExit(f"missing ecological primary citation: {citation}")

    doi_count = len(re.findall(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+", text))
    if doi_count < 24:
        raise SystemExit(f"unexpectedly sparse Literature Cited DOI count: {doi_count}")

    summary = {
        "submission_version": "v0.3-ecological-v2",
        "target_journal": "American Journal of Botany",
        "abstract_words": words,
        "abstract_limit": 250,
        "core_doi_strings": doi_count,
        "internal_project_tokens_absent": True,
        "current_molecular_macro_ecological_values_present": True,
        "public_data_boundary_present": True,
        "archive_doi_placeholder_count": 1,
        "status": "submission-clean claim/style gate passed",
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
