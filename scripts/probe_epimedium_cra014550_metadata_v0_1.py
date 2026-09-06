#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, urllib.request
from pathlib import Path

URLS = [
    'https://ngdc.cncb.ac.cn/gsa/browse/CRA014550',
    'https://ngdc.cncb.ac.cn/gsa/browse/CRA014550/',
]


def fetch(url: str) -> tuple[str, str | None]:
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (compatible; chun-atlas-metadata-probe/0.1)',
        'Accept': 'text/html,application/xhtml+xml',
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read().decode('utf-8', errors='replace')
            return data, None
    except Exception as e:  # fail closed but keep diagnostic runnable
        return '', f'{type(e).__name__}: {e}'


def uniq(pattern: str, text: str) -> list[str]:
    return sorted(set(re.findall(pattern, text)))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()

    attempts = []
    combined = ''
    for url in URLS:
        text, err = fetch(url)
        attempts.append({'url': url, 'bytes': len(text.encode("utf-8")), 'error': err})
        combined += '\n' + text

    runs = uniq(r'\bCRR\d+\b', combined)
    experiments = uniq(r'\bCRX\d+\b', combined)
    samples = uniq(r'\bSAMC\d+\b', combined)
    projects = uniq(r'\bPRJCA\d+\b', combined)
    fastq_urls = sorted(set(re.findall(r'https://download\.cncb\.ac\.cn/[^"\'<>\s]+(?:fastq|fq)\.gz', combined)))

    if runs:
        status = 'PROJECT_PAGE_EXPOSES_RUN_ACCESSIONS'
    elif combined.strip():
        status = 'PROJECT_PAGE_RETRIEVED_BUT_RUNS_NOT_EXPOSED'
    else:
        status = 'REMOTE_METADATA_UNRESOLVED'

    summary = {
        'version': 'v0.1',
        'project': 'CRA014550',
        'status': status,
        'attempts': attempts,
        'run_accessions': runs,
        'experiment_accessions': experiments,
        'sample_accessions': samples,
        'project_accessions': projects,
        'fastq_urls_found': fastq_urls,
        'admission_rule': 'probe output is diagnostic only; no run is admitted until species/organ/state/replicate metadata are verified',
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
