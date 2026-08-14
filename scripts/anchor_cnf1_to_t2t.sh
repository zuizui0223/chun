#!/usr/bin/env bash
set -euo pipefail

ASSEMBLY="${ASSEMBLY:-GCA_049201075.1}"
QUERY="${QUERY:-JF343560.1}"
OUTDIR="${OUTDIR:-build/camellia_t2t_fls_anchor}"
mkdir -p "$OUTDIR/bin" "$OUTDIR/reference"

# NCBI Datasets v2 is downloaded from the current official NCBI binary endpoint.
curl -L --fail --retry 3 \
  -o "$OUTDIR/bin/datasets" \
  'https://ftp.ncbi.nlm.nih.gov/pub/datasets/command-line/v2/linux-amd64/datasets'
chmod +x "$OUTDIR/bin/datasets"
"$OUTDIR/bin/datasets" --version | tee "$OUTDIR/datasets_version.txt"

# Request only annotation-scale files needed to anchor the experimentally
# validated cDNA; do not download the 2.72-Gb genomic FASTA in this first gate.
"$OUTDIR/bin/datasets" download genome accession "$ASSEMBLY" \
  --include cds,protein,gff3,rna \
  --filename "$OUTDIR/reference/${ASSEMBLY}.zip" \
  --no-progressbar
unzip -q "$OUTDIR/reference/${ASSEMBLY}.zip" -d "$OUTDIR/reference/${ASSEMBLY}"

find "$OUTDIR/reference/${ASSEMBLY}" -type f -maxdepth 5 | sort > "$OUTDIR/reference_files.txt"

CDS_FASTA="$(find "$OUTDIR/reference/${ASSEMBLY}" -type f \( -name 'cds_from_genomic.fna' -o -name '*cds*.fna' \) | head -n 1 || true)"
GFF="$(find "$OUTDIR/reference/${ASSEMBLY}" -type f -name '*.gff' -o -name '*.gff3' | head -n 1 || true)"
if [[ -z "$CDS_FASTA" || ! -s "$CDS_FASTA" ]]; then
  echo "No CDS FASTA was delivered for $ASSEMBLY; cannot anchor $QUERY against annotation." >&2
  cat "$OUTDIR/reference_files.txt" >&2
  exit 2
fi

# Fetch the exact published CnFLS cDNA accession from NCBI Nucleotide.
curl -L --fail --retry 3 \
  "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id=${QUERY}&rettype=fasta&retmode=text" \
  -o "$OUTDIR/${QUERY}.fasta"
if ! grep -q '^>' "$OUTDIR/${QUERY}.fasta"; then
  echo "Failed to recover FASTA for $QUERY" >&2
  exit 3
fi

# BLAST+ is supplied by the runner/host. The workflow installs ncbi-blast+.
makeblastdb -in "$CDS_FASTA" -dbtype nucl -out "$OUTDIR/cds_db" >/dev/null
blastn \
  -query "$OUTDIR/${QUERY}.fasta" \
  -db "$OUTDIR/cds_db" \
  -evalue 1e-20 \
  -perc_identity 60 \
  -qcov_hsp_perc 50 \
  -max_target_seqs 100 \
  -outfmt '6 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore qcovs' \
  > "$OUTDIR/${QUERY}_vs_${ASSEMBLY}_cds.tsv"

python - "$OUTDIR/${QUERY}_vs_${ASSEMBLY}_cds.tsv" "$OUTDIR/cnf1_anchor_summary.csv" <<'PY'
import csv, sys
src, out = sys.argv[1:]
fields = ['qseqid','sseqid','pident','length','mismatch','gapopen','qstart','qend','sstart','send','evalue','bitscore','qcovs']
rows=[]
with open(src, newline='', encoding='utf-8') as h:
    for r in csv.DictReader(h, delimiter='\t', fieldnames=fields):
        rows.append(r)
if not rows:
    raise SystemExit('No CnFLS1-like CDS hits passed the permissive anchor screen')
rows.sort(key=lambda r:(-float(r['bitscore']), -float(r['pident']), -float(r['qcovs'])))
for i,r in enumerate(rows,1):
    r['rank']=str(i)
with open(out,'w',newline='',encoding='utf-8') as h:
    w=csv.DictWriter(h,fieldnames=['rank']+fields)
    w.writeheader(); w.writerows(rows)
top=rows[0]
print(f"top_hit={top['sseqid']} pident={top['pident']} qcovs={top['qcovs']} bitscore={top['bitscore']}")
print(f"candidate_hits={len(rows)}")
# This is an anchor gate, not a functional-orthology assertion. Still require
# a near-full-length strong top match before using the result downstream.
if float(top['pident']) < 85 or float(top['qcovs']) < 80:
    raise SystemExit('Top T2T CDS hit is too weak for a confident CnFLS1 annotation anchor')
PY

if [[ -n "$GFF" && -s "$GFF" ]]; then
  cp "$GFF" "$OUTDIR/reference_annotation.gff3"
fi

echo "CnFLS1 T2T anchor gate completed for $QUERY -> $ASSEMBLY"
