#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def split_ids(value: str) -> list[str]:
    return [x.strip() for x in (value or "").split(";") if x.strip()]


def source_grade(authority: str, url: str, status: str) -> tuple[str, str]:
    a = authority.casefold()
    u = url.casefold()
    s = status.casefold()
    if "insufficient" in s:
        return "C_insufficient_exact_colour", "exclude_from_state_seed"
    if "flora of china" in a or "world flora online" in a or "efloras.org" in u or "iplant.cn/foc" in u:
        return "A_authoritative_flora", "cite_exact_species_flora_or_flora_treatment"
    if "peer-reviewed" in a or "pmc.ncbi.nlm.nih.gov" in u:
        return "A_peer_reviewed_taxonomic_source", "cite_peer_reviewed_species_description"
    if "china national protected" in a or "iplant.cn/bhzw" in u:
        return "A_official_biodiversity_database", "cite_official_species_record"
    if "ffpri" in a or "ffpri.go.jp" in u:
        return "A_official_institutional_species_source", "cite_official_institutional_species_page"
    if "international camellia register" in a or "camellia.iflora.cn" in u:
        return "B_curated_species_register", "cite_register_species_page_and_underlying_primary_reference_when_available"
    return "C_other_secondary", "manual_citation_review_required"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", type=Path, required=True)
    ap.add_argument("--wild-colour", type=Path, required=True)
    ap.add_argument("--micro-sources", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()

    registry = read_csv(args.registry)
    wild = read_csv(args.wild_colour)
    micro = read_csv(args.micro_sources)
    by_result = {r["result_id"]: r for r in registry}
    errors: list[str] = []

    if len({r["accepted_species"] for r in wild}) != len(wild):
        errors.append("wild-colour registry has duplicate accepted species")

    wild_out: list[dict[str, str]] = []
    for r in wild:
        grade, policy = source_grade(r["source_authority"], r["source_url"], r["wild_colour_status"])
        if not r["source_authority"].strip() or not r["source_url"].startswith("https://") or not r["evidence_note"].strip():
            errors.append(f"{r['accepted_species']}: incomplete source authority/url/evidence note")
        if r["evidence_granularity"] != "species":
            errors.append(f"{r['accepted_species']}: evidence granularity is not species")
        if r["strict_state"] and grade.startswith("C_"):
            errors.append(f"{r['accepted_species']}: strict state relies on grade {grade}")
        if r["dominant_state"] and grade.startswith("C_"):
            errors.append(f"{r['accepted_species']}: dominant state relies on grade {grade}")
        if r["strict_state"] and any(x in r["wild_colour_status"] for x in ["polymorphic", "dominant_", "insufficient"]):
            errors.append(f"{r['accepted_species']}: strict state conflicts with wild status {r['wild_colour_status']}")
        wild_out.append({
            "accepted_species": r["accepted_species"],
            "strict_state": r["strict_state"],
            "dominant_state": r["dominant_state"],
            "wild_colour_status": r["wild_colour_status"],
            "source_authority": r["source_authority"],
            "source_url": r["source_url"],
            "source_grade": grade,
            "manuscript_citation_policy": policy,
            "provenance_caveat": "yes" if "provenance_uncertain" in r["wild_colour_status"] else "no",
            "evidence_note": r["evidence_note"],
        })

    micro_ids = [r["source_id"] for r in micro]
    if len(micro_ids) != len(set(micro_ids)):
        errors.append("duplicate micro source_id")
    micro_out: list[dict[str, str]] = []
    covered_micro_results: set[str] = set()
    for r in micro:
        if not r["citation"].strip() or not r["doi_or_stable_locator"].strip():
            errors.append(f"{r['source_id']}: missing exact citation/locator")
        if not r["public_accessions_or_runs"].strip():
            errors.append(f"{r['source_id']}: missing public accession/run")
        if not r["verification_status"].startswith("verified_"):
            errors.append(f"{r['source_id']}: source not marked verified")
        result_ids = split_ids(r["result_ids"])
        if not result_ids:
            errors.append(f"{r['source_id']}: no result IDs")
        for rid in result_ids:
            if rid not in by_result:
                errors.append(f"{r['source_id']}: unknown result ID {rid}")
            else:
                covered_micro_results.add(rid)
        micro_out.append(dict(r))

    required_micro = {
        r["result_id"] for r in registry
        if r["layer"] == "micro" and r["status"] in {"authoritative", "sensitivity"}
    }
    missing_micro = sorted(required_micro - covered_micro_results)
    if missing_micro:
        errors.append(f"micro Paper 1 results without exact source provenance: {missing_micro}")

    if errors:
        raise SystemExit("\n".join(errors))

    args.out_dir.mkdir(parents=True, exist_ok=True)
    wild_fields = list(wild_out[0])
    with (args.out_dir / "wild_colour_source_audit.csv").open("w", newline="", encoding="utf-8") as handle:
        w = csv.DictWriter(handle, fieldnames=wild_fields, lineterminator="\n")
        w.writeheader(); w.writerows(wild_out)
    with (args.out_dir / "micro_source_audit.csv").open("w", newline="", encoding="utf-8") as handle:
        w = csv.DictWriter(handle, fieldnames=list(micro_out[0]), lineterminator="\n")
        w.writeheader(); w.writerows(micro_out)

    strict = [r for r in wild_out if r["strict_state"]]
    dominant = [r for r in wild_out if r["dominant_state"]]
    strict_b = sorted(r["accepted_species"] for r in strict if r["source_grade"].startswith("B_"))
    dominant_b = sorted(r["accepted_species"] for r in dominant if r["source_grade"].startswith("B_"))
    caveat_strict = sorted(r["accepted_species"] for r in strict if r["provenance_caveat"] == "yes")
    summary = {
        "provenance_audit_version": "v0.1",
        "wild_species_rows": len(wild_out),
        "strict_seed_n": len(strict),
        "dominant_seed_n": len(dominant),
        "wild_source_grade_counts_all": dict(Counter(r["source_grade"] for r in wild_out)),
        "wild_source_grade_counts_strict": dict(Counter(r["source_grade"] for r in strict)),
        "wild_source_grade_counts_dominant": dict(Counter(r["source_grade"] for r in dominant)),
        "strict_seed_curated_register_species": strict_b,
        "dominant_seed_curated_register_species": dominant_b,
        "strict_seed_provenance_caveats": caveat_strict,
        "micro_source_rows": len(micro_out),
        "micro_result_ids_covered": sorted(covered_micro_results),
        "all_current_micro_results_have_exact_source_provenance": not missing_micro,
        "manuscript_rule": (
            "Use exact species-level source locators for wild-colour states; label curated-register sources as such and cite the underlying primary reference when available. "
            "Use primary article DOI/stable locator plus versioned public accessions/runs for sequence-aware micro claims."
        ),
    }
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
