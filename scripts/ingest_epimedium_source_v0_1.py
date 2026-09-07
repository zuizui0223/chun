#!/usr/bin/env python3
"""Retrieve the open Epimedium supplement and inventory real worksheet cells.

Uses the documented Europe PMC fullTextXML and supplementaryFiles endpoints.
This stage does NOT decode colour codes or infer historical transitions.
The minimal XLSX reader preserves source row/column positions and merge metadata.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import posixpath
import re
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

DOI = '10.3389/fpls.2023.1234148'
PMCID = 'PMC10616310'
API = 'https://www.ebi.ac.uk/europepmc/webservices/rest'
NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
MAX_BYTES = 80_000_000


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def retrieve(url: str) -> tuple[bytes, str]:
    req = urllib.request.Request(url, headers={'User-Agent': 'CHUN-open-data-audit/0.1'})
    with urllib.request.urlopen(req, timeout=90) as response:
        payload = response.read(MAX_BYTES + 1)
        resolved = response.url
    if len(payload) > MAX_BYTES:
        raise ValueError('source exceeds download size limit')
    return payload, resolved


def col_index(address: str) -> int:
    match = re.fullmatch(r'([A-Z]+)[1-9][0-9]*', address)
    if not match:
        raise ValueError(f'invalid XLSX cell address: {address}')
    n = 0
    for char in match[1]:
        n = n * 26 + ord(char) - 64
    return n - 1


def inspect_xlsx(payload: bytes) -> list[dict]:
    with zipfile.ZipFile(io.BytesIO(payload)) as z:
        if sum(x.file_size for x in z.infolist()) > MAX_BYTES:
            raise ValueError('uncompressed XLSX exceeds limit')
        strings = []
        if 'xl/sharedStrings.xml' in z.namelist():
            root = ET.fromstring(z.read('xl/sharedStrings.xml'))
            strings = [''.join(el.itertext()) for el in root.findall('s:si', NS)]
        rels = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
        targets = {el.attrib['Id']: el.attrib['Target'] for el in rels}
        book = ET.fromstring(z.read('xl/workbook.xml'))
        sheets = []
        for sheet in book.findall('s:sheets/s:sheet', NS):
            target = targets[sheet.attrib['{' + NS['r'] + '}id']]
            target = target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/' + target)
            root = ET.fromstring(z.read(target))
            records, max_col = [], 0
            for row in root.findall('s:sheetData/s:row', NS):
                cells, formula_cells = {}, []
                for c in row.findall('s:c', NS):
                    addr, kind = c.attrib['r'], c.attrib.get('t', 'n')
                    idx = col_index(addr)
                    max_col = max(max_col, idx + 1)
                    if c.find('s:f', NS) is not None:
                        formula_cells.append(addr)
                    v = c.find('s:v', NS)
                    val = '' if v is None else (v.text or '')
                    if kind == 's':
                        val = strings[int(val)] if val else ''
                    elif kind == 'inlineStr':
                        node = c.find('s:is', NS)
                        val = '' if node is None else ''.join(node.itertext())
                    cells[idx] = val
                if any(v != '' for v in cells.values()):
                    records.append({'source_row': int(row.attrib['r']), 'cells': cells,
                                    'formula_cells': formula_cells})
            merges = [x.attrib['ref'] for x in root.findall('s:mergeCells/s:mergeCell', NS)]
            sheets.append({'name': sheet.attrib['name'], 'path': target, 'columns': max_col,
                           'merge_ranges': merges, 'records': records})
        return sheets


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--out-dir', type=Path, required=True)
    ap.add_argument('--local-zip', type=Path)
    ap.add_argument('--local-xml', type=Path)
    a = ap.parse_args()
    a.out_dir.mkdir(parents=True, exist_ok=True)
    xml_url, zip_url = f'{API}/{PMCID}/fullTextXML', f'{API}/{PMCID}/supplementaryFiles'
    xml, xml_resolved = (a.local_xml.read_bytes(), str(a.local_xml)) if a.local_xml else retrieve(xml_url)
    article = ET.fromstring(xml)
    dois = [n.text for n in article.findall('.//article-id') if n.attrib.get('pub-id-type') == 'doi']
    if DOI not in dois:
        raise ValueError(f'article DOI mismatch: {dois}')
    licenses = [' '.join(n.itertext()).strip() for n in article.findall('.//license')]
    if not licenses:
        raise ValueError('source license not found')
    payload, zip_resolved = (a.local_zip.read_bytes(), str(a.local_zip)) if a.local_zip else retrieve(zip_url)
    manifest = {'source_doi': DOI, 'pmcid': PMCID, 'license_statements': licenses,
                'xml_url': xml_url, 'xml_resolved_url': xml_resolved, 'xml_sha256': digest(xml),
                'supplement_url': zip_url, 'supplement_resolved_url': zip_resolved,
                'supplement_sha256': digest(payload), 'supplement_bytes': len(payload),
                'archive_members': [], 'workbooks': [],
                'biological_interpretation_gate': 'NOT_DECODED_NO_ASR', 'paper1_science_changed': False}
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        if sum(x.file_size for x in archive.infolist()) > MAX_BYTES:
            raise ValueError('uncompressed source archive exceeds limit')
        for entry in archive.infolist():
            if entry.is_dir():
                continue
            manifest['archive_members'].append({'name': entry.filename, 'bytes': entry.file_size})
            if not entry.filename.lower().endswith('.xlsx'):
                continue
            raw = archive.read(entry)
            basename = Path(entry.filename).name
            (a.out_dir / basename).write_bytes(raw)
            sheets = inspect_xlsx(raw)
            wb = {'source_filename': entry.filename, 'sha256': digest(raw), 'bytes': len(raw), 'sheets': []}
            for index, sheet in enumerate(sheets, 1):
                filename = f'{Path(basename).stem}_sheet{index}.csv'
                with (a.out_dir / filename).open('w', newline='', encoding='utf-8') as fh:
                    writer = csv.writer(fh)
                    writer.writerow(['source_row'] + [f'col_{i+1}' for i in range(sheet['columns'])])
                    for record in sheet['records']:
                        writer.writerow([record['source_row']] + [record['cells'].get(i, '') for i in range(sheet['columns'])])
                wb['sheets'].append({'name': sheet['name'], 'source_xml': sheet['path'],
                    'csv': filename, 'nonempty_rows': len(sheet['records']), 'columns': sheet['columns'],
                    'merge_ranges': sheet['merge_ranges'],
                    'formula_cells': [c for r in sheet['records'] for c in r['formula_cells']],
                    'preview': [{'source_row': r['source_row'], 'cells': r['cells']} for r in sheet['records'][:8]]})
            manifest['workbooks'].append(wb)
    if not manifest['workbooks']:
        raise ValueError('no XLSX in real supplementary archive')
    (a.out_dir / 'source_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
