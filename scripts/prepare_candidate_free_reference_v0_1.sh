#!/usr/bin/env bash
set -euo pipefail

# Prepare the fixed candidate-free Camellia reference without consulting any
# flower-colour or expression outcome. The primary reference is the annotated
# Shuchazao RefSeq assembly, selected because family identity is resolvable from
# its reference annotation. Expression values and contrast directions are never
# consulted during reference or family selection.

OUT_ROOT=${1:?usage: prepare_candidate_free_reference_v0_1.sh OUT_ROOT}
REF_ACCESSION=${REF_ACCESSION:-GCF_004153795.1}
REF_DIR="$OUT_ROOT/reference"
DIAG="$OUT_ROOT/reference_route_diagnostic.txt"
mkdir -p "$REF_DIR"
: > "$DIAG"

log() { printf '%s\n' "$*" | tee -a "$DIAG"; }
file_bytes() { stat -c '%s' "$1" 2>/dev/null || printf 'NA'; }

RNA_FASTA=''
GFF=''
REFERENCE_ROUTE=''
GWH_RNA=''
GWH_GFF=''

if [[ "$REF_ACCESSION" == 'GCF_004153795.1' ]]; then
  GWH_BASE='https://download.cncb.ac.cn/assembly/ncbi/Plants/GCF/004/153/Camellia_sinensis_black_tea_AHAU_CSS_1_GCF_004153795.1'
  GWH_GFF="$GWH_BASE/GCF_004153795.1_AHAU_CSS_1_genomic.gff.gz"
  GWH_RNA="$GWH_BASE/GCF_004153795.1_AHAU_CSS_1_rna_from_genomic.fna.gz"
fi

log "reference_accession=$REF_ACCESSION"
log 'reference_selection_rule=annotation_informative_refseq_without_expression_or_colour_outcome'
log 'primary_route=GWH_NCBI_RefSeq_direct_RNA_GFF'
log 'fallback_route=NCBI_Datasets_RNA_GFF'
log "gwh_rna_url=$GWH_RNA"
log "gwh_gff_url=$GWH_GFF"

if [[ -n "$GWH_RNA" && -n "$GWH_GFF" ]]; then
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
      REFERENCE_ROUTE='GWH_NCBI_RefSeq_direct_RNA_GFF'
    fi
  fi
else
  log 'primary_route_status=no_direct_route_registered_for_accession'
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
    --include rna,gff3 --filename "$OUT_ROOT/reference.zip"
  rm -rf "$REF_DIR/package"
  unzip -q "$OUT_ROOT/reference.zip" -d "$REF_DIR/package"
  RNA_FASTA=$(find "$REF_DIR/package" -type f \( -name 'rna.fna' -o -name '*_rna.fna' -o -name 'rna_from_genomic.fna' \) | head -n1)
  GFF=$(find "$REF_DIR/package" -type f \( -name 'genomic.gff' -o -name '*.gff' -o -name '*.gff3' \) | head -n1)
  test -n "$RNA_FASTA" && test -s "$RNA_FASTA"
  test -n "$GFF" && test -s "$GFF"
  REFERENCE_ROUTE='NCBI_Datasets_RNA_GFF'
fi

test -s "$RNA_FASTA"
test -s "$GFF"
log "reference_route=$REFERENCE_ROUTE"
log "rna_fasta=$RNA_FASTA"
log "rna_fasta_bytes=$(file_bytes "$RNA_FASTA")"
log "gff=$GFF"
log "gff_bytes=$(file_bytes "$GFF")"
log 'reference_status=ready'

printf 'reference=%s\nroute=%s\nrna_fasta=%s\ngff=%s\n' \
  "$REF_ACCESSION" "$REFERENCE_ROUTE" "$RNA_FASTA" "$GFF" \
  > "$OUT_ROOT/reference_contract.txt"

if [[ -n "${GITHUB_ENV:-}" ]]; then
  printf 'REF_ACCESSION=%s\nRNA_FASTA=%s\nGFF=%s\nREFERENCE_ROUTE=%s\n' \
    "$REF_ACCESSION" "$RNA_FASTA" "$GFF" "$REFERENCE_ROUTE" >> "$GITHUB_ENV"
fi
