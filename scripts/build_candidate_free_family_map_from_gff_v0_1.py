#!/usr/bin/env python3
"""Map annotated Camellia transcripts to preregistered pigment gene families.

The mapping is annotation-driven and independent of flower-colour outcome. All
transcript paralogs whose gene, transcript, CDS, or RNA-FASTA annotation matches a
frozen family pattern are retained. No differential-expression result is consulted.
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
TRANSCRIPT_FEATURES = {"mRNA", "transcript", "ncRNA", "RNA"}


def attrs(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for part in text.strip().split(";"):
        if not part or "=" not in part:
            continue
        k, v = part.split("=", 1)
        out[k] = unquote(v)
    return out


def family_matches(text: str) -> list[str]:
    found = [family for family, pats in COMPILED.items() if any(p.search(text) for p in pats)]
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


def alias_set(x: str) -> set[str]:
    if not x:
        return set()
    vals = {x, normalize_id(x)}
    if "|" in x:
        tail = x.split("|")[-1]
        vals |= {tail, normalize_id(tail)}
    return {v for v in vals if v}


def fasta_headers(path: Path) -> dict[str, tuple[str, str]]:
    """Return alias -> (canonical FASTA token, full header)."""
    out: dict[str, tuple[str, str]] = {}
    with path.open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if not line.startswith(">"):
                continue
            header = line[1:].strip()
            token = header.split()[0]
            aliases = set(alias_set(token))
            for m in re.finditer(r"(?:transcript_id|gene|locus_tag)=([^\]\s]+)", header):
                aliases |= alias_set(m.group(1))
            for a in aliases:
                out[a] = (token, header)
    return out


def family_from_text(text: str) -> tuple[str, str] | None:
    matches = family_matches(text)
    if len(matches) == 1:
        return matches[0], text
    return None


def parse_gff(path: Path) -> list[dict[str, str]]:
    records: list[tuple[str, dict[str, str], str]] = []
    with path.open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if not line or line.startswith("#"):
                continue
            cols = line.rstrip("\n").split("\t")
            if len(cols) != 9:
                continue
            records.append((cols[2], attrs(cols[8]), cols[8]))

    gene_family_by_alias: dict[str, tuple[str, str]] = {}
    for feature, a, raw_attr in records:
        if feature != "gene":
            continue
        text = " ".join([raw_attr, *a.values()])
        hit = family_from_text(text)
        if hit is None:
            continue
        for key in ("ID", "Name", "gene", "locus_tag"):
            for alias in alias_set(a.get(key, "")):
                gene_family_by_alias[alias] = hit

    transcripts: dict[str, dict[str, object]] = {}
    transcript_alias_to_key: dict[str, str] = {}
    for feature, a, raw_attr in records:
        if feature not in TRANSCRIPT_FEATURES:
            continue
        tid = a.get("ID") or a.get("transcript_id") or a.get("Name")
        if not tid:
            continue
        parent_values: list[str] = []
        if a.get("Parent"):
            parent_values.extend(a["Parent"].split(","))
        for key in ("gene", "gene_id"):
            if a.get(key):
                parent_values.append(a[key])
        entry = transcripts.setdefault(tid, {"parents": set(), "candidates": []})
        entry["parents"].update(parent_values)
        direct_text = " ".join([raw_attr, *a.values()])
        direct = family_from_text(direct_text)
        if direct:
            entry["candidates"].append((direct[0], "transcript_annotation", direct[1]))
        for p in parent_values:
            for alias in alias_set(p):
                if alias in gene_family_by_alias:
                    fam, evidence = gene_family_by_alias[alias]
                    entry["candidates"].append((fam, "parent_gene_annotation", evidence))
        for alias in alias_set(tid):
            transcript_alias_to_key[alias] = tid
        for key in ("transcript_id", "Name"):
            for alias in alias_set(a.get(key, "")):
                transcript_alias_to_key[alias] = tid

    # CDS products often carry the most informative enzyme names in GenBank GFF3.
    for feature, a, raw_attr in records:
        if feature != "CDS":
            continue
        direct_text = " ".join([raw_attr, *a.values()])
        hit = family_from_text(direct_text)
        if hit is None:
            continue
        parents: list[str] = []
        if a.get("Parent"):
            parents.extend(a["Parent"].split(","))
        if a.get("transcript_id"):
            parents.append(a["transcript_id"])
        for p in parents:
            tkey = None
            if p in transcripts:
                tkey = p
            else:
                for alias in alias_set(p):
                    if alias in transcript_alias_to_key:
                        tkey = transcript_alias_to_key[alias]
                        break
            if tkey is not None:
                transcripts[tkey]["candidates"].append((hit[0], "cds_annotation", hit[1]))

    rows: list[dict[str, str]] = []
    for tid, info in transcripts.items():
        candidates = list(info["candidates"])
        families = {x[0] for x in candidates}
        if len(families) != 1:
            continue
        fam = next(iter(families))
        rows.append(
            {
                "gff_transcript_id": tid,
                "gene_family": fam,
                "mapping_basis": "+".join(sorted({x[1] for x in candidates})),
                "annotation_evidence": candidates[0][2],
            }
        )
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gff", type=Path, required=True)
    ap.add_argument("--rna-fasta", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()

    headers = fasta_headers(args.rna_fasta)
    gff_rows = parse_gff(args.gff)

    resolved: list[dict[str, str]] = []
    unresolved: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for row in gff_rows:
        match = None
        for alias in alias_set(row["gff_transcript_id"]):
            if alias in headers:
                match = headers[alias]
                break
        if match is None:
            unresolved.append(row)
            continue
        token, header = match
        key = (token, row["gene_family"])
        if key in seen:
            continue
        seen.add(key)
        resolved.append(
            {
                "transcript_id": token,
                "gene_family": row["gene_family"],
                "mapping_basis": row["mapping_basis"],
                "gff_transcript_id": row["gff_transcript_id"],
                "fasta_header": header,
            }
        )

    # Independent fallback when RNA FASTA headers themselves contain product/gene labels.
    canonical_seen: set[str] = set()
    for _alias, (token, header) in headers.items():
        if token in canonical_seen:
            continue
        canonical_seen.add(token)
        if any(r["transcript_id"] == token for r in resolved):
            continue
        hit = family_from_text(header)
        if hit:
            resolved.append(
                {
                    "transcript_id": token,
                    "gene_family": hit[0],
                    "mapping_basis": "rna_fasta_annotation",
                    "gff_transcript_id": "",
                    "fasta_header": header,
                }
            )

    args.out_dir.mkdir(parents=True, exist_ok=True)
    with (args.out_dir / "transcript_family_map.csv").open("w", newline="", encoding="utf-8") as fh:
        fields = ["transcript_id", "gene_family", "mapping_basis", "gff_transcript_id", "fasta_header"]
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(sorted(resolved, key=lambda r: (r["gene_family"], r["transcript_id"])))

    counts = Counter(r["gene_family"] for r in resolved)
    summary = {
        "status": "annotation_driven_candidate_free_family_map",
        "n_mapped_transcripts": len(resolved),
        "mapped_transcripts_per_family": {f: counts.get(f, 0) for f in PATTERNS},
        "families_with_at_least_one_transcript": sorted(f for f in PATTERNS if counts.get(f, 0) > 0),
        "n_families_with_at_least_one_transcript": sum(counts.get(f, 0) > 0 for f in PATTERNS),
        "n_gff_transcript_candidates_not_matched_to_fasta": len(unresolved),
        "annotation_sources": ["gene", "transcript", "CDS", "RNA_FASTA_header"],
        "selection_rule": "annotation pattern only; all matching paralogs retained; no expression or colour outcome used",
    }
    (args.out_dir / "family_mapping_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
