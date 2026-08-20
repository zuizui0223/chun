#!/usr/bin/env python3
"""Add frozen ecological-anchor/outgroup proteins to the 339 runtime91 alignments.

The existing runtime91 alignment is immutable. Extra sequences are aligned only into
its existing columns with MAFFT --add --keeplength, and the script verifies that every
pre-existing aligned sequence is byte-identical afterwards.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import tempfile
from pathlib import Path


def read_fasta(path: Path) -> list[tuple[str, str]]:
    records: list[tuple[str, str]] = []
    name: str | None = None
    seq: list[str] = []
    with path.open(encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if not line:
                continue
            if line.startswith(">"):
                if name is not None:
                    records.append((name, "".join(seq)))
                name = line[1:].split()[0]
                seq = []
            else:
                if name is None:
                    raise SystemExit(f"sequence before header in {path}")
                seq.append(line)
    if name is not None:
        records.append((name, "".join(seq)))
    if not records:
        raise SystemExit(f"empty FASTA: {path}")
    return records


def write_fasta(path: Path, records: list[tuple[str, str]]) -> None:
    with path.open("w", encoding="utf-8") as out:
        for name, seq in records:
            out.write(f">{name}\n")
            for i in range(0, len(seq), 80):
                out.write(seq[i : i + 80] + "\n")


def extra_markers(path: Path) -> tuple[str, dict[str, str]]:
    records = read_fasta(path)
    taxon: str | None = None
    by_locus: dict[str, str] = {}
    for header, seq in records:
        parts = header.split("|")
        if len(parts) < 2 or not parts[1].startswith("locus_"):
            raise SystemExit(f"unexpected marker header in {path}: {header}")
        this_taxon = parts[0]
        locus = parts[1].split("locus_", 1)[1]
        if taxon is None:
            taxon = this_taxon
        elif taxon != this_taxon:
            raise SystemExit(f"multiple taxon labels in {path}: {taxon}, {this_taxon}")
        if locus in by_locus:
            raise SystemExit(f"duplicate locus {locus} in {path}")
        by_locus[locus] = seq.replace("-", "")
    assert taxon is not None
    return taxon, by_locus


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-alignments", type=Path, required=True)
    ap.add_argument("--extra-markers", type=Path, action="append", required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--expected-loci", type=int, default=339)
    args = ap.parse_args()

    base_files = sorted(args.base_alignments.rglob("locus_*.aln.faa"))
    if len(base_files) != args.expected_loci:
        raise SystemExit(f"expected {args.expected_loci} base alignments, found {len(base_files)}")

    extras: dict[str, dict[str, str]] = {}
    for path in args.extra_markers:
        taxon, loci = extra_markers(path)
        if taxon in extras:
            raise SystemExit(f"duplicate extra taxon: {taxon}")
        extras[taxon] = loci

    expected_extra_counts = {
        "Camellia_japonica": 332,
        "Camellia_nitidissima": 338,
        "Polyspora_speciosa": 338,
    }
    for taxon, expected in expected_extra_counts.items():
        if taxon not in extras:
            raise SystemExit(f"required extra taxon missing: {taxon}")
        if len(extras[taxon]) != expected:
            raise SystemExit(f"{taxon}: expected {expected} frozen loci, found {len(extras[taxon])}")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, object]] = []
    added_counts = {t: 0 for t in extras}
    min_base_taxa = 10**9
    max_base_taxa = 0
    min_expanded_taxa = 10**9
    max_expanded_taxa = 0

    for base in base_files:
        m = re.fullmatch(r"locus_(\d+)\.aln\.faa", base.name)
        if not m:
            raise SystemExit(f"unexpected alignment name: {base.name}")
        locus = m.group(1)
        original = read_fasta(base)
        original_map = dict(original)
        if len(original_map) != len(original):
            raise SystemExit(f"duplicate base taxon header in {base}")
        lengths = {len(seq) for _, seq in original}
        if len(lengths) != 1:
            raise SystemExit(f"base alignment has unequal lengths: {base}")
        base_len = next(iter(lengths))
        additions: list[tuple[str, str]] = []
        for taxon, loci in extras.items():
            if taxon in original_map:
                raise SystemExit(f"extra taxon already exists in base alignment: {taxon}, locus {locus}")
            seq = loci.get(locus)
            if seq:
                additions.append((taxon, seq))
                added_counts[taxon] += 1

        out_path = args.out_dir / base.name
        if additions:
            with tempfile.TemporaryDirectory(prefix=f"add_{locus}_") as td:
                add_path = Path(td) / "additions.faa"
                write_fasta(add_path, additions)
                proc = subprocess.run(
                    [
                        "mafft",
                        "--amino",
                        "--quiet",
                        "--thread",
                        "1",
                        "--add",
                        str(add_path),
                        "--keeplength",
                        str(base),
                    ],
                    check=True,
                    text=True,
                    capture_output=True,
                )
                out_path.write_text(proc.stdout, encoding="utf-8")
        else:
            out_path.write_text(base.read_text(encoding="utf-8"), encoding="utf-8")

        expanded = read_fasta(out_path)
        expanded_map = dict(expanded)
        if len(expanded_map) != len(expanded):
            raise SystemExit(f"duplicate expanded header at locus {locus}")
        for taxon, seq in original_map.items():
            if expanded_map.get(taxon) != seq:
                raise SystemExit(f"immutable runtime91 alignment changed: {taxon}, locus {locus}")
        for taxon, _ in additions:
            if taxon not in expanded_map:
                raise SystemExit(f"MAFFT failed to add {taxon} at locus {locus}")
        expanded_lengths = {len(seq) for _, seq in expanded}
        if expanded_lengths != {base_len}:
            raise SystemExit(f"expanded alignment length drift at locus {locus}: {expanded_lengths} vs {base_len}")

        n_base = len(original)
        n_expanded = len(expanded)
        min_base_taxa = min(min_base_taxa, n_base)
        max_base_taxa = max(max_base_taxa, n_base)
        min_expanded_taxa = min(min_expanded_taxa, n_expanded)
        max_expanded_taxa = max(max_expanded_taxa, n_expanded)
        rows.append(
            {
                "locus": locus,
                "alignment_length_aa": base_len,
                "base_taxa": n_base,
                "expanded_taxa": n_expanded,
                "added_Camellia_japonica": int("Camellia_japonica" in expanded_map),
                "added_Camellia_nitidissima": int("Camellia_nitidissima" in expanded_map),
                "added_Polyspora_speciosa": int("Polyspora_speciosa" in expanded_map),
            }
        )

    for taxon, expected in expected_extra_counts.items():
        if added_counts[taxon] != expected:
            raise SystemExit(f"{taxon}: added to {added_counts[taxon]} loci, expected {expected}")

    with args.manifest.open("w", newline="", encoding="utf-8") as fh:
        fields = list(rows[0])
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    summary = {
        "base_runtime_taxa": 91,
        "camellia_ecological_anchor_taxa_added": 2,
        "outgroup_taxa_added": 1,
        "maximum_tip_set": 94,
        "frozen_loci": args.expected_loci,
        "expanded_alignments": len(rows),
        "added_loci_by_taxon": added_counts,
        "missing_loci_by_taxon": {
            taxon: sorted(set(re.search(r"locus_(\d+)", p.name).group(1) for p in base_files) - set(loci), key=int)
            for taxon, loci in extras.items()
        },
        "min_base_taxa_per_locus": min_base_taxa,
        "max_base_taxa_per_locus": max_base_taxa,
        "min_expanded_taxa_per_locus": min_expanded_taxa,
        "max_expanded_taxa_per_locus": max_expanded_taxa,
        "alignment_rule": "MAFFT --add --keeplength; all runtime91 aligned sequences verified byte-identical after expansion",
        "claim_ceiling": "frozen nuclear alignment expansion only; no topology, rooting, flower-colour history, or ecological causation inferred",
    }
    args.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
