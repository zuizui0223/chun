#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ALLOWED_STATUS = {"current", "historical", "superseded", "consumed"}
ALLOWED_PLACEMENT = {"main", "supplement", "provenance_only", "exclude"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def ids(value: str) -> list[str]:
    return [x.strip() for x in (value or "").split(";") if x.strip()]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", type=Path, required=True)
    ap.add_argument("--disposition", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()

    registry = read_csv(args.registry)
    disposition = read_csv(args.disposition)
    if not registry or not disposition:
        raise SystemExit("registry/disposition must be non-empty")

    by_result = {r["result_id"]: r for r in registry}
    if len(by_result) != len(registry):
        raise SystemExit("duplicate result_id in authoritative registry")

    analysis_ids = [r["analysis_id"].strip() for r in disposition]
    dupes = [x for x, n in Counter(analysis_ids).items() if not x or n > 1]
    if dupes:
        raise SystemExit(f"empty/duplicate analysis_id values: {dupes}")

    errors: list[str] = []
    result_to_rows: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in disposition:
        aid = row["analysis_id"]
        status = row["current_status"]
        placement = row["manuscript_placement"]
        if status not in ALLOWED_STATUS:
            errors.append(f"{aid}: invalid current_status={status}")
        if placement not in ALLOWED_PLACEMENT:
            errors.append(f"{aid}: invalid manuscript_placement={placement}")
        if not row["source_key"].strip() or not row["topic"].strip() or not row["notes"].strip():
            errors.append(f"{aid}: source_key/topic/notes must be non-empty")
        if status == "superseded" and placement not in {"provenance_only", "exclude"}:
            errors.append(f"{aid}: superseded analysis cannot be {placement}")
        if status == "consumed" and placement != "provenance_only":
            errors.append(f"{aid}: consumed intermediate must be provenance_only")
        if status in {"superseded", "consumed"} and not row["replacement_or_current_anchor"].strip():
            errors.append(f"{aid}: {status} analysis requires replacement/current anchor")
        for rid in ids(row["result_ids"]):
            if rid not in by_result:
                errors.append(f"{aid}: unknown result_id {rid}")
                continue
            rr = by_result[rid]
            result_to_rows[rid].append(row)
            if placement == "main" and (rr["status"] == "superseded" or rr["manuscript_role"] == "exclude"):
                errors.append(f"{aid}: Main placement references superseded/excluded result {rid}")

    superseded_ids = [r["result_id"] for r in registry if r["status"] == "superseded"]
    for rid in superseded_ids:
        rows = result_to_rows.get(rid, [])
        if not rows:
            errors.append(f"superseded registry result {rid} lacks disposition pointer")
        if not any(r["manuscript_placement"] == "exclude" for r in rows):
            errors.append(f"superseded registry result {rid} lacks explicit exclude disposition")
        if any(r["manuscript_placement"] == "main" for r in rows):
            errors.append(f"superseded registry result {rid} appears in Main disposition")

    main_sources = [r for r in disposition if r["manuscript_placement"] == "main"]
    if not main_sources:
        errors.append("no Main analyses")
    if any(r["current_status"] == "superseded" for r in main_sources):
        errors.append("Main contains superseded analysis")

    if errors:
        raise SystemExit("\n".join(errors))

    args.out_dir.mkdir(parents=True, exist_ok=True)
    for placement in sorted(ALLOWED_PLACEMENT):
        rows = [r for r in disposition if r["manuscript_placement"] == placement]
        if rows:
            with (args.out_dir / f"{placement}_analyses.csv").open("w", newline="", encoding="utf-8") as handle:
                w = csv.DictWriter(handle, fieldnames=list(disposition[0]), lineterminator="\n")
                w.writeheader(); w.writerows(rows)

    summary = {
        "analysis_disposition_version": "v0.1",
        "n_analyses": len(disposition),
        "status_counts": dict(Counter(r["current_status"] for r in disposition)),
        "placement_counts": dict(Counter(r["manuscript_placement"] for r in disposition)),
        "n_superseded_registry_results": len(superseded_ids),
        "superseded_registry_results_with_explicit_exclude": sum(
            any(r["manuscript_placement"] == "exclude" for r in result_to_rows.get(rid, [])) for rid in superseded_ids
        ),
        "main_contains_superseded": False,
        "policy": (
            "Main uses current analyses only; sensitivity analyses may appear in Supplement or be cited as explicit robustness panels; "
            "consumed intermediates remain provenance-only; superseded headline analyses are excluded from the manuscript pipeline."
        ),
    }
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
