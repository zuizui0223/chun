#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

EXPECTED_TITLE = "Flower-color evolutionary memory is transient but lacks a universal phenotypic scale"
EXPECTED_STATUS = "SCIENCE_AND_JOURNAL_FORMAT_READY_METADATA_HOLD"
EXPECTED_ROUTE = "Evolution Letters v0.3"
ORCID_RE = re.compile(r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$")
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$", re.I)
CREDIT_ROLES = {
    "Conceptualization",
    "Data curation",
    "Formal analysis",
    "Funding acquisition",
    "Investigation",
    "Methodology",
    "Project administration",
    "Resources",
    "Software",
    "Supervision",
    "Validation",
    "Visualization",
    "Writing – original draft",
    "Writing – review & editing",
}
TOP_LEVEL = {
    "schema_version",
    "paper_title",
    "phase1_author_identity",
    "phase2_declarations",
    "phase3_archive",
    "governance",
}


def text_ok(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_metadata(x: dict) -> dict:
    if not isinstance(x, dict) or set(x) != TOP_LEVEL:
        raise ValueError(f"metadata top-level schema drift: {set(x) ^ TOP_LEVEL if isinstance(x, dict) else 'not-object'}")
    if x.get("schema_version") != "v0.1":
        raise ValueError("metadata schema version drift")
    if x.get("paper_title") != EXPECTED_TITLE:
        raise ValueError("paper title drift")

    gov = x.get("governance")
    if not isinstance(gov, dict):
        raise ValueError("governance must be an object")
    if gov.get("do_not_infer_missing_human_metadata") is not True:
        raise ValueError("human metadata must not be inferred")
    if gov.get("science_status") != EXPECTED_STATUS:
        raise ValueError("science-status contract drift")
    if gov.get("submission_route") != EXPECTED_ROUTE:
        raise ValueError("submission-route contract drift")

    p1 = x.get("phase1_author_identity")
    if not isinstance(p1, dict):
        raise ValueError("phase1_author_identity must be an object")
    authors = p1.get("authors")
    affiliations = p1.get("affiliations")
    corr = p1.get("corresponding_author")
    if not isinstance(authors, list) or not isinstance(affiliations, list) or not isinstance(corr, dict):
        raise ValueError("phase1 container types invalid")

    phase1_missing: list[str] = []
    if not authors:
        phase1_missing.append("final author list/order")
    if not affiliations:
        phase1_missing.append("full affiliations/addresses")

    affiliation_ids: set[str] = set()
    for i, aff in enumerate(affiliations):
        if not isinstance(aff, dict):
            raise ValueError(f"affiliation[{i}] must be an object")
        for field in ("id", "institution", "address"):
            if not text_ok(aff.get(field)):
                phase1_missing.append(f"affiliation[{i}].{field}")
        if text_ok(aff.get("id")):
            aid = aff["id"].strip()
            if aid in affiliation_ids:
                raise ValueError(f"duplicate affiliation id: {aid}")
            affiliation_ids.add(aid)

    author_names: list[str] = []
    author_orcids: dict[str, str] = {}
    for i, author in enumerate(authors):
        if not isinstance(author, dict):
            raise ValueError(f"author[{i}] must be an object")
        name = author.get("name")
        ids = author.get("affiliation_ids")
        orcid = author.get("orcid")
        if not text_ok(name):
            phase1_missing.append(f"author[{i}].name")
        else:
            author_names.append(name.strip())
        if not isinstance(ids, list) or not ids:
            phase1_missing.append(f"author[{i}].affiliation_ids")
        elif affiliation_ids and any(not isinstance(v, str) or v not in affiliation_ids for v in ids):
            raise ValueError(f"author[{i}] references unknown affiliation id")
        if not text_ok(orcid):
            phase1_missing.append(f"author[{i}].orcid")
        elif not ORCID_RE.match(orcid.strip()):
            raise ValueError(f"author[{i}] ORCID format invalid")
        elif text_ok(name):
            author_orcids[name.strip()] = orcid.strip()

    if len(author_names) != len(set(author_names)):
        raise ValueError("duplicate author names in ordered list")

    for field in ("author_name", "email", "postal_address", "orcid"):
        if not text_ok(corr.get(field)):
            phase1_missing.append(f"corresponding_author.{field}")
    corr_name = corr.get("author_name")
    corr_email = corr.get("email")
    corr_orcid = corr.get("orcid")
    if text_ok(corr_name) and author_names and corr_name.strip() not in author_names:
        raise ValueError("corresponding author must match one ordered author name")
    if text_ok(corr_email) and not EMAIL_RE.match(corr_email.strip()):
        raise ValueError("corresponding author email format invalid")
    if text_ok(corr_orcid) and not ORCID_RE.match(corr_orcid.strip()):
        raise ValueError("corresponding author ORCID format invalid")
    if text_ok(corr_name) and text_ok(corr_orcid) and corr_name.strip() in author_orcids:
        if author_orcids[corr_name.strip()] != corr_orcid.strip():
            raise ValueError("corresponding author ORCID disagrees with ordered author record")

    p2 = x.get("phase2_declarations")
    if not isinstance(p2, dict):
        raise ValueError("phase2_declarations must be an object")
    phase2_missing: list[str] = []
    if not text_ok(p2.get("acknowledgments")):
        phase2_missing.append("acknowledgments or explicit None")

    funding_status = p2.get("funding_status")
    sources = p2.get("funding_sources")
    if funding_status not in {"funded", "none"}:
        phase2_missing.append("funding_status=funded|none")
    if not isinstance(sources, list):
        raise ValueError("funding_sources must be a list")
    if funding_status == "funded":
        if not sources or any(not text_ok(v) for v in sources):
            phase2_missing.append("funding_sources")
    if funding_status == "none" and sources:
        raise ValueError("funding_sources must be empty when funding_status=none")

    credit = p2.get("credit_roles")
    if not isinstance(credit, list):
        raise ValueError("credit_roles must be a list")
    credited_authors: list[str] = []
    for i, row in enumerate(credit):
        if not isinstance(row, dict) or not text_ok(row.get("author_name")):
            raise ValueError(f"credit_roles[{i}] requires author_name")
        roles = row.get("roles")
        if not isinstance(roles, list) or not roles:
            raise ValueError(f"credit_roles[{i}] requires non-empty roles")
        bad = [role for role in roles if role not in CREDIT_ROLES]
        if bad:
            raise ValueError(f"credit_roles[{i}] contains non-CRediT roles: {bad}")
        credited_authors.append(row["author_name"].strip())
    if len(credited_authors) != len(set(credited_authors)):
        raise ValueError("duplicate credit_roles author entries")
    if author_names and set(credited_authors) != set(author_names):
        phase2_missing.append("CRediT roles for every ordered author")
    elif not author_names and not credit:
        phase2_missing.append("CRediT roles for every ordered author")

    if not text_ok(p2.get("conflict_of_interest")):
        phase2_missing.append("conflict_of_interest")

    p3 = x.get("phase3_archive")
    if not isinstance(p3, dict):
        raise ValueError("phase3_archive must be an object")
    phase3_missing: list[str] = []
    for field in ("archive_doi", "archive_version", "archive_url"):
        if not text_ok(p3.get(field)):
            phase3_missing.append(field)
    if text_ok(p3.get("archive_doi")) and not DOI_RE.match(p3["archive_doi"].strip()):
        raise ValueError("archive DOI format invalid")

    phase1_complete = not phase1_missing
    phase2_complete = not phase2_missing
    phase3_complete = not phase3_missing
    if not phase1_complete:
        current_state = "AWAITING_PHASE1_AUTHOR_IDENTITY"
    elif not phase2_complete:
        current_state = "AWAITING_PHASE2_DECLARATIONS"
    elif not phase3_complete:
        current_state = "AWAITING_PHASE3_ARCHIVE_DOI"
    else:
        current_state = "READY_FOR_FINAL_BUNDLE"

    if gov.get("current_state") != current_state:
        raise ValueError(f"governance.current_state drift: stored={gov.get('current_state')} computed={current_state}")

    return {
        "schema_version": "v0.1",
        "phase1_complete": phase1_complete,
        "phase2_complete": phase2_complete,
        "phase3_complete": phase3_complete,
        "current_state": current_state,
        "phase1_missing": sorted(set(phase1_missing)),
        "phase2_missing": sorted(set(phase2_missing)),
        "phase3_missing": sorted(set(phase3_missing)),
        "authors_count": len(authors),
        "affiliations_count": len(affiliations),
        "ready_for_final_bundle": phase1_complete and phase2_complete and phase3_complete,
        "scientific_results_changed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--summary", type=Path)
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()

    metadata = json.loads(args.input.read_text(encoding="utf-8"))
    summary = validate_metadata(metadata)
    if args.summary:
        args.summary.parent.mkdir(parents=True, exist_ok=True)
        args.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if args.require_complete and not summary["ready_for_final_bundle"]:
        raise SystemExit("submission metadata is not complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
