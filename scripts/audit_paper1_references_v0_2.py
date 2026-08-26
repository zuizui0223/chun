#!/usr/bin/env python3
"""Audit Paper 1 v0.2 in-text/reference-registry/Literature-Cited consistency."""
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


def read_registry(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        raise SystemExit("reference registry is empty")
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manuscript", type=Path, required=True)
    ap.add_argument("--registry", type=Path, required=True)
    args = ap.parse_args()

    text = args.manuscript.read_text(encoding="utf-8")
    marker = "# LITERATURE CITED"
    if text.count(marker) != 1:
        raise SystemExit(f"expected exactly one {marker!r} heading")
    body, refs = text.split(marker, 1)

    if "# FINAL SUBMISSION ITEMS" in text or "# OPEN ITEMS" in text:
        raise SystemExit("internal submission TODO headings must not remain in the review manuscript")

    rows = read_registry(args.registry)
    missing_citations: list[str] = []
    missing_dois: list[str] = []
    duplicate_dois: list[str] = []

    for row in rows:
        author = row["first_author"].strip()
        year = row["year"].strip()
        doi = row["doi"].strip()

        if author == "World Flora Online Consortium":
            citation_patterns = [
                rf"World Flora Online Consortium,\s*{re.escape(year)}",
                rf"World Flora Online Consortium\s*\({re.escape(year)}\)",
            ]
        else:
            citation_patterns = [
                rf"\b{re.escape(author)}\s+et al\.?,\s*{re.escape(year)}\b",
                rf"\b{re.escape(author)}\s+et al\.\s*\({re.escape(year)}\)",
                rf"\b{re.escape(author)}\s+and\s+[A-Za-z.-]+,\s*{re.escape(year)}\b",
                rf"\b{re.escape(author)}\s+and\s+[A-Za-z.-]+\s*\({re.escape(year)}\)",
                rf"\b{re.escape(author)},\s*{re.escape(year)}\b",
                rf"\b{re.escape(author)}\s*\({re.escape(year)}\)",
            ]
        if not any(re.search(p, body) for p in citation_patterns):
            missing_citations.append(row["reference_id"])

        doi_url = f"https://doi.org/{doi}"
        n = refs.count(doi_url)
        if n == 0:
            missing_dois.append(row["reference_id"])
        elif n > 1:
            duplicate_dois.append(row["reference_id"])

    # Registry is authoritative: every DOI in the Literature Cited block should be registered.
    listed_dois = set(re.findall(r"https://doi\.org/([^\s)]+)", refs))
    registry_dois = {r["doi"] for r in rows}
    unregistered = sorted(listed_dois - registry_dois)

    if missing_citations or missing_dois or duplicate_dois or unregistered:
        raise SystemExit({
            "missing_in_text_citations": missing_citations,
            "missing_literature_cited_dois": missing_dois,
            "duplicate_literature_cited_dois": duplicate_dois,
            "unregistered_literature_cited_dois": unregistered,
        })

    print({
        "status": "paper1_v0_2_reference_governance_pass",
        "n_registry_references": len(rows),
        "n_literature_cited_dois": len(listed_dois),
        "todo_headings_present": False,
    })


if __name__ == "__main__":
    main()
