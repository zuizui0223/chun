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

DOI_RE = re.compile(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.I)
MAX_RETRIEVE = 1000
USER_AGENT = "chun-paper1-bibliographic-audit/0.1"
TEXT_SUFFIXES = {".csv", ".md", ".json", ".txt", ".yml", ".yaml"}
RELEVANT_TERMS = {
    "camellia", "flower", "floral", "petal", "color", "colour", "coloration",
    "pigment", "anthocyanin", "flavonol", "flavonoid", "carotenoid", "yellow",
    "golden", "pollination", "pollinator", "transcriptome", "metabolome",
}


def normalize_doi(value: str | None) -> str:
    if not value:
        return ""
    value = value.strip().lower()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
        if value.startswith(prefix):
            value = value[len(prefix):]
    value = value.strip().rstrip(".,;:)]}>'\"")
    match = DOI_RE.search(value)
    return match.group(0).lower().rstrip(".,;:)]}>'\"") if match else ""


def http_json(base: str, params: dict[str, Any], attempts: int = 3) -> dict[str, Any]:
    url = base + "?" + urllib.parse.urlencode(params, doseq=True)
    last: Exception | None = None
    for attempt in range(attempts):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=60) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as exc:  # network/API failure must remain visible
            last = exc
            if attempt + 1 < attempts:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"API request failed after {attempts} attempts: {url}: {last}")


def scan_known_dois(repo_root: Path) -> set[str]:
    known: set[str] = set()
    roots = [repo_root / "data", repo_root / "docs", repo_root / "manuscript"]
    files: list[Path] = [repo_root / "README.md"]
    for root in roots:
        if root.exists():
            files.extend(p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in TEXT_SUFFIXES)
    for path in files:
        if not path.exists():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for match in DOI_RE.finditer(text):
            doi = normalize_doi(match.group(0))
            if doi:
                known.add(doi)
    return known


def year_from_crossref(item: dict[str, Any]) -> str:
    for key in ("published-print", "published-online", "published", "issued", "created"):
        obj = item.get(key) or {}
        parts = obj.get("date-parts") or []
        if parts and parts[0]:
            return str(parts[0][0])
    return ""


def title_relevant(title: str) -> bool:
    tokens = set(re.findall(r"[a-z]+", title.lower()))
    return "camellia" in tokens and bool(tokens & (RELEVANT_TERMS - {"camellia"}))


def openalex_query(query: str) -> tuple[int, list[dict[str, Any]], bool]:
    base = "https://api.openalex.org/works"
    cursor = "*"
    records: list[dict[str, Any]] = []
    total = 0
    first = True
    while len(records) < MAX_RETRIEVE:
        data = http_json(base, {
            "search": query,
            "per-page": min(200, MAX_RETRIEVE - len(records)),
            "cursor": cursor,
            "select": "id,doi,title,publication_year,primary_location,type",
        })
        if first:
            total = int((data.get("meta") or {}).get("count") or 0)
            first = False
        batch = data.get("results") or []
        for item in batch:
            primary = item.get("primary_location") or {}
            source = primary.get("source") or {}
            records.append({
                "doi": normalize_doi(item.get("doi")),
                "title": item.get("title") or "",
                "year": str(item.get("publication_year") or ""),
                "venue": source.get("display_name") or "",
                "source_id": item.get("id") or "",
                "url": item.get("doi") or item.get("id") or "",
            })
        cursor = (data.get("meta") or {}).get("next_cursor")
        if not batch or not cursor or len(records) >= total:
            break
    return total, records[:MAX_RETRIEVE], total > len(records)


def crossref_query(query: str) -> tuple[int, list[dict[str, Any]], bool]:
    data = http_json("https://api.crossref.org/works", {
        "query.bibliographic": query,
        "rows": MAX_RETRIEVE,
        "select": "DOI,title,published-print,published-online,published,issued,created,container-title,type,URL",
    })
    message = data.get("message") or {}
    total = int(message.get("total-results") or 0)
    records: list[dict[str, Any]] = []
    for item in message.get("items") or []:
        titles = item.get("title") or []
        containers = item.get("container-title") or []
        records.append({
            "doi": normalize_doi(item.get("DOI")),
            "title": titles[0] if titles else "",
            "year": year_from_crossref(item),
            "venue": containers[0] if containers else "",
            "source_id": item.get("DOI") or item.get("URL") or "",
            "url": item.get("URL") or ("https://doi.org/" + item.get("DOI", "") if item.get("DOI") else ""),
        })
    return total, records[:MAX_RETRIEVE], total > len(records)


def pubmed_query(query: str) -> tuple[int, list[dict[str, Any]], bool]:
    search = http_json("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi", {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": MAX_RETRIEVE,
        "tool": "chun-paper1-audit",
    })
    result = search.get("esearchresult") or {}
    total = int(result.get("count") or 0)
    ids = result.get("idlist") or []
    records: list[dict[str, Any]] = []
    for start in range(0, len(ids), 200):
        chunk = ids[start:start + 200]
        summary = http_json("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi", {
            "db": "pubmed",
            "id": ",".join(chunk),
            "retmode": "json",
            "tool": "chun-paper1-audit",
        })
        sr = summary.get("result") or {}
        for pmid in chunk:
            item = sr.get(pmid) or {}
            doi = ""
            for aid in item.get("articleids") or []:
                if str(aid.get("idtype") or "").lower() == "doi":
                    doi = normalize_doi(aid.get("value"))
                    break
            pubdate = str(item.get("pubdate") or "")
            m = re.search(r"\b(18|19|20)\d{2}\b", pubdate)
            records.append({
                "doi": doi,
                "title": item.get("title") or "",
                "year": m.group(0) if m else "",
                "venue": item.get("fulljournalname") or item.get("source") or "",
                "source_id": pmid,
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            })
    return total, records[:MAX_RETRIEVE], total > len(records)


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--queries", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    args = ap.parse_args()

    run_utc = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    known_dois = scan_known_dois(args.repo_root)
    with args.queries.open(newline="", encoding="utf-8-sig") as handle:
        query_rows = list(csv.DictReader(handle))
    if not query_rows:
        raise SystemExit("query registry is empty")

    count_rows: list[dict[str, Any]] = []
    record_rows: list[dict[str, Any]] = []
    failures: list[str] = []
    db_funcs = {
        "openalex": ("openalex_query", openalex_query, "https://api.openalex.org/works"),
        "crossref": ("crossref_query", crossref_query, "https://api.crossref.org/works"),
        "pubmed": ("pubmed_query", pubmed_query, "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"),
    }

    for row in query_rows:
        for db, (field, func, endpoint) in db_funcs.items():
            query = (row.get(field) or "").strip()
            if not query:
                failures.append(f"{row.get('query_id')}:{db}:empty query")
                continue
            try:
                total, records, capped = func(query)
            except Exception as exc:
                failures.append(f"{row.get('query_id')}:{db}:{exc}")
                continue
            count_rows.append({
                "query_id": row["query_id"],
                "scope": row.get("scope", ""),
                "concept": row.get("concept", ""),
                "database": db,
                "query": query,
                "hit_count": total,
                "retrieved_count": len(records),
                "retrieval_capped": str(bool(capped)).lower(),
                "api_endpoint": endpoint,
                "run_utc": run_utc,
            })
            for rec in records:
                doi = rec.get("doi") or ""
                title = rec.get("title") or ""
                record_rows.append({
                    "database": db,
                    "query_id": row["query_id"],
                    "scope": row.get("scope", ""),
                    "doi": doi,
                    "title": title,
                    "year": rec.get("year", ""),
                    "venue": rec.get("venue", ""),
                    "source_id": rec.get("source_id", ""),
                    "url": rec.get("url", ""),
                    "known_in_repo": str(bool(doi and doi in known_dois)).lower(),
                    "title_relevant": str(title_relevant(title)).lower(),
                })

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.out_dir / "query_counts.csv", count_rows, [
        "query_id", "scope", "concept", "database", "query", "hit_count", "retrieved_count",
        "retrieval_capped", "api_endpoint", "run_utc",
    ])
    write_csv(args.out_dir / "records.csv", record_rows, [
        "database", "query_id", "scope", "doi", "title", "year", "venue", "source_id", "url",
        "known_in_repo", "title_relevant",
    ])

    by_doi: dict[str, list[dict[str, Any]]] = defaultdict(list)
    no_doi: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for rec in record_rows:
        if rec["doi"]:
            by_doi[rec["doi"]].append(rec)
        else:
            key = (re.sub(r"\W+", " ", rec["title"].lower()).strip(), rec["year"])
            no_doi[key].append(rec)

    candidate_rows: list[dict[str, Any]] = []
    for doi, group in sorted(by_doi.items()):
        if doi in known_dois:
            continue
        representative = max(group, key=lambda r: (r["title_relevant"] == "true", len(r["title"])))
        candidate_rows.append({
            "doi": doi,
            "title": representative["title"],
            "year": representative["year"],
            "venue": representative["venue"],
            "databases": ";".join(sorted({r["database"] for r in group})),
            "query_ids": ";".join(sorted({r["query_id"] for r in group})),
            "title_relevant": str(any(r["title_relevant"] == "true" for r in group)).lower(),
            "screen_status": "pending_manual_screen",
        })
    write_csv(args.out_dir / "candidate_new_dois.csv", candidate_rows, [
        "doi", "title", "year", "venue", "databases", "query_ids", "title_relevant", "screen_status",
    ])

    no_doi_rows: list[dict[str, Any]] = []
    for (title_key, year), group in sorted(no_doi.items()):
        representative = max(group, key=lambda r: len(r["title"]))
        no_doi_rows.append({
            "title": representative["title"],
            "year": year,
            "venue": representative["venue"],
            "databases": ";".join(sorted({r["database"] for r in group})),
            "query_ids": ";".join(sorted({r["query_id"] for r in group})),
            "title_relevant": str(any(r["title_relevant"] == "true" for r in group)).lower(),
        })
    write_csv(args.out_dir / "candidate_no_doi.csv", no_doi_rows, [
        "title", "year", "venue", "databases", "query_ids", "title_relevant",
    ])

    summary = {
        "search_version": "v0.1",
        "run_utc": run_utc,
        "query_registry": str(args.queries),
        "conceptual_query_families": len(query_rows),
        "database_queries_expected": len(query_rows) * len(db_funcs),
        "database_queries_completed": len(count_rows),
        "databases": sorted(db_funcs),
        "known_repo_dois_before_search": len(known_dois),
        "retrieved_records": len(record_rows),
        "unique_external_dois": len(by_doi),
        "new_doi_candidates": len(candidate_rows),
        "new_title_relevant_doi_candidates": sum(r["title_relevant"] == "true" for r in candidate_rows),
        "unique_no_doi_records": len(no_doi_rows),
        "title_relevant_no_doi_records": sum(r["title_relevant"] == "true" for r in no_doi_rows),
        "retrieval_cap_per_database_query": MAX_RETRIEVE,
        "failures": failures,
        "status": "complete" if not failures and len(count_rows) == len(query_rows) * len(db_funcs) else "incomplete",
        "claim_boundary": "Database counts and candidate retrieval only. Eligibility and independence require explicit manual screening; this output does not by itself establish PRISMA completeness.",
    }
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if failures or summary["status"] != "complete":
        raise SystemExit("bibliographic database search incomplete; inspect summary.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
