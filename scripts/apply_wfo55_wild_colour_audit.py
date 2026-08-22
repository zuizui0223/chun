#!/usr/bin/env python3
import argparse
import csv
import json
from collections import Counter
from pathlib import Path


def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    malformed = [row for row in rows if None in row]
    if malformed:
        raise SystemExit(f"malformed CSV rows with extra columns in {path}: {len(malformed)}")
    return rows


def write_csv(path, rows, fieldnames):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--aggregation", required=True)
    parser.add_argument("--audit", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    aggregation = read_csv(args.aggregation)
    audit = read_csv(args.audit)
    audit_by_species = {row["accepted_species"]: row for row in audit}
    if len(audit_by_species) != len(audit):
        raise SystemExit("duplicate accepted species in audit registry")

    observed = [row for row in aggregation if row["fan_aggregation_status"] != "unobserved"]
    missing = sorted(set(row["accepted_species"] for row in observed) - set(audit_by_species))
    extra = sorted(set(audit_by_species) - set(row["accepted_species"] for row in observed))
    if missing or extra:
        raise SystemExit(f"audit coverage mismatch missing={missing} extra={extra}")

    joined = []
    strict = []
    dominant = []
    for row in aggregation:
        evidence = audit_by_species.get(row["accepted_species"])
        joined_row = dict(row)
        for key in [
            "wild_colour_status",
            "strict_state",
            "dominant_state",
            "evidence_granularity",
            "source_authority",
            "source_url",
            "evidence_note",
            "audit_decision",
        ]:
            joined_row[key] = evidence[key] if evidence else ""
        joined.append(joined_row)

        if evidence and evidence["strict_state"]:
            strict.append(
                {
                    "accepted_species": row["accepted_species"],
                    "colour_state": evidence["strict_state"],
                    "wild_colour_status": evidence["wild_colour_status"],
                    "audit_decision": evidence["audit_decision"],
                }
            )
        if evidence and evidence["dominant_state"]:
            dominant.append(
                {
                    "accepted_species": row["accepted_species"],
                    "colour_state": evidence["dominant_state"],
                    "wild_colour_status": evidence["wild_colour_status"],
                    "audit_decision": evidence["audit_decision"],
                }
            )

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    joined_fields = list(aggregation[0]) + [
        "wild_colour_status",
        "strict_state",
        "dominant_state",
        "evidence_granularity",
        "source_authority",
        "source_url",
        "evidence_note",
        "audit_decision",
    ]
    write_csv(out_dir / "wfo55_wild_colour_audited_join.csv", joined, joined_fields)
    seed_fields = ["accepted_species", "colour_state", "wild_colour_status", "audit_decision"]
    write_csv(out_dir / "wfo55_wild_colour_strict_seed.csv", strict, seed_fields)
    write_csv(out_dir / "wfo55_wild_colour_dominant_seed.csv", dominant, seed_fields)

    provisional_hard = sum(bool(row["hard_state_for_next_gate"]) for row in aggregation)
    strict_from_prior_hard = [
        row for row in strict
        if next(x for x in aggregation if x["accepted_species"] == row["accepted_species"])["hard_state_for_next_gate"]
    ]
    summary = {
        "n_accepted_camellia_species": len(aggregation),
        "n_fan_observed_or_conflicting": len(observed),
        "n_audited_observed_species": len(audit),
        "audit_coverage_complete": not missing and not extra,
        "n_provisional_hard_states_before_wild_audit": provisional_hard,
        "strict_seed_n": len(strict),
        "strict_state_counts": dict(Counter(row["colour_state"] for row in strict)),
        "dominant_seed_n": len(dominant),
        "dominant_state_counts": dict(Counter(row["colour_state"] for row in dominant)),
        "n_demoted_from_provisional_hard_in_strict": provisional_hard - len(strict_from_prior_hard),
        "wild_status_counts": dict(Counter(row["wild_colour_status"] for row in audit)),
        "strict_excluded_observed_species": sorted(
            row["accepted_species"] for row in observed
            if not audit_by_species[row["accepted_species"]]["strict_state"]
        ),
        "dominant_excluded_observed_species": sorted(
            row["accepted_species"] for row in observed
            if not audit_by_species[row["accepted_species"]]["dominant_state"]
        ),
        "analysis_decision": {
            "strict_history": "use only species-level wild evidence consistent with one state at fresh anthesis; polymorphic, dominant-only, and exact-colour-insufficient species are missing",
            "dominant_sensitivity": "add species with explicit dominant colour or age/tint caveat, while preserving polymorphic and insufficient species as missing",
            "next_gate": "rebuild colour history and branch transitions on the WFO55 accepted-species tree under both strict and dominant seeds; only transitions robust to both may enter branch-climate or micro-macro causal tests",
        },
        "claim_ceiling": "wild/floristic trait audit and two scenario seeds only; no ancestral-state or ecological-causation inference",
    }
    (out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
