#!/usr/bin/env python3
"""Build provenance-frozen FLS queries for SRR22729450.

The source CnFLS2 transcript F01.PB8395 is not publicly exposed as a full
sequence, but its qRT-PCR primer pair is public. This script retrieves the two
tea FLS paralogs already crosswalked in chun plus the published CnFLS1 cDNA,
then emits full-length, amplicon and primer query FASTA files for a targeted
blastn_vdb search of the F01 PacBio run.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import zipfile
from pathlib import Path
from urllib.parse import urlencode

import requests

TPIA = "https://tpia.teaplants.cn/getGeneSeqByGeneNames"
NCBI_EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
FWD = "AGCAATCACCACCGTCAAAGG"
REV = "CTCTTAGACTCAGCATCCTTAGC"
TEA = {"CSA008358_CSS0045924": "CSS0045924", "CSA006950_CSS0007745": "CSS0007745"}


def rc(seq: str) -> str:
    return seq.translate(str.maketrans("ACGTNacgtn", "TGCANtgcan"))[::-1]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_fasta(text: str) -> dict[str, str]:
    records: dict[str, str] = {}
    header: str | None = None
    parts: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith(">"):
            if header is not None:
                records[header.split("\t")[0].split()[0]] = "".join(parts).upper()
            header = line[1:]
            parts = []
        elif header is not None:
            parts.append(re.sub(r"\s+", "", line))
    if header is not None:
        records[header.split("\t")[0].split()[0]] = "".join(parts).upper()
    return records


def fetch_tpia_transcripts(session: requests.Session) -> tuple[dict[str, str], dict[str, object]]:
    params = {
        "geneNames": ",".join(TEA.values()),
        "cds": 0,
        "trans": 1,
        "exon": 0,
        "down": 0,
        "up": 0,
        "teaType": "Shuchazao2",
    }
    response = session.get(TPIA + "?" + urlencode(params), timeout=180)
    response.raise_for_status()
    raw = response.content
    records: dict[str, str] = {}
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        for name in archive.namelist():
            if name.lower().endswith(".txt"):
                records.update(parse_fasta(archive.read(name).decode("utf-8", errors="replace")))
    missing = [gene for gene in TEA.values() if gene not in records]
    if missing:
        raise SystemExit(f"TPIA transcript export missing required IDs: {missing}")
    return records, {
        "url": response.url,
        "sha256": digest(raw),
        "bytes": len(raw),
        "record_count": len(records),
    }


def fetch_ncbi_fasta(session: requests.Session, accession: str) -> tuple[str, dict[str, object]]:
    response = session.get(
        NCBI_EFETCH,
        params={"db": "nuccore", "id": accession, "rettype": "fasta", "retmode": "text"},
        timeout=90,
    )
    response.raise_for_status()
    records = parse_fasta(response.text)
    if not records:
        raise SystemExit(f"NCBI returned no FASTA record for {accession}")
    sequence = next(iter(records.values()))
    return sequence, {
        "accession": accession,
        "url": response.url,
        "sha256": digest(response.content),
        "bp": len(sequence),
    }


def exact_amplicon(sequence: str) -> tuple[str, int, int]:
    left = sequence.find(FWD)
    right_primer = rc(REV)
    candidates: list[tuple[int, int]] = []
    start = 0
    while True:
        pos = sequence.find(right_primer, start)
        if pos < 0:
            break
        if left >= 0 and pos >= left:
            candidates.append((left, pos + len(right_primer)))
        start = pos + 1
    if not candidates:
        raise SystemExit("CSA008358 transcript lacks the expected exact paired primer sites")
    begin, end = min(candidates, key=lambda pair: abs((pair[1] - pair[0]) - 246))
    return sequence[begin:end], begin, end


def write_fasta(path: Path, records: list[tuple[str, str]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for name, sequence in records:
            handle.write(f">{name}\n")
            for i in range(0, len(sequence), 80):
                handle.write(sequence[i : i + 80] + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers["User-Agent"] = "chun-cnfls2-sra-query/0.1 (public sequence audit)"

    tea_records, tea_meta = fetch_tpia_transcripts(session)
    cnfls1, cnfls1_meta = fetch_ncbi_fasta(session, "JF343560.1")

    full_records: list[tuple[str, str]] = []
    manifest: list[dict[str, object]] = []
    for label, gene_id in TEA.items():
        sequence = tea_records[gene_id]
        query_id = f"tea_{label}"
        full_records.append((query_id, sequence))
        manifest.append(
            {
                "query_id": query_id,
                "source_id": gene_id,
                "query_class": "full_transcript",
                "bp": len(sequence),
                "sha256": digest(sequence.encode()),
                "role": "tea_FLS_paralog_reference",
            }
        )
    full_records.append(("cnitidissima_CnFLS1_JF343560_1", cnfls1))
    manifest.append(
        {
            "query_id": "cnitidissima_CnFLS1_JF343560_1",
            "source_id": "JF343560.1",
            "query_class": "full_cDNA",
            "bp": len(cnfls1),
            "sha256": digest(cnfls1.encode()),
            "role": "published_CnFLS1_outgroup_reference",
        }
    )

    amplicon, amp_start, amp_end = exact_amplicon(tea_records[TEA["CSA008358_CSS0045924"]])
    if len(amplicon) != 246:
        raise SystemExit(f"Expected 246-bp CSA008358 amplicon, recovered {len(amplicon)} bp")

    write_fasta(args.output_dir / "full_queries.fasta", full_records)
    write_fasta(args.output_dir / "amplicon_query.fasta", [("tea_CSA008358_CnFLS2_like_amplicon_246bp", amplicon)])
    write_fasta(
        args.output_dir / "primer_queries.fasta",
        [("CnFLS2_forward_primer", FWD), ("CnFLS2_reverse_primer", REV)],
    )

    with (args.output_dir / "query_manifest.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(manifest[0]))
        writer.writeheader()
        writer.writerows(manifest)

    summary = {
        "source_transcript": "F01.PB8395",
        "source_class": "CnFLS2",
        "source_forward_primer": FWD,
        "source_reverse_primer": REV,
        "tpia_transcript_export": tea_meta,
        "cnfls1_fetch": cnfls1_meta,
        "amplicon_query_bp": len(amplicon),
        "amplicon_start_0based": amp_start,
        "amplicon_end_exclusive": amp_end,
        "amplicon_sha256": digest(amplicon.encode()),
        "decision": "queries are suitable for targeted SRR22729450 blastn_vdb screening",
        "claim_ceiling": "query construction and local amplicon provenance only; no F01.PB8395 read or formal orthology recovered yet",
    }
    (args.output_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
