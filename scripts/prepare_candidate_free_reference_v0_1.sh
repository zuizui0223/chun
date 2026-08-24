#!/usr/bin/env bash
set -euo pipefail

# Prepare the fixed candidate-free Camellia reference without consulting any
# flower-colour or expression outcome. Primary route downloads the RNA and GFF
# distributions of the exact GCA_013676235.1 assembly directly. The former
# genome+GFF reconstruction remains a fallback only.

OUT_ROOT=${1:?usage: prepare_candidate_free_reference_v0_1.sh OUT_ROOT}
REF_ACCESSION=${REF_ACCESSION:-GCA_013676235.1}
REF_DIR="$OUT_ROOT/reference"
DIAG="$OUT_ROOT/reference_route_diagnostic.txt"
mkdir -p "$REF_DIR"
: > "$DIAG"

GWH_BASE='https://download.cncb.ac.cn/assembly/ncbi/Plants/GCA/013/676/Camellia_sinensis_black_tea_HZAU_G240_1.0_GCA_013676235.1'
GWH_GFF="$GWH_BASE/GCA_013676235.1_HZAU_G240_1.0_genomic.gff.gz"
GWH_RNA="$GWH_BASE/GCA_013676235.1_HZAU_G240_1.0_rna_from_genomic.fna.gz"

log() { printf '%s\n' "$*" | tee -a "$DIAG"; }
file_bytes() { stat -c '%s' "$1" 2>/dev/null || printf 'NA'; }

log "reference_accession=$REF_ACCESSION"
log "primary_route=GWH_integrated_NCBI_direct_RNA_GFF"
log "fallback_route=NCBI_Datasets_genome_GFF_plus_gffread"
log "gwh_rna_url=$GWH_RNA"
log "gwh_gff_url=$GWH_GFF"

RNA_FASTA=''
GFF=''
REFERENCE_ROUTE=''

log 'attempt_primary_route=1'
set +e
curl -fL --retry 3 --retry-delay 2 --connect-timeout 20 --max-time 900 \
  "$GWH_RNA" -o "$REF_DIR/rna_from_genomic.fna.gz"
RNA_RC=$?
curl -fL --retry 3 --retry-delay 2 --connect-timeout 20 --max-time 900 \
  "$GWH_GFF" -o "$REF_DIR/genomic.gff.gz"
GFF_RC=$?
set -e
log "primary_rna_curl_rc=$RNA_RC"
log "primary_gff_curl_rc=$GFF_RC"

if [[ $RNA_RC -eq 0 && $GFF_RC -eq 0 ]] \
   && gzip -t "$REF_DIR/rna_from_genomic.fna.gz" \
   && gzip -t "$REF_DIR/genomic.gff.gz"; then
  gzip -dc "$REF_DIR/rna_from_genomic.fna.gz" > "$REF_DIR/rna_from_genomic.fna"
  gzip -dc "$REF_DIR/genomic.gff.gz" > "$REF_DIR/genomic.gff"
  if [[ -s "$REF_DIR/rna_from_genomic.fna" && -s "$REF_DIR/genomic.gff" ]]; then
    RNA_FASTA="$REF_DIR/rna_from_genomic.fna"
    GFF="$REF_DIR/genomic.gff"
    REFERENCE_ROUTE='GWH_integrated_NCBI_direct_RNA_GFF'
  fi
fi

if [[ -z "$REFERENCE_ROUTE" ]]; then
  log 'primary_route_status=failed_or_invalid'
  log 'attempt_fallback_route=1'
  rm -f "$REF_DIR/rna_from_genomic.fna.gz" "$REF_DIR/genomic.gff.gz" \
        "$REF_DIR/rna_from_genomic.fna" "$REF_DIR/genomic.gff"
  DATASETS="$OUT_ROOT/datasets"
  curl -fsSL --retry 3 --connect-timeout 20 \
    https://ftp.ncbi.nlm.nih.gov/pub/datasets/command-line/v2/linux-amd64/datasets \
    -o "$DATASETS"
  chmod +x "$DATASETS"
  "$DATASETS" download genome accession "$REF_ACCESSION" \
    --include genome,gff3 --filename "$OUT_ROOT/reference.zip"
  rm -rf "$REF_DIR/package"
  unzip -q "$OUT_ROOT/reference.zip" -d "$REF_DIR/package"
  GENOME_FASTA=$(find "$REF_DIR/package" -type f -name 'genomic.fna' | head -n1)
  GFF=$(find "$REF_DIR/package" -type f \( -name 'genomic.gff' -o -name '*.gff' -o -name '*.gff3' \) | head -n1)
  test -n "$GENOME_FASTA" && test -s "$GENOME_FASTA"
  test -n "$GFF" && test -s "$GFF"
  RNA_FASTA="$REF_DIR/reconstructed_transcripts.fna"
  gffread "$GFF" -g "$GENOME_FASTA" -w "$RNA_FASTA"
  test -s "$RNA_FASTA"
  REFERENCE_ROUTE='NCBI_Datasets_genome_GFF_plus_gffread'
  log "fallback_genome_bytes=$(file_bytes "$GENOME_FASTA")"
fi

test -s "$RNA_FASTA"
test -s "$GFF"
log "reference_route=$REFERENCE_ROUTE"
log "rna_fasta=$RNA_FASTA"
log "rna_fasta_bytes=$(file_bytes "$RNA_FASTA")"
log "gff=$GFF"
log "gff_bytes=$(file_bytes "$GFF")"
log "reference_status=ready"

printf 'reference=%s\nroute=%s\nrna_fasta=%s\ngff=%s\n' \
  "$REF_ACCESSION" "$REFERENCE_ROUTE" "$RNA_FASTA" "$GFF" \
  > "$OUT_ROOT/reference_contract.txt"

if [[ -n "${GITHUB_ENV:-}" ]]; then
  printf 'RNA_FASTA=%s\nGFF=%s\nREFERENCE_ROUTE=%s\n' \
    "$RNA_FASTA" "$GFF" "$REFERENCE_ROUTE" >> "$GITHUB_ENV"
fi
