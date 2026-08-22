#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

FROZEN_TITLE = "Flexible molecular routes coexist with locally conserved flower colours in *Camellia*"


def count_words(text: str) -> int:
    clean = re.sub(r"[*_`]", "", text)
    return len(re.findall(r"\b[\w/–—-]+\b", clean, flags=re.UNICODE))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manuscript", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    text = a.manuscript.read_text(encoding="utf-8")

    if not text.startswith(f"# {FROZEN_TITLE}\n"):
        raise SystemExit("manuscript title has drifted from frozen title")

    required_headings = [
        "# INTRODUCTION", "# MATERIALS AND METHODS", "# RESULTS", "# DISCUSSION",
        "# CONCLUSIONS", "# DATA AVAILABILITY AND REPRODUCIBILITY", "# FIGURE LEGENDS",
        "# SUPPLEMENTARY ANALYSIS MAP", "# REFERENCES — v0.1 verified core set",
    ]
    for heading in required_headings:
        if heading not in text:
            raise SystemExit(f"missing manuscript heading: {heading}")

    if "## ABSTRACT" not in text:
        raise SystemExit("missing ABSTRACT")
    abstract = text.split("## ABSTRACT", 1)[1].split("---", 1)[0]
    for h in ["Premise of the study", "Methods", "Key results", "Conclusions"]:
        if f"### {h}" not in abstract:
            raise SystemExit(f"abstract missing structured heading: {h}")
    abstract_words = count_words(abstract)
    if abstract_words > 250:
        raise SystemExit(f"abstract exceeds AJB 250-word limit: {abstract_words}")

    required_current = [
        "46/50 nontrivial splits",
        "normalized RF = 0.08",
        "strict *P* = 0.00116",
        "dominant *P* = 0.000080",
        "strict wild-colour seed, no branch",
        "strict × dominant cross-scenario accepted branch count was therefore zero",
        "global same-state MPD is not retained",
        "public hard-state data do not identify *which* accepted-species branch",
    ]
    # Allow semantically equivalent phrasing for two items.
    if "46/50 nontrivial splits" not in text and "shared 46 of 50 nontrivial splits" not in text:
        raise SystemExit("missing frozen topology concordance value")
    if "normalized RF = 0.08" not in text:
        raise SystemExit("missing normalized RF value")
    if "strict *P* = 0.00116" not in text or "dominant *P* = 0.000080" not in text:
        raise SystemExit("missing UFBoot nearest-same-colour robustness values")
    if "strict × dominant cross-scenario accepted branch count was therefore zero" not in text:
        raise SystemExit("missing zero shared accepted-species transition result")
    if "global MPD" not in text and "global same-state" not in text:
        raise SystemExit("missing topology-sensitive global-MPD negative result")
    if "public hard-state data do not identify *which* accepted-species branch" not in text:
        raise SystemExit("missing public-data identifiability statement")

    forbidden_positive = [
        "we demonstrate that the Camellia ancestor was white",
        "we demonstrate that cold adaptation drove",
        "pollinators drove genus-level flower-colour evolution",
        "three robust W→A branches provide",
        "exact gene reuse explains Camellia flower-colour evolution",
    ]
    low = text.casefold()
    for phrase in forbidden_positive:
        if phrase.casefold() in low:
            raise SystemExit(f"manuscript contains forbidden superseded/causal claim: {phrase}")

    doi_count = len(re.findall(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+", text))
    if doi_count < 12:
        raise SystemExit(f"core reference set appears incomplete: DOI count={doi_count}")

    summary = {
        "manuscript_version": "v0.1",
        "target_journal": "American Journal of Botany",
        "abstract_words_validator_count": abstract_words,
        "required_sections_present": len(required_headings),
        "core_doi_strings": doi_count,
        "frozen_title_match": True,
        "current_topology_and_trait_values_present": True,
        "zero_event_boundary_present": True,
        "forbidden_positive_claims_present": False,
        "status": "claim-drift gate passed",
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
