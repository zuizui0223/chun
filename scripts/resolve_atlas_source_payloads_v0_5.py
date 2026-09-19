#!/usr/bin/env python3
"""Public-source acquisition using current, documented publisher distribution.

PMC OA API was retired on/after 2026-08-24. This uses its documented public
S3 article-version objects instead: https://pmc.ncbi.nlm.nih.gov/tools/pmcaws/ .
The original inventory module supplies read-only archive/OOXML parsers.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import urllib.parse as up
import zipfile
import io
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET
from ingest_atlas_public_sources_v0_5 import (get, record_bytes, inventory_file,
    archive_inventory, Links, ANT_PAGE, MD5)

S3 = 'https://pmc-oa-opendata.s3.amazonaws.com/'

def https_s3(value):
    p = up.urlsplit(value)
    if p.scheme == 's3' and p.netloc == 'pmc-oa-opendata':
        return S3 + p.path.lstrip('/'), up.parse_qs(p.query).get('md5', [None])[0]
    if p.scheme == 'https' and p.hostname == 'pmc-oa-opendata.s3.amazonaws.com':
        return value.split('?')[0], up.parse_qs(p.query).get('md5', [None])[0]
    raise ValueError('Unexpected metadata download host')

def pmc_epimedium(folder):
    query = S3 + '?' + up.urlencode({'list-type': '2', 'prefix': 'PMC10616310.', 'delimiter': '/'})
    listing, resolved = get(query)
    record_bytes(listing, resolved, 's3_versions.xml', folder)
    prefixes = [x.text for x in ET.fromstring(listing).findall('.//{*}CommonPrefixes/{*}Prefix')]
    if not prefixes: raise ValueError('No public PMC article versions found')
    prefixes.sort(key=lambda v: int(v.rstrip('/').split('.')[-1]))
    prefix = prefixes[-1]; stem = prefix.rstrip('/')
    data, resolved = get(S3 + prefix + stem + '.json')
    metadata = json.loads(data)
    record_bytes(data, resolved, 'pmc_article_metadata.json', folder)
    if metadata.get('doi', '').lower() != '10.3389/fpls.2023.1234148':
        raise ValueError('PMC DOI does not match target article')
    if metadata.get('is_retracted') is not False:
        raise ValueError('Retraction status unresolved/not permitted')
    if metadata.get('license_code') not in {'CC BY', 'CC0', 'CC BY-SA'}:
        raise ValueError('License requires further review: ' + str(metadata.get('license_code')))
    print('PMC_METADATA', json.dumps(metadata, ensure_ascii=False), flush=True)
    objects = []
    for value in metadata.get('media_urls', []):
        if not isinstance(value, str) or not up.urlsplit(value).path.lower().endswith('.xlsx'): continue
        url, expected = https_s3(value)
        payload, actual_url = get(url)
        if expected is None or hashlib.md5(payload).hexdigest() != expected:
            raise ValueError('Missing/mismatched PMC media MD5: ' + url)
        name = up.unquote(Path(up.urlsplit(url).path).name)
        prov = record_bytes(payload, actual_url, name, folder)
        objects.append({'provenance': prov, 'inventory': inventory_file(name, payload, folder)})
    # Keep the primary source XML for matching table captions and column legends.
    if metadata.get('xml_url'):
        url, expected = https_s3(metadata['xml_url']); payload, loc = get(url)
        if expected and hashlib.md5(payload).hexdigest() != expected: raise ValueError('PMC XML MD5 mismatch')
        record_bytes(payload, loc, stem + '.xml', folder)
    if not objects: raise ValueError('No XLSX in this article version')
    return {'source': 'EPIMEDIUM', 'status': 'DOWNLOADED_CHECKSUM_VERIFIED',
            'doi': metadata['doi'], 'license': metadata['license_code'],
            'available_versions': prefixes, 'chosen_version': prefix, 'objects': objects}

def antirrhineae(folder):
    raw, loc = get(ANT_PAGE); text = raw.decode('utf-8')
    record_bytes(raw, loc, 'landing.html', folder)
    parser = Links(); parser.feed(text)
    links = list(dict.fromkeys(up.urljoin(loc, u) for u, t in parser.links if 'flower_colour_data.zip' in u + t))
    attempts = []
    for i, url in enumerate(links[:4]):
        data, resolved = get(url)
        prov = record_bytes(data, resolved, 'download_' + str(i) + '.bin', folder)
        valid_zip = zipfile.is_zipfile(io.BytesIO(data))
        attempt = {'provenance': prov, 'is_zip': valid_zip, 'magic_hex': data[:16].hex()}
        if not valid_zip:
            preview = data[:2000].decode('utf-8', errors='replace')
            attempt['response_preview'] = preview
            p = Links(); p.feed(data.decode('utf-8', errors='replace'))
            attempt['response_links'] = p.links[:20]
        attempts.append(attempt)
        if prov['md5'] == MD5 and valid_zip:
            return {'source': 'ANTIRRHINEAE', 'status': 'DOWNLOADED_CHECKSUM_VERIFIED',
                    'provenance': prov, 'members': archive_inventory(data, folder / 'inventory', 'zip')}
    return {'source': 'ANTIRRHINEAE', 'status': 'BLOCKED_SOURCE_CHECKSUM',
            'expected_md5': MD5, 'attempts': attempts}

def main():
    p = argparse.ArgumentParser(); p.add_argument('--out', type=Path, required=True); a = p.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    results = {'retrieved_at_utc': datetime.now(timezone.utc).isoformat(),
               'paper1_inputs_changed': False, 'pooled_analysis': 'NOT_RUN', 'sources': []}
    for name, fn in [('antirrhineae', antirrhineae), ('epimedium', pmc_epimedium)]:
        try: r = fn(a.out / name)
        except Exception as e: r = {'source': name.upper(), 'status': 'BLOCKED_EXCEPTION', 'error': str(e)}
        results['sources'].append(r)
        (a.out / 'source_inventory.json').write_text(json.dumps(results, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print('SOURCE_RESULT', json.dumps(r, ensure_ascii=False), flush=True)
    return 0 if any(r['status'].startswith('DOWNLOADED') for r in results['sources']) else 1

if __name__ == '__main__': raise SystemExit(main())
