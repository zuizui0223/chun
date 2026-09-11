#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ORCID_RE = re.compile(r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$")
DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$", re.I)
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
CREDIT_ROLES = {
    "Conceptualization", "Data curation", "Formal analysis", "Funding acquisition",
    "Investigation", "Methodology", "Project administration", "Resources", "Software",
    "Supervision", "Validation", "Visualization", "Writing – original draft",
    "Writing – review & editing",
}
EXPECTED_TITLE = "Hierarchical molecular repeatability coexists with local flower-colour conservatism in Camellia"


def text_ok(x: object) -> bool:
    return isinstance(x, str) and bool(x.strip())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--summary", type=Path)
    ap.add_argument("--require-phase1", action="store_true")
    ap.add_argument("--require-complete", action="store_true")
    a = ap.parse_args()

    x = json.loads(a.input.read_text(encoding="utf-8"))
    required_top = {"schema_version", "paper_title", "phase1_author_identity", "phase2_declarations", "phase3_archive", "governance"}
    if set(x) != required_top:
        raise SystemExit(f"metadata top-level schema drift: {set(x) ^ required_top}")
    if x["schema_version"] != "v1.0" or x["paper_title"] != EXPECTED_TITLE:
        raise SystemExit("metadata version/title contract drift")

    gov = x["governance"]
    if gov.get("do_not_infer_missing_human_metadata") is not True:
        raise SystemExit("human-metadata non-inference contract must remain true")
    if gov.get("paper1_science_version") != "v0.2.2" or gov.get("paper1_framing_version") != "v0.3.4" or gov.get("submission_route") != "AJB v1.0":
        raise SystemExit("frozen Paper 1 governance contract drift")

    p1 = x["phase1_author_identity"]
    authors = p1.get("authors")
    affs = p1.get("affiliations")
    corr = p1.get("corresponding_author")
    if not isinstance(authors, list) or not isinstance(affs, list) or not isinstance(corr, dict):
        raise SystemExit("phase1 container types invalid")

    phase1_missing: list[str] = []
    if not authors:
        phase1_missing.append("final author list/order")
    if not affs:
        phase1_missing.append("full affiliations/addresses")

    aff_ids: set[str] = set()
    for i, aff in enumerate(affs):
        if not isinstance(aff, dict):
            raise SystemExit(f"affiliation[{i}] must be an object")
        for field in ("id", "institution", "address"):
            if not text_ok(aff.get(field)):
                phase1_missing.append(f"affiliation[{i}].{field}")
        if text_ok(aff.get("id")):
            aid = aff["id"].strip()
            if aid in aff_ids:
                raise SystemExit(f"duplicate affiliation id: {aid}")
            aff_ids.add(aid)

    author_names: list[str] = []
    for i, author in enumerate(authors):
        if not isinstance(author, dict):
            raise SystemExit(f"author[{i}] must be an object")
        name = author.get("name")
        ids = author.get("affiliation_ids")
        if not text_ok(name):
            phase1_missing.append(f"author[{i}].name")
        else:
            author_names.append(name.strip())
        if not isinstance(ids, list) or not ids:
            phase1_missing.append(f"author[{i}].affiliation_ids")
        elif aff_ids and any(not isinstance(v, str) or v not in aff_ids for v in ids):
            raise SystemExit(f"author[{i}] references unknown affiliation id")
    if len(author_names) != len(set(author_names)):
        raise SystemExit("duplicate author names in ordered list")

    for field in ("author_name", "email", "postal_address", "orcid"):
        if not text_ok(corr.get(field)):
            phase1_missing.append(f"corresponding_author.{field}")
    if text_ok(corr.get("author_name")) and author_names and corr["author_name"].strip() not in author_names:
        raise SystemExit("corresponding author must match one ordered author name")
    if text_ok(corr.get("email")) and not EMAIL_RE.match(corr["email"].strip()):
        raise SystemExit("corresponding author email format invalid")
    if text_ok(corr.get("orcid")) and not ORCID_RE.match(corr["orcid"].strip()):
        raise SystemExit("ORCID must use 0000-0000-0000-0000 format")

    p2 = x["phase2_declarations"]
    phase2_missing: list[str] = []
    if not text_ok(p2.get("acknowledgments")):
        phase2_missing.append("acknowledgments")
    fs = p2.get("funding_status")
    if fs not in {"funded", "none"}:
        phase2_missing.append("funding_status=funded|none")
    sources = p2.get("funding_sources")
    if not isinstance(sources, list):
        raise SystemExit("funding_sources must be a list")
    if fs == "funded" and not sources:
        phase2_missing.append("funding_sources")
    if fs == "none" and sources:
        raise SystemExit("funding_sources must be empty when funding_status=none")

    credit = p2.get("credit_roles")
    if not isinstance(credit, list):
        raise SystemExit("credit_roles must be a list")
    credited_authors: set[str] = set()
    for i, row in enumerate(credit):
        if not isinstance(row, dict) or not text_ok(row.get("author_name")) or not isinstance(row.get("roles"), list) or not row.get("roles"):
            raise SystemExit(f"credit_roles[{i}] requires author_name and non-empty roles")
        bad = [r for r in row["roles"] if r not in CREDIT_ROLES]
        if bad:
            raise SystemExit(f"credit_roles[{i}] contains non-CRediT roles: {bad}")
        credited_authors.add(row["author_name"].strip())
    if author_names and set(author_names) != credited_authors:
        phase2_missing.append("CRediT roles for every ordered author")

    if not text_ok(p2.get("conflict_of_interest")):
        phase2_missing.append("conflict_of_interest")
    for field in ("originality_and_no_simultaneous_submission_confirmed", "all_authors_approved_version_and_order"):
        if p2.get(field) is not True:
            phase2_missing.append(field)
    ps = p2.get("preprint_status")
    if ps not in {"none", "present"}:
        phase2_missing.append("preprint_status=none|present")
    if ps == "present" and not text_ok(p2.get("preprint_details")):
        phase2_missing.append("preprint_details")
    if not text_ok(p2.get("generative_ai_disclosure_after_policy_review")):
        phase2_missing.append("generative_ai_disclosure_after_policy_review")

    p3 = x["phase3_archive"]
    phase3_missing: list[str] = []
    for field in ("archive_doi", "archive_version", "archive_url"):
        if not text_ok(p3.get(field)):
            phase3_missing.append(field)
    if text_ok(p3.get("archive_doi")) and not DOI_RE.match(p3["archive_doi"].strip()):
        raise SystemExit("archive DOI format invalid")

    p1_complete = not phase1_missing
    p2_complete = not phase2_missing
    p3_complete = not phase3_missing
    current_state = (
        "READY_FOR_FINAL_BUNDLE" if p1_complete and p2_complete and p3_complete
        else "AWAITING_PHASE1_AUTHOR_IDENTITY" if not p1_complete
        else "AWAITING_PHASE2_DECLARATIONS" if not p2_complete
        else "AWAITING_PHASE3_ARCHIVE_DOI"
    )

    summary = {
        "schema_version": "v1.0",
        "phase1_complete": p1_complete,
        "phase2_complete": p2_complete,
        "phase3_complete": p3_complete,
        "current_state": current_state,
        "phase1_missing": sorted(set(phase1_missing)),
        "phase2_missing": sorted(set(phase2_missing)),
        "phase3_missing": sorted(set(phase3_missing)),
        "authors_count": len(authors),
        "affiliations_count": len(affs),
        "ready_for_final_bundle": p1_complete and p2_complete and p3_complete,
        "scientific_results_changed": False,
    }
    if gov.get("current_state") != current_state:
        raise SystemExit(f"governance.current_state drift: stored={gov.get('current_state')} computed={current_state}")
    if a.summary:
        a.summary.parent.mkdir(parents=True, exist_ok=True)
        a.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))

    if a.require_complete and not summary["ready_for_final_bundle"]:
        raise SystemExit("submission metadata is not complete")
    if a.require_phase1 and not p1_complete:
        raise SystemExit("phase1 author identity block is not complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
