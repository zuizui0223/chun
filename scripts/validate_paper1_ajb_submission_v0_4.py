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


def abstract_words(text: str) -> int:
    block = text.split("## ABSTRACT", 1)[1].split("**Key words:**", 1)[0]
    pieces = []
    for i, h in enumerate(HEADINGS):
        marker = f"### {h}"
        if marker not in block:
            raise SystemExit(f"missing AJB abstract heading {h}")
        after = block.split(marker, 1)[1]
        if i + 1 < len(HEADINGS):
            pieces.append(after.split(f"### {HEADINGS[i+1]}", 1)[0])
        else:
            pieces.append(after)
    return count_words(" ".join(pieces))


def literature_entries(text: str) -> list[str]:
    marker = "# LITERATURE CITED"
    if marker not in text:
        raise SystemExit("LITERATURE CITED missing")
    refs = text.split(marker, 1)[1].strip()
    entries = [x.strip() for x in re.split(r"\n\s*\n", refs) if x.strip()]
    if len(entries) < 20:
        raise SystemExit(f"unexpectedly small Literature Cited: {len(entries)}")
    return entries


def first_author_key(entry: str) -> str:
    clean = re.sub(r"[*_`]", "", entry).strip()
    return clean.split(",", 1)[0].casefold()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manuscript", type=Path, required=True)
    ap.add_argument("--appendix-map", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--submission-version", default="v0.4")
    ap.add_argument("--require-ecology-v2", action="store_true")
    a = ap.parse_args()
    text = a.manuscript.read_text(encoding="utf-8")

    if not text.startswith(f"# {TITLE}\n"):
        raise SystemExit("frozen title mismatch")
    words = abstract_words(text)
    if words > 250:
        raise SystemExit(f"AJB abstract exceeds 250 words: {words}")

    required_sections = [
        "# INTRODUCTION", "# MATERIALS AND METHODS", "# RESULTS", "# DISCUSSION",
        "# CONCLUSIONS", "# DATA AVAILABILITY STATEMENT", "# FIGURE LEGENDS", "# LITERATURE CITED",
    ]
    for s in required_sections:
        if s not in text:
            raise SystemExit(f"missing AJB manuscript section: {s}")
    if "# SUPPLEMENTARY ANALYSIS MAP" in text:
        raise SystemExit("internal Supplementary map section remains in upload manuscript")

    exact_statement = "Additional supporting information may be found online in the Supporting Information section at the end of the article."
    if exact_statement not in text:
        raise SystemExit("AJB Supporting Information statement missing")
    for i in range(1, 10):
        if f"Appendix S{i}" not in text:
            raise SystemExit(f"Appendix S{i} missing from manuscript")
    if text.count("[ARCHIVE DOI TO ADD AT SUBMISSION]") != 1:
        raise SystemExit("expected exactly one archive DOI placeholder")

    required_claims = [
        "46 of 50 nontrivial splits", "normalized RF = 0.08", "strict *P* = 0.00116",
        "dominant *P* = 0.000080", "strict × dominant cross-scenario accepted branch count was therefore zero",
        "Berruti et al. (2015)", "Geng et al., 2022", "Qu et al., 2024",
        "World Flora Online Consortium, 2026", "Wickramaratne and Vitarana, 1985",
        "Berardi et al., 2026; Lacey, 2026",
    ]
    for x in required_claims:
        if x not in text:
            raise SystemExit(f"missing frozen claim/citation: {x}")
    if a.require_ecology_v2:
        ecological_claims = [
            "geometric mean RR was **3.53**",
            "geometric mean was **2.42**",
            "(**5/5** in the expected direction",
            "Five studies across four taxa",
            "no accepted-species colour-transition branch was robust to both strict and dominant",
            "direct abiotic evidence for petal pigment deployment remained sparse",
        ]
        for claim in ecological_claims:
            if claim not in text:
                raise SystemExit(f"missing ecological-v2 claim: {claim}")

    required_reference_forms = [
        "Berruti, A., A. Christiaens, E. De Keyser, M.-C. Van Labeke, and V. Scariot. 2015.",
        "Geng, F., R. Nie, N. Yang, L. Cai, Y. Hu, S. Chen, X. Cheng, et al. 2022.",
        "Jiang, H.-D., D.-J. Zeng, H.-Z. Qin, L.-H. Peng, Y.-S. Yang, Z.-Y. Chen, R. Zou, et al. 2025.",
        "Qu, Y., Z. Ou, Q. Q. Yong, X. Yao, and J. Luo. 2024.",
        "Zan, T., Y.-T. He, M. Zhang, T. Yonezawa, H. Ma, Q.-M. Zhao, W.-Y. Kuo, et al. 2023.",
        "Zhang, Q., R. A. Folk, Z.-Q. Mo, H. Ye, Z.-Y. Zhang, H. Peng, J.-L. Zhao, et al. 2023.",
    ]
    for x in required_reference_forms:
        if x not in text:
            raise SystemExit(f"missing AJB-style reference form: {x}")

    forbidden = [
        "Larcher et al. (2015)", "Larcher, R., et al. 2015.", "Draft v0", "# OPEN ITEMS",
        "`data/", "`docs/", "`scripts/", "GitHub Actions", "PR #", "PR#",
        "Lacey, 2026; Berardi et al., 2026",
        "Geng, F., R. Nie, N. Yang, L. Cai, Y. Hu, S. Chen, X. Cheng, Z. Wang, and L. Chen. 2022.",
        "Jiang, H.-D., D.-J. Zeng, H.-Z. Qin, L.-H. Peng, Y.-S. Yang, Z.-Y. Chen, R. Zou, J.-M. Tang,",
        "Qu, Y., Z. Ou, Q. Q. Yong, X. Yao, et al. 2024.",
        "Zan, T., Y.-T. He, M. Zhang, T. Yonezawa, H. Ma, Q.-M. Zhao, W.-Y. Kuo, W.-J. Zhang,",
        "Zhang, Q., R. A. Folk, Z.-Q. Mo, H. Ye, Z.-Y. Zhang, H. Peng, J.-L. Zhao, S.-X. Yang,",
    ]
    for x in forbidden:
        if x in text:
            raise SystemExit(f"upload manuscript retains stale/internal/style token: {x}")

    entries = literature_entries(text)
    keys = [first_author_key(x) for x in entries]
    if keys != sorted(keys):
        raise SystemExit(f"Literature Cited is not alphabetized by first author: {keys}")
    if not (keys.index("berardi") < keys.index("berruti") < keys.index("chai")):
        raise SystemExit("Berruti reference is not correctly placed after Berardi and before Chai")

    appendix_rows = [line for line in a.appendix_map.read_text(encoding="utf-8").splitlines()[1:] if line.strip()]
    if len(appendix_rows) != 9:
        raise SystemExit("AJB appendix mapping does not contain 9 entries")

    summary = {
        "submission_version": a.submission_version,
        "target_journal": "American Journal of Botany",
        "abstract_words": words,
        "appendix_count": 9,
        "literature_cited_entries": len(entries),
        "literature_cited_alphabetized": True,
        "ajb_long_author_rule_gate": True,
        "same_year_in_text_order_gate": True,
        "ajb_supporting_information_statement": True,
        "archive_doi_placeholder_count": 1,
        "bibliographic_correction_gate": True,
        "internal_project_tokens_absent": True,
        "scientific_results_changed": False,
        "ecological_v2_claim_gate": a.require_ecology_v2,
        "status": "AJB upload-format and reference-style gate passed",
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
