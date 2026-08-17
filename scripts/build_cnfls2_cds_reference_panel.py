#!/usr/bin/env python3
"""Build a coding-sequence panel for the recovered CnFLS2 GWH candidate."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path

import requests

TARGETS = ("CSA006950", "CSA008358")


def sha256_sequence(sequence: str) -> str:
    return hashlib.sha256(sequence.encode()).hexdigest()


def parse_fasta(text: str) -> list[tuple[str, str]]:
    records: list[tuple[str, str]] = []
    header: str | None = None
    seq: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith(">"):
            if header is not None:
                records.append((header.split()[0], "".join(seq).upper()))
            header, seq = line[1:].strip(), []
        elif header is not None:
            seq.append(re.sub(r"\s+", "", line))
    if header is not None:
        records.append((header.split()[0], "".join(seq).upper()))
    return records


def write_fasta(path: Path, records: list[tuple[str, str]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for name, sequence in records:
            handle.write(f">{name}\n")
            for start in range(0, len(sequence), 80):
                handle.write(sequence[start : start + 80] + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tpia-records", type=Path, required=True)
    parser.add_argument("--candidate-fasta", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    references: dict[str, str] = {}
    with args.tpia_records.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row.get("crosswalk_column") != "yk10" or row.get("sequence_type") != "cds":
                continue
            for target in TARGETS:
                if target in row.get("header", "") and target not in references:
                    references[target] = row["sequence"].upper()
    missing = [target for target in TARGETS if target not in references]
    if missing:
        raise SystemExit(f"Missing Yunkang10 CDS references: {missing}")

    session = requests.Session()
    session.headers["User-Agent"] = "chun-cnfls2-recovery/0.3 (public CDS panel)"
    response = session.get(
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
        params={"db": "nuccore", "id": "JF343560.1", "rettype": "fasta", "retmode": "text"},
        timeout=90,
    )
    response.raise_for_status()
    cnfls1 = parse_fasta(response.text)
    if len(cnfls1) != 1:
        raise SystemExit(f"Expected one CnFLS1 record, got {len(cnfls1)}")

    candidates = parse_fasta(args.candidate_fasta.read_text(encoding="utf-8"))
    if not candidates:
        raise SystemExit("Candidate FASTA is empty")

    panel = [
        ("tea_CSA006950_CDS", references["CSA006950"]),
        ("tea_CSA008358_CDS", references["CSA008358"]),
        ("CnFLS1_JF343560.1", cnfls1[0][1]),
    ]
    write_fasta(args.out_dir / "reference_sequences.fasta", panel)
    write_fasta(args.out_dir / "reference_and_candidates.fasta", panel + candidates)

    summary = {
        "reference_layer": "coding_sequence",
        "references": [
            {"name": name, "bp": len(sequence), "sha256": sha256_sequence(sequence)}
            for name, sequence in panel
        ],
        "candidates": [
            {"name": name, "bp": len(sequence), "sha256": sha256_sequence(sequence)}
            for name, sequence in candidates
        ],
        "decision": "compare recovered GWH mRNA candidate against CDS/cDNA references; intron-bearing TPIA transcript exports are excluded",
        "claim_ceiling": "coding-sequence similarity and exploratory gene placement; source-read recovery is still required for exact F01.PB8395 identity",
    }
    (args.out_dir / "cds_reference_panel_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
