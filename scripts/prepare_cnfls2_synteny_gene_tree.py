#!/usr/bin/env python3
"""Prepare exact-crosswalk neighborhoods and an FLS-family protein panel.

The script uses the admitted C. nitidissima transcript `GWHTFILD005297.1` and
the TPIA2 exact Longjing43 crosswalk `GWHTACFB016172`. It resolves their GFF
gene parents, extracts local gene neighborhoods, chooses one representative
protein per neighboring gene, and builds a broader FLS-family panel from
candidate-vs-proteome BLASTP results.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable
from urllib.parse import unquote

from Bio import SeqIO
from Bio.SeqRecord import SeqRecord

BLAST_FIELDS = ["qseqid", "sseqid", "pident", "length", "qlen", "slen", "qcovs", "evalue", "bitscore"]
TRANSCRIPT_TYPES = {"mrna", "transcript", "rna", "lnc_rna", "ncrna"}


@dataclass
class Gene:
    gene_id: str
    seqid: str
    start: int
    end: int
    strand: str
    transcripts: set[str] = field(default_factory=set)
    protein_ids: set[str] = field(default_factory=set)


def strip_version(identifier: str) -> str:
    return re.sub(r"\.\d+$", "", identifier)


def clean_id(identifier: str) -> str:
    return unquote(identifier.strip().strip('"').strip("'"))


def id_variants(identifier: str) -> set[str]:
    identifier = clean_id(identifier)
    variants = {identifier, strip_version(identifier)}
    for prefix in ("gene:", "transcript:", "rna:", "protein:", "cds:"):
        if identifier.lower().startswith(prefix):
            core = identifier[len(prefix) :]
            variants.update({core, strip_version(core)})
    current = list(variants)
    for value in current:
        if value.startswith("GWHT"):
            variants.add("GWHP" + value[4:])
            variants.add(strip_version("GWHP" + value[4:]))
        if value.startswith("GWHP"):
            variants.add("GWHT" + value[4:])
            variants.add(strip_version("GWHT" + value[4:]))
    return {value for value in variants if value}


def parse_attributes(text: str) -> dict[str, list[str]]:
    attributes: dict[str, list[str]] = defaultdict(list)
    for raw_item in text.strip().strip(";").split(";"):
        item = raw_item.strip()
        if not item:
            continue
        if "=" in item:
            key, value = item.split("=", 1)
        elif " " in item:
            key, value = item.split(None, 1)
        else:
            continue
        key = key.strip()
        for part in value.strip().strip('"').split(","):
            part = clean_id(part)
            if part:
                attributes[key].append(part)
    return dict(attributes)


def first_attr(attributes: dict[str, list[str]], keys: Iterable[str]) -> str:
    for key in keys:
        values = attributes.get(key)
        if values:
            return values[0]
    return ""


def read_proteins(path: Path) -> tuple[dict[str, str], dict[str, str]]:
    exact: dict[str, str] = {}
    aliases: dict[str, str] = {}
    for record in SeqIO.parse(path, "fasta"):
        sequence = str(record.seq).replace("*", "").upper()
        if not sequence:
            continue
        exact[record.id] = sequence
        tokens = {record.id}
        tokens.update(re.findall(r"GWH[P|T|G][A-Z]+\d+(?:\.\d+)?", record.description))
        for token in tokens:
            for variant in id_variants(token):
                aliases.setdefault(variant, record.id)
    if not exact:
        raise SystemExit(f"No protein records found in {path}")
    return exact, aliases


def lookup_protein(identifier: str, proteins: dict[str, str], aliases: dict[str, str]) -> str | None:
    for variant in id_variants(identifier):
        if variant in proteins:
            return variant
        if variant in aliases:
            return aliases[variant]
    return None


def parse_gff(path: Path) -> tuple[dict[str, Gene], dict[str, str], dict[str, set[str]]]:
    genes: dict[str, Gene] = {}
    transcript_parent_raw: dict[str, list[str]] = defaultdict(list)
    transcript_proteins: dict[str, set[str]] = defaultdict(set)

    with path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if not line or line.startswith("#"):
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 9:
                continue
            seqid, _, feature_type, start, end, _, strand, _, attr_text = parts[:9]
            try:
                start_i = int(start)
                end_i = int(end)
            except ValueError:
                continue
            attrs = parse_attributes(attr_text)
            lower_type = feature_type.lower()
            feature_id = first_attr(attrs, ["ID", "gene_id", "transcript_id", "Name"])
            parents = attrs.get("Parent", []) + attrs.get("gene", [])

            if lower_type == "gene":
                gene_id = feature_id or first_attr(attrs, ["locus_tag", "Name"])
                if gene_id:
                    genes[gene_id] = Gene(gene_id, seqid, start_i, end_i, strand)
            elif lower_type in TRANSCRIPT_TYPES or "transcript" in lower_type:
                transcript_id = feature_id or first_attr(attrs, ["transcript_id"])
                if transcript_id:
                    transcript_parent_raw[transcript_id].extend(parents)
            elif lower_type == "cds":
                protein_ids: list[str] = []
                for key in ["protein_id", "proteinId", "protein", "Name"]:
                    protein_ids.extend(attrs.get(key, []))
                for transcript_id in parents:
                    transcript_proteins[transcript_id].update(protein_ids)

    gene_alias: dict[str, str] = {}
    for gene_id in genes:
        for variant in id_variants(gene_id):
            gene_alias.setdefault(variant, gene_id)

    transcript_to_gene: dict[str, str] = {}
    for transcript_id, parents in transcript_parent_raw.items():
        resolved = ""
        for parent in parents:
            for variant in id_variants(parent):
                if variant in gene_alias:
                    resolved = gene_alias[variant]
                    break
            if resolved:
                break
        if resolved:
            transcript_to_gene[transcript_id] = resolved
            genes[resolved].transcripts.add(transcript_id)
            genes[resolved].protein_ids.update(transcript_proteins.get(transcript_id, set()))

    return genes, transcript_to_gene, transcript_proteins


def resolve_transcript_gene(target: str, genes: dict[str, Gene], transcript_to_gene: dict[str, str]) -> str:
    aliases: dict[str, str] = {}
    for transcript, gene in transcript_to_gene.items():
        for variant in id_variants(transcript):
            aliases.setdefault(variant, gene)
    for variant in id_variants(target):
        if variant in aliases:
            return aliases[variant]
    # Last-resort exact text association retained fail-closed: only one gene may match.
    matches = [gene_id for gene_id, gene in genes.items() if any(strip_version(t) == strip_version(target) for t in gene.transcripts)]
    if len(matches) == 1:
        return matches[0]
    raise SystemExit(f"Could not resolve target transcript {target} to one GFF gene")


def representative_protein(gene: Gene, proteins: dict[str, str], aliases: dict[str, str]) -> tuple[str, str] | None:
    candidates: set[str] = set()
    for transcript in gene.transcripts:
        candidates.update(id_variants(transcript))
        if transcript.startswith("GWHT"):
            candidates.update(id_variants("GWHP" + transcript[4:]))
    for protein_id in gene.protein_ids:
        candidates.update(id_variants(protein_id))
    resolved: dict[str, str] = {}
    for candidate in candidates:
        found = lookup_protein(candidate, proteins, aliases)
        if found:
            resolved[found] = proteins[found]
    if not resolved:
        return None
    return max(resolved.items(), key=lambda item: (len(item[1]), item[0]))


def write_fasta(path: Path, records: list[SeqRecord]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    SeqIO.write(records, path, "fasta")


def read_blast(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with path.open(encoding="utf-8") as handle:
        reader = csv.DictReader(handle, fieldnames=BLAST_FIELDS, delimiter="\t")
        for raw in reader:
            if not raw.get("sseqid"):
                continue
            try:
                rows.append(
                    {
                        **raw,
                        "pident_num": float(raw["pident"]),
                        "length_num": int(raw["length"]),
                        "qcov_num": float(raw["qcovs"]),
                        "evalue_num": float(raw["evalue"]),
                        "bitscore_num": float(raw["bitscore"]),
                    }
                )
            except (ValueError, TypeError):
                continue
    return rows


def build_neighborhood(
    species: str,
    genes: dict[str, Gene],
    target_gene_id: str,
    proteins: dict[str, str],
    aliases: dict[str, str],
    radius: int,
) -> tuple[list[dict[str, object]], list[SeqRecord]]:
    target_gene = genes[target_gene_id]
    ordered = sorted(
        (gene for gene in genes.values() if gene.seqid == target_gene.seqid),
        key=lambda gene: (gene.start, gene.end, gene.gene_id),
    )
    target_index = next(i for i, gene in enumerate(ordered) if gene.gene_id == target_gene_id)
    begin = max(0, target_index - radius)
    end = min(len(ordered), target_index + radius + 1)
    metadata: list[dict[str, object]] = []
    records: list[SeqRecord] = []
    for genome_index, gene in enumerate(ordered[begin:end], start=begin):
        relative = genome_index - target_index
        representative = representative_protein(gene, proteins, aliases)
        protein_id = ""
        protein_length: int | str = ""
        label = ""
        if representative:
            protein_id, sequence = representative
            protein_length = len(sequence)
            label = f"{species}__{protein_id}"
            records.append(SeqRecord(seq=__import__("Bio.Seq", fromlist=["Seq"]).Seq(sequence), id=label, description=f"gene={gene.gene_id} relative_index={relative}"))
        metadata.append(
            {
                "species": species,
                "seqid": gene.seqid,
                "gene_id": gene.gene_id,
                "start": gene.start,
                "end": gene.end,
                "strand": gene.strand,
                "relative_index": relative,
                "is_target": "yes" if gene.gene_id == target_gene_id else "no",
                "representative_protein_id": protein_id,
                "protein_label": label,
                "protein_length": protein_length,
                "transcripts": ";".join(sorted(gene.transcripts)),
                "protein_resolution": "representative_longest_child" if representative else "no_protein_resolved",
                "claim_boundary": "local annotated gene order; homology requires reciprocal sequence evidence",
            }
        )
    return metadata, records


def select_family_candidates(
    species: str,
    hits: list[dict[str, object]],
    proteins: dict[str, str],
    aliases: dict[str, str],
    target_protein: str,
    maximum: int,
) -> tuple[list[dict[str, object]], list[SeqRecord]]:
    by_subject: dict[str, dict[str, object]] = {}
    for row in hits:
        if row["evalue_num"] > 1e-10 or row["qcov_num"] < 50 or row["pident_num"] < 30 or row["length_num"] < 150:
            continue
        subject = str(row["sseqid"])
        found = lookup_protein(subject, proteins, aliases)
        if not found:
            continue
        current = by_subject.get(found)
        if current is None or float(row["bitscore_num"]) > float(current["bitscore_num"]):
            by_subject[found] = row
    if target_protein not in by_subject:
        by_subject[target_protein] = {
            "sseqid": target_protein,
            "pident_num": 100.0,
            "qcov_num": 100.0,
            "evalue_num": 0.0,
            "bitscore_num": math.inf,
            "length_num": len(proteins[target_protein]),
        }
    ranked = sorted(by_subject.items(), key=lambda item: (float(item[1]["bitscore_num"]), float(item[1]["qcov_num"])), reverse=True)
    ranked = ranked[:maximum]

    metadata: list[dict[str, object]] = []
    records: list[SeqRecord] = []
    seen_sequences: set[str] = set()
    rank = 0
    for protein_id, row in ranked:
        sequence = proteins[protein_id]
        sequence_hash = hashlib.sha256(sequence.encode()).hexdigest()
        if sequence_hash in seen_sequences and protein_id != target_protein:
            continue
        seen_sequences.add(sequence_hash)
        rank += 1
        label = f"{species}__{protein_id}"
        records.append(SeqRecord(seq=__import__("Bio.Seq", fromlist=["Seq"]).Seq(sequence), id=label, description="FLS_family_candidate"))
        metadata.append(
            {
                "species": species,
                "rank": rank,
                "protein_id": protein_id,
                "protein_label": label,
                "is_target": "yes" if protein_id == target_protein else "no",
                "protein_length": len(sequence),
                "pident_to_cn_candidate": round(float(row["pident_num"]), 6),
                "qcov_to_cn_candidate": round(float(row["qcov_num"]), 6),
                "evalue": row["evalue_num"],
                "bitscore": row["bitscore_num"],
                "sequence_sha256": sequence_hash,
                "claim_boundary": "candidate-panel membership only; FLS identity and orthology require tree/context evidence",
            }
        )
    return metadata, records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cn-gff", type=Path, required=True)
    parser.add_argument("--cn-proteins", type=Path, required=True)
    parser.add_argument("--tea-gff", type=Path, required=True)
    parser.add_argument("--tea-proteins", type=Path, required=True)
    parser.add_argument("--cn-family-hits", type=Path, required=True)
    parser.add_argument("--tea-family-hits", type=Path, required=True)
    parser.add_argument("--cn-target-transcript", default="GWHTFILD005297.1")
    parser.add_argument("--tea-target-transcript", default="GWHTACFB016172")
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--radius", type=int, default=10)
    parser.add_argument("--family-max-per-species", type=int, default=20)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    cn_proteins, cn_aliases = read_proteins(args.cn_proteins)
    tea_proteins, tea_aliases = read_proteins(args.tea_proteins)
    cn_genes, cn_transcript_to_gene, _ = parse_gff(args.cn_gff)
    tea_genes, tea_transcript_to_gene, _ = parse_gff(args.tea_gff)

    cn_target_gene = resolve_transcript_gene(args.cn_target_transcript, cn_genes, cn_transcript_to_gene)
    tea_target_gene = resolve_transcript_gene(args.tea_target_transcript, tea_genes, tea_transcript_to_gene)

    cn_target_protein = lookup_protein(args.cn_target_transcript.replace("GWHT", "GWHP", 1), cn_proteins, cn_aliases)
    tea_target_protein = lookup_protein(args.tea_target_transcript.replace("GWHT", "GWHP", 1), tea_proteins, tea_aliases)
    if not cn_target_protein:
        representative = representative_protein(cn_genes[cn_target_gene], cn_proteins, cn_aliases)
        cn_target_protein = representative[0] if representative else None
    if not tea_target_protein:
        representative = representative_protein(tea_genes[tea_target_gene], tea_proteins, tea_aliases)
        tea_target_protein = representative[0] if representative else None
    if not cn_target_protein or not tea_target_protein:
        raise SystemExit(f"Could not resolve target proteins: cn={cn_target_protein}, tea={tea_target_protein}")

    cn_neighborhood_meta, cn_neighborhood_records = build_neighborhood(
        "CN", cn_genes, cn_target_gene, cn_proteins, cn_aliases, args.radius
    )
    tea_neighborhood_meta, tea_neighborhood_records = build_neighborhood(
        "TEA", tea_genes, tea_target_gene, tea_proteins, tea_aliases, args.radius
    )
    neighborhood_meta = cn_neighborhood_meta + tea_neighborhood_meta
    neighborhood_fields = list(neighborhood_meta[0])
    with (args.out_dir / "neighborhood_metadata.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=neighborhood_fields)
        writer.writeheader()
        writer.writerows(neighborhood_meta)
    write_fasta(args.out_dir / "cn_neighborhood.faa", cn_neighborhood_records)
    write_fasta(args.out_dir / "tea_neighborhood.faa", tea_neighborhood_records)

    cn_family_meta, cn_family_records = select_family_candidates(
        "CN", read_blast(args.cn_family_hits), cn_proteins, cn_aliases, cn_target_protein, args.family_max_per_species
    )
    tea_family_meta, tea_family_records = select_family_candidates(
        "TEA", read_blast(args.tea_family_hits), tea_proteins, tea_aliases, tea_target_protein, args.family_max_per_species
    )
    family_meta = cn_family_meta + tea_family_meta
    family_fields = list(family_meta[0])
    with (args.out_dir / "family_candidate_metadata.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=family_fields)
        writer.writeheader()
        writer.writerows(family_meta)
    write_fasta(args.out_dir / "fls_family_candidates.faa", cn_family_records + tea_family_records)

    target_records = [
        SeqRecord(seq=__import__("Bio.Seq", fromlist=["Seq"]).Seq(cn_proteins[cn_target_protein]), id=f"CN__{cn_target_protein}", description="CnFLS2_like_target"),
        SeqRecord(seq=__import__("Bio.Seq", fromlist=["Seq"]).Seq(tea_proteins[tea_target_protein]), id=f"TEA__{tea_target_protein}", description="CSA008358_Longjing43_crosswalk_target"),
    ]
    write_fasta(args.out_dir / "target_pair.faa", target_records)

    summary = {
        "cn_target_transcript": args.cn_target_transcript,
        "cn_target_gene": cn_target_gene,
        "cn_target_protein": cn_target_protein,
        "tea_target_transcript": args.tea_target_transcript,
        "tea_target_gene": tea_target_gene,
        "tea_target_protein": tea_target_protein,
        "cn_genes_parsed": len(cn_genes),
        "tea_genes_parsed": len(tea_genes),
        "neighborhood_radius_genes": args.radius,
        "cn_neighborhood_genes": len(cn_neighborhood_meta),
        "tea_neighborhood_genes": len(tea_neighborhood_meta),
        "cn_neighborhood_proteins": len(cn_neighborhood_records),
        "tea_neighborhood_proteins": len(tea_neighborhood_records),
        "cn_family_candidates": len(cn_family_records),
        "tea_family_candidates": len(tea_family_records),
        "decision": "run reciprocal neighborhood BLASTP and an exploratory protein family tree",
        "claim_ceiling": "input preparation and exact-crosswalk target resolution only; synteny and family placement not yet inferred",
    }
    (args.out_dir / "preparation_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
