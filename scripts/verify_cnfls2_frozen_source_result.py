#!/usr/bin/env python3
"""Verify the compact, provenance-frozen CnFLS2 PacBio source result.

The expensive remote SRA search has already completed successfully and is
retained as an explicit workflow-dispatch audit. Pull requests instead verify
that the frozen query, consensus, metrics, primer sites and successful artifact
provenance remain internally coherent.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

FWD = "AGCAATCACCACCGTCAAAGG"
REV = "CTCTTAGACTCAGCATCCTTAGC"


def reverse_complement(sequence: str) -> str:
    return sequence.translate(str.maketrans("ACGTNacgtn", "TGCANtgcan"))[::-1]


def read_fasta(path: Path) -> tuple[str, str]:
    header = ""
    pieces: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith(">"):
            if header:
                raise SystemExit(f"Expected one FASTA record in {path}")
            header = line[1:]
        else:
            pieces.append(line)
    if not header or not pieces:
        raise SystemExit(f"No FASTA sequence found in {path}")
    sequence = "".join(pieces).upper()
    if any(base not in "ACGTN" for base in sequence):
        raise SystemExit(f"Unexpected nucleotide symbols in {path}")
    return header, sequence


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", type=Path, required=True)
    parser.add_argument("--consensus", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--provenance", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    query_header, query = read_fasta(args.query)
    consensus_header, consensus = read_fasta(args.consensus)
    summary = json.loads(args.summary.read_text(encoding="utf-8"))
    provenance = json.loads(args.provenance.read_text(encoding="utf-8"))

    if len(query) != int(summary["query_bp"]):
        raise SystemExit("Frozen query length disagrees with the summary")
    query_sha = hashlib.sha256(query.encode()).hexdigest()
    if query_sha != summary["query_sha256"]:
        raise SystemExit("Frozen query SHA256 disagrees with the summary")
    if len(consensus) != len(query):
        raise SystemExit("Frozen consensus and query lengths differ")

    matches = sum(a == b for a, b in zip(query, consensus))
    identity = 100.0 * matches / len(query)
    if abs(identity - float(summary["consensus_identity_to_query_percent_on_covered_positions"])) > 1e-6:
        raise SystemExit(f"Frozen consensus identity mismatch: computed={identity}")

    reverse_site = reverse_complement(REV)
    primer_checks = {
        "query_forward_exact": FWD in query,
        "query_reverse_site_exact": reverse_site in query,
        "consensus_forward_exact": FWD in consensus,
        "consensus_reverse_site_exact": reverse_site in consensus,
    }
    if not all(primer_checks.values()):
        raise SystemExit(f"Frozen primer-site verification failed: {primer_checks}")

    required_thresholds = {
        "admitted_unique_reads": int(summary["admitted_unique_reads"]) >= 100,
        "full_length_like_reads": int(summary["full_length_like_reads_qcov_ge_95"]) >= 50,
        "consensus_query_coverage": float(summary["consensus_query_coverage_percent"]) == 100.0,
        "consensus_identity": float(summary["consensus_identity_to_query_percent_on_covered_positions"]) >= 99.0,
        "minimum_position_depth": int(summary["coverage_min_on_covered_positions"]) >= 10,
        "primer_positions_complete": int(summary["primer_positions_covered"]) == int(summary["primer_positions_total"]),
        "primer_consensus_mismatches": int(summary["primer_consensus_mismatches"]) == 0,
    }
    if not all(required_thresholds.values()):
        raise SystemExit(f"Frozen biological thresholds failed: {required_thresholds}")

    provenance_checks = {
        "workflow_success": provenance.get("workflow_conclusion") == "success",
        "workflow_run_id": int(provenance.get("workflow_run_id", 0)) == 32050007025,
        "artifact_id": int(provenance.get("artifact_id", 0)) == 9294590784,
        "artifact_digest": str(provenance.get("artifact_digest", "")).startswith("sha256:"),
        "source_run": provenance.get("source_run") == summary["run"] == "SRR22729450",
        "query_id": provenance.get("query") == summary["query"] == query_header.split()[0],
    }
    if not all(provenance_checks.values()):
        raise SystemExit(f"Frozen provenance verification failed: {provenance_checks}")

    result = {
        "query_header": query_header,
        "consensus_header": consensus_header,
        "query_bp": len(query),
        "query_sha256": query_sha,
        "consensus_identity_percent": identity,
        "consensus_mismatches": len(query) - matches,
        "primer_checks": primer_checks,
        "biological_thresholds": required_thresholds,
        "provenance_checks": provenance_checks,
        "decision": "frozen CnFLS2 PacBio source result is internally coherent and tied to a successful full remote computation",
        "claim_ceiling": "compact integrity gate; the complete remote SRA search remains reproducible through workflow_dispatch",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
