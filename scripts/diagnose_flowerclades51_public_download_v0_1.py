#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import http.cookiejar
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

DOI="10.5061/dryad.r4xgxd2sc"
API="https://datadryad.org/api/v2"
DSPATH="/datasets/"+urllib.parse.quote("doi:"+DOI,safe="")
LANDING="https://datadryad.org/dataset/"+urllib.parse.quote("doi:"+DOI,safe="/")
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"


def api_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":"CHUN-source-diagnostic/0.1","Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=60) as r:
        return json.loads(r.read().decode())


def fid(meta):
    h=meta['_links']['self']['href']
    m=re.search(r'/files/(\d+)$',h)
    assert m,h
    return m.group(1)


def main():
    ds=api_json(API+DSPATH)
    vh=ds['_links']['stash:version']['href']
    base=vh if vh.startswith('http') else API+vh.removeprefix('/api/v2')
    files=api_json(base.rstrip('/')+'/files?per_page=100')['_embedded']['stash:files']
    wanted={x['path']:x for x in files if x['path'] in {'final_dataset.csv','trees.zip'}}
    assert set(wanted)=={'final_dataset.csv','trees.zip'}, wanted.keys()

    jar=http.cookiejar.CookieJar()
    op=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    with op.open(urllib.request.Request(LANDING,headers={'User-Agent':UA,'Accept':'text/html'}),timeout=60) as r:
        r.read()

    out=[]
    for name in ('final_dataset.csv','trees.zip'):
        m=wanted[name]
        u=f"https://datadryad.org/stash/downloads/file_stream/{fid(m)}"
        req=urllib.request.Request(u,headers={'User-Agent':UA,'Referer':LANDING,'Accept':'*/*'})
        with op.open(req,timeout=180) as r:
            b=r.read()
            final=urllib.parse.urlsplit(r.geturl())
            row={
                'path':name,
                'file_id':fid(m),
                'api_size':m.get('size'),
                'api_digest_type':m.get('digestType'),
                'api_digest':m.get('digest'),
                'http_status':getattr(r,'status',None),
                'final_scheme':final.scheme,
                'final_host':final.netloc,
                'final_path':final.path,
                'content_type':r.headers.get('Content-Type'),
                'content_length_header':r.headers.get('Content-Length'),
                'content_disposition':r.headers.get('Content-Disposition'),
                'downloaded_bytes':len(b),
                'downloaded_sha256':hashlib.sha256(b).hexdigest(),
                'digest_match':hashlib.sha256(b).hexdigest().lower()==str(m.get('digest','')).lower(),
            }
            out.append(row)
    p=Path('build/flowerclades51_public_download_diagnostic_v0_1.json')
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps({'source_doi':DOI,'responses':out},indent=2)+'\n')
    print(json.dumps({'source_doi':DOI,'responses':out},indent=2))

if __name__=='__main__':
    main()
