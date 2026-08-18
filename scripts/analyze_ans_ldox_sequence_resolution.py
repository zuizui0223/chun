#!/usr/bin/env python3
"""Resolve admitted Camellia ANS/LDOX source features to public sequences.

The analysis keeps three evidence layers separate:

1. source identifiers reported by expression studies;
2. reference-model sequences used by those studies;
3. species-native or cloned sequences directly linked by accession/primers.

A reference-mapped locus is not promoted to a species-native locus merely
because reads from that species were counted against it.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
DNA = re.compile(r"^[ACGTRYSWKMBDHVN]+$", re.I)
LOC_RE = re.compile(r"LOC\d+")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--source-features", type=Path, required=True)
    p.add_argument("--references", type=Path, required=True)
    p.add_argument("--tea-root", type=Path, required=True)
    p.add_argument("--oleifera-root", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--email", default="")
    p.add_argument("--api-key", default="")
    return p.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        rows = []
        for raw in csv.DictReader(f):
            if None in raw:
                raise ValueError(f"{path}: malformed CSV row with extra fields")
            rows.append({k: (v or "").strip() for k, v in raw.items()})
        return rows


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def fetch_genbank(accession: str, db: str, email: str, api_key: str) -> str:
    q = {"db": db, "id": accession, "rettype": "gb", "retmode": "text"}
    if email:
        q["email"] = email
    if api_key:
        q["api_key"] = api_key
    req = Request(
        EFETCH + "?" + urlencode(q),
        headers={"User-Agent": f"chun-ans-resolution/0.1 ({email or 'no-email'})"},
    )
    last: Exception | None = None
    for attempt in range(5):
        try:
            with urlopen(req, timeout=90) as response:
                text = response.read().decode()
            if "LOCUS" not in text or "//" not in text:
                raise RuntimeError("incomplete GenBank response")
            return text
        except Exception as exc:
            last = exc
            if attempt < 4:
                time.sleep(min(2 ** (attempt + 1), 16))
    raise RuntimeError(f"could not fetch {db}:{accession}") from last


def sha(seq: str) -> str:
    return hashlib.sha256(seq.upper().encode()).hexdigest()


def find_files(root: Path, names: set[str]) -> list[Path]:
    if not root.exists():
        return []
    return sorted(p for p in root.rglob("*") if p.is_file() and p.name in names)


def classify_fasta(path: Path) -> str:
    name = path.name.lower()
    if "protein" in name or name.endswith(".faa"):
        return "protein"
    if "cds" in name:
        return "cds"
    if "rna" in name or "transcript" in name:
        return "rna"
    if "gene" in name or "genomic" in name:
        return "genomic"
    return "nucleotide"


def read_fasta_paths(paths: list[Path], source: str) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for path in paths:
        for record in SeqIO.parse(path, "fasta"):
            out.append(
                {
                    "record": record,
                    "source": source,
                    "file": str(path),
                    "sequence_type": classify_fasta(path),
                }
            )
    return out


def feature_symbol(feature: str) -> str:
    match = LOC_RE.search(feature)
    return match.group(0) if match else feature


def sanitize(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value)


def reverse_complement(seq: str) -> str:
    return str(Seq(seq).reverse_complement())


def all_starts(seq: str, motif: str) -> list[int]:
    if not motif:
        return []
    return [m.start() for m in re.finditer(f"(?={re.escape(motif)})", seq)]


def paired_primer_hits(seq: str, forward: str, reverse: str) -> list[tuple[str, int, int, int]]:
    """Return orientation, zero-based start, exclusive end, amplicon length."""
    seq = seq.upper()
    forward = forward.upper()
    reverse = reverse.upper()
    results: list[tuple[str, int, int, int]] = []
    for orientation, oriented in [("plus", seq), ("minus", reverse_complement(seq))]:
        f_hits = all_starts(oriented, forward)
        r_motif = reverse_complement(reverse)
        r_hits = all_starts(oriented, r_motif)
        for f_start in f_hits:
            for r_start in r_hits:
                if r_start >= f_start + len(forward):
                    end = r_start + len(r_motif)
                    results.append((orientation, f_start, end, end - f_start))
    return results


def single_primer_counts(seq: str, forward: str, reverse: str) -> tuple[int, int]:
    seq = seq.upper()
    orientations = [seq, reverse_complement(seq)]
    f = sum(len(all_starts(x, forward.upper())) for x in orientations)
    r = sum(len(all_starts(x, reverse_complement(reverse.upper()))) for x in orientations)
    return f, r


BLAST_FIELDS = [
    "qseqid", "sseqid", "pident", "length", "mismatch", "gaps",
    "qstart", "qend", "sstart", "send", "qlen", "slen", "evalue", "bitscore",
]


def write_fasta(path: Path, records: list[SeqRecord]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as f:
        SeqIO.write(records, f, "fasta")


def run_blast(program: str, query: Path, subject: Path, output: Path, evalue: str) -> list[dict[str, object]]:
    cmd = [
        program, "-query", str(query), "-subject", str(subject),
        "-evalue", evalue, "-max_target_seqs", "1000", "-max_hsps", "1",
        "-outfmt", "6 " + " ".join(BLAST_FIELDS), "-out", str(output),
    ]
    if program == "blastp":
        cmd += ["-seg", "no"]
    elif program == "blastn":
        cmd += ["-task", "blastn", "-dust", "no", "-word_size", "7"]
    elif program == "blastx":
        cmd += ["-seg", "no"]
    subprocess.run(cmd, check=True)
    rows: list[dict[str, object]] = []
    if output.exists():
        for line in output.read_text().splitlines():
            values = line.split("\t")
            row: dict[str, object] = dict(zip(BLAST_FIELDS, values, strict=True))
            qspan = abs(int(str(row["qend"])) - int(str(row["qstart"]))) + 1
            sspan = abs(int(str(row["send"])) - int(str(row["sstart"]))) + 1
            row["qcov"] = qspan / int(str(row["qlen"]))
            row["scov"] = sspan / int(str(row["slen"]))
            rows.append(row)
    return rows


def fetch_reference_proteins(refs: list[dict[str, str]], out_dir: Path, email: str, api_key: str) -> tuple[list[SeqRecord], list[dict[str, object]]]:
    gb_dir = out_dir / "reference_genbank"
    gb_dir.mkdir(parents=True, exist_ok=True)
    proteins: list[SeqRecord] = []
    manifest: list[dict[str, object]] = []
    for index, row in enumerate(refs):
        accession = row["accession"]
        text = fetch_genbank(accession, "protein", email, api_key)
        path = gb_dir / f"{accession}.gb"
        path.write_text(text, encoding="utf-8", newline="\n")
        records = list(SeqIO.parse(path, "genbank"))
        if len(records) != 1:
            raise ValueError(f"{accession}: expected one protein record")
        record = records[0]
        seq = str(record.seq).upper().rstrip("*")
        if not seq:
            raise ValueError(f"{accession}: empty protein sequence")
        expected = row["expected_taxon"]
        organism = record.annotations.get("organism", "")
        if expected and expected.lower() not in organism.lower():
            raise ValueError(f"{accession}: organism mismatch ({organism!r} != {expected!r})")
        proteins.append(SeqRecord(Seq(seq), id=accession, description=f"{row['role']} {organism}"))
        manifest.append(
            {
                "record_class": "reference_protein",
                "source_feature": row["role"],
                "requested_accession": accession,
                "record_accession": record.id,
                "organism": organism,
                "description": record.description,
                "sequence_type": "protein",
                "sequence_length": len(seq),
                "sha256": sha(seq),
                "source_file": str(path),
                "selection_status": "versioned_public_reference",
            }
        )
        if index + 1 < len(refs):
            time.sleep(0.12 if api_key else 0.4)
    return proteins, manifest


def load_tea_feature_sequences(source_rows: list[dict[str, str]], tea_root: Path) -> tuple[dict[str, list[dict[str, object]]], dict[str, list[dict[str, object]]], list[dict[str, object]]]:
    nt_by_feature: dict[str, list[dict[str, object]]] = {}
    protein_by_feature: dict[str, list[dict[str, object]]] = {}
    manifest: list[dict[str, object]] = []
    for row in source_rows:
        if row["admission_status"] != "reference_feature_to_resolve":
            continue
        feature = row["source_feature"]
        symbol = feature_symbol(feature)
        root = tea_root / sanitize(symbol)
        nt_items = read_fasta_paths(find_files(root, {"rna.fna", "cds.fna", "cds_from_genomic.fna", "gene.fna"}), feature)
        protein_items = read_fasta_paths(find_files(root, {"protein.faa"}), feature)
        nt_by_feature[feature] = nt_items
        protein_by_feature[feature] = protein_items
        for item in nt_items + protein_items:
            record = item["record"]
            assert isinstance(record, SeqRecord)
            seq = str(record.seq).upper().rstrip("*")
            manifest.append(
                {
                    "record_class": "mapped_reference_feature",
                    "source_feature": feature,
                    "requested_accession": symbol,
                    "record_accession": record.id,
                    "organism": row["reference_taxon"],
                    "description": record.description,
                    "sequence_type": item["sequence_type"],
                    "sequence_length": len(seq),
                    "sha256": sha(seq),
                    "source_file": item["file"],
                    "selection_status": "all_downloaded_isoforms",
                }
            )
    return nt_by_feature, protein_by_feature, manifest


def load_oleifera_sequences(oleifera_root: Path) -> tuple[list[dict[str, object]], list[dict[str, object]], list[Path]]:
    nt = read_fasta_paths(find_files(oleifera_root, {"rna.fna", "cds.fna", "cds_from_genomic.fna"}), "GCA_022316695.1")
    proteins = read_fasta_paths(find_files(oleifera_root, {"protein.faa"}), "GCA_022316695.1")
    gff = find_files(oleifera_root, {"genomic.gff", "genomic.gff3"})
    return nt, proteins, gff


def choose_representative_protein(feature: str, items: list[dict[str, object]]) -> SeqRecord | None:
    records = []
    for item in items:
        record = item["record"]
        assert isinstance(record, SeqRecord)
        seq = str(record.seq).upper().rstrip("*")
        if seq:
            records.append(SeqRecord(Seq(seq), id=f"{sanitize(feature)}__{record.id}", description=record.description))
    if not records:
        return None
    records.sort(key=lambda x: (len(x.seq), x.id), reverse=True)
    return records[0]


def gff_feature_count(paths: list[Path], token: str) -> tuple[int, list[str]]:
    count = 0
    lines: list[str] = []
    for path in paths:
        with path.open(errors="replace") as f:
            for line in f:
                if token in line:
                    count += 1
                    if len(lines) < 20:
                        lines.append(line.rstrip())
    return count, lines


def map_primer_linked_record_to_protein(nt_record: SeqRecord, protein_records: list[dict[str, object]], work_dir: Path, tag: str) -> dict[str, object]:
    proteins = []
    for item in protein_records:
        rec = item["record"]
        assert isinstance(rec, SeqRecord)
        seq = str(rec.seq).upper().rstrip("*")
        if seq:
            proteins.append(SeqRecord(Seq(seq), id=rec.id, description=rec.description))
    empty = {"best_protein_accession": "", "best_protein_identity": "", "best_protein_query_coverage": "", "best_protein_bitscore": ""}
    if not proteins:
        return empty
    query = work_dir / f"{sanitize(tag)}_query.fna"
    subject = work_dir / f"{sanitize(tag)}_proteins.faa"
    output = work_dir / f"{sanitize(tag)}_blastx.tsv"
    write_fasta(query, [nt_record])
    write_fasta(subject, proteins)
    hits = run_blast("blastx", query, subject, output, "1e-10")
    if not hits:
        return empty
    best = max(hits, key=lambda x: float(str(x["bitscore"])))
    return {
        "best_protein_accession": best["sseqid"],
        "best_protein_identity": f"{float(str(best['pident'])) / 100:.6f}",
        "best_protein_query_coverage": f"{float(best['qcov']):.6f}",
        "best_protein_bitscore": best["bitscore"],
    }


def primer_audit(source_rows: list[dict[str, str]], candidate_nt: list[dict[str, object]], oleifera_proteins: list[dict[str, object]], work_dir: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for source in source_rows:
        forward = source["forward_primer"].upper()
        reverse = source["reverse_primer"].upper()
        if not forward or not reverse:
            continue
        if not DNA.fullmatch(forward) or not DNA.fullmatch(reverse):
            raise ValueError(f"{source['source_feature']}: invalid primer")
        exact_pair_count = 0
        for item in candidate_nt:
            record = item["record"]
            assert isinstance(record, SeqRecord)
            seq = str(record.seq).upper()
            pairs = paired_primer_hits(seq, forward, reverse)
            f_count, r_count = single_primer_counts(seq, forward, reverse)
            if not pairs and not f_count and not r_count:
                continue
            if pairs:
                exact_pair_count += len(pairs)
                for index, (orientation, start, end, amp_bp) in enumerate(pairs, 1):
                    oriented = seq if orientation == "plus" else reverse_complement(seq)
                    amplicon = oriented[start:end]
                    mapped = map_primer_linked_record_to_protein(
                        record,
                        oleifera_proteins if item["source"] == "GCA_022316695.1" else [],
                        work_dir,
                        f"{source['source_feature']}_{record.id}_{index}",
                    )
                    expected = source["expected_amplicon_or_orf_bp"]
                    rows.append(
                        {
                            "assay_feature": source["source_feature"],
                            "independence_cluster": source["independence_cluster"],
                            "target_taxon": source["taxon"],
                            "searched_sequence_source": item["source"],
                            "sequence_type": item["sequence_type"],
                            "record_accession": record.id,
                            "record_description": record.description,
                            "forward_exact_hits_both_orientations": f_count,
                            "reverse_complement_exact_hits_both_orientations": r_count,
                            "pair_status": "exact_paired_primer_link",
                            "orientation": orientation,
                            "predicted_amplicon_bp": amp_bp,
                            "expected_amplicon_or_orf_bp": expected,
                            "amplicon_matches_expected": str(amp_bp == int(expected)) if expected else "",
                            "amplicon_sha256": sha(amplicon),
                            **mapped,
                            "claim_boundary": source["claim_boundary"],
                        }
                    )
            else:
                rows.append(
                    {
                        "assay_feature": source["source_feature"],
                        "independence_cluster": source["independence_cluster"],
                        "target_taxon": source["taxon"],
                        "searched_sequence_source": item["source"],
                        "sequence_type": item["sequence_type"],
                        "record_accession": record.id,
                        "record_description": record.description,
                        "forward_exact_hits_both_orientations": f_count,
                        "reverse_complement_exact_hits_both_orientations": r_count,
                        "pair_status": "single_primer_exact_only",
                        "orientation": "",
                        "predicted_amplicon_bp": "",
                        "expected_amplicon_or_orf_bp": source["expected_amplicon_or_orf_bp"],
                        "amplicon_matches_expected": "",
                        "amplicon_sha256": "",
                        "best_protein_accession": "",
                        "best_protein_identity": "",
                        "best_protein_query_coverage": "",
                        "best_protein_bitscore": "",
                        "claim_boundary": source["claim_boundary"],
                    }
                )
        if exact_pair_count == 0 and not any(row["assay_feature"] == source["source_feature"] for row in rows):
            rows.append(
                {
                    "assay_feature": source["source_feature"],
                    "independence_cluster": source["independence_cluster"],
                    "target_taxon": source["taxon"],
                    "searched_sequence_source": "all_admitted_candidate_nucleotides",
                    "sequence_type": "",
                    "record_accession": "",
                    "record_description": "",
                    "forward_exact_hits_both_orientations": 0,
                    "reverse_complement_exact_hits_both_orientations": 0,
                    "pair_status": "no_exact_primer_link",
                    "orientation": "",
                    "predicted_amplicon_bp": "",
                    "expected_amplicon_or_orf_bp": source["expected_amplicon_or_orf_bp"],
                    "amplicon_matches_expected": "",
                    "amplicon_sha256": "",
                    "best_protein_accession": "",
                    "best_protein_identity": "",
                    "best_protein_query_coverage": "",
                    "best_protein_bitscore": "",
                    "claim_boundary": source["claim_boundary"],
                }
            )
    return rows


def pairwise_proteins(queries: list[SeqRecord], refs: list[SeqRecord], work_dir: Path) -> list[dict[str, object]]:
    if not queries or not refs:
        return []
    query_path = work_dir / "source_query_proteins.faa"
    subject_path = work_dir / "reference_proteins.faa"
    output = work_dir / "source_vs_reference_blastp.tsv"
    write_fasta(query_path, queries)
    write_fasta(subject_path, refs)
    hits = run_blast("blastp", query_path, subject_path, output, "1e-20")
    rows: list[dict[str, object]] = []
    by_query: dict[str, list[dict[str, object]]] = defaultdict(list)
    for hit in hits:
        by_query[str(hit["qseqid"])].append(hit)
    for query in queries:
        qhits = sorted(by_query.get(query.id, []), key=lambda x: float(str(x["bitscore"])), reverse=True)
        for rank, hit in enumerate(qhits, 1):
            rows.append(
                {
                    "query_id": query.id,
                    "reference_accession": hit["sseqid"],
                    "rank": rank,
                    "protein_identity": f"{float(str(hit['pident'])) / 100:.6f}",
                    "protein_query_coverage": f"{float(hit['qcov']):.6f}",
                    "protein_subject_coverage": f"{float(hit['scov']):.6f}",
                    "alignment_aa": hit["length"],
                    "mismatches": hit["mismatch"],
                    "gaps": hit["gaps"],
                    "evalue": hit["evalue"],
                    "bitscore": hit["bitscore"],
                }
            )
    return rows


def source_resolution(source_rows: list[dict[str, str]], nt_by_feature: dict[str, list[dict[str, object]]], protein_by_feature: dict[str, list[dict[str, object]]], primer_rows: list[dict[str, object]], gff_paths: list[Path]) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for source in source_rows:
        feature = source["source_feature"]
        nt_items = nt_by_feature.get(feature, [])
        protein_items = protein_by_feature.get(feature, [])
        exact = [x for x in primer_rows if x["assay_feature"] == feature and x["pair_status"] == "exact_paired_primer_link"]
        gff_count, gff_lines = gff_feature_count(gff_paths, feature) if source["reference_assembly"] == "GCA_022316695.1" else (0, [])
        status = source["admission_status"]
        if exact:
            if source["expected_amplicon_or_orf_bp"] and any(x["amplicon_matches_expected"] == "True" for x in exact):
                status = "exact_expected_length_primer_link"
            else:
                status = "exact_paired_primer_link"
        elif protein_items:
            status = "reference_feature_sequence_recovered"
        elif source["public_sequence_anchor"]:
            status = "published_reference_anchor_only"
        elif gff_count:
            status = "source_model_found_in_reference_annotation"
        reference_ready = status in {"exact_expected_length_primer_link", "exact_paired_primer_link", "reference_feature_sequence_recovered", "source_model_found_in_reference_annotation"}
        species_native_ready = status == "exact_expected_length_primer_link" and source["source_namespace"] == "primer-defined cloned ORF"
        out.append(
            {
                "independence_cluster": source["independence_cluster"],
                "taxon": source["taxon"],
                "source_feature": feature,
                "source_namespace": source["source_namespace"],
                "reference_taxon": source["reference_taxon"],
                "reference_assembly": source["reference_assembly"],
                "public_sequence_anchor": source["public_sequence_anchor"],
                "downloaded_nucleotide_records": len(nt_items),
                "downloaded_protein_records": len(protein_items),
                "gff_exact_source_id_lines": gff_count,
                "gff_example": " || ".join(gff_lines[:3]),
                "exact_paired_primer_records": len(exact),
                "resolution_status": status,
                "reference_model_lineage_ready": "yes" if reference_ready else "no",
                "species_native_strict_node_ready": "yes" if species_native_ready else "no",
                "claim_boundary": source["claim_boundary"],
            }
        )
    return out


def summarize(source_rows: list[dict[str, str]], resolution_rows: list[dict[str, object]], primer_rows: list[dict[str, object]], pairwise_rows: list[dict[str, object]]) -> dict[str, object]:
    by_feature = {str(x["source_feature"]): x for x in resolution_rows}
    retic_loc = [row for row in resolution_rows if row["independence_cluster"] == "CRETICULATA" and str(row["source_feature"]).startswith("gene-LOC")]
    sasanqua = by_feature.get("Cao1_scaffold_14-gene-740.10", {})
    crans = by_feature.get("CrANS", {})
    best_by_query: dict[str, dict[str, object]] = {}
    for row in pairwise_rows:
        if int(row["rank"]) == 1:
            best_by_query[str(row["query_id"])] = row
    reference_groups: dict[str, list[str]] = defaultdict(list)
    for query_id, best in best_by_query.items():
        feature = query_id.split("__", 1)[0]
        reference_groups[str(best["reference_accession"])].append(feature)
    return {
        "analysis_version": "v0.1",
        "source_feature_count": len(source_rows),
        "reticulata_reference_loc_features_recovered": sum(int(row["downloaded_protein_records"]) > 0 for row in retic_loc),
        "reticulata_reference_loc_features_total": len(retic_loc),
        "novel_12638_status": by_feature.get("novel.12638", {}).get("resolution_status", "missing"),
        "crans_resolution_status": crans.get("resolution_status", "missing"),
        "crans_exact_expected_1068_links": sum(row["assay_feature"] == "CrANS" and row["pair_status"] == "exact_paired_primer_link" and row["amplicon_matches_expected"] == "True" for row in primer_rows),
        "sasanqua_resolution_status": sasanqua.get("resolution_status", "missing"),
        "sasanqua_exact_primer_links": sum(row["assay_feature"] == "Cao1_scaffold_14-gene-740.10" and row["pair_status"] == "exact_paired_primer_link" for row in primer_rows),
        "best_reference_by_source_query": best_by_query,
        "reference_lineages_shared_by_multiple_source_features": {ref: sorted(set(features)) for ref, features in reference_groups.items() if len(set(features)) >= 2},
        "decision_gate": {
            "same_node_candidate": "requires independently source-linked sequences with the same best reference lineage, near-full coverage, and a separate tree/context check before promotion",
            "different_paralog_candidate": "requires all compared clusters to be source-linked while their resolved strict labels differ",
            "unresolved": "family annotation, mapped reference IDs, or one-sided primers do not create a species-native strict node",
        },
        "claim_boundary": {
            "supported": ["public recovery status of the admitted source features", "exact primer-to-reference-sequence links", "protein similarity to versioned Camellia ANS references", "separation of mapping-reference IDs from species-native loci"],
            "not_supported": ["species-native identity from a reference-mapped feature alone", "strict orthology from pairwise similarity alone", "duplication age", "macro-transition enrichment", "adaptive selection"],
        },
    }


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    work = args.out_dir / "work"
    work.mkdir(exist_ok=True)
    source_rows = read_csv(args.source_features)
    ref_rows = read_csv(args.references)
    if len({row["source_feature"] for row in source_rows}) != len(source_rows):
        raise ValueError("duplicate source_feature")
    if len({row["accession"] for row in ref_rows}) != len(ref_rows):
        raise ValueError("duplicate reference accession")
    reference_proteins, manifest_refs = fetch_reference_proteins(ref_rows, args.out_dir, args.email, args.api_key)
    nt_by_feature, protein_by_feature, manifest_features = load_tea_feature_sequences(source_rows, args.tea_root)
    oleifera_nt, oleifera_proteins, oleifera_gff = load_oleifera_sequences(args.oleifera_root)
    all_candidate_nt: list[dict[str, object]] = []
    for values in nt_by_feature.values():
        all_candidate_nt.extend(values)
    all_candidate_nt.extend(oleifera_nt)
    primer_rows = primer_audit(source_rows, all_candidate_nt, oleifera_proteins, work)
    query_proteins: list[SeqRecord] = []
    for feature, items in sorted(protein_by_feature.items()):
        representative = choose_representative_protein(feature, items)
        if representative:
            query_proteins.append(representative)
    oleifera_protein_lookup = {}
    for item in oleifera_proteins:
        rec = item["record"]
        assert isinstance(rec, SeqRecord)
        oleifera_protein_lookup[rec.id] = rec
    for row in primer_rows:
        accession = str(row["best_protein_accession"])
        feature = str(row["assay_feature"])
        if accession and accession in oleifera_protein_lookup:
            rec = oleifera_protein_lookup[accession]
            seq = str(rec.seq).upper().rstrip("*")
            query_id = f"{sanitize(feature)}__{accession}"
            if not any(x.id == query_id for x in query_proteins):
                query_proteins.append(SeqRecord(Seq(seq), id=query_id, description=rec.description))
    pairwise_rows = pairwise_proteins(query_proteins, reference_proteins, work)
    resolution_rows = source_resolution(source_rows, nt_by_feature, protein_by_feature, primer_rows, oleifera_gff)
    manifest = manifest_refs + manifest_features
    for item in oleifera_nt + oleifera_proteins:
        rec = item["record"]
        assert isinstance(rec, SeqRecord)
        implicated = (
            "Cao1_scaffold_14-gene-740.10" in rec.description
            or any(row["record_accession"] == rec.id and row["pair_status"] == "exact_paired_primer_link" for row in primer_rows)
            or any(row["best_protein_accession"] == rec.id for row in primer_rows)
        )
        if implicated:
            seq = str(rec.seq).upper().rstrip("*")
            manifest.append(
                {
                    "record_class": "oleifera_reference_source_anchor",
                    "source_feature": "Cao1_scaffold_14-gene-740.10",
                    "requested_accession": "GCA_022316695.1",
                    "record_accession": rec.id,
                    "organism": "Camellia oleifera",
                    "description": rec.description,
                    "sequence_type": item["sequence_type"],
                    "sequence_length": len(seq),
                    "sha256": sha(seq),
                    "source_file": item["file"],
                    "selection_status": "source_id_or_primer_implicated",
                }
            )
    summary = summarize(source_rows, resolution_rows, primer_rows, pairwise_rows)
    write_csv(args.out_dir / "sequence_manifest.csv", manifest, ["record_class", "source_feature", "requested_accession", "record_accession", "organism", "description", "sequence_type", "sequence_length", "sha256", "source_file", "selection_status"])
    write_csv(args.out_dir / "source_feature_resolution.csv", resolution_rows, ["independence_cluster", "taxon", "source_feature", "source_namespace", "reference_taxon", "reference_assembly", "public_sequence_anchor", "downloaded_nucleotide_records", "downloaded_protein_records", "gff_exact_source_id_lines", "gff_example", "exact_paired_primer_records", "resolution_status", "reference_model_lineage_ready", "species_native_strict_node_ready", "claim_boundary"])
    write_csv(args.out_dir / "primer_linkage.csv", primer_rows, ["assay_feature", "independence_cluster", "target_taxon", "searched_sequence_source", "sequence_type", "record_accession", "record_description", "forward_exact_hits_both_orientations", "reverse_complement_exact_hits_both_orientations", "pair_status", "orientation", "predicted_amplicon_bp", "expected_amplicon_or_orf_bp", "amplicon_matches_expected", "amplicon_sha256", "best_protein_accession", "best_protein_identity", "best_protein_query_coverage", "best_protein_bitscore", "claim_boundary"])
    write_csv(args.out_dir / "protein_reference_similarity.csv", pairwise_rows, ["query_id", "reference_accession", "rank", "protein_identity", "protein_query_coverage", "protein_subject_coverage", "alignment_aa", "mismatches", "gaps", "evalue", "bitscore"])
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
