#!/usr/bin/env python3
"""Retrieve open Zhang et al. (2023) supplements; preserve source cells.

No majority colour, pigment chemistry, historical direction or ASR is inferred.
Source XLSX files are read with stdlib ZIP/XML and are never modified.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import posixpath
import re
import time
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

DOI = '10.3389/fpls.2023.1234148'
BASE = 'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10616310/'
NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
RNS = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
MAX_BYTES = 64 * 1024 * 1024


def fetch(url: str) -> bytes:
    last = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'CHUN-open-data-audit/0.1'})
            with urllib.request.urlopen(req, timeout=90) as res:
                data = res.read(MAX_BYTES + 1)
            if len(data) > MAX_BYTES:
                raise ValueError('source exceeds 64 MiB limit')
            return data
        except (OSError, ValueError) as exc:
            last = exc
            if attempt < 2:
                time.sleep(2 ** attempt)
    raise RuntimeError(f'failed to retrieve {url}: {last}')


def col_index(address: str) -> int:
    match = re.fullmatch(r'([A-Z]+)[0-9]+', address)
    if not match:
        raise ValueError(f'invalid cell address: {address}')
    value = 0
    for letter in match.group(1):
        value = value * 26 + ord(letter) - 64
    return value - 1


def sheets(data: bytes):
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        if sum(info.file_size for info in z.infolist()) > MAX_BYTES:
            raise ValueError('expanded workbook exceeds size limit')
        strings = []
        if 'xl/sharedStrings.xml' in z.namelist():
            ss = ET.fromstring(z.read('xl/sharedStrings.xml'))
            strings = [''.join(x.itertext()) for x in ss.findall('s:si', NS)]
        relroot = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
        rels = {r.attrib['Id']: r.attrib['Target'] for r in relroot}
        root = ET.fromstring(z.read('xl/workbook.xml'))
        for sheet in root.findall('s:sheets/s:sheet', NS):
            target = rels[sheet.attrib[f'{{{RNS}}}id']]
            path = target.lstrip('/') if target.startswith('/') else posixpath.normpath(posixpath.join('xl', target))
            if '..' in Path(path).parts:
                raise ValueError('unsafe workbook relationship')
            xml = ET.fromstring(z.read(path))
            rows = []
            for row in xml.findall('s:sheetData/s:row', NS):
                cells = {}
                formulas = []
                for cell in row.findall('s:c', NS):
                    i = col_index(cell.attrib['r'])
                    v = cell.find('s:v', NS)
                    kind = cell.attrib.get('t', '')
                    text = v.text if v is not None and v.text is not None else ''
                    if kind == 's':
                        text = strings[int(text)] if text else ''
                    elif kind == 'inlineStr':
                        inline = cell.find('s:is', NS)
                        text = ''.join(inline.itertext()) if inline is not None else ''
                    formula = cell.find('s:f', NS)
                    if formula is not None:
                        formulas.append({'cell': cell.attrib['r'], 'formula': formula.text, 'cached_value': text})
                    cells[i] = text
                values = [cells.get(i, '') for i in range(max(cells, default=-1) + 1)]
                rows.append({'source_row': int(row.attrib['r']), 'values': values, 'formulas': formulas})
            yield sheet.attrib['name'], rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--zip', type=Path, help='reuse already downloaded source bundle')
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    data = a.zip.read_bytes() if a.zip else fetch(BASE + 'supplementaryFiles')
    if not zipfile.is_zipfile(io.BytesIO(data)):
        raise ValueError(f'not a ZIP: {data[:150]!r}')
    (a.out / 'PMC10616310_supplementary.zip').write_bytes(data)
    xml = fetch(BASE + 'fullTextXML') if not a.zip else b''
    if xml:
        if DOI.encode() not in xml:
            raise ValueError('article DOI does not match expected source')
        (a.out / 'PMC10616310.xml').write_bytes(xml)
    manifest = {'source_doi': DOI, 'source_url': BASE + 'supplementaryFiles',
                'source_sha256': hashlib.sha256(data).hexdigest(), 'source_bytes': len(data),
                'members': [], 'sheets': [], 'event_identity': 'NOT_TESTED',
                'paper1_inputs_changed': False}
    with zipfile.ZipFile(io.BytesIO(data)) as bundle:
        for info in bundle.infolist():
            if info.is_dir():
                continue
            if info.file_size > MAX_BYTES:
                raise ValueError('oversized archive member')
            blob = bundle.read(info)
            manifest['members'].append({'name': info.filename, 'bytes': len(blob),
                                        'sha256': hashlib.sha256(blob).hexdigest()})
            if not info.filename.lower().endswith('.xlsx'):
                continue
            basename = re.sub(r'[^A-Za-z0-9_.-]+', '_', Path(info.filename).name)
            (a.out / basename).write_bytes(blob)
            for name, rows in sheets(blob):
                safe = re.sub(r'[^A-Za-z0-9_.-]+', '_', name)
                stem = f'{Path(basename).stem}__{safe}'
                (a.out / (stem + '.json')).write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n')
                with (a.out / (stem + '.csv')).open('w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    for row in rows:
                        writer.writerow([row['source_row'], *row['values']])
                nonempty = [r for r in rows if any(str(x).strip() for x in r['values'])]
                item = {'workbook': basename, 'sheet': name, 'physical_rows': len(rows),
                        'nonempty_rows': len(nonempty), 'max_columns': max((len(r['values']) for r in rows), default=0),
                        'source_cells': stem + '.json', 'preview': nonempty[:8]}
                manifest['sheets'].append(item)
    if not manifest['sheets']:
        raise ValueError('no XLSX worksheets recovered')
    (a.out / 'source_inventory.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
