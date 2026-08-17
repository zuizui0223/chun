#!/usr/bin/env python3
"""Translate the admitted CnFLS2-like CDS into a protein query."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from Bio import SeqIO
from Bio.SeqRecord import SeqRecord


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cds", type=Path, required=True)
    parser.add_argument("--protein", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    args = parser.parse_args()

    records = list(SeqIO.parse(args.cds, "fasta"))
    if len(records) != 1:
        raise SystemExit(f"Expected one CDS record, found {len(records)}")
    cds = records[0].seq.upper()
    if len(cds) % 3:
        raise SystemExit(f"CDS length is not divisible by 3: {len(cds)}")
    translated = cds.translate(to_stop=False)
    if translated.endswith("*"):
        translated = translated[:-1]
    if "*" in str(translated):
        raise SystemExit("Candidate CDS contains an internal stop codon")
    if len(translated) < 250:
        raise SystemExit(f"Translated protein unexpectedly short: {len(translated)} aa")

    output = SeqRecord(
        translated,
        id="GWHPFILD005297.1",
        description="translated_from_GWHTFILD005297.1 CnFLS2-like candidate",
    )
    args.protein.parent.mkdir(parents=True, exist_ok=True)
    SeqIO.write([output], args.protein, "fasta")

    summary = {
        "source_cds_id": records[0].id,
        "protein_id": output.id,
        "cds_bp": len(cds),
        "protein_aa": len(translated),
        "cds_sha256": hashlib.sha256(str(cds).encode()).hexdigest(),
        "protein_sha256": hashlib.sha256(str(translated).encode()).hexdigest(),
        "decision": "protein query admitted for whole-proteome and local-synteny searches",
        "claim_ceiling": "translation of an admitted CDS only; no orthology inferred",
    }
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
