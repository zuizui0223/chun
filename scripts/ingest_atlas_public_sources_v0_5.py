#!/usr/bin/env python3
"""Retrieve public atlas sources and inventory actual bytes; never infer trait states.

Only public scholarly URLs are fetched. No credentials are sent. Archives are
read as data, not executed. XLSX is inspected read-only using its public OOXML
XML structure; no workbook is edited. Outputs retain source filenames/rows.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import html
import io
import json
import posixpath
import re
import tarfile
import urllib.parse
import urllib.request
import zipfile
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from xml.etree import ElementTree as ET

LIMIT = 100 * 1024 * 1024
MD5 = '950f85b80427d357bfeff09608ba02e9'
ANT_PAGE = 'https://research-explorer.ista.ac.at/record/5550'
EPI_PAGE = 'https://www.frontiersin.org/journals/plant-science/articles/10.3389/fpls.2023.1234148/full'
NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
REL = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'

class Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.links = []; self.current = None
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == 'a' and d.get('href'):
            self.current = [d['href'], d.get('title', '')]
    def handle_data(self, data):
        if self.current is not None: self.current[1] += data
    def handle_endtag(self, tag):
        if tag == 'a' and self.current is not None:
            self.links.append(tuple(self.current)); self.current = None

def get(url: str) -> tuple[bytes, str]:
    if urllib.parse.urlsplit(url).scheme not in {'https', 'ftp'}:
        raise ValueError('Only scholarly HTTPS/FTP sources supported')
    req = urllib.request.Request(url, headers={'User-Agent': 'chun-atlas-public-source-audit/0.5'})
    with urllib.request.urlopen(req, timeout=40) as response:
        data = response.read(LIMIT + 1)
        if len(data) > LIMIT: raise ValueError('Remote object exceeds 100 MiB limit')
        return data, response.geturl()

def slug(value: str) -> str:
    return re.sub(r'[^A-Za-z0-9_.-]+', '_', value).strip('_')[:160] or 'object'

def record_bytes(data: bytes, url: str, name: str, folder: Path) -> dict:
    folder.mkdir(parents=True, exist_ok=True)
    p = folder / slug(name); p.write_bytes(data)
    return {'file': str(p), 'source_url': url, 'bytes': len(data),
            'sha256': hashlib.sha256(data).hexdigest(), 'md5': hashlib.md5(data).hexdigest()}

def xlsx_grids(data: bytes) -> list[tuple[str, list[tuple[int, list[str]]]]]:
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        if sum(x.file_size for x in z.infolist()) > LIMIT: raise ValueError('OOXML exceeds limit')
        shared = []
        if 'xl/sharedStrings.xml' in z.namelist():
            shared = [''.join(n.itertext()) for n in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si', NS)]
        rels = {r.attrib['Id']: r.attrib['Target'] for r in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        sheets = []
        for sheet in ET.fromstring(z.read('xl/workbook.xml')).findall('s:sheets/s:sheet', NS):
            target = rels[sheet.attrib['{' + REL + '}id']]
            path = target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/' + target)
            if not path.startswith('xl/'): raise ValueError('Invalid sheet relationship')
            rows = []
            for row in ET.fromstring(z.read(path)).findall('s:sheetData/s:row', NS):
                values = {}
                for cell in row.findall('s:c', NS):
                    ref = cell.attrib.get('r', '')
                    match = re.match(r'([A-Z]+)', ref)
                    if not match: continue
                    index = 0
                    for c in match.group(1): index = index * 26 + ord(c) - 64
                    typ = cell.attrib.get('t', '')
                    val = cell.findtext('s:v', '', NS)
                    if typ == 's': val = shared[int(val)] if val else ''
                    elif typ == 'inlineStr': val = ''.join(cell.find('s:is', NS).itertext())
                    values[index - 1] = val
                if values and any(x.strip() for x in values.values()):
                    rows.append((int(row.attrib['r']), [values.get(i, '') for i in range(max(values) + 1)]))
            sheets.append((sheet.attrib['name'], rows))
        return sheets

def inventory_file(name: str, data: bytes, folder: Path) -> dict:
    result = {'name': name, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
    suffix = Path(name).suffix.lower()
    if suffix == '.xlsx':
        tables = []
        for sheet_name, rows in xlsx_grids(data):
            dest = folder / (slug(name + '__' + sheet_name) + '.csv')
            with dest.open('w', encoding='utf-8', newline='') as fh:
                writer = csv.writer(fh)
                for idx, values in rows: writer.writerow([idx, *values])
            tables.append({'sheet': sheet_name, 'nonempty_rows': len(rows),
                           'max_source_row': max((i for i, _ in rows), default=0),
                           'max_columns': max((len(v) for _, v in rows), default=0),
                           'csv_file': str(dest), 'preview': rows[:10]})
        result['sheets'] = tables
    elif suffix in {'.csv', '.txt', '.tsv', '.nex', '.nexus', '.tre', '.tree', '.r'}:
        try: text = data.decode('utf-8-sig')
        except UnicodeDecodeError: text = data.decode('cp1252')
        dest = folder / slug(name); dest.write_text(text, encoding='utf-8')
        result.update({'nonempty_lines': sum(bool(x.strip()) for x in text.splitlines()),
                       'preview': text.splitlines()[:12], 'text_file': str(dest)})
    return result

def archive_inventory(data: bytes, folder: Path, fmt: str) -> list[dict]:
    folder.mkdir(parents=True, exist_ok=True)
    files = []
    if fmt == 'zip':
        archive = zipfile.ZipFile(io.BytesIO(data))
        entries = [(i.filename, i.file_size, lambda i=i: archive.read(i)) for i in archive.infolist() if not i.is_dir()]
    else:
        archive = tarfile.open(fileobj=io.BytesIO(data), mode='r:gz')
        entries = [(i.name, i.size, lambda i=i: archive.extractfile(i).read()) for i in archive.getmembers() if i.isfile()]
    try:
        if sum(n for _, n, _ in entries) > 3 * LIMIT: raise ValueError('Expanded archive exceeds limit')
        for i, (name, n, reader) in enumerate(entries):
            parts = PurePosixPath(name).parts
            if name.startswith('/') or '..' in parts: raise ValueError('Unsafe archive member')
            if n > LIMIT: raise ValueError('Member exceeds size limit')
            if '/__MACOSX/' in '/' + name or Path(name).name.startswith('._'): continue
            member_dir = folder / ('member_' + str(i)); member_dir.mkdir(exist_ok=True)
            # All original data are preserved inside the downloaded source archive.
            files.append(inventory_file(name, reader(), member_dir))
    finally: archive.close()
    return files

def antirrhineae(root: Path) -> dict:
    errors = []; links = []
    for page in [ANT_PAGE, 'https://doi.org/10.15479/AT:ISTA:34']:
        try:
            data, resolved = get(page)
            record_bytes(data, resolved, 'landing.html', root)
            parser = Links(); parser.feed(data.decode('utf-8'))
            links += [urllib.parse.urljoin(resolved, u) for u, label in parser.links
                      if ('flower_colour_data' in label + u or '.zip' in label + u or ('/file/' in u and 'download' in u))]
            if links: break
            errors.append('No archive link in ' + resolved)
        except Exception as exc: errors.append(page + ': ' + str(exc))
    for url in dict.fromkeys(links):
        try:
            data, resolved = get(url)
            digest = hashlib.md5(data).hexdigest()
            if digest != MD5: raise ValueError('Published MD5 mismatch: ' + digest)
            provenance = record_bytes(data, resolved, 'IST-2016-34-v1+1_tellis_flower_colour_data.zip', root)
            files = archive_inventory(data, root / 'inventory', 'zip')
            return {'source': 'ANTIRRHINEAE', 'status': 'DOWNLOADED_CHECKSUM_VERIFIED',
                    'provenance': provenance, 'members': files, 'attempt_errors': errors}
        except Exception as exc: errors.append(url + ': ' + str(exc))
    return {'source': 'ANTIRRHINEAE', 'status': 'BLOCKED_DOWNLOAD', 'attempt_errors': errors}

def epimedium(root: Path) -> dict:
    errors = []; candidates = []; objects = []
    try:
        data, resolved = get(EPI_PAGE)
        record_bytes(data, resolved, 'landing.html', root)
        text = data.decode('utf-8'); parser = Links(); parser.feed(text)
        candidates += [urllib.parse.urljoin(resolved, u) for u, label in parser.links if '.xlsx' in (u + label).lower()]
        # Publisher JSON sometimes escapes URLs. The original page is retained.
        clean = html.unescape(text.replace('\\/', '/').replace('\\u002F', '/'))
        candidates += re.findall(r'https://[^\s<>"\x27]+\.xlsx(?:\?[^\s<>"\x27]*)?', clean, re.I)
        print('EPIMEDIUM_DISCOVERED_XLSX', json.dumps(list(dict.fromkeys(candidates))), flush=True)
    except Exception as exc: errors.append(EPI_PAGE + ': ' + str(exc))
    for i, url in enumerate(dict.fromkeys(candidates)):
        if i >= 8: break
        try:
            data, resolved = get(url)
            name = urllib.parse.unquote(Path(urllib.parse.urlsplit(resolved).path).name)
            provenance = record_bytes(data, resolved, name, root / 'publisher')
            objects.append({'provenance': provenance, 'inventory': inventory_file(name, data, root / 'publisher')})
        except Exception as exc: errors.append(url + ': ' + str(exc))
    if objects:
        return {'source': 'EPIMEDIUM', 'status': 'DOWNLOADED_XLSX_INVENTORIED', 'objects': objects, 'attempt_errors': errors}
    # Legitimate alternative: PMC's public Open Access package, not a captcha bypass.
    api = 'https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id=PMC10616310'
    try:
        data, resolved = get(api); record_bytes(data, resolved, 'pmc_oa.xml', root)
        xml = ET.fromstring(data)
        for link in xml.findall('.//link'):
            if link.attrib.get('format') != 'tgz': continue
            url = link.attrib['href']
            payload, location = get(url)
            provenance = record_bytes(payload, location, 'PMC10616310.tar.gz', root)
            files = archive_inventory(payload, root / 'inventory', 'tgz')
            return {'source': 'EPIMEDIUM', 'status': 'DOWNLOADED_OA_PACKAGE',
                    'provenance': provenance, 'members': files, 'attempt_errors': errors}
        errors.append(data.decode('utf-8')[:3000])
    except Exception as exc: errors.append(api + ': ' + str(exc))
    return {'source': 'EPIMEDIUM', 'status': 'BLOCKED_DOWNLOAD', 'attempt_errors': errors}

def self_test() -> None:
    # Tiny genuine OOXML fixture tests sparse cells, numeric and shared strings.
    b = io.BytesIO()
    with zipfile.ZipFile(b, 'w') as z:
        z.writestr('xl/workbook.xml', f'<workbook xmlns="{NS["s"]}" xmlns:r="{REL}"><sheets><sheet name="S4" sheetId="1" r:id="rId1"/></sheets></workbook>')
        z.writestr('xl/_rels/workbook.xml.rels', '<Relationships><Relationship Id="rId1" Target="worksheets/sheet1.xml"/></Relationships>')
        z.writestr('xl/sharedStrings.xml', f'<sst xmlns="{NS["s"]}"><si><t>WHITE</t></si></sst>')
        z.writestr('xl/worksheets/sheet1.xml', f'<worksheet xmlns="{NS["s"]}"><sheetData><row r="3"><c r="A3" t="s"><v>0</v></c><c r="C3"><v>2</v></c></row></sheetData></worksheet>')
    assert xlsx_grids(b.getvalue()) == [('S4', [(3, ['WHITE', '', '2'])])]
    print('SELF_TEST_PASS', flush=True)

def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument('--out', type=Path); ap.add_argument('--self-test', action='store_true'); a = ap.parse_args()
    if a.self_test: self_test(); return 0
    if a.out is None: ap.error('--out is required')
    a.out.mkdir(parents=True, exist_ok=True)
    summary = {'retrieved_at_utc': datetime.now(timezone.utc).isoformat(),
               'paper1_inputs_changed': False, 'pooled_analysis': 'NOT_RUN', 'sources': []}
    for name, fn in [('antirrhineae', antirrhineae), ('epimedium', epimedium)]:
        try: result = fn(a.out / name)
        except Exception as exc: result = {'source': name, 'status': 'BLOCKED_EXCEPTION', 'error': str(exc)}
        summary['sources'].append(result)
        print('SOURCE_RESULT', json.dumps(result, ensure_ascii=False), flush=True)
        (a.out / 'source_inventory.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return 0 if any(s['status'].startswith('DOWNLOADED') for s in summary['sources']) else 1

if __name__ == '__main__': raise SystemExit(main())
