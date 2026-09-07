#!/usr/bin/env python3
"""Acquire the open Angraecinae source bundle and inventory raw trait inputs.

This stage does not infer ancestral states or copy published transition counts.
"""
from __future__ import annotations
import argparse, csv, hashlib, io, json, urllib.request, xml.etree.ElementTree as ET, zipfile
from pathlib import Path

DOI = '10.1371/journal.pone.0163194'
PMCID = 'PMC5036805'
BASE = 'https://www.ebi.ac.uk/europepmc/webservices/rest'
TREEBASE = 'http://purl.org/phylo/treebase/phylows/study/TB2:S19429'
LIMIT = 100_000_000


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def get(url: str) -> tuple[bytes, str]:
    req = urllib.request.Request(url, headers={'User-Agent': 'CHUN-Angraecinae-source-audit/0.1'})
    with urllib.request.urlopen(req, timeout=90) as r:
        data = r.read(LIMIT + 1)
        resolved = r.url
    if len(data) > LIMIT:
        raise ValueError('download exceeds size limit')
    return data, resolved


def safe_decode(raw: bytes) -> tuple[str, str]:
    for enc in ('utf-8-sig', 'utf-8', 'latin-1'):
        try:
            return raw.decode(enc), enc
        except UnicodeDecodeError:
            pass
    raise ValueError('unable to decode text member')


def csv_summary(raw: bytes) -> dict:
    text, enc = safe_decode(raw)
    rows = list(csv.reader(io.StringIO(text)))
    width = max((len(r) for r in rows), default=0)
    return {
        'encoding': enc,
        'rows': len(rows),
        'max_columns': width,
        'preview': rows[:6],
        'contains_flower_colour_token': 'flower color' in text.lower() or 'flower colour' in text.lower(),
        'contains_green_token': 'green' in text.lower(),
        'contains_white_token': 'white' in text.lower(),
    }


def unpack(payload: bytes, out: Path, inventory: list[dict], depth: int = 0) -> None:
    if depth > 3:
        raise ValueError('archive nesting exceeds limit')
    with zipfile.ZipFile(io.BytesIO(payload)) as z:
        if sum(i.file_size for i in z.infolist()) > LIMIT:
            raise ValueError('expanded archive exceeds size limit')
        for item in z.infolist():
            if item.is_dir():
                continue
            target = out / item.filename
            if not target.resolve().is_relative_to(out.resolve()):
                raise ValueError('unsafe archive member')
            raw = z.read(item)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
            row = {'path': str(target.relative_to(out.parent)), 'bytes': len(raw), 'sha256': sha(raw)}
            suffix = target.suffix.lower()
            if suffix in ('.csv', '.tsv', '.txt'):
                try:
                    row['text_table'] = csv_summary(raw)
                except Exception as e:
                    row['text_table_error'] = type(e).__name__ + ': ' + str(e)
            inventory.append(row)
            if suffix == '.zip':
                unpack(raw, target.with_suffix(''), inventory, depth + 1)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--out-dir', type=Path, required=True)
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    xml_url = f'{BASE}/{PMCID}/fullTextXML'
    xml, xml_resolved = get(xml_url)
    root = ET.fromstring(xml)
    dois = [x.text for x in root.findall('.//article-id') if x.attrib.get('pub-id-type') == 'doi']
    if DOI not in dois:
        raise ValueError(f'DOI mismatch: {dois}')
    licenses = [' '.join(x.itertext()).strip() for x in root.findall('.//license')]
    if not licenses:
        raise ValueError('source license missing')
    (args.out_dir / 'article.xml').write_bytes(xml)

    zip_url = f'{BASE}/{PMCID}/supplementaryFiles'
    payload, zip_resolved = get(zip_url)
    (args.out_dir / 'supplementary.zip').write_bytes(payload)
    inventory: list[dict] = []
    unpack(payload, args.out_dir / 'files', inventory)
    csv_members = [x for x in inventory if Path(x['path']).suffix.lower() == '.csv']
    if len(csv_members) < 3:
        raise ValueError(f'expected multiple CSV supplementary tables, found {len(csv_members)}')

    manifest = {
        'version': 'v0.1',
        'source_doi': DOI,
        'pmcid': PMCID,
        'license_statements': licenses,
        'article_xml_url': xml_url,
        'article_xml_resolved_url': xml_resolved,
        'article_xml_sha256': sha(xml),
        'supplement_url': zip_url,
        'supplement_resolved_url': zip_resolved,
        'supplement_sha256': sha(payload),
        'supplement_bytes': len(payload),
        'treebase_study': TREEBASE,
        'inventory': inventory,
        'csv_member_count': len(csv_members),
        'expected_primary_trait': 'FLOWER_COLOR',
        'expected_binary_states_from_article': {'0': 'GREEN', '1': 'WHITE'},
        'atlas_asr_status': 'NOT_RUN_SOURCE_ACQUISITION_ONLY',
        'paper1_science_changed': False,
    }
    (args.out_dir / 'source_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({
        'source_doi': DOI,
        'supplement_sha256': manifest['supplement_sha256'],
        'csv_member_count': len(csv_members),
        'members': [x['path'] for x in inventory],
        'atlas_asr_status': manifest['atlas_asr_status'],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
