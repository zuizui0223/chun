#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

HEADINGS = [
    "Premise of the study",
    "Methods",
    "Key results",
    "Conclusions",
]


def section(text: str, start: str, stop: str | None) -> str:
    marker = f"### {start}"
    if marker not in text:
        raise SystemExit(f"missing heading: {start}")
    after = text.split(marker, 1)[1]
    if stop:
        next_marker = f"### {stop}"
        if next_marker not in after:
            raise SystemExit(f"missing next heading: {stop}")
        return after.split(next_marker, 1)[0]
    return after.split("## Claim checks", 1)[0]


def count_words(text: str) -> int:
    clean = re.sub(r"[*_`]", "", text)
    return len(re.findall(r"\b[\w/–—-]+\b", clean, flags=re.UNICODE))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    text = a.file.read_text(encoding="utf-8")

    if "## Primary title" not in text or "## Running head" not in text or "## Structured abstract" not in text:
        raise SystemExit("missing title/running-head/abstract blocks")

    title = text.split("## Primary title", 1)[1].split("## Running head", 1)[0].strip().strip("*")
    running = text.split("## Running head", 1)[1].split("## Alternative titles", 1)[0].strip().strip("*")
    if len(running) > 65:
        raise SystemExit(f"running head exceeds 65 characters: {len(running)}")
    if not title:
        raise SystemExit("empty title")

    pieces = []
    for i, heading in enumerate(HEADINGS):
        stop = HEADINGS[i + 1] if i + 1 < len(HEADINGS) else None
        pieces.append(section(text, heading, stop))
    abstract = " ".join(pieces)
    words = count_words(abstract)
    if words > 250:
        raise SystemExit(f"AJB abstract exceeds 250 words: {words}")

    required_claims = [
        "46/50",
        "0.00116",
        "0.000080",
        "no accepted-species colour-transition branch",
        "topology-sensitive",
    ]
    for x in required_claims:
        if x not in abstract:
            raise SystemExit(f"abstract missing frozen result/boundary: {x}")

    forbidden = [
        "definitive white ancestor",
        "universal cold adaptation",
        "pollinator-driven evolution",
        "three W→A",
    ]
    lower = abstract.casefold()
    for x in forbidden:
        if x.casefold() in lower:
            raise SystemExit(f"abstract contains superseded/forbidden claim: {x}")

    summary = {
        "target_journal": "American Journal of Botany",
        "title": title,
        "title_characters": len(title),
        "running_head": running,
        "running_head_characters": len(running),
        "abstract_words": words,
        "abstract_word_limit": 250,
        "required_headings": HEADINGS,
        "format_gate": "pass",
        "scientific_gate": "contains current robustness values and public-data boundary; no superseded headline phrases",
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
