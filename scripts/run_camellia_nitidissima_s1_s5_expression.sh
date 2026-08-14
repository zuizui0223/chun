#!/usr/bin/env bash
set -euo pipefail

MANIFEST="${MANIFEST:-data/camellia_srp112181_admitted_manifest_v0_1.csv}"
OUTDIR="${OUTDIR:-build/camellia_nitidissima_s1_s5_expression}"
THREADS="${THREADS:-2}"
GWH_ASSEMBLY="${GWH_ASSEMBLY:-GWHFILD00000000.1}"
mkdir -p "$OUTDIR/reference" "$OUTDIR/quant" "$OUTDIR/fastq" "$OUTDIR/sra_cache" "$OUTDIR/results"

command -v salmon >/dev/null || { echo 'salmon is required' >&2; exit 2; }
command -v prefetch >/dev/null || { echo 'NCBI SRA Toolkit prefetch is required' >&2; exit 2; }
command -v fasterq-dump >/dev/null || { echo 'NCBI SRA Toolkit fasterq-dump is required' >&2; exit 2; }

salmon --version | tee "$OUTDIR/salmon_version.txt"
prefetch --version 2>&1 | tee "$OUTDIR/sra_toolkit_version.txt"

# Use the same submitter annotation that anchored JF343560.1 to
# GWHTFILD024733.1. This avoids mixing NCBI's unannotated GenBank assembly copy
# with a different transcript model.
GWH_BASE="https://download.cncb.ac.cn/gwh/Plants/Camellia_nitidissima_Camellia_nitidissima_${GWH_ASSEMBLY}"
curl -L --fail --retry 3 \
  "${GWH_BASE}/${GWH_ASSEMBLY}.RNA.fasta.gz" \
  -o "$OUTDIR/reference/${GWH_ASSEMBLY}.RNA.fasta.gz"
gzip -dc "$OUTDIR/reference/${GWH_ASSEMBLY}.RNA.fasta.gz" \
  > "$OUTDIR/reference/${GWH_ASSEMBLY}.RNA.fasta"
sha256sum "$OUTDIR/reference/${GWH_ASSEMBLY}.RNA.fasta" \
  > "$OUTDIR/reference/RNA.sha256"

for target in GWHTFILD024733.1 GWHTFILD005297.1 GWHTFILD024731.1; do
  if ! grep -q "^>${target}\([[:space:]]\|$\)" "$OUTDIR/reference/${GWH_ASSEMBLY}.RNA.fasta"; then
    echo "Required anchored/candidate FLS transcript $target is absent from the GWH RNA annotation" >&2
    exit 3
  fi
done

salmon index \
  -t "$OUTDIR/reference/${GWH_ASSEMBLY}.RNA.fasta" \
  -i "$OUTDIR/salmon_index" \
  -p "$THREADS" \
  --keepDuplicates

# Run one admitted library at a time to keep temporary disk bounded. The frozen
# manifest already validates run hashes/metadata against live NCBI provenance.
mapfile -t RUNS < <(python - "$MANIFEST" <<'PY'
import csv, sys
rows=list(csv.DictReader(open(sys.argv[1], newline='', encoding='utf-8')))
if len(rows) != 15:
    raise SystemExit(f'expected 15 admitted rows, found {len(rows)}')
for row in rows:
    if row.get('admission_status','').strip() != 'admit':
        raise SystemExit(f"non-admitted row present: {row.get('run')}")
    print(row['run'].strip())
PY
)

export NCBI_SETTINGS="/"
for run in "${RUNS[@]}"; do
  echo "=== ${run} ==="
  rm -rf "$OUTDIR/sra_cache/${run}" "$OUTDIR/fastq/${run}" "$OUTDIR/quant/${run}"
  mkdir -p "$OUTDIR/fastq/${run}"

  # Pin the exact run accession, not a BioProject query. --max-size u permits
  # the larger S5 replicate while still limiting the job to the 15 frozen runs.
  prefetch "$run" \
    --max-size u \
    --output-directory "$OUTDIR/sra_cache"

  fasterq-dump "$OUTDIR/sra_cache/${run}/${run}.sra" \
    --split-files \
    --threads "$THREADS" \
    --outdir "$OUTDIR/fastq/${run}" \
    --temp "$OUTDIR/fastq/${run}/tmp"

  R1="$OUTDIR/fastq/${run}/${run}_1.fastq"
  R2="$OUTDIR/fastq/${run}/${run}_2.fastq"
  if [[ ! -s "$R1" || ! -s "$R2" ]]; then
    echo "$run did not yield both paired FASTQ files" >&2
    exit 4
  fi

  salmon quant \
    -i "$OUTDIR/salmon_index" \
    -l A \
    -1 "$R1" \
    -2 "$R2" \
    -p "$THREADS" \
    --validateMappings \
    --seqBias \
    -o "$OUTDIR/quant/${run}"

  # Preserve quantification, discard bulky temporary sequence files.
  rm -rf "$OUTDIR/fastq/${run}" "$OUTDIR/sra_cache/${run}"
done

python scripts/summarize_camellia_fls_expression.py \
  --manifest "$MANIFEST" \
  --quant-dir "$OUTDIR/quant" \
  --out-dir "$OUTDIR/results"

python - "$OUTDIR/quant" "$OUTDIR/results/library_mapping_summary.csv" <<'PY'
import csv, json, pathlib, sys
qdir=pathlib.Path(sys.argv[1]); out=pathlib.Path(sys.argv[2])
rows=[]
for p in sorted(qdir.glob('SRR*/aux_info/meta_info.json')):
    meta=json.load(open(p, encoding='utf-8'))
    rows.append({
        'run': p.parents[1].name,
        'num_processed': meta.get('num_processed',''),
        'num_mapped': meta.get('num_mapped',''),
        'percent_mapped': meta.get('percent_mapped',''),
        'salmon_version': meta.get('salmon_version',''),
    })
if len(rows) != 15:
    raise SystemExit(f'expected 15 Salmon meta_info records, found {len(rows)}')
with open(out,'w',newline='',encoding='utf-8') as h:
    w=csv.DictWriter(h,fieldnames=['run','num_processed','num_mapped','percent_mapped','salmon_version'])
    w.writeheader(); w.writerows(rows)
print('Salmon mapping summaries recovered for all 15 admitted runs.')
PY

echo "C. nitidissima S1-S5 T2T-anchored expression reanalysis completed."
