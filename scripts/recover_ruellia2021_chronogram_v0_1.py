#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, re, urllib.parse, urllib.request
from pathlib import Path

DOI='10.5061/dryad.qnk98sfff'
API='https://datadryad.org/api/v2'
TARGET='Ruellia_chronogram.tre'
LANDING='https://datadryad.org/dataset/'+urllib.parse.quote('doi:'+DOI,safe='/')
UA='Mozilla/5.0 CHUN-ruellia-chronogram/0.1'

def get(url, accept='*/*'):
    req=urllib.request.Request(url,headers={'User-Agent':UA,'Accept':accept})
    with urllib.request.urlopen(req,timeout=120) as r:
        return r.read(), dict(r.headers), r.geturl(), r.status

def jget(url): return json.loads(get(url,'application/json')[0])

def file_id(meta):
    href=meta.get('_links',{}).get('self',{}).get('href','')
    m=re.search(r'/files/(\d+)$',href)
    if not m: raise SystemExit(f'no file id in {href!r}')
    return int(m.group(1))


def main():
    ds=jget(API+'/datasets/'+urllib.parse.quote('doi:'+DOI,safe=''))
    vh=ds['_links']['stash:version']['href']
    vurl=vh if vh.startswith('http') else API+vh.removeprefix('/api/v2')
    fl=jget(vurl.rstrip('/')+'/files?per_page=100')
    files=fl.get('_embedded',{}).get('stash:files',[])
    by={f.get('path'):f for f in files}
    if TARGET not in by: raise SystemExit(f'{TARGET} absent; files={sorted(by)}')
    m=by[TARGET]; fid=file_id(m)
    url=f'https://datadryad.org/stash/downloads/file_stream/{fid}'
    body,hdr,final,status=get(url)
    ctype=hdr.get('Content-Type','')
    text_prefix=body[:300].decode('utf-8','replace') if 'html' in ctype.lower() or body[:20].lstrip().startswith(b'<') else None
    expected=str(m.get('digest') or '')
    dtype=str(m.get('digestType') or '').lower()
    sha=hashlib.sha256(body).hexdigest(); md5=hashlib.md5(body).hexdigest()
    if dtype in {'sha-256','sha256'}: match=(sha.lower()==expected.lower())
    elif dtype=='md5': match=(md5.lower()==expected.lower())
    else: match=None
    is_tree=(b'(' in body and b';' in body and 'html' not in ctype.lower() and len(body)>1000)
    out={
      'status':'TREE_BYTES_RECOVERED' if is_tree else 'HOLD_PUBLIC_ROUTE_NOT_TREE_BYTES',
      'source_doi':DOI,'target':TARGET,'file_id':fid,'api_size':m.get('size'),
      'digest_type_api':m.get('digestType'),'digest_api':m.get('digest'),
      'http_status':status,'final_url':final,'content_type':ctype,'downloaded_bytes':len(body),
      'sha256_downloaded':sha,'md5_downloaded':md5,'digest_match':match,
      'html_text_prefix':text_prefix,
      'hplc_outcomes_opened':False,'auc_computed':False
    }
    Path('build').mkdir(exist_ok=True)
    Path('build/ruellia2021_chronogram_recovery_v0_1.json').write_text(json.dumps(out,indent=2)+'\n')
    if is_tree:
        Path('build/Ruellia_chronogram.tre').write_bytes(body)
    print(json.dumps(out,indent=2))

if __name__=='__main__': main()
