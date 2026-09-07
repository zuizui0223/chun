#!/usr/bin/env python3
"""Recover the original Cornidia source files, not published ASR summaries.

The acquisition step emits only a source inventory; it does not count origins.
All extracted members are bounded and confined to the requested directory.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

DOI = '10.3389/fpls.2021.661522'
PMCID = 'PMC8276264'
BASE = 'https://www.ebi.ac.uk/europepmc/webservices/rest'
LIMIT = 80_000_000


def get(url: str) -> tuple[bytes, str]:
    req = urllib.request.Request(url, headers={'User-Agent': 'CHUN-source-reanalysis/0.2'})
    with urllib.request.urlopen(req, timeout=90) as res:
        raw, resolved = res.read(LIMIT + 1), res.url
    if len(raw) > LIMIT:
        raise ValueError('source download exceeds bounded size')
    return raw, resolved


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def unpack(raw: bytes, out: Path, inventory: list, origin: str, depth: int = 0) -> None:
    if depth > 3:
        raise ValueError('nested archive depth exceeds limit')
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        if sum(x.file_size for x in z.infolist()) > LIMIT:
            raise ValueError('unpacked archive exceeds size limit')
        for ent in z.infolist():
            if ent.is_dir():
                continue
            path = out / ent.filename
            if not path.resolve().is_relative_to(out.resolve()):
                raise ValueError('unsafe archive member')
            content = z.read(ent)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
            item = {'origin': origin, 'member': ent.filename, 'path': str(path),
                    'bytes': len(content), 'sha256': sha(content)}
            inventory.append(item)
            ext = path.suffix.lower()
            if ext == '.zip':
                unpack(content, path.with_suffix(''), inventory, ent.filename, depth + 1)
            elif ext in ('.nex', '.nexus', '.nwk', '.tre', '.tree', '.treefile', '.txt', '.fasta', '.fas', '.phy'):
                text = content.decode('utf-8-sig', errors='replace')
                item['preview'] = text[:1600]
                item['tree_statements'] = re.findall(r'(?im)^\s*tree\s+[^;]+;', text)
                item['nexus_dimensions'] = re.findall(r'(?i)dimensions[^;]*;', text)
            elif ext == '.pdf':
                import fitz
                doc = fitz.open(stream=content, filetype='pdf')
                text = '\n'.join(page.get_text() for page in doc)
                path.with_suffix('.txt').write_text(text, encoding='utf-8')
                item['pdf_pages'] = len(doc)
                item['text_preview'] = text[:5000]
                item['drawing_counts'] = [len(page.get_drawings()) for page in doc]
            elif ext == '.docx':
                with zipfile.ZipFile(io.BytesIO(content)) as dz:
                    root = ET.fromstring(dz.read('word/document.xml'))
                text = '\n'.join(' '.join(p.itertext()) for p in root.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'))
                path.with_suffix('.txt').write_text(text, encoding='utf-8')
                item['text_preview'] = text[:5000]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--out-dir', type=Path, required=True)
    a = ap.parse_args()
    a.out_dir.mkdir(parents=True, exist_ok=True)
    xml_url = f'{BASE}/{PMCID}/fullTextXML'
    xml, resolved = get(xml_url)
    root = ET.fromstring(xml)
    if DOI not in [n.text for n in root.findall('.//article-id') if n.get('pub-id-type') == 'doi']:
        raise ValueError('wrong source DOI')
    licenses = [' '.join(n.itertext()) for n in root.findall('.//license')]
    if not licenses:
        raise ValueError('source license missing')
    (a.out_dir / 'article.xml').write_bytes(xml)
    manifest = {'doi': DOI, 'pmcid': PMCID, 'licenses': licenses,
                'xml_url': xml_url, 'xml_resolved': resolved, 'xml_sha256': sha(xml),
                'inventory': [], 'atlas_asr_status': 'NOT_RUN',
                'paper1_science_changed': False}
    zip_url = f'{BASE}/{PMCID}/supplementaryFiles'
    raw, resolved = get(zip_url)
    (a.out_dir / 'supplementary.zip').write_bytes(raw)
    manifest.update(supplement_url=zip_url, supplement_resolved=resolved,
                    supplement_bytes=len(raw), supplement_sha256=sha(raw))
    unpack(raw, a.out_dir / 'files', manifest['inventory'], zip_url)
    if not manifest['inventory']:
        raise ValueError('empty source archive')
    # Preserve the published figure source for visual terminal coding; no OCR.
    pdf_url = 'https://www.frontiersin.org/journals/plant-science/articles/10.3389/fpls.2021.661522/pdf'
    try:
        raw, resolved = get(pdf_url)
        import fitz
        doc = fitz.open(stream=raw, filetype='pdf')
        (a.out_dir / 'article.pdf').write_bytes(raw)
        pages = []
        for i, page in enumerate(doc):
            text = page.get_text()
            (a.out_dir / f'article_page_{i+1}.txt').write_text(text, encoding='utf-8')
            if re.search(r'FIGURE\s+5\s*\|', text):
                page.get_pixmap(matrix=fitz.Matrix(2, 2)).save(str(a.out_dir / f'figure5_page_{i+1}.png'))
                (a.out_dir / f'figure5_page_{i+1}_vectors.json').write_text(json.dumps(page.get_drawings(), default=str), encoding='utf-8')
                pages.append({'page': i + 1, 'drawings': len(page.get_drawings()), 'images': len(page.get_images()), 'text': text})
        manifest['article_pdf'] = {'url': pdf_url, 'resolved': resolved, 'sha256': sha(raw), 'pages': len(doc), 'figure5': pages}
    except Exception as e:
        manifest['article_pdf_error'] = type(e).__name__ + ': ' + str(e)
    (a.out_dir / 'source_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
