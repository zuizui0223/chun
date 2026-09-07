#!/usr/bin/env python3
"""Acquire the original Linoideae source archive; no inferred ancestral states."""
from __future__ import annotations
import argparse, hashlib, io, json, urllib.request, xml.etree.ElementTree as ET, zipfile
from pathlib import Path
DOI='10.3390/plants11121579'
PMCID='PMC9231132'
BASE='https://www.ebi.ac.uk/europepmc/webservices/rest'
LIMIT=80000000
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
def get(url):
    req=urllib.request.Request(url,headers={'User-Agent':'CHUN-Linoideae-source-audit/0.2'})
    with urllib.request.urlopen(req,timeout=60) as r:
        data=r.read(LIMIT+1); resolved=r.url
    if len(data)>LIMIT: raise ValueError('download exceeds limit')
    return data,resolved

def sha(data): return hashlib.sha256(data).hexdigest()

def unpack(data,out,inventory,depth=0):
    if depth>3: raise ValueError('archive nesting exceeds limit')
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        if sum(i.file_size for i in z.infolist())>LIMIT: raise ValueError('expanded archive exceeds limit')
        for i in z.infolist():
            if i.is_dir(): continue
            p=out/i.filename
            if not p.resolve().is_relative_to(out.resolve()): raise ValueError('unsafe archive member')
            raw=z.read(i); p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(raw)
            row={'path':str(p),'bytes':len(raw),'sha256':sha(raw)}; inventory.append(row)
            if p.suffix.lower()=='.zip': unpack(raw,p.with_suffix(''),inventory,depth+1)
            elif p.suffix.lower()=='.docx':
                with zipfile.ZipFile(io.BytesIO(raw)) as d: root=ET.fromstring(d.read('word/document.xml'))
                paragraphs=[''.join(q.itertext()) for q in root.findall('.//'+W+'p')]
                p.with_suffix('.txt').write_text('\n'.join(paragraphs),encoding='utf-8')
                tables=[]
                for t in root.findall('.//'+W+'tbl'):
                    tables.append([[' '.join(''.join(q.itertext()) for q in c.findall('.//'+W+'p')) for c in r.findall(W+'tc')] for r in t.findall(W+'tr')])
                p.with_suffix('.tables.json').write_text(json.dumps(tables,ensure_ascii=False,indent=2),encoding='utf-8')
                row['table_shapes']=[[len(t),max(map(len,t),default=0)] for t in tables]
            elif p.suffix.lower()=='.pdf':
                import fitz
                d=fitz.open(stream=raw,filetype='pdf')
                p.with_suffix('.txt').write_text('\n'.join(q.get_text() for q in d),encoding='utf-8')
                row['pages']=len(d)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out-dir',type=Path,required=True); a=ap.parse_args()
    a.out_dir.mkdir(parents=True,exist_ok=True)
    raw,resolved=get(f'{BASE}/{PMCID}/fullTextXML'); root=ET.fromstring(raw)
    if DOI not in [x.text for x in root.findall('.//article-id') if x.get('pub-id-type')=='doi']: raise ValueError('wrong DOI')
    licenses=[' '.join(x.itertext()) for x in root.findall('.//license')]
    if not licenses: raise ValueError('missing license')
    (a.out_dir/'article.xml').write_bytes(raw)
    manifest={'doi':DOI,'pmcid':PMCID,'licenses':licenses,'xml_sha256':sha(raw),'xml_resolved':resolved,'inventory':[],'atlas_asr_status':'NOT_RUN'}
    raw,resolved=get(f'{BASE}/{PMCID}/supplementaryFiles')
    (a.out_dir/'supplementary.zip').write_bytes(raw)
    manifest.update(supplement_sha256=sha(raw),supplement_resolved=resolved)
    unpack(raw,a.out_dir/'files',manifest['inventory'])
    if not manifest['inventory']: raise ValueError('empty source archive')
    pdf_urls=['https://mdpi-res.com/d_attachment/plants/plants-11-01579/article_deploy/plants-11-01579.pdf','https://www.mdpi.com/2223-7747/11/12/1579/pdf']
    manifest['pdf_attempts']=[]
    for url in pdf_urls:
        try:
            raw,resolved=get(url)
            import fitz
            d=fitz.open(stream=raw,filetype='pdf'); (a.out_dir/'article.pdf').write_bytes(raw)
            manifest['article_pdf']={'url':url,'resolved':resolved,'sha256':sha(raw),'pages':len(d)}
            for i,p in enumerate(d):
                text=p.get_text(); (a.out_dir/f'article_page_{i+1}.txt').write_text(text,encoding='utf-8')
                if 'Figure 2.' in text:
                    p.get_pixmap(matrix=fitz.Matrix(3,3)).save(str(a.out_dir/f'figure2_page_{i+1}.png'))
            break
        except Exception as e: manifest['pdf_attempts'].append({'url':url,'error':type(e).__name__+': '+str(e)})
    (a.out_dir/'source_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(manifest,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
