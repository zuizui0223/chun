#!/usr/bin/env python3
from __future__ import annotations
import argparse, gzip, hashlib, json, re, urllib.request
from pathlib import Path

BASE = 'https://download.cncb.ac.cn/gwh/Plants/Epimedium_pubescens_IMPLAD_EP_1.0_GWHBECS00000000/'
FILES = {
    'gff': BASE + 'GWHBECS00000000.gff.gz',
    'protein': BASE + 'GWHBECS00000000.Protein.faa.gz',
}
TERMS = {
    'PAL': [r'\bPAL\b', r'phenylalanine ammonia[- ]lyase'],
    'CHS': [r'\bCHS\b', r'chalcone synthase'],
    'CHI': [r'\bCHI\b', r'chalcone isomerase'],
    'F3H': [r'\bF3H\b', r'flavanone 3[- ]hydroxylase'],
    'F3H_DERIVATIVE': [r"F3['’]H", r"F3['’]5['’]H", r'flavonoid 3'],
    'DFR': [r'\bDFR\b', r'dihydroflavonol 4[- ]reductase'],
    'ANS': [r'\bANS\b', r'anthocyanidin synthase', r'leucoanthocyanidin dioxygenase'],
    'FLS': [r'\bFLS\b', r'flavonol synthase'],
    'LAR': [r'\bLAR\b', r'leucoanthocyanidin reductase'],
    'ANR': [r'\bANR\b', r'anthocyanidin reductase'],
}


def download(url: str) -> tuple[bytes, str | None]:
    req = urllib.request.Request(url, headers={'User-Agent':'chun-atlas-reference-probe/0.1'})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.read(), None
    except Exception as e:
        return b'', f'{type(e).__name__}: {e}'


def text_from_gz(data: bytes) -> str:
    try:
        return gzip.decompress(data).decode('utf-8', errors='replace')
    except Exception:
        return ''


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()

    resources = {}
    combined = ''
    for name, url in FILES.items():
        data, error = download(url)
        text = text_from_gz(data) if data else ''
        combined += '\n' + text
        resources[name] = {
            'url': url,
            'bytes': len(data),
            'sha256': hashlib.sha256(data).hexdigest() if data else None,
            'decompressed_chars': len(text),
            'error': error,
        }

    hits = {}
    for family, patterns in TERMS.items():
        matched = set()
        for line in combined.splitlines():
            if any(re.search(p, line, flags=re.I) for p in patterns):
                matched.add(line[:500])
        hits[family] = {'line_hits': len(matched), 'examples': sorted(matched)[:5]}

    mandatory = ['PAL','CHS','CHI','F3H','DFR','ANS','FLS']
    detected = [x for x in mandatory if hits[x]['line_hits'] > 0]
    status = 'ANNOTATION_TEXT_DETECTS_ALL_PRIMARY_FAMILIES' if len(detected) == len(mandatory) else 'ANNOTATION_TEXT_INCOMPLETE_REQUIRE_SEQUENCE_OR_DOMAIN_MAPPING'

    summary = {
        'version': 'v0.1',
        'reference': 'GWHBECS00000000',
        'resources': resources,
        'family_text_hits': hits,
        'primary_family_text_detected': detected,
        'primary_family_text_total': len(mandatory),
        'status': status,
        'interpretation': 'text hits are an annotation inventory only; absence is not biological absence and triggers sequence/domain-based mapping rather than outcome imputation',
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
