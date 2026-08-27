#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from run_paper1_bibliographic_db_search_v0_1 import normalize_doi, scan_known_dois

USER_AGENT = "chun-paper1-citation-chase/0.1"
MAX_FORWARD = 1000


def get_json(url: str, attempts: int = 3) -> dict[str, Any]:
    last: Exception | None = None
    for attempt in range(attempts):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=60) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            last = exc
            if attempt + 1 < attempts:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"request failed after {attempts} attempts: {url}: {last}")


def get_json_params(base: str, params: dict[str, Any]) -> dict[str, Any]:
    return get_json(base + "?" + urllib.parse.urlencode(params, doseq=True))


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def clean_openalex_id(value: str) -> str:
    return value.rsplit("/", 1)[-1] if value else ""


def priority_flags(title: str) -> tuple[bool, bool]:
    low = title.lower()
    camellia = "camellia" in low
    colour_terms = (
        "flower color", "flower colour", "floral color", "floral colour", "flower coloration",
        "flower pigmentation", "petal color", "petal colour", "anthocyan", "flavonol", "flavonoid",
        "carotenoid", "yellow flower", "pollination", "pollinator", "transcriptom", "metabolom",
        "phylogenom", "convergen", "parallel evolution",
    )
    relevant = (camellia and any(x in low for x in colour_terms)) or any(
        x in low for x in ("flower color", "flower colour", "floral color", "floral colour")
    )
    return camellia, relevant


def crossref_seed(doi: str) -> dict[str, Any]:
    encoded = urllib.parse.quote(doi, safe="")
    data = get_json(f"https://api.crossref.org/works/{encoded}")
    return data.get("message") or {}


def openalex_seed(doi: str) -> dict[str, Any]:
    doi_url = "https://doi.org/" + doi
    encoded = urllib.parse.quote(doi_url, safe=":/")
    return get_json(f"https://api.openalex.org/works/{encoded}")


def forward_citations(openalex_id: str) -> list[dict[str, Any]]:
    wid = clean_openalex_id(openalex_id)
    if not wid:
        return []
    cursor = "*"
    rows: list[dict[str, Any]] = []
    while len(rows) < MAX_FORWARD:
        data = get_json_params(
            "https://api.openalex.org/works",
            {
                "filter": f"cites:{wid}",
                "per-page": min(200, MAX_FORWARD - len(rows)),
                "cursor": cursor,
                "select": "id,doi,title,publication_year,primary_location,type",
            },
        )
        batch = data.get("results") or []
        for item in batch:
            source = ((item.get("primary_location") or {}).get("source") or {})
            rows.append(
                {
                    "doi": normalize_doi(item.get("doi")),
                    "title": item.get("title") or "",
                    "year": str(item.get("publication_year") or ""),
                    "venue": source.get("display_name") or "",
                    "openalex_id": clean_openalex_id(item.get("id") or ""),
                    "url": item.get("doi") or item.get("id") or "",
                }
            )
        cursor = (data.get("meta") or {}).get("next_cursor")
        if not batch or not cursor:
            break
    return rows[:MAX_FORWARD]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    args = ap.parse_args()

    run_utc = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    known_dois = scan_known_dois(args.repo_root)
    with args.seeds.open(newline="", encoding="utf-8-sig") as handle:
        seeds = list(csv.DictReader(handle))
    if not seeds:
        raise SystemExit("citation-chase seed registry is empty")

    seed_rows: list[dict[str, Any]] = []
    back_rows: list[dict[str, Any]] = []
    forward_rows: list[dict[str, Any]] = []
    failures: list[str] = []

    for seed in seeds:
        sid = seed["seed_id"]
        doi = normalize_doi(seed["doi"])
        if not doi:
            failures.append(f"{sid}: invalid DOI")
            continue
        try:
            cr = crossref_seed(doi)
            oa = openalex_seed(doi)
        except Exception as exc:
            failures.append(f"{sid}: seed resolution failed: {exc}")
            continue

        refs = cr.get("reference") or []
        oa_id = oa.get("id") or ""
        seed_rows.append(
            {
                "seed_id": sid,
                "doi": doi,
                "scope": seed.get("scope", ""),
                "role": seed.get("role", ""),
                "title": oa.get("title") or (cr.get("title") or [""])[0],
                "openalex_id": clean_openalex_id(oa_id),
                "crossref_reference_count": len(refs),
                "openalex_cited_by_count": int(oa.get("cited_by_count") or 0),
                "run_utc": run_utc,
            }
        )

        for i, ref in enumerate(refs, start=1):
            ref_doi = normalize_doi(ref.get("DOI"))
            title = (ref.get("article-title") or ref.get("unstructured") or "").strip()
            camellia, relevant = priority_flags(title)
            back_rows.append(
                {
                    "seed_id": sid,
                    "relation": "backward",
                    "ordinal": i,
                    "doi": ref_doi,
                    "title_or_unstructured": title,
                    "year": str(ref.get("year") or ""),
                    "journal": ref.get("journal-title") or "",
                    "known_in_repo": str(bool(ref_doi and ref_doi in known_dois)).lower(),
                    "camellia_in_title": str(camellia).lower(),
                    "priority_relevant": str(relevant).lower(),
                }
            )

        try:
            fw = forward_citations(oa_id)
        except Exception as exc:
            failures.append(f"{sid}: forward citation retrieval failed: {exc}")
            fw = []
        for rec in fw:
            camellia, relevant = priority_flags(rec["title"])
            forward_rows.append(
                {
                    "seed_id": sid,
                    "relation": "forward",
                    "doi": rec["doi"],
                    "title": rec["title"],
                    "year": rec["year"],
                    "venue": rec["venue"],
                    "openalex_id": rec["openalex_id"],
                    "url": rec["url"],
                    "known_in_repo": str(bool(rec["doi"] and rec["doi"] in known_dois)).lower(),
                    "camellia_in_title": str(camellia).lower(),
                    "priority_relevant": str(relevant).lower(),
                }
            )

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(
        args.out_dir / "seed_resolution.csv",
        seed_rows,
        ["seed_id", "doi", "scope", "role", "title", "openalex_id", "crossref_reference_count", "openalex_cited_by_count", "run_utc"],
    )
    write_csv(
        args.out_dir / "backward_references.csv",
        back_rows,
        ["seed_id", "relation", "ordinal", "doi", "title_or_unstructured", "year", "journal", "known_in_repo", "camellia_in_title", "priority_relevant"],
    )
    write_csv(
        args.out_dir / "forward_citations.csv",
        forward_rows,
        ["seed_id", "relation", "doi", "title", "year", "venue", "openalex_id", "url", "known_in_repo", "camellia_in_title", "priority_relevant"],
    )

    candidate_by_doi: dict[str, dict[str, Any]] = {}
    no_doi_candidates: list[dict[str, Any]] = []
    for row in back_rows:
        if row["known_in_repo"] == "true" or row["priority_relevant"] != "true":
            continue
        if row["doi"]:
            candidate_by_doi.setdefault(
                row["doi"],
                {
                    "doi": row["doi"], "title": row["title_or_unstructured"], "year": row["year"],
                    "source_relation": "backward", "seed_ids": set(), "camellia_in_title": row["camellia_in_title"],
                },
            )["seed_ids"].add(row["seed_id"])
        else:
            no_doi_candidates.append(
                {
                    "title": row["title_or_unstructured"], "year": row["year"], "source_relation": "backward",
                    "seed_id": row["seed_id"], "camellia_in_title": row["camellia_in_title"],
                    "screen_status": "pending_manual_screen",
                }
            )
    for row in forward_rows:
        if row["known_in_repo"] == "true" or row["priority_relevant"] != "true" or not row["doi"]:
            continue
        entry = candidate_by_doi.setdefault(
            row["doi"],
            {
                "doi": row["doi"], "title": row["title"], "year": row["year"],
                "source_relation": "forward", "seed_ids": set(), "camellia_in_title": row["camellia_in_title"],
            },
        )
        entry["seed_ids"].add(row["seed_id"])
        if entry["source_relation"] != "forward":
            entry["source_relation"] = "backward;forward"

    candidate_rows = []
    for doi, row in sorted(candidate_by_doi.items()):
        candidate_rows.append(
            {
                "doi": doi,
                "title": row["title"],
                "year": row["year"],
                "source_relation": row["source_relation"],
                "seed_ids": ";".join(sorted(row["seed_ids"])),
                "camellia_in_title": row["camellia_in_title"],
                "screen_status": "pending_manual_screen",
            }
        )
    write_csv(
        args.out_dir / "new_priority_doi_candidates.csv",
        candidate_rows,
        ["doi", "title", "year", "source_relation", "seed_ids", "camellia_in_title", "screen_status"],
    )
    write_csv(
        args.out_dir / "new_priority_no_doi_candidates.csv",
        no_doi_candidates,
        ["title", "year", "source_relation", "seed_id", "camellia_in_title", "screen_status"],
    )

    summary = {
        "citation_chase_version": "v0.1",
        "run_utc": run_utc,
        "seed_registry": str(args.seeds),
        "seeds_expected": len(seeds),
        "seeds_resolved": len(seed_rows),
        "backward_reference_records": len(back_rows),
        "forward_citation_records": len(forward_rows),
        "known_repo_dois_before_chase": len(known_dois),
        "new_priority_doi_candidates": len(candidate_rows),
        "new_priority_camellia_doi_candidates": sum(r["camellia_in_title"] == "true" for r in candidate_rows),
        "new_priority_no_doi_candidates": len(no_doi_candidates),
        "failures": failures,
        "status": "complete" if not failures and len(seed_rows) == len(seeds) else "incomplete",
        "claim_boundary": "retrieval only; biological eligibility and independence require explicit manual screening",
    }
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if summary["status"] != "complete":
        raise SystemExit("citation chase incomplete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
