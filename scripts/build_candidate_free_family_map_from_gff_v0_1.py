#!/usr/bin/env python3
"""Map annotated Camellia transcripts to preregistered pigment gene families.

The mapping is deliberately annotation-driven and independent of flower-colour outcome.
All transcript paralogs whose gene symbol/product annotation matches a frozen family
pattern are retained. The script never selects transcripts by differential expression.

Inputs:
- NCBI/GenBank GFF3 annotation
- corresponding transcript/RNA FASTA

Outputs:
- transcript_family_map.csv
- family_mapping_summary.json
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import unquote

PATTERNS: dict[str, list[str]] = {
    "CHS": [r"\bCHS\d*\b", r"chalcone synthase"],
    "CHI": [r"\bCHI\d*\b", r"chalcone isomerase"],
    "F3H": [r"\bF3H\d*\b", r"flavanone 3[- ]hydroxylase"],
    "F3'H": [r"\bF3['′]?H\d*\b", r"flavonoid 3['′][- ]hydroxylase"],
    "F3'5'H": [r"\bF3['′]?5['′]?H\d*\b", r"flavonoid 3['′],?5['′][- ]hydroxylase"],
    "DFR": [r"\bDFR\d*\b", r"dihydroflavonol 4[- ]reductase"],
    "ANS/LDOX": [r"\bANS\d*\b", r"\bLDOX\d*\b", r"anthocyanidin synthase", r"leucoanthocyanidin dioxygenase"],
    "UFGT/3GT": [r"\bUFGT\d*\b", r"anthocyanidin 3[- ]O[- ]glucosyltransferase", r"flavonoid 3[- ]O[- ]glucosyltransferase"],
    "FLS": [r"\bFLS\d*\b", r"flavonol synthase"],
    "ANR": [r"\bANR\d*\b", r"\bBANYULS\b", r"anthocyanidin reductase"],
    "LAR": [r"\bLAR\d*\b", r"leucoanthocyanidin reductase"],
    "PSY": [r"\bPSY\d*\b", r"phytoene synthase"],
    "PDS": [r"\bPDS\d*\b", r"phytoene desaturase"],
    "ZDS": [r"\bZDS\d*\b", r"zeta[- ]carotene desaturase", r"ζ[- ]carotene desaturase"],
    "CRTISO": [r"\bCRTISO\d*\b", r"carotenoid isomerase"],
    "LCYB": [r"\bLCYB\d*\b", r"lycopene beta[- ]cyclase", r"lycopene β[- ]cyclase"],
    "LCYE": [r"\bLCYE\d*\b", r"lycopene epsilon[- ]cyclase", r"lycopene ε[- ]cyclase"],
    "BCH": [r"\bBCH\d*\b", r"beta[- ]carotene hydroxylase", r"β[- ]carotene hydroxylase", r"beta[- ]ring hydroxylase"],
    "ZEP": [r"\bZEP\d*\b", r"zeaxanthin epoxidase"],
}
COMPILED = {k: [re.compile(p, re.I) for p in ps] for k, ps in PATTERNS.items()}


def attrs(text: str) -> dict[str, str]:
    out = {}
    for part in text.strip().split(";"):
        if not part:
            continue
        if "=" in part:
            k, v = part.split("=", 1)
            out[k] = unquote(v)
    return out


def family_matches(text: str) -> list[str]:
    found = []
    for family, patterns in COMPILED.items():
        if any(p.search(text) for p in patterns):
            found.append(family)
    # Avoid classifying F3'5'H as F3'H when both symbols happen to match text.
    if "F3'5'H" in found and "F3'H" in found:
        found.remove("F3'H")
    return found


def normalize_id(x: str) -> str:
    x = x.strip()
    for prefix in ("rna-", "gene-", "cds-"):
        if x.startswith(prefix):
            x = x[len(prefix):]
    if x.startswith("lcl|"):
        x = x[4:]
    return x


def fasta_headers(path: Path) -> dict[str, str]:
    out = {}
    with path.open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if not line.startswith(">"):
                continue
            header = line[1:].strip()
            token = header.split()[0]
            aliases = {token, normalize_id(token)}
            if "|" in token:
                aliases.add(token.split("|")[-1])
                aliases.add(normalize_id(token.split("|")[-1]))
            # Common NCBI headers expose accession or transcript identifiers in brackets.
            for m in re.finditer(r"(?:transcript_id|gene|locus_tag)=([^\]\s]+)", header):
                aliases.add(m.group(1))
                aliases.add(normalize_id(m.group(1)))
            for alias in aliases:
                out[alias] = header
    return out


def parse_gff(path: Path) -> tuple[dict[str, tuple[str, str]], dict[str, set[str]], list[dict[str, str]]]:
    gene_family: dict[str, tuple[str, str]] = {}
    gene_alias_family: dict[str, tuple[str, str]] = {}
    transcript_parents: dict[str, set[str]] = defaultdict(set)
    transcript_rows: list[dict[str, str]] = []

    raw = []
    with path.open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if not line or line.startswith("#"):
                continue
            cols = line.rstrip("\n").split("\t")
            if len(cols) != 9:
                continue
            feature = cols[2]
            a = attrs(cols[8])
            raw.append((feature, a, cols[8]))
            if feature == "gene":
                text = " ".join([cols[8], *a.values()])
                matches = family_matches(text)
                if len(matches) == 1:
                    gid = a.get("ID", "")
                    evidence = text
                    if gid:
                        gene_family[gid] = (matches[0], evidence)
                        gene_alias_family[normalize_id(gid)] = (matches[0], evidence)
                    for key in ("Name", "gene", "locus_tag"):
                        if a.get(key):
                            gene_alias_family[a[key]] = (matches[0], evidence)
                            gene_alias_family[normalize_id(a[key])] = (matches[0], evidence)

    for feature, a, raw_attr in raw:
        if feature not in {"mRNA", "transcript", "ncRNA", "RNA"}:
            continue
        tid = a.get("ID") or a.get("transcript_id") or a.get("Name")
        if not tid:
            continue
        parent_values = []
        if a.get("Parent"):
            parent_values.extend(a["Parent"].split(","))
        if a.get("gene"):
            parent_values.append(a["gene"])
        if a.get("gene_id"):
            parent_values.append(a["gene_id"])
        for p in parent_values:
            transcript_parents[tid].add(p)

        direct_text = " ".join([raw_attr, *a.values()])
        direct = family_matches(direct_text)
        candidates: list[tuple[str, str, str]] = []
        if len(direct) == 1:
            candidates.append((direct[0], "transcript_annotation", direct_text))
        for p in parent_values:
            if p in gene_family:
                candidates.append((gene_family[p][0], "parent_gene_annotation", gene_family[p][1]))
            elif normalize_id(p) in gene_alias_family:
                fam, ev = gene_alias_family[normalize_id(p)]
                candidates.append((fam, "parent_gene_alias", ev))
        families = {x[0] for x in candidates}
        if len(families) == 1:
            fam = next(iter(families))
            transcript_rows.append(
                {
                    "gff_transcript_id": tid,
                    "gene_family": fam,
                    "mapping_basis": "+".join(sorted({x[1] for x in candidates})),
                    "annotation_evidence": candidates[0][2],
                }
            )
    return gene_family, transcript_parents, transcript_rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gff", type=Path, required=True)
    ap.add_argument("--rna-fasta", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()

    headers = fasta_headers(args.rna_fasta)
    _genes, _parents, gff_rows = parse_gff(args.gff)

    resolved = []
    unresolved = []
    seen = set()
    for row in gff_rows:
        gff_id = row["gff_transcript_id"]
        aliases = [gff_id, normalize_id(gff_id)]
        match = next((a for a in aliases if a in headers), None)
        if match is None:
            # Search exact token aliases only; never fuzzy-match sequence IDs.
            unresolved.append(row)
            continue
        header = headers[match]
        fasta_token = header.split()[0]
        key = (fasta_token, row["gene_family"])
        if key in seen:
            continue
        seen.add(key)
        resolved.append(
            {
                "transcript_id": fasta_token,
                "gene_family": row["gene_family"],
                "mapping_basis": row["mapping_basis"],
                "gff_transcript_id": gff_id,
                "fasta_header": header,
            }
        )

    # Fallback: annotation-bearing RNA FASTA headers can independently establish family.
    existing_transcripts = {r["transcript_id"] for r in resolved}
    for alias, header in headers.items():
        token = header.split()[0]
        if alias != token or token in existing_transcripts:
            continue
        matches = family_matches(header)
        if len(matches) == 1:
            resolved.append(
                {
                    "transcript_id": token,
                    "gene_family": matches[0],
                    "mapping_basis": "rna_fasta_annotation",
                    "gff_transcript_id": "",
                    "fasta_header": header,
                }
            )
            existing_transcripts.add(token)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    map_path = args.out_dir / "transcript_family_map.csv"
    with map_path.open("w", newline="", encoding="utf-8") as fh:
        fields = ["transcript_id", "gene_family", "mapping_basis", "gff_transcript_id", "fasta_header"]
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader(); w.writerows(sorted(resolved, key=lambda r: (r["gene_family"], r["transcript_id"])))

    counts = Counter(r["gene_family"] for r in resolved)
    summary = {
        "status": "annotation_driven_candidate_free_family_map",
        "n_mapped_transcripts": len(resolved),
        "mapped_transcripts_per_family": {f: counts.get(f, 0) for f in PATTERNS},
        "families_with_at_least_one_transcript": sorted([f for f in PATTERNS if counts.get(f, 0) > 0]),
        "n_families_with_at_least_one_transcript": sum(counts.get(f, 0) > 0 for f in PATTERNS),
        "n_gff_transcript_candidates_not_matched_to_fasta": len(unresolved),
        "selection_rule": "annotation pattern only; no expression or colour outcome used",
    }
    (args.out_dir / "family_mapping_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
