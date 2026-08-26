#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 6 ]; then
  echo "usage: $0 RUN MAX_PAIRS OUT_R1 OUT_R2 METADATA_OUT SUMMARY_OUT" >&2
  exit 2
fi
RUN="$1"; MAX_PAIRS="$2"; OUT_R1="$3"; OUT_R2="$4"; METADATA_OUT="$5"; SUMMARY_OUT="$6"
mkdir -p "$(dirname "$OUT_R1")" "$(dirname "$OUT_R2")" "$(dirname "$METADATA_OUT")" "$(dirname "$SUMMARY_OUT")"
rm -f "$OUT_R1" "$OUT_R2"

# Primary route: ENA paired FASTQ prefix with its verified-full-file fallback.
set +e
python scripts/download_ena_fastq_prefix_v0_1.py \
  --run "$RUN" --max-spots "$MAX_PAIRS" \
  --out-r1 "$OUT_R1" --out-r2 "$OUT_R2" \
  --metadata-out "$METADATA_OUT" --summary-out "$SUMMARY_OUT"
ENA_RC=$?
set -e
if [ "$ENA_RC" -eq 0 ]; then
  exit 0
fi

echo "$RUN: ENA FASTQ route failed (rc=$ENA_RC); using validated public NCBI AWS normalized SRA fallback" >&2
rm -f "$OUT_R1" "$OUT_R2"
TMP_ROOT="$(dirname "$SUMMARY_OUT")/aws_sra_${RUN}"
rm -rf "$TMP_ROOT"
mkdir -p "$TMP_ROOT/reads"
SRA="$TMP_ROOT/${RUN}.sra"
URL="https://sra-pub-run-odp.s3.amazonaws.com/sra/${RUN}/${RUN}"

curl --fail --location --retry 5 --retry-all-errors --connect-timeout 30 "$URL" -o "$SRA"
test -s "$SRA"
BYTES=$(stat -c %s "$SRA")
test "$BYTES" -gt 1000000
vdb-validate "$SRA"
fastq-dump "$SRA" --split-files -O "$TMP_ROOT/reads" -X "$MAX_PAIRS"
test -s "$TMP_ROOT/reads/${RUN}_1.fastq"
test -s "$TMP_ROOT/reads/${RUN}_2.fastq"
mv "$TMP_ROOT/reads/${RUN}_1.fastq" "$OUT_R1"
mv "$TMP_ROOT/reads/${RUN}_2.fastq" "$OUT_R2"

python - "$RUN" "$MAX_PAIRS" "$OUT_R1" "$OUT_R2" "$SUMMARY_OUT" "$URL" "$BYTES" <<'PY'
import json,re,sys
from pathlib import Path
run,max_pairs,r1,r2,summary,url,sra_bytes=sys.argv[1:]
expected=int(max_pairs)
def rec(fh):
    x=[fh.readline() for _ in range(4)]
    if not x[0]: return None
    if any(not y for y in x[1:]): raise SystemExit('truncated FASTQ')
    return x
def rid(h): return re.sub(r'(?:/|_)[12]$','',h[1:].strip().split()[0])
n=0
with open(r1) as a,open(r2) as b:
    while True:
        x=rec(a); y=rec(b)
        if x is None and y is None: break
        if x is None or y is None: raise SystemExit('paired FASTQ length mismatch')
        if rid(x[0])!=rid(y[0]): raise SystemExit(f'pair ID mismatch at {n+1}')
        n+=1
if n!=expected: raise SystemExit(f'expected {expected} pairs, got {n}')
s={
 'status':'ready','run':run,'route':'NCBI_AWS_normalized_SRA_local_fastq_dump_fallback',
 'requested_max_pairs':expected,'actual_pairs':n,'sra_url':url,'sra_bytes':int(sra_bytes),
 'integrity_note':'ENA route failed; AWS normalized SRA object passed vdb-validate before bounded local fastq-dump conversion.'
}
Path(summary).write_text(json.dumps(s,indent=2)+'\n')
print(json.dumps(s,indent=2))
PY
rm -rf "$TMP_ROOT"
