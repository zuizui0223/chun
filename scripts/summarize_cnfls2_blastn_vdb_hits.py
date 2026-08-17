#!/usr/bin/env python3
"""Summarize targeted blastn_vdb hits against SRR22729450.

This is a discovery/provenance step. It ranks SRA subjects using full-transcript,
amplicon and primer evidence without converting the whole 18.7-Gb PacBio run.
The output is designed to identify a small set of spots for later extraction.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import defaultdict
from pathlib import Path

FIELDS = [
    "qseqid",
    "sseqid",
    "pident",
    "length",
    "mismatch",
    "gapopen",
    "qstart",
    "qend",
    "sstart",
    "send",
    "evalue",
    "bitscore",
    "qlen",
    "slen",
    "sseq",
]
RUN = "SRR22729450"


def fnum(value: str, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def inum(value: str, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def read_hits(path: Path, source: str) -> list[dict[str, object]]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    rows: list[dict[str, object]] = []
    with path.open(encoding="utf-8", errors="replace") as handle:
        reader = csv.DictReader(handle, fieldnames=FIELDS, delimiter="\t")
        for raw in reader:
            if not raw.get("qseqid") or not raw.get("sseqid"):
                continue
            qlen = max(1, inum(raw.get("qlen", "0"), 1))
            aln_len = inum(raw.get("length", "0"))
            row: dict[str, object] = dict(raw)
            row.update(
                {
                    "source": source,
                    "pident_num": fnum(raw.get("pident", "0")),
                    "length_num": aln_len,
                    "bitscore_num": fnum(raw.get("bitscore", "0")),
                    "qcov": min(1.0, aln_len / qlen),
                    "qlen_num": qlen,
                    "slen_num": inum(raw.get("slen", "0")),
                }
            )
            rows.append(row)
    return rows


def spot_id_from_subject(subject: str) -> int | None:
    patterns = [
        rf"{RUN}[./_](\d+)",
        rf"{RUN}\.(\d+)(?:\.|$)",
        r"(?:^|[|./_])(\d{1,12})(?:[./_]|$)",
    ]
    for pattern in patterns:
        match = re.search(pattern, subject)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                pass
    return None


def choose_best(rows: list[dict[str, object]]) -> dict[str, object] | None:
    if not rows:
        return None
    return max(
        rows,
        key=lambda row: (
            float(row["bitscore_num"]),
            float(row["qcov"]),
            float(row["pident_num"]),
            int(row["length_num"]),
        ),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--full-hits", type=Path, required=True)
    parser.add_argument("--amplicon-hits", type=Path, required=True)
    parser.add_argument("--primer-hits", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--max-candidates", type=int, default=50)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    full = read_hits(args.full_hits, "full")
    amplicon = read_hits(args.amplicon_hits, "amplicon")
    primers = read_hits(args.primer_hits, "primer")
    all_rows = full + amplicon + primers

    by_subject: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in all_rows:
        by_subject[str(row["sseqid"])].append(row)

    candidates: list[dict[str, object]] = []
    for subject, rows in by_subject.items():
        full_rows = [row for row in rows if row["source"] == "full"]
        amp_rows = [row for row in rows if row["source"] == "amplicon"]
        primer_rows = [row for row in rows if row["source"] == "primer"]
        best_full = choose_best(full_rows)
        best_amp = choose_best(amp_rows)
        primer_queries = sorted({str(row["qseqid"]) for row in primer_rows})
        exact_source_name = "F01.PB8395" in subject

        full_qcov = float(best_full["qcov"]) if best_full else 0.0
        full_identity = float(best_full["pident_num"]) if best_full else 0.0
        full_length = int(best_full["length_num"]) if best_full else 0
        amp_qcov = float(best_amp["qcov"]) if best_amp else 0.0
        amp_identity = float(best_amp["pident_num"]) if best_amp else 0.0
        primer_count = len(primer_queries)

        eligible = (
            exact_source_name
            or (full_qcov >= 0.40 and full_identity >= 65.0 and full_length >= 300)
            or (amp_qcov >= 0.55 and amp_identity >= 65.0)
            or primer_count >= 2
        )
        if not eligible:
            continue

        spot_id = spot_id_from_subject(subject)
        rank_score = (
            (10000.0 if exact_source_name else 0.0)
            + 1500.0 * primer_count
            + 1200.0 * amp_qcov
            + 6.0 * amp_identity
            + 800.0 * full_qcov
            + 4.0 * full_identity
            + math.log1p(max(0, full_length)) * 10.0
        )
        candidates.append(
            {
                "rank_score": round(rank_score, 6),
                "sseqid": subject,
                "spot_id": spot_id if spot_id is not None else "",
                "source_name_exact": "yes" if exact_source_name else "no",
                "primer_query_count": primer_count,
                "primer_queries": ";".join(primer_queries),
                "best_amplicon_qcov": round(amp_qcov, 6),
                "best_amplicon_pident": round(amp_identity, 6),
                "best_amplicon_bitscore": round(float(best_amp["bitscore_num"]), 6) if best_amp else "",
                "best_full_query": str(best_full["qseqid"]) if best_full else "",
                "best_full_qcov": round(full_qcov, 6),
                "best_full_pident": round(full_identity, 6),
                "best_full_length": full_length,
                "best_full_bitscore": round(float(best_full["bitscore_num"]), 6) if best_full else "",
                "subject_length": int(best_full["slen_num"]) if best_full else (int(best_amp["slen_num"]) if best_amp else ""),
                "claim_boundary": "targeted SRA search candidate only; spot extraction and primer/full-length validation required",
            }
        )

    candidates.sort(key=lambda row: float(row["rank_score"]), reverse=True)
    candidates = candidates[: args.max_candidates]
    fields = [
        "rank_score",
        "sseqid",
        "spot_id",
        "source_name_exact",
        "primer_query_count",
        "primer_queries",
        "best_amplicon_qcov",
        "best_amplicon_pident",
        "best_amplicon_bitscore",
        "best_full_query",
        "best_full_qcov",
        "best_full_pident",
        "best_full_length",
        "best_full_bitscore",
        "subject_length",
        "claim_boundary",
    ]
    with (args.output_dir / "candidate_subjects.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(candidates)

    spot_ids = sorted({int(row["spot_id"]) for row in candidates if str(row["spot_id"]).isdigit()})
    (args.output_dir / "candidate_spot_ids.txt").write_text(
        "".join(f"{spot}\n" for spot in spot_ids), encoding="utf-8"
    )

    summary = {
        "run": RUN,
        "full_hit_rows": len(full),
        "amplicon_hit_rows": len(amplicon),
        "primer_hit_rows": len(primers),
        "unique_subjects_with_any_hit": len(by_subject),
        "eligible_candidate_subjects": len(candidates),
        "candidate_subjects_with_numeric_spot_id": len(spot_ids),
        "source_name_exact_matches": sum(row["source_name_exact"] == "yes" for row in candidates),
        "decision": "extract ranked numeric spots next" if spot_ids else "no extractable numeric spot IDs yet; inspect blastn_vdb subject naming or use streaming fallback",
        "claim_ceiling": "targeted hit discovery only; no candidate read has yet been extracted or assigned to F01.PB8395",
    }
    (args.output_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if not candidates:
        raise SystemExit("No eligible CnFLS2/FLS candidate subjects were found")


if __name__ == "__main__":
    main()
