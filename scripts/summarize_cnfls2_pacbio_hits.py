#!/usr/bin/env python3
"""Summarize primer/full-length support for the CnFLS2-class candidate in SRA."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path

FIELDS = [
    "qseqid", "sseqid", "pident", "length", "mismatch", "gapopen",
    "qstart", "qend", "sstart", "send", "evalue", "bitscore", "qlen",
    "slen", "qcovs", "qseq", "sseq",
]
FWD_START_0 = 95
FWD_LENGTH = 21
REV_BIND_START_0 = 318
REV_BIND_LENGTH = 22


def read_single_fasta(path: Path) -> tuple[str, str]:
    name = None
    sequence = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith(">"):
            if name is not None:
                raise SystemExit("Expected one FASTA record")
            name = line[1:].split()[0]
        elif name is not None:
            sequence.append(line)
    if name is None or not sequence:
        raise SystemExit("Query FASTA is empty")
    return name, "".join(sequence).upper()


def as_number(value: str):
    try:
        return int(value)
    except ValueError:
        return float(value)


def aligned_calls(row: dict[str, object]):
    query_position = int(row["qstart"]) - 1
    for query_base, subject_base in zip(str(row["qseq"]).upper(), str(row["sseq"]).upper()):
        if query_base == "-":
            continue
        position = query_position
        query_position += 1
        if subject_base in {"A", "C", "G", "T"}:
            yield position, subject_base


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", type=Path, required=True)
    parser.add_argument("--hits", type=Path, required=True)
    parser.add_argument("--run", default="SRR22729450")
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--minimum-pident", type=float, default=80.0)
    parser.add_argument("--minimum-qcov", type=float, default=70.0)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    query_name, query_sequence = read_single_fasta(args.query)
    rows = []
    with args.hits.open(encoding="utf-8") as handle:
        for raw in handle:
            if not raw.strip():
                continue
            values = raw.rstrip("\n").split("\t")
            if len(values) != len(FIELDS):
                raise SystemExit(f"Unexpected blastn_vdb field count: {len(values)}")
            row = dict(zip(FIELDS, values))
            for field in FIELDS[2:15]:
                row[field] = as_number(str(row[field]))
            rows.append(row)
    if not rows:
        raise SystemExit("blastn_vdb returned no candidate hits")

    # Use one best HSP per raw read to avoid duplicate weighting.
    best_by_read = {}
    for row in rows:
        key = str(row["sseqid"])
        rank = (float(row["qcovs"]), float(row["bitscore"]), int(row["length"]), float(row["pident"]))
        if key not in best_by_read or rank > best_by_read[key][0]:
            best_by_read[key] = (rank, row)
    best_rows = [item[1] for item in best_by_read.values()]
    best_rows.sort(key=lambda row: (-float(row["qcovs"]), -float(row["bitscore"]), -float(row["pident"]), str(row["sseqid"])))
    admitted = [
        row for row in best_rows
        if float(row["pident"]) >= args.minimum_pident and float(row["qcovs"]) >= args.minimum_qcov
    ]
    if not admitted:
        raise SystemExit("No PacBio read passes the declared identity/coverage gate")

    calls = [Counter() for _ in query_sequence]
    for row in admitted:
        for position, base in aligned_calls(row):
            if 0 <= position < len(calls):
                calls[position][base] += 1
    consensus = []
    coverage = []
    for position, counter in enumerate(calls):
        total = sum(counter.values())
        coverage.append(total)
        consensus.append(counter.most_common(1)[0][0] if counter else "N")
    consensus_sequence = "".join(consensus)
    covered_positions = [i for i, depth in enumerate(coverage) if depth > 0]
    consensus_matches = sum(consensus_sequence[i] == query_sequence[i] for i in covered_positions)
    consensus_identity = 100.0 * consensus_matches / len(covered_positions) if covered_positions else 0.0

    primer_positions = list(range(FWD_START_0, FWD_START_0 + FWD_LENGTH)) + list(
        range(REV_BIND_START_0, REV_BIND_START_0 + REV_BIND_LENGTH)
    )
    primer_covered = [i for i in primer_positions if coverage[i] > 0]
    primer_mismatches = sum(consensus_sequence[i] != query_sequence[i] for i in primer_covered)

    csv_fields = [field for field in FIELDS if field not in {"qseq", "sseq"}] + ["admission_status", "claim_boundary"]
    with (args.out_dir / "best_read_hits.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=csv_fields)
        writer.writeheader()
        for row in best_rows:
            output = {field: row[field] for field in FIELDS if field not in {"qseq", "sseq"}}
            output["admission_status"] = "admitted" if row in admitted else "below_declared_gate"
            output["claim_boundary"] = "raw-read alignment support; source transcript naming requires combined provenance"
            writer.writerow(output)

    with (args.out_dir / "consensus_coverage.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["position_1based", "query_base", "consensus_base", "depth", "matches_query"])
        writer.writeheader()
        for index, (query_base, consensus_base, depth) in enumerate(zip(query_sequence, consensus_sequence, coverage), start=1):
            writer.writerow({
                "position_1based": index,
                "query_base": query_base,
                "consensus_base": consensus_base,
                "depth": depth,
                "matches_query": "yes" if depth > 0 and query_base == consensus_base else ("no" if depth > 0 else "uncovered"),
            })
    with (args.out_dir / "pacbio_consensus.fasta").open("w", encoding="utf-8") as handle:
        handle.write(f">{query_name}_SRR22729450_consensus admitted_reads={len(admitted)}\n")
        for start in range(0, len(consensus_sequence), 80):
            handle.write(consensus_sequence[start : start + 80] + "\n")

    best = best_rows[0]
    full_length_like = [row for row in admitted if float(row["qcovs"]) >= 95.0]
    summary = {
        "run": args.run,
        "query": query_name,
        "query_bp": len(query_sequence),
        "query_sha256": hashlib.sha256(query_sequence.encode()).hexdigest(),
        "raw_hsps": len(rows),
        "unique_read_hits": len(best_rows),
        "admitted_unique_reads": len(admitted),
        "minimum_pident": args.minimum_pident,
        "minimum_query_coverage": args.minimum_qcov,
        "full_length_like_reads_qcov_ge_95": len(full_length_like),
        "best_read": {
            key: best[key]
            for key in ["sseqid", "pident", "length", "mismatch", "gapopen", "qstart", "qend", "sstart", "send", "evalue", "bitscore", "qlen", "slen", "qcovs"]
        },
        "consensus_positions_covered": len(covered_positions),
        "consensus_query_coverage_percent": round(100.0 * len(covered_positions) / len(query_sequence), 6),
        "consensus_identity_to_query_percent_on_covered_positions": round(consensus_identity, 6),
        "coverage_median_on_covered_positions": statistics.median(coverage[i] for i in covered_positions),
        "coverage_min_on_covered_positions": min(coverage[i] for i in covered_positions),
        "coverage_max": max(coverage),
        "primer_positions_total": len(primer_positions),
        "primer_positions_covered": len(primer_covered),
        "primer_consensus_mismatches": primer_mismatches,
        "decision": (
            "public PacBio source-read support recovered for the unique GWH CnFLS2-class candidate"
            if full_length_like and len(primer_covered) == len(primer_positions)
            else "partial public PacBio support recovered; retain source-transcript identity as provisional"
        ),
        "claim_ceiling": (
            "read-level support for presence of the candidate in the F01 PacBio run; exact F01.PB8395 naming additionally relies on the source primer/transcript-group provenance, and formal cross-species orthology still requires a broader gene tree and synteny"
        ),
    }
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
