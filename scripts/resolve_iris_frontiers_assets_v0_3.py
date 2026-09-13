#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, re, urllib.request, xml.etree.ElementTree as ET
from pathlib import Path

A='569811'; P='7588356'; X='{http://www.w3.org/1999/xlink}href'; UA='chun-iris-assets/0.3'
XML=f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={P}&retmode=xml'

def fetch(u):
    q=urllib.request.Request(u,headers={'User-Agent':UA})
    with urllib.request.urlopen(q,timeout=30) as r: return r.geturl(),(r.headers.get('Content-Type') or '').split(';',1)[0].lower(),r.read()

def html(ct,b):
    p=b[:256].lstrip().lower(); return ct in {'text/html','application/xhtml+xml'} or p.startswith(b'<html') or p.startswith(b'<!doctype html') or b'<html' in p

def text(e): return ' '.join(''.join(e.itertext()).split()) if e is not None else ''

def get_targets(x):
    root=ET.fromstring(x); out=[]
    for sm in root.findall('.//supplementary-material'):
        d=f"{text(sm.find('label'))} {text(sm.find('caption'))}".strip(); hs=[e.attrib[X] for e in sm.iter() if X in e.attrib]
        if re.search(r'Supplementary\s+Table\s*1|Data table',d,re.I): out.append(('traits',d,hs[0]))
        if re.search(r'Supplementary\s+Material\s*1|Accession numbers',d,re.I): out.append(('accessions',d,hs[0]))
    return out

def paths(filename):
    p=Path(filename); stem=p.stem; ext=p.suffix.lstrip('.').lower(); names=[p.name,stem+'.'+ext.upper()]
    slugs=[]
    m=re.fullmatch(r'Table[_-]?(\d+)',stem,re.I)
    if m: slugs=[f'{A}_supplementary-materials_tables_{m.group(1)}_{ext}',f'{A}_table_{m.group(1)}']
    m=re.fullmatch(r'Data[_-]?Sheet[_-]?(\d+)',stem,re.I)
    if m: slugs=[f'{A}_supplementary-materials_datasheets_{m.group(1)}_{ext}',f'{A}_data-sheet_{m.group(1)}']
    m=re.fullmatch(r'Supplementary[_-]?Material[_-]?(\d+)',stem,re.I)
    if m: slugs=[f'{A}_supplementary-materials_{m.group(1)}_{ext}',f'{A}_supplementary-material_{m.group(1)}']
    if not slugs:
        s=re.sub('[^a-z0-9]+','_',stem.lower()).strip('_'); slugs=[f'{A}_supplementary-materials_{s}_{ext}',f'{A}_{s}']
    for api in ('v3','v4'):
        for name in names:
            for slug in slugs:
                for ordinal in (1,2):
                    yield f'https://www.frontiersin.org/api/{api}/articles/{A}/file/{name}/{slug}/{ordinal}'
    for name in names:
        for slug in slugs:
            for ordinal in (1,2):
                yield f'https://public-pages-files-2025.frontiersin.org/articles/{A}/file/{name}/{slug}/{ordinal}'

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out',type=Path,required=True); a=ap.parse_args()
    _,_,x=fetch(XML); targets=get_targets(x); assert {t[0] for t in targets}=={'traits','accessions'},targets
    resolved=[]
    for kind,desc,href in targets:
        ats=[]; hit=None
        for u in paths(Path(href).name):
            try:
                f,ct,b=fetch(u); r={'url':u,'final_url':f,'content_type':ct,'bytes':len(b),'magic_hex':b[:16].hex(),'html':html(ct,b)}; ats.append(r)
                if len(b)>100 and not r['html']:
                    hit={**r,'sha256':hashlib.sha256(b).hexdigest()}; break
            except Exception as e: ats.append({'url':u,'error':repr(e)})
        resolved.append({'kind':kind,'description':desc,'xml_href':href,'resolved':hit,'attempts':ats})
    out={'version':'v0.3','status':'RESOLVER_ONLY_NO_VALUES','targets':resolved,'all_resolved':all(r['resolved'] for r in resolved),'row_level_values_emitted':False,'auc_computed':False}
    a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
    if not out['all_resolved']: raise SystemExit('not all Iris assets resolved')
    return 0
if __name__=='__main__': raise SystemExit(main())
