#!/usr/bin/env python3
"""Map the published CnFLS2 qRT-PCR primer pair to public GWH transcripts.

Feng 2024 groups F01.PB8395 with CnFLS2 and reports its primer pair. This
script scans the public C. nitidissima GWH RNA FASTA for compatible full-length
transcripts, then writes those candidates beside the two tea FLS source
paralogs and published CnFLS1 cDNA. Primer compatibility narrows a paralog
hypothesis; it does not prove F01.PB8395 identity or formal orthology.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import re
from pathlib import Path
from typing import Iterable, Iterator

import requests

FWD = "AGCAATCACCACCGTCAAAGG"
REV = "CTCTTAGACTCAGCATCCTTAGC"
EXPECTED_AMPLICON_BP = 246
TEA_TARGETS = ("CSA006950", "CSA008358")
KNOWN_GWH_FLS = {
    "GWHTFILD024733.1": "CnFLS1 genome anchor",
    "GWHTFILD005297.1": "distant FLS-family candidate",
    "GWHTFILD024731.1": "adjacent developmentally differentiated FLS-family candidate",
}


def rc(seq: str) -> str:
    return seq.translate(str.maketrans("ACGTNacgtn", "TGCANtgcan"))[::-1]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def fasta_records_gz(path: Path) -> Iterator[tuple[str, str, str]]:
    header: str | None = None
    seq: list[str] = []
    with gzip.open(path, "rt", encoding="utf-8", errors="replace") as handle:
        for raw in handle:
            line = raw.strip()
            if not line:
                continue
            if line.startswith(">"):
                if header is not None:
                    yield header.split()[0], header, "".join(seq).upper()
                header, seq = line[1:].strip(), []
            elif header is not None:
                seq.append(re.sub(r"\s+", "", line))
    if header is not None:
        yield header.split()[0], header, "".join(seq).upper()


def fasta_records_text(text: str) -> Iterator[tuple[str, str, str]]:
    header: str | None = None
    seq: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith(">"):
            if header is not None:
                yield header.split()[0], header, "".join(seq).upper()
            header, seq = line[1:].strip(), []
        elif header is not None:
            seq.append(re.sub(r"\s+", "", line))
    if header is not None:
        yield header.split()[0], header, "".join(seq).upper()


def hamming_hits(seq: str, primer: str, max_mismatches: int) -> list[tuple[int, int]]:
    """Return (mismatches,start) via an exact-seed pigeonhole search."""
    length = len(primer)
    parts = max_mismatches + 1
    cuts = [round(i * length / parts) for i in range(parts + 1)]
    starts: set[int] = set()
    for index in range(parts):
        left, right = cuts[index], cuts[index + 1]
        seed = primer[left:right]
        pos = seq.find(seed)
        while pos >= 0:
            start = pos - left
            if 0 <= start <= len(seq) - length:
                starts.add(start)
            pos = seq.find(seed, pos + 1)
    hits = []
    for start in starts:
        window = seq[start : start + length]
        mismatches = sum(a != b for a, b in zip(window, primer))
        if mismatches <= max_mismatches:
            hits.append((mismatches, start))
    return sorted(hits)


def best_pair(seq: str, max_mismatches: int, max_product: int) -> dict[str, int] | None:
    reverse_target = rc(REV)
    pairs = []
    for fm, fp in hamming_hits(seq, FWD, max_mismatches):
        for rm, rp in hamming_hits(seq, reverse_target, max_mismatches):
            product = rp + len(reverse_target) - fp
            if rp > fp and 80 <= product <= max_product:
                pairs.append((fm + rm, abs(product - EXPECTED_AMPLICON_BP), fm, rm, product, fp, rp))
    if not pairs:
        return None
    total, _, fm, rm, product, fp, rp = min(pairs)
    return {
        "total_mismatches": total,
        "forward_mismatches": fm,
        "reverse_mismatches": rm,
        "forward_start_0based": fp,
        "reverse_start_0based": rp,
        "amplicon_bp": product,
    }


def write_fasta(path: Path, records: Iterable[tuple[str, str]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for name, seq in records:
            handle.write(f">{name}\n")
            for start in range(0, len(seq), 80):
                handle.write(seq[start : start + 80] + "\n")


def load_tea_references(path: Path) -> dict[str, str]:
    selected: dict[str, str] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row.get("crosswalk_column") != "yk10" or row.get("sequence_type") != "transcript":
                continue
            header = row.get("header", "")
            for target in TEA_TARGETS:
                if target in header and target not in selected:
                    selected[target] = row["sequence"].upper()
    missing = [target for target in TEA_TARGETS if target not in selected]
    if missing:
        raise SystemExit(f"Missing Yunkang10 transcript reference(s): {missing}")
    return selected


def fetch_ncbi_fasta(session: requests.Session, accession: str) -> tuple[str, dict[str, object]]:
    response = session.get(
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
        params={"db": "nuccore", "id": accession, "rettype": "fasta", "retmode": "text"},
        timeout=90,
    )
    response.raise_for_status()
    records = list(fasta_records_text(response.text))
    if len(records) != 1:
        raise SystemExit(f"Expected one FASTA record for {accession}, got {len(records)}")
    _, header, seq = records[0]
    return seq, {
        "accession": accession,
        "header": header,
        "bp": len(seq),
        "response_sha256": sha256_bytes(response.content),
        "url": response.url,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gwh-rna", type=Path, required=True)
    parser.add_argument("--tpia-records", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--max-primer-mismatches", type=int, default=2)
    parser.add_argument("--max-product", type=int, default=1200)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    tea = load_tea_references(args.tpia_records)
    session = requests.Session()
    session.headers["User-Agent"] = "chun-cnfls2-recovery/0.2 (public sequence audit)"
    cnfls1, cnfls1_meta = fetch_ncbi_fasta(session, "JF343560.1")

    candidates: list[dict[str, object]] = []
    sequences: dict[str, str] = {}
    n_transcripts = 0
    for transcript_id, header, source_seq in fasta_records_gz(args.gwh_rna):
        n_transcripts += 1
        best = None
        for orientation, oriented in (("source", source_seq), ("reverse_complement", rc(source_seq))):
            pair = best_pair(oriented, args.max_primer_mismatches, args.max_product)
            if pair is None:
                continue
            key = (pair["total_mismatches"], abs(pair["amplicon_bp"] - EXPECTED_AMPLICON_BP))
            if best is None or key < best[0]:
                best = (key, orientation, pair, oriented)
        if best is None:
            continue
        _, orientation, pair, oriented_seq = best
        safe_id = transcript_id.replace("|", "_")
        sequences[safe_id] = oriented_seq
        candidates.append(
            {
                "transcript_id": transcript_id,
                "header": header,
                "orientation_used": orientation,
                "sequence_bp": len(oriented_seq),
                "sequence_sha256": sha256_bytes(oriented_seq.encode()),
                **pair,
                "expected_amplicon_bp": EXPECTED_AMPLICON_BP,
                "known_gwh_fls_status": KNOWN_GWH_FLS.get(transcript_id, "not_in_predeclared_three_locus_panel"),
                "claim_boundary": "primer-compatible GWH transcript candidate; not yet proven identical to F01.PB8395",
            }
        )

    candidates.sort(key=lambda row: (int(row["total_mismatches"]), abs(int(row["amplicon_bp"]) - EXPECTED_AMPLICON_BP), str(row["transcript_id"])))
    candidate_fasta = [(str(row["transcript_id"]).replace("|", "_"), sequences[str(row["transcript_id"]).replace("|", "_")]) for row in candidates]
    fields = [
        "transcript_id", "header", "orientation_used", "sequence_bp", "sequence_sha256",
        "total_mismatches", "forward_mismatches", "reverse_mismatches",
        "forward_start_0based", "reverse_start_0based", "amplicon_bp",
        "expected_amplicon_bp", "known_gwh_fls_status", "claim_boundary",
    ]
    with (args.out_dir / "gwh_primer_candidates.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(candidates)

    references = [
        ("tea_CSA006950", tea["CSA006950"]),
        ("tea_CSA008358", tea["CSA008358"]),
        ("CnFLS1_JF343560.1", cnfls1),
    ]
    write_fasta(args.out_dir / "candidate_sequences.fasta", candidate_fasta)
    write_fasta(args.out_dir / "reference_sequences.fasta", references)
    write_fasta(args.out_dir / "reference_and_candidates.fasta", references + candidate_fasta)

    summary = {
        "source_transcript": "F01.PB8395",
        "source_class": "CnFLS2",
        "source_forward_primer": FWD,
        "source_reverse_primer": REV,
        "expected_amplicon_bp_from_tea_exact_match": EXPECTED_AMPLICON_BP,
        "gwh_rna_path": str(args.gwh_rna),
        "gwh_rna_file_sha256": sha256_file(args.gwh_rna),
        "gwh_transcripts_scanned": n_transcripts,
        "max_mismatches_per_primer": args.max_primer_mismatches,
        "compatible_transcripts": len(candidates),
        "exact_pair_transcripts": sum(int(row["total_mismatches"]) == 0 for row in candidates),
        "best_candidate": candidates[0] if candidates else None,
        "predeclared_known_fls_candidates_recovered": [row["transcript_id"] for row in candidates if row["transcript_id"] in KNOWN_GWH_FLS],
        "cnfls1_reference": cnfls1_meta,
        "decision": "GWH primer-compatible full-length candidate(s) recovered; compare sequence placement before any strict orthology claim" if candidates else "no compatible GWH transcript recovered under declared bounds",
        "claim_ceiling": "GWH annotation and local primer compatibility only; F01.PB8395 identity still requires PacBio source-read or consensus recovery",
    }
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if not candidates:
        raise SystemExit("No primer-compatible GWH transcript candidate recovered")


if __name__ == "__main__":
    main()
