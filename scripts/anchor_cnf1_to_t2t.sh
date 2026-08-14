#!/usr/bin/env bash
set -euo pipefail

ASSEMBLY="${ASSEMBLY:-GCA_049201075.1}"
GWH_ASSEMBLY="${GWH_ASSEMBLY:-GWHFILD00000000.1}"
QUERY="${QUERY:-JF343560.1}"
OUTDIR="${OUTDIR:-build/camellia_t2t_fls_anchor}"
mkdir -p "$OUTDIR/bin" "$OUTDIR/reference"

# NCBI carries the GenBank copy of the assembly. Probe it first because this is
# a stable cross-database identity check, but do not assume the GenBank copy
# carries the submitter's gene annotation.
curl -L --fail --retry 3 \
  -o "$OUTDIR/bin/datasets" \
  'https://ftp.ncbi.nlm.nih.gov/pub/datasets/command-line/v2/linux-amd64/datasets'
chmod +x "$OUTDIR/bin/datasets"
"$OUTDIR/bin/datasets" --version | tee "$OUTDIR/datasets_version.txt"

"$OUTDIR/bin/datasets" download genome accession "$ASSEMBLY" \
  --include cds,protein,gff3,rna \
  --filename "$OUTDIR/reference/${ASSEMBLY}.zip" \
  --no-progressbar
unzip -q "$OUTDIR/reference/${ASSEMBLY}.zip" -d "$OUTDIR/reference/${ASSEMBLY}"
find "$OUTDIR/reference/${ASSEMBLY}" -maxdepth 6 -type f | sort > "$OUTDIR/reference_files.txt"

CDS_FASTA="$(find "$OUTDIR/reference/${ASSEMBLY}" -type f \( -name 'cds_from_genomic.fna' -o -name '*cds*.fna' \) | head -n 1 || true)"
GFF="$(find "$OUTDIR/reference/${ASSEMBLY}" -type f \( -name '*.gff' -o -name '*.gff3' \) | head -n 1 || true)"
ANNOTATION_SOURCE="NCBI:${ASSEMBLY}"

# GCA_049201075.1 currently exposes the assembly through NCBI without the
# submitter annotation. The primary GWH registration for the same T2T resource
# explicitly publishes DNA/GFF/RNA/CDS/Protein. Use that authoritative
# annotation rather than lowering the anchor criterion or inventing gene IDs.
if [[ -z "$CDS_FASTA" || ! -s "$CDS_FASTA" ]]; then
  echo "NCBI $ASSEMBLY has no delivered CDS annotation; switching to primary GWH annotation $GWH_ASSEMBLY." >&2
  GWH_BASE="https://download.cncb.ac.cn/gwh/Plants/Camellia_nitidissima_Camellia_nitidissima_${GWH_ASSEMBLY}"
  curl -L --fail --retry 3 \
    "${GWH_BASE}/${GWH_ASSEMBLY}.CDS.fasta.gz" \
    -o "$OUTDIR/reference/${GWH_ASSEMBLY}.CDS.fasta.gz"
  curl -L --fail --retry 3 \
    "${GWH_BASE}/${GWH_ASSEMBLY}.gff.gz" \
    -o "$OUTDIR/reference/${GWH_ASSEMBLY}.gff.gz"
  gzip -dc "$OUTDIR/reference/${GWH_ASSEMBLY}.CDS.fasta.gz" \
    > "$OUTDIR/reference/${GWH_ASSEMBLY}.CDS.fasta"
  gzip -dc "$OUTDIR/reference/${GWH_ASSEMBLY}.gff.gz" \
    > "$OUTDIR/reference/${GWH_ASSEMBLY}.gff"
  CDS_FASTA="$OUTDIR/reference/${GWH_ASSEMBLY}.CDS.fasta"
  GFF="$OUTDIR/reference/${GWH_ASSEMBLY}.gff"
  ANNOTATION_SOURCE="NGDC_GWH:${GWH_ASSEMBLY}"
fi

if [[ ! -s "$CDS_FASTA" ]]; then
  echo "No non-empty CDS FASTA could be recovered from NCBI or NGDC/GWH." >&2
  exit 2
fi

# Freeze provenance/checksums before any sequence inference.
{
  echo "genbank_assembly=${ASSEMBLY}"
  echo "gwh_assembly=${GWH_ASSEMBLY}"
  echo "annotation_source=${ANNOTATION_SOURCE}"
  echo "cds_file=${CDS_FASTA}"
  echo "gff_file=${GFF}"
} > "$OUTDIR/annotation_provenance.txt"
sha256sum "$CDS_FASTA" > "$OUTDIR/cds.sha256"
if [[ -n "$GFF" && -s "$GFF" ]]; then
  sha256sum "$GFF" > "$OUTDIR/gff.sha256"
fi

# Fetch the exact experimentally characterized CnFLS cDNA accession.
curl -L --fail --retry 3 \
  "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id=${QUERY}&rettype=fasta&retmode=text" \
  -o "$OUTDIR/${QUERY}.fasta"
if ! grep -q '^>' "$OUTDIR/${QUERY}.fasta"; then
  echo "Failed to recover FASTA for $QUERY" >&2
  exit 3
fi
sha256sum "$OUTDIR/${QUERY}.fasta" > "$OUTDIR/query.sha256"

makeblastdb -in "$CDS_FASTA" -dbtype nucl -out "$OUTDIR/cds_db" >/dev/null
blastn \
  -query "$OUTDIR/${QUERY}.fasta" \
  -db "$OUTDIR/cds_db" \
  -evalue 1e-20 \
  -perc_identity 60 \
  -qcov_hsp_perc 50 \
  -max_target_seqs 100 \
  -outfmt '6 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore qcovs' \
  > "$OUTDIR/${QUERY}_vs_T2T_cds.tsv"

python - "$OUTDIR/${QUERY}_vs_T2T_cds.tsv" "$OUTDIR/cnf1_anchor_summary.csv" "$ANNOTATION_SOURCE" <<'PY'
import csv, sys
src, out, annotation_source = sys.argv[1:]
fields = ['qseqid','sseqid','pident','length','mismatch','gapopen','qstart','qend','sstart','send','evalue','bitscore','qcovs']
rows=[]
with open(src, newline='', encoding='utf-8') as h:
    for r in csv.DictReader(h, delimiter='\t', fieldnames=fields):
        r['annotation_source'] = annotation_source
        rows.append(r)
if not rows:
    raise SystemExit('No CnFLS1-like CDS hits passed the permissive anchor screen')
rows.sort(key=lambda r:(-float(r['bitscore']), -float(r['qcovs']), -float(r['pident'])))
for i,r in enumerate(rows,1):
    r['rank']=str(i)
out_fields=['rank','annotation_source']+fields
with open(out,'w',newline='',encoding='utf-8') as h:
    w=csv.DictWriter(h,fieldnames=out_fields)
    w.writeheader(); w.writerows(rows)
top=rows[0]
print(f"annotation_source={annotation_source}")
print(f"top_hit={top['sseqid']} pident={top['pident']} qcovs={top['qcovs']} bitscore={top['bitscore']}")
print(f"candidate_hits={len(rows)}")
# This is an annotation anchor, not a final orthology call. Still require a
# strong near-full-length top match before locus IDs are admitted downstream.
if float(top['pident']) < 85 or float(top['qcovs']) < 80:
    raise SystemExit('Top T2T CDS hit is too weak for a confident CnFLS1 annotation anchor')
PY

if [[ -n "$GFF" && -s "$GFF" ]]; then
  cp "$GFF" "$OUTDIR/reference_annotation.gff3"
fi

echo "CnFLS1 T2T anchor gate completed for $QUERY using $ANNOTATION_SOURCE"
