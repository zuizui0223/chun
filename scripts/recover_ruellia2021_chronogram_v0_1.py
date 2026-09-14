#!/usr/bin/env python3
from __future__ import annotations
import hashlib, http.cookiejar, json, re, urllib.error, urllib.parse, urllib.request
from pathlib import Path

DOI='10.5061/dryad.qnk98sfff'
API='https://datadryad.org/api/v2'
TARGET='Ruellia_chronogram.tre'
LANDING='https://datadryad.org/dataset/'+urllib.parse.quote('doi:'+DOI,safe='/')
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/140 Safari/537.36'


def opener():
    jar=http.cookiejar.CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))


def request(op, url, accept='*/*', referer=None):
    headers={'User-Agent':UA,'Accept':accept,'Accept-Language':'en-US,en;q=0.9'}
    if referer: headers['Referer']=referer
    req=urllib.request.Request(url,headers=headers)
    try:
        with op.open(req,timeout=120) as r:
            body=r.read()
            return {'ok':True,'status':r.status,'final_url':r.geturl(),'headers':dict(r.headers),'body':body}
    except urllib.error.HTTPError as e:
        try: body=e.read()
        except Exception: body=b''
        return {'ok':False,'status':e.code,'final_url':e.geturl(),'headers':dict(e.headers or {}),'body':body,'reason':str(e.reason)}
    except Exception as e:
        return {'ok':False,'status':None,'final_url':url,'headers':{},'body':b'','reason':repr(e)}


def jget(op,url):
    r=request(op,url,'application/json')
    if not r['ok']: raise SystemExit(f'JSON request failed {url}: {r}')
    return json.loads(r['body'])


def file_id(meta):
    href=meta.get('_links',{}).get('self',{}).get('href','')
    m=re.search(r'/files/(\d+)$',href)
    if not m: raise SystemExit(f'no file id in {href!r}')
    return int(m.group(1))


def summarize_attempt(name,r,expected_size,dtype,expected_digest):
    body=r.pop('body')
    ctype=str(r.get('headers',{}).get('Content-Type',''))
    sha=hashlib.sha256(body).hexdigest(); md5=hashlib.md5(body).hexdigest()
    treeish=(len(body)>1000 and b'(' in body and b';' in body and 'html' not in ctype.lower())
    if dtype in {'sha-256','sha256'}: match=(sha.lower()==expected_digest.lower())
    elif dtype=='md5': match=(md5.lower()==expected_digest.lower())
    else: match=None
    prefix=None
    if body and ('html' in ctype.lower() or body[:20].lstrip().startswith(b'<')):
        prefix=re.sub(r'\s+',' ',body[:500].decode('utf-8','replace')).strip()
    out={
      'route':name,'ok':r.get('ok'),'http_status':r.get('status'),'final_url':r.get('final_url'),
      'content_type':ctype,'content_length_header':r.get('headers',{}).get('Content-Length'),
      'location_header':r.get('headers',{}).get('Location'),'reason':r.get('reason'),
      'downloaded_bytes':len(body),'expected_size':expected_size,
      'sha256_downloaded':sha,'md5_downloaded':md5,'digest_match':match,
      'treeish_payload':treeish,'text_prefix_if_html':prefix,
    }
    return out, body, treeish, match


def main():
    op=opener()
    ds=jget(op,API+'/datasets/'+urllib.parse.quote('doi:'+DOI,safe=''))
    vh=ds['_links']['stash:version']['href']
    vurl=vh if vh.startswith('http') else API+vh.removeprefix('/api/v2')
    fl=jget(op,vurl.rstrip('/')+'/files?per_page=100')
    files=fl.get('_embedded',{}).get('stash:files',[])
    by={f.get('path'):f for f in files}
    if TARGET not in by: raise SystemExit(f'{TARGET} absent; files={sorted(by)}')
    m=by[TARGET]; fid=file_id(m)
    dtype=str(m.get('digestType') or '').lower(); expected=str(m.get('digest') or '')
    expected_size=m.get('size')

    # Establish ordinary public landing-page session. Its content is not parsed for any trait outcome.
    landing=request(op,LANDING,'text/html')
    routes=[
      ('public_file_stream',f'https://datadryad.org/stash/downloads/file_stream/{fid}',LANDING),
      ('api_file_download',f'{API}/files/{fid}/download',None),
    ]
    attempts=[]; recovered=None
    for name,url,ref in routes:
        r=request(op,url,'*/*',referer=ref)
        s,body,treeish,match=summarize_attempt(name,r,expected_size,dtype,expected)
        attempts.append(s)
        if treeish and (match is True or not expected):
            recovered=body; break

    out={
      'version':'v0.1',
      'status':'TREE_BYTES_RECOVERED' if recovered is not None else 'HOLD_SOURCE_ACCESS_TREE_OUTCOMES_UNOPENED',
      'source_doi':DOI,'target':TARGET,
      'dataset_identifier':ds.get('identifier'),'dataset_version_number':ds.get('versionNumber'),
      'version_href':vh,'file_id':fid,'api_size':expected_size,
      'digest_type_api':m.get('digestType'),'digest_api':m.get('digest'),
      'file_metadata_links':m.get('_links',{}),
      'landing_http_status':landing.get('status'),'landing_final_url':landing.get('final_url'),
      'attempts':attempts,
      'hplc_outcomes_opened':False,'auc_computed':False,'winner_computed':False
    }
    Path('build').mkdir(exist_ok=True)
    Path('build/ruellia2021_chronogram_recovery_v0_1.json').write_text(json.dumps(out,indent=2)+'\n')
    if recovered is not None:
        Path('build/Ruellia_chronogram.tre').write_bytes(recovered)
    print(json.dumps(out,indent=2))

if __name__=='__main__': main()
