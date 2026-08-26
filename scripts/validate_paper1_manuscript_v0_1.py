#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

FROZEN_TITLE = "Flexible molecular routes coexist with locally conserved flower colours in *Camellia*"
ABSTRACT_HEADINGS = ["Premise of the study", "Methods", "Key results", "Conclusions"]


def count_words(text: str) -> int:
    clean = re.sub(r"[*_`]", "", text)
    return len(re.findall(r"\b[\w/–—-]+\b", clean, flags=re.UNICODE))


def abstract_body(text: str) -> str:
    if "## ABSTRACT" not in text:
        raise SystemExit("missing ABSTRACT")
    block = text.split("## ABSTRACT", 1)[1].split("**Key words:**", 1)[0]
    pieces = []
    for i, heading in enumerate(ABSTRACT_HEADINGS):
        marker = f"### {heading}"
        if marker not in block:
            raise SystemExit(f"abstract missing structured heading: {heading}")
        after = block.split(marker, 1)[1]
        if i + 1 < len(ABSTRACT_HEADINGS):
            next_marker = f"### {ABSTRACT_HEADINGS[i + 1]}"
            if next_marker not in after:
                raise SystemExit(f"abstract missing next structured heading: {ABSTRACT_HEADINGS[i + 1]}")
            pieces.append(after.split(next_marker, 1)[0])
        else:
            pieces.append(after)
    return " ".join(pieces)


def require_any(text: str, choices: list[str], label: str) -> None:
    if not any(x in text for x in choices):
        raise SystemExit(f"missing {label}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manuscript", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--max-abstract-words", type=int, default=250)
    ap.add_argument("--version-label", default="submission_candidate")
    ap.add_argument("--require-ecology-v2", action="store_true")
    a = ap.parse_args()
    text = a.manuscript.read_text(encoding="utf-8")

    if not text.startswith(f"# {FROZEN_TITLE}\n"):
        raise SystemExit("manuscript title has drifted from frozen title")

    required_headings = [
        "# INTRODUCTION", "# MATERIALS AND METHODS", "# RESULTS", "# DISCUSSION",
        "# CONCLUSIONS", "# DATA AVAILABILITY AND REPRODUCIBILITY", "# FIGURE LEGENDS",
        "# SUPPLEMENTARY ANALYSIS MAP",
    ]
    for heading in required_headings:
        if heading not in text:
            raise SystemExit(f"missing manuscript heading: {heading}")
    if not re.search(r"^# REFERENCES — v0\.[12] verified core set$", text, flags=re.MULTILINE):
        raise SystemExit("missing versioned REFERENCES heading (expected v0.1 or v0.2 verified core set)")

    abstract_words = count_words(abstract_body(text))
    if abstract_words > a.max_abstract_words:
        raise SystemExit(f"abstract exceeds configured ceiling {a.max_abstract_words}: {abstract_words}")

    require_any(text, ["46/50 nontrivial splits", "46 of 50 nontrivial splits"], "frozen topology concordance value")
    if "normalized RF = 0.08" not in text:
        raise SystemExit("missing normalized RF value")
    if "strict *P* = 0.00116" not in text or "dominant *P* = 0.000080" not in text:
        raise SystemExit("missing UFBoot nearest-same-colour robustness values")
    if "strict × dominant cross-scenario accepted branch count was therefore zero" not in text:
        raise SystemExit("missing zero shared accepted-species transition result")
    if "global MPD" not in text and "global same-state" not in text and "mean pairwise-distance" not in text:
        raise SystemExit("missing topology-sensitive global-MPD negative result")
    if "public hard-state data do not identify *which* accepted-species branch" not in text:
        raise SystemExit("missing public-data identifiability statement")

    if a.require_ecology_v2:
        ecological_required = [
            "geometric mean RR was **3.53**",
            "geometric mean was **2.42**",
            "**5/5** in the expected direction",
            "Five studies across four taxa",
            "direct abiotic evidence for petal pigment deployment remained sparse",
            "reproductive-service filtering",
        ]
        for phrase in ecological_required:
            if phrase not in text:
                raise SystemExit(f"missing ecological-driver v2 result: {phrase}")

    forbidden_positive = [
        "we demonstrate that the Camellia ancestor was white",
        "we demonstrate that cold adaptation drove",
        "pollinators drove genus-level flower-colour evolution",
        "three robust W→A branches provide",
        "exact gene reuse explains Camellia flower-colour evolution",
        "red-specific bird syndrome",
    ]
    low = text.casefold()
    for phrase in forbidden_positive:
        if phrase.casefold() in low:
            raise SystemExit(f"manuscript contains forbidden superseded/causal claim: {phrase}")

    doi_count = len(re.findall(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+", text))
    if doi_count < 12:
        raise SystemExit(f"core reference set appears incomplete: DOI count={doi_count}")

    summary = {
        "manuscript_version_label": a.version_label,
        "target_journal": "American Journal of Botany",
        "abstract_words_validator_count": abstract_words,
        "abstract_word_ceiling": a.max_abstract_words,
        "abstract_count_rule": "body text under four AJB structured headings; headings excluded",
        "required_sections_present": len(required_headings),
        "core_doi_strings": doi_count,
        "frozen_title_match": True,
        "current_topology_and_trait_values_present": True,
        "ecological_driver_v2_required": a.require_ecology_v2,
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
