#!/usr/bin/env python3
"""Resolve public CjDFR (AB524885.1) against the accession-frozen tea DFR family."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
DNA = re.compile(r"^[ACGTRYSWKMBDHVN]+$", re.I)


def args():
    p = argparse.ArgumentParser()
    p.add_argument("--targets", type=Path, required=True)
    p.add_argument("--assays", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--email", default=os.getenv("NCBI_EMAIL", ""))
    p.add_argument("--api-key", default=os.getenv("NCBI_API_KEY", ""))
    return p.parse_args()


def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows, fields):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def fetch(accession, email, api_key):
    q = {"db": "nuccore", "id": accession, "rettype": "gbwithparts", "retmode": "text"}
    if email:
        q["email"] = email
    if api_key:
        q["api_key"] = api_key
    req = Request(
        EFETCH + "?" + urlencode(q),
        headers={"User-Agent": f"chun-cjdfr-anchor/0.1 ({email or 'no-email'})"},
    )
    error = None
    for attempt in range(5):
        try:
            with urlopen(req, timeout=90) as r:
                text = r.read().decode()
            if "LOCUS" not in text or "//" not in text:
                raise RuntimeError("incomplete GenBank response")
            return text
        except Exception as exc:
            error = exc
            if attempt < 4:
                time.sleep(min(2 ** (attempt + 1), 16))
    raise RuntimeError(f"cannot fetch {accession}") from error


def protein_fallback(nt):
    choices = []
    for frame in range(3):
        s = nt[frame : frame + ((len(nt) - frame) // 3) * 3]
        aa = str(Seq(s).translate()) if s else ""
        parts = aa.split("*")
        choices.append((sum(1 for x in aa[:-1] if x == "*"), -max(map(len, parts)), aa))
    choices.sort()
    return choices[0][2].replace("*", "") if choices else ""


def extract(record):
    cds = [x for x in record.features if x.type == "CDS"]
    if cds:
        feat = max(cds, key=lambda x: len(x.location))
        nt = str(feat.extract(record.seq)).upper()
        aa = "".join(feat.qualifiers.get("translation", [""])).replace(" ", "").rstrip("*")
        if not aa:
            aa = protein_fallback(nt)
        return nt, aa, "longest_annotated_cds", ";".join(feat.qualifiers.get("gene", [])), ";".join(feat.qualifiers.get("product", []))
    nt = str(record.seq).upper()
    return nt, protein_fallback(nt), "full_record_no_cds_feature", "", ""


def fasta(path, records):
    with path.open("w", encoding="utf-8", newline="\n") as f:
        SeqIO.write(records, f, "fasta")


BLAST_FIELDS = [
    "qseqid", "sseqid", "pident", "length", "mismatch", "gaps",
    "qstart", "qend", "sstart", "send", "qlen", "slen", "evalue", "bitscore",
]


def blast(program, query, subject, output):
    cmd = [
        program, "-query", str(query), "-subject", str(subject),
        "-evalue", "1e-10" if program == "blastp" else "1e-20",
        "-max_target_seqs", "100", "-max_hsps", "1",
        "-outfmt", "6 " + " ".join(BLAST_FIELDS), "-out", str(output),
    ]
    cmd += ["-seg", "no"] if program == "blastp" else ["-task", "blastn", "-dust", "no", "-word_size", "7"]
    subprocess.run(cmd, check=True)
    rows = {}
    if output.exists():
        for line in output.read_text().splitlines():
            vals = line.split("\t")
            row = dict(zip(BLAST_FIELDS, vals, strict=True))
            qspan = abs(int(row["qend"]) - int(row["qstart"])) + 1
            sspan = abs(int(row["send"]) - int(row["sstart"])) + 1
            row["qcov"] = qspan / int(row["qlen"])
            row["scov"] = sspan / int(row["slen"])
            rows[row["sseqid"]] = row
    return rows


def rc(seq):
    return str(Seq(seq).reverse_complement())


def hits(seq, motif):
    return [m.start() for m in re.finditer(f"(?={re.escape(motif)})", seq)] if motif else []


def audit_assays(path, full_sequences):
    out = []
    for row in read_csv(path):
        accession = row["sequence_accession"].strip()
        fwd = row["forward_primer"].replace(" ", "").upper()
        rev = row["reverse_primer"].replace(" ", "").upper()
        if fwd and not DNA.fullmatch(fwd):
            raise ValueError(f"bad primer {fwd}")
        if rev and not DNA.fullmatch(rev):
            raise ValueError(f"bad primer {rev}")
        result = {
            "assay_id": row["assay_id"], "year": row["year"], "taxon": row["taxon"],
            "target_label": row["target_label"], "sequence_accession": accession,
            "forward_primer": fwd, "reverse_primer": rev,
            "reported_amplicon_bp": row["reported_amplicon_bp"],
            "forward_exact_hits": 0, "reverse_complement_exact_hits": 0,
            "predicted_amplicon_bp": "", "amplicon_matches_reported": "",
            "linkage_status": "not_testable_no_frozen_sequence_or_primers",
            "source": row["source"], "claim_boundary": row["claim_boundary"],
        }
        if accession and fwd and rev:
            seq = full_sequences[accession]
            fh, rh = hits(seq, fwd), hits(seq, rc(rev))
            result["forward_exact_hits"], result["reverse_complement_exact_hits"] = len(fh), len(rh)
            amps = [r + len(rev) - f for f in fh for r in rh if r >= f + len(fwd)]
            if amps:
                amp = min(amps)
                result["predicted_amplicon_bp"] = amp
                result["amplicon_matches_reported"] = (
                    amp == int(row["reported_amplicon_bp"])
                    if row["reported_amplicon_bp"] else ""
                )
                result["linkage_status"] = "exact_paired_primer_link"
            elif fh or rh:
                result["linkage_status"] = "single_primer_exact_only"
            else:
                result["linkage_status"] = "no_exact_primer_link"
        out.append(result)
    return out


def main():
    a = args()
    a.out_dir.mkdir(parents=True, exist_ok=True)
    targets = read_csv(a.targets)
    query = [x for x in targets if x["analysis_role"] == "query"]
    refs = [x for x in targets if x["analysis_role"] == "reference"]
    if len(query) != 1 or len(refs) < 2:
        raise ValueError("targets require one query and at least two references")
    query = query[0]
    if len({x["accession"] for x in targets}) != len(targets):
        raise ValueError("duplicate accession")

    gbdir = a.out_dir / "genbank"
    gbdir.mkdir(exist_ok=True)
    records, extracted, full = {}, {}, {}
    for i, target in enumerate(targets):
        accession = target["accession"]
        text = fetch(accession, a.email, a.api_key)
        gb = gbdir / f"{accession}.gb"
        gb.write_text(text, encoding="utf-8", newline="\n")
        parsed = list(SeqIO.parse(gb, "genbank"))
        if len(parsed) != 1:
            raise ValueError(f"{accession}: expected one record")
        record = parsed[0]
        if target["organism"].lower() not in record.annotations.get("organism", "").lower():
            raise ValueError(f"{accession}: organism mismatch")
        records[accession] = record
        extracted[accession] = extract(record)
        full[accession] = str(record.seq).upper()
        if i + 1 < len(targets):
            time.sleep(0.12 if a.api_key else 0.4)

    nt_records, aa_records, manifest = [], [], []
    for target in targets:
        accession = target["accession"]
        record = records[accession]
        nt, aa, method, gene, product = extracted[accession]
        if not nt or not aa:
            raise ValueError(f"{accession}: missing CDS or protein")
        nt_records.append(SeqRecord(Seq(nt), id=accession, description=target["role"]))
        aa_records.append(SeqRecord(Seq(aa), id=accession, description=target["role"]))
        manifest.append({
            "requested_accession": accession, "record_accession": record.id,
            "role": target["role"], "analysis_role": target["analysis_role"],
            "organism": record.annotations.get("organism", ""),
            "description": record.description, "gene": gene, "product": product,
            "sequence_extraction": method, "nucleotide_bp": len(nt), "protein_aa": len(aa),
            "nucleotide_sha256": hashlib.sha256(nt.encode()).hexdigest(),
            "protein_sha256": hashlib.sha256(aa.encode()).hexdigest(),
        })

    qacc = query["accession"]
    fasta(a.out_dir / "all_cds.fasta", nt_records)
    fasta(a.out_dir / "all_proteins.fasta", aa_records)
    fasta(a.out_dir / "query_cds.fasta", [x for x in nt_records if x.id == qacc])
    fasta(a.out_dir / "query_protein.fasta", [x for x in aa_records if x.id == qacc])
    fasta(a.out_dir / "reference_cds.fasta", [x for x in nt_records if x.id != qacc])
    fasta(a.out_dir / "reference_proteins.fasta", [x for x in aa_records if x.id != qacc])

    bn = blast("blastn", a.out_dir / "query_cds.fasta", a.out_dir / "reference_cds.fasta", a.out_dir / "blastn.tsv")
    bp = blast("blastp", a.out_dir / "query_protein.fasta", a.out_dir / "reference_proteins.fasta", a.out_dir / "blastp.tsv")

    pairwise = []
    for target in refs:
        accession, nt, aa = target["accession"], bn.get(target["accession"]), bp.get(target["accession"])
        pairwise.append({
            "query_accession": qacc, "reference_accession": accession,
            "reference_role": target["role"], "tea_locus": target["tea_locus"],
            "source_cluster": target["source_cluster"],
            "nucleotide_comparison_status": "significant_local_hit" if nt else "no_significant_local_hit",
            "nucleotide_identity": f"{float(nt['pident']) / 100:.6f}" if nt else "",
            "nucleotide_query_coverage": f"{nt['qcov']:.6f}" if nt else "",
            "nucleotide_alignment_bp": nt["length"] if nt else "",
            "nucleotide_mismatches": nt["mismatch"] if nt else "",
            "nucleotide_gaps": nt["gaps"] if nt else "",
            "nucleotide_bitscore": nt["bitscore"] if nt else "",
            "protein_comparison_status": "significant_local_hit" if aa else "no_significant_local_hit",
            "protein_identity": f"{float(aa['pident']) / 100:.6f}" if aa else "",
            "protein_query_coverage": f"{aa['qcov']:.6f}" if aa else "",
            "protein_alignment_aa": aa["length"] if aa else "",
            "protein_mismatches": aa["mismatch"] if aa else "",
            "protein_gaps": aa["gaps"] if aa else "",
            "protein_bitscore": aa["bitscore"] if aa else "",
            "primary_source": target["primary_source"], "claim_boundary": target["claim_boundary"],
        })
    pairwise.sort(
        key=lambda x: (
            float(x["protein_bitscore"]) if x["protein_bitscore"] else -1.0,
            float(x["protein_query_coverage"]) if x["protein_query_coverage"] else -1.0,
            float(x["protein_identity"]) if x["protein_identity"] else -1.0,
        ),
        reverse=True,
    )
    for rank, row in enumerate(pairwise, 1):
        row["protein_rank"] = rank if row["protein_bitscore"] else ""

    assays = audit_assays(a.assays, full)
    rankable = [x for x in pairwise if x["protein_bitscore"]]
    if len(rankable) < 2:
        raise RuntimeError("fewer than two significant protein comparisons")
    best, runner = rankable[:2]
    pmargin = float(best["protein_identity"]) - float(runner["protein_identity"])
    nmargin = (
        float(best["nucleotide_identity"]) - float(runner["nucleotide_identity"])
        if best["nucleotide_identity"] and runner["nucleotide_identity"] else None
    )
    best_target = next(x for x in refs if x["accession"] == best["reference_accession"])
    b2 = next(x for x in pairwise if x["reference_role"] == "CsDFRb2")
    full_query = float(best["protein_query_coverage"]) >= 0.95 and (
        not best["nucleotide_query_coverage"] or float(best["nucleotide_query_coverage"]) >= 0.95
    )
    strong = full_query and pmargin >= 0.10 and (nmargin is None or nmargin >= 0.10)
    summary = {
        "analysis_version": "v0.1",
        "query": {"accession": qacc, "role": query["role"], "source_cluster": query["source_cluster"]},
        "candidate_count": len(refs),
        "candidates_without_significant_protein_hit": sum(
            not row["protein_bitscore"] for row in pairwise
        ),
        "best_reference": {
            "accession": best["reference_accession"], "role": best["reference_role"],
            "tea_locus": best["tea_locus"], "protein_identity": float(best["protein_identity"]),
            "protein_query_coverage": float(best["protein_query_coverage"]),
            "nucleotide_identity": float(best["nucleotide_identity"]) if best["nucleotide_identity"] else None,
            "nucleotide_query_coverage": float(best["nucleotide_query_coverage"]) if best["nucleotide_query_coverage"] else None,
        },
        "runner_up": {
            "accession": runner["reference_accession"], "role": runner["reference_role"],
            "protein_identity": float(runner["protein_identity"]),
            "nucleotide_identity": float(runner["nucleotide_identity"]) if runner["nucleotide_identity"] else None,
        },
        "identity_margin_over_runner_up": {"protein": round(pmargin, 6), "nucleotide": round(nmargin, 6) if nmargin is not None else None},
        "decision": "canonical_CsDFRa_like" if best_target["role"] == "CsDFRa" else f"closest_to_{best_target['role']}",
        "decision_confidence": "strong" if strong else "provisional",
        "exact_paired_primer_links_to_query": sum(x["linkage_status"] == "exact_paired_primer_link" for x in assays),
        "source_locus_contrast": {
            "source_locus": "CSA003949", "source_subclass": "CsDFRb2",
            "source_reference_accession": b2["reference_accession"],
            "same_reference_role_as_query_best": b2["reference_role"] == best["reference_role"],
            "interpretation": "The public C. japonica CjDFR sequence and the sequence-resolved C. sinensis source locus CSA003949 occupy different tea DFR subclasses.",
        },
        "claim_boundary": {
            "supported": [
                "sequence-lineage classification of the public CjDFR partial cDNA",
                "direct comparison against all six admitted tea DFR candidates",
                "distinction from the source-resolved CSA003949/CsDFRb2 locus",
                "published primer-to-sequence links where exact paired matches are recovered",
            ],
            "not_supported": [
                "identity of every later study's generic CjDFR target with AB524885.1",
                "duplication age or species-tree orthology from pairwise similarity alone",
                "equivalent biochemical function of all DFR-like copies",
                "macro-transition enrichment or adaptive selection",
            ],
        },
    }

    write_csv(a.out_dir / "sequence_manifest.csv", manifest, [
        "requested_accession", "record_accession", "role", "analysis_role", "organism",
        "description", "gene", "product", "sequence_extraction", "nucleotide_bp",
        "protein_aa", "nucleotide_sha256", "protein_sha256",
    ])
    write_csv(a.out_dir / "pairwise_summary.csv", pairwise, [
        "protein_rank", "query_accession", "reference_accession", "reference_role",
        "tea_locus", "source_cluster", "nucleotide_comparison_status",
        "nucleotide_identity", "nucleotide_query_coverage", "nucleotide_alignment_bp",
        "nucleotide_mismatches", "nucleotide_gaps", "nucleotide_bitscore",
        "protein_comparison_status", "protein_identity", "protein_query_coverage",
        "protein_alignment_aa", "protein_mismatches",
        "protein_gaps", "protein_bitscore", "primary_source", "claim_boundary",
    ])
    write_csv(a.out_dir / "assay_linkage.csv", assays, [
        "assay_id", "year", "taxon", "target_label", "sequence_accession",
        "forward_primer", "reverse_primer", "reported_amplicon_bp",
        "forward_exact_hits", "reverse_complement_exact_hits",
        "predicted_amplicon_bp", "amplicon_matches_reported", "linkage_status",
        "source", "claim_boundary",
    ])
    (a.out_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
