#!/usr/bin/env python3
"""Freeze the provenance-gated GWH CnFLS2 candidate recovery result."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

BLAST_FIELDS = [
    "qseqid", "sseqid", "pident", "length", "mismatch", "gapopen",
    "qstart", "qend", "sstart", "send", "evalue", "bitscore",
    "qlen", "slen", "qcovs",
]


def as_number(value: str):
    try:
        return int(value)
    except ValueError:
        return float(value)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--primer-summary", type=Path, required=True)
    parser.add_argument("--cds-panel-summary", type=Path, required=True)
    parser.add_argument("--blast", type=Path, required=True)
    parser.add_argument("--tree", type=Path, required=True)
    parser.add_argument("--json-output", type=Path, required=True)
    parser.add_argument("--csv-output", type=Path, required=True)
    args = parser.parse_args()

    primer = json.loads(args.primer_summary.read_text(encoding="utf-8"))
    panel = json.loads(args.cds_panel_summary.read_text(encoding="utf-8"))
    hits = []
    with args.blast.open(encoding="utf-8") as handle:
        for raw in handle:
            if not raw.strip():
                continue
            values = raw.rstrip("\n").split("\t")
            if len(values) != len(BLAST_FIELDS):
                raise SystemExit(f"Unexpected BLAST field count: {len(values)}")
            row = dict(zip(BLAST_FIELDS, values))
            for field in BLAST_FIELDS[2:]:
                row[field] = as_number(row[field])
            row["claim_boundary"] = "pairwise coding-sequence similarity; not by itself formal orthology"
            hits.append(row)
    if not hits:
        raise SystemExit("No BLAST hits")
    hits.sort(key=lambda row: (-float(row["pident"]), -int(row["qcovs"]), -float(row["bitscore"]), str(row["sseqid"])))

    closest = hits[0]
    alternatives = [row for row in hits[1:]]
    identity_margin = float(closest["pident"]) - max(float(row["pident"]) for row in alternatives)
    candidate = primer["best_candidate"]
    tree = args.tree.read_text(encoding="utf-8").strip()
    expected_closest = "tea_CSA008358_CDS"
    if closest["sseqid"] != expected_closest:
        raise SystemExit(f"Unexpected closest reference: {closest['sseqid']}")
    if int(candidate["total_mismatches"]) != 0 or int(candidate["amplicon_bp"]) != 246:
        raise SystemExit("Primer gate no longer gives an exact 246-bp candidate")
    if int(primer["compatible_transcripts"]) != 1:
        raise SystemExit("GWH candidate is no longer unique under the declared primer gate")

    decision = (
        "The published F01.PB8395/CnFLS2 primer pair uniquely identifies "
        "GWHTFILD005297.1 among the public GWH transcript set. Its full coding "
        "sequence is nearly identical to tea CSA008358 and strongly separated "
        "from tea CSA006950 and published CnFLS1. This promotes CSA008358 and "
        "GWHTFILD005297.1 to a sequence-supported same-paralog/orthology "
        "hypothesis, while exact F01.PB8395 identity and formal orthology remain "
        "held out for PacBio source-read recovery and broader gene-tree/synteny tests."
    )
    summary = {
        "source_study_transcript": primer["source_transcript"],
        "source_class": primer["source_class"],
        "source_longread_run": "SRR22729450",
        "gwh_transcripts_scanned": primer["gwh_transcripts_scanned"],
        "primer_compatible_transcripts": primer["compatible_transcripts"],
        "exact_primer_pair_transcripts": primer["exact_pair_transcripts"],
        "candidate_transcript": candidate["transcript_id"],
        "candidate_gene": "GWHGFILD004416.1",
        "candidate_original_gene": "Cpet02g11620",
        "candidate_bp": candidate["sequence_bp"],
        "candidate_sequence_sha256": candidate["sequence_sha256"],
        "primer_forward_mismatches": candidate["forward_mismatches"],
        "primer_reverse_mismatches": candidate["reverse_mismatches"],
        "primer_amplicon_bp": candidate["amplicon_bp"],
        "closest_reference": closest["sseqid"],
        "closest_reference_identity_percent": closest["pident"],
        "closest_reference_alignment_bp": closest["length"],
        "closest_reference_mismatches": closest["mismatch"],
        "closest_reference_gap_opens": closest["gapopen"],
        "closest_reference_query_coverage_percent": closest["qcovs"],
        "identity_margin_over_next_reference_percentage_points": round(identity_margin, 3),
        "exploratory_tree_newick": tree,
        "cds_panel": panel,
        "decision": decision,
        "chun_inference": (
            "The early pink-directed tea locus CSA008358 and the C. nitidissima "
            "CnFLS2-class candidate GWHTFILD005297.1 are likely counterparts, "
            "whereas the later white-directed CSA006950 belongs to a different "
            "FLS paralog. The apparent developmental FLS sign switch is therefore "
            "consistent with paralog substitution rather than reversal of one locus."
        ),
        "claim_ceiling": (
            "sequence-supported same-paralog/orthology hypothesis; do not call "
            "GWHTFILD005297.1 the exact F01.PB8395 source transcript until public "
            "PacBio reads/consensus recover it, and do not call formal orthology "
            "without broader FLS-family gene-tree and synteny evidence"
        ),
    }

    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    with args.csv_output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(hits[0]))
        writer.writeheader()
        writer.writerows(hits)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
