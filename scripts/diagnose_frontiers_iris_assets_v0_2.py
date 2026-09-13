#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json, re, urllib.request, xml.etree.ElementTree as ET
from pathlib import Path

ARTICLE_ID='569811'
PMC_NUMERIC='7588356'
XML_URL=f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={PMC_NUMERIC}&retmode=xml'
XLINK='{http://www.w3.org/1999/xlink}href'
UA='chun-iris-frontiers-v3-diagnostic/0.2'
HOSTS=['https://www.frontiersin.org/api/v3/articles','https://www.frontiersin.org/api/v4/articles','https://public-pages-files-2025.frontiersin.org/articles']

def fetch(url):
    req=urllib.request.Request(url,headers={'User-Agent':UA})
    with urllib.request.urlopen(req,timeout=30) as r:
        return r.geturl(),(r.headers.get('Content-Type') or '').split(';',1)[0].lower(),r.read()

def html(ct,b):
    p=b[:256].lstrip().lower()
    return ct in {'text/html','application/xhtml+xml'} or p.startswith(b'<html') or p.startswith(b'<!doctype html') or b'<html' in p

def text(e): return ' '.join(''.join(e.itertext()).split()) if e is not None else ''

def targets(xml):
    root=ET.fromstring(xml); out=[]
    for sm in root.findall('.//supplementary-material'):
        d=f"{text(sm.find('label'))} {text(sm.find('caption'))}".strip()
        if not (re.search(r'Supplementary\s+Table\s*1|Data table',d,re.I) or re.search(r'Supplementary\s+Material\s*1|Accession numbers',d,re.I)): continue
        hs=[e.attrib[XLINK] for e in sm.iter() if XLINK in e.attrib]
        out.append({'description':d,'hrefs':hs})
    return out

def slugs(filename):
    name=Path(filename).name; stem=Path(name).stem; ext=Path(name).suffix.lstrip('.').lower()
    s=re.sub('[^a-z0-9]+','_',stem.lower()).strip('_')
    vs=[f'{ARTICLE_ID}_{s}',f'{ARTICLE_ID}_supplementary-materials_{s}_{ext}']
    m=re.fullmatch(r'table[_-]?(\d+)',stem,re.I)
    if m:
        n=m.group(1); vs += [f'{ARTICLE_ID}_table_{n}',f'{ARTICLE_ID}_supplementary-materials_tables_{n}_{ext}']
    m=re.fullmatch(r'data[_-]?sheet[_-]?(\d+)',stem,re.I)
    if m:
        n=m.group(1); vs += [f'{ARTICLE_ID}_data-sheet_{n}',f'{ARTICLE_ID}_supplementary-materials_datasheets_{n}_{ext}']
    m=re.fullmatch(r'supplementary[_-]?material[_-]?(\d+)',stem,re.I)
    if m:
        n=m.group(1); vs += [f'{ARTICLE_ID}_supplementary-material_{n}',f'{ARTICLE_ID}_supplementary-materials_{n}_{ext}']
    return list(dict.fromkeys(vs))

def variants(filename):
    names=list(dict.fromkeys([Path(filename).name,Path(filename).name.upper(),Path(filename).stem+'.'+Path(filename).suffix.lstrip('.').upper()]))
    for host in HOSTS:
        for name in names:
            for slug in slugs(filename):
                for ordinal in (1,2,3):
                    yield f'{host}/{ARTICLE_ID}/file/{name}/{slug}/{ordinal}'

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out',type=Path,required=True); a=ap.parse_args()
    _,_,xml=fetch(XML_URL); ts=targets(xml)
    diagnostics=[]
    for t in ts:
        if not t['hrefs']: raise SystemExit(f'no href: {t}')
        filename=Path(t['hrefs'][0]).name; succ=[]; attempts=[]
        for url in variants(filename):
            try:
                final,ct,b=fetch(url); rec={'url':url,'final_url':final,'content_type':ct,'bytes':len(b),'magic_hex':b[:16].hex(),'html':html(ct,b)}
                attempts.append(rec)
                if len(b)>100 and not rec['html']:
                    succ.append({**rec,'sha256':hashlib.sha256(b).hexdigest()})
                    break
            except Exception as e: attempts.append({'url':url,'error':repr(e)})
        diagnostics.append({'description':t['description'],'xml_href':t['hrefs'][0],'filename':filename,'successes':succ,'attempts':attempts})
    out={'version':'v0.2','status':'LEGACY_FRONTIERS_ROUTE_DIAGNOSTIC_NO_VALUES','targets':ts,'diagnostics':diagnostics,'row_level_values_emitted':False,'auc_computed':False}
    a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
    return 0
if __name__=='__main__': raise SystemExit(main())
