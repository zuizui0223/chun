#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

from Bio import SeqIO

ACCESSION_URL = "https://pmc-oa-opendata.s3.amazonaws.com/PMC7588356.1/Data_Sheet_1.csv"
ACCESSION_SHA256 = "942d684256eb4527d02b274d9da374c8cc5585a190ef20a9058c231460a4ad71"
LOCI = ["matK", "trnL", "ndhF", "trnK", "rbcL", "ITS"]
EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
UA = "chun-iris-primary-tree/0.1"


def fetch(url: str, retries: int = 8) -> bytes:
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=180) as r:
                return r.read()
        except Exception:
            if i == retries - 1:
                raise
            time.sleep(min(30, 2 ** i))
    raise RuntimeError("unreachable")


def clean(x: str) -> str:
    return re.sub(r"\s+", " ", str(x or "")).strip()


def normalize_accession(x: str) -> str:
    x = clean(x)
    if not x or x == "-":
        return ""
    return x.split()[0]


def safe_taxon(raw: str) -> str:
    s = clean(raw).replace("×", "x")
    s = re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")
    return s


def parse_source(data: bytes) -> list[dict[str, str]]:
    rows = list(csv.reader(io.StringIO(data.decode("utf-8-sig")), delimiter=";"))
    if rows[1] != ["organism", *LOCI]:
        raise SystemExit(f"accession header drifted: {rows[1]}")
    out = []
    for r in rows[2:]:
        r = r + [""] * (7 - len(r))
        d = dict(zip(["organism", *LOCI], [clean(x) for x in r[:7]]))
        if not d["organism"]:
            continue
        if d["organism"] == "Iris_darwasica":
            continue
        out.append(d)
    return out


def efetch_fasta(accessions: list[str]) -> dict[str, str]:
    seqs: dict[str, str] = {}
    for start in range(0, len(accessions), 80):
        batch = accessions[start:start+80]
        q = urllib.parse.urlencode({
            "db": "nuccore",
            "id": ",".join(batch),
            "rettype": "fasta",
            "retmode": "text",
        })
        raw = fetch(EFETCH + "?" + q)
        for rec in SeqIO.parse(io.StringIO(raw.decode("utf-8")), "fasta"):
            acc = rec.id.split(".")[0]
            seqs[acc] = str(rec.seq).upper()
        time.sleep(0.4)
    missing = [a for a in accessions if a.split(".")[0] not in seqs]
    for acc in missing:
        q = urllib.parse.urlencode({"db":"nuccore","id":acc,"rettype":"fasta","retmode":"text"})
        raw = fetch(EFETCH + "?" + q)
        records = list(SeqIO.parse(io.StringIO(raw.decode("utf-8")), "fasta"))
        if len(records) != 1:
            raise SystemExit(f"could not uniquely fetch accession {acc}: n={len(records)}")
        seqs[acc.split(".")[0]] = str(records[0].seq).upper()
        time.sleep(0.4)
    return seqs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()
    out = args.out_dir
    out.mkdir(parents=True, exist_ok=True)

    source = fetch(ACCESSION_URL)
    if hashlib.sha256(source).hexdigest() != ACCESSION_SHA256:
        raise SystemExit("frozen accession source SHA drifted")
    rows = parse_source(source)
    if len(rows) != 227:
        raise SystemExit(f"expected 227 source tree rows after darwasica exclusion, got {len(rows)}")

    taxa = [safe_taxon(r["organism"]) for r in rows]
    if len(taxa) != len(set(taxa)):
        raise SystemExit("tree tip labels are not unique")

    assignments: dict[str, list[tuple[str, str]]] = {loc: [] for loc in LOCI}
    all_acc: set[str] = set()
    for r in rows:
        taxon = safe_taxon(r["organism"])
        for loc in LOCI:
            acc = normalize_accession(r[loc])
            if acc:
                assignments[loc].append((taxon, acc))
                all_acc.add(acc)

    accessions = sorted(all_acc)
    seqs = efetch_fasta(accessions)

    lengths: dict[str, list[int]] = {}
    for loc in LOCI:
        fasta = out / f"{loc}.source_full_records.fasta"
        lens = []
        with fasta.open("w", encoding="utf-8") as fh:
            for taxon, acc in assignments[loc]:
                key = acc.split(".")[0]
                seq = seqs.get(key, "")
                if not seq:
                    raise SystemExit(f"missing downloaded sequence for {loc} {taxon} {acc}")
                fh.write(f">{taxon}\n{seq}\n")
                lens.append(len(seq))
        lengths[loc] = lens

    cross: dict[str, list[str]] = {}
    locs_by_acc: dict[str, set[str]] = {}
    for loc, vals in assignments.items():
        for _, acc in vals:
            locs_by_acc.setdefault(acc.split(".")[0], set()).add(loc)
    for acc, locs in locs_by_acc.items():
        if len(locs) > 1:
            cross[acc] = sorted(locs)

    receipt = {
        "version": "v0.1",
        "status": "IRIS_PRIMARY_TREE_INPUTS_PREPARED_TRAIT_BLIND",
        "source_sha256": ACCESSION_SHA256,
        "tree_taxa_after_darwasica_exclusion": len(rows),
        "tree_tip_labels_unique": True,
        "loci": LOCI,
        "sequence_semantics": "FULL_GENBANK_RECORD_PER_SOURCE_MARKER_ASSIGNMENT",
        "unique_accessions_downloaded": len(accessions),
        "per_locus_sequence_counts": {loc: len(assignments[loc]) for loc in LOCI},
        "per_locus_length_minmax": {loc: [min(lengths[loc]), max(lengths[loc])] if lengths[loc] else [0,0] for loc in LOCI},
        "cross_locus_duplicate_accessions": len(cross),
        "matK_trnK_shared_accessions": sum(set(locs) == {"matK","trnK"} for locs in cross.values()),
        "Iris_darwasica_excluded": True,
        "Iris_cedretii_present_tree_only_candidate": any(r["organism"] == "Iris_cedretii" for r in rows),
        "trait_file_read": False,
        "trait_values_used": False,
        "auc_computed": False,
        "decision_computed": False,
        "paper1_science_changed": False,
    }
    (out / "tree_input_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    (out / "tree_taxa.txt").write_text("\n".join(taxa) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
