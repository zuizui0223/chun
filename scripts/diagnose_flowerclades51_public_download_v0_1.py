#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import html
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


def clean_text(s: str) -> str:
    s=re.sub(r'<script\b[^>]*>.*?</script>', ' ', s, flags=re.I|re.S)
    s=re.sub(r'<style\b[^>]*>.*?</style>', ' ', s, flags=re.I|re.S)
    s=re.sub(r'<[^>]+>', ' ', s)
    s=html.unescape(s)
    return re.sub(r'\s+',' ',s).strip()


def structural_html_diagnostic(b: bytes) -> dict:
    try:
        s=b.decode('utf-8','replace')
    except Exception:
        return {'html_decodable':False}
    tm=re.search(r'<title[^>]*>(.*?)</title>',s,flags=re.I|re.S)
    title=clean_text(tm.group(1)) if tm else None
    hrefs=[]
    for m in re.finditer(r'\bhref\s*=\s*["\']([^"\']+)["\']',s,flags=re.I):
        u=html.unescape(m.group(1))
        if any(k in u.lower() for k in ('download','file_stream','sign','login','help','api','dataset')):
            hrefs.append(u)
    actions=[]
    for m in re.finditer(r'<form\b[^>]*\baction\s*=\s*["\']([^"\']*)["\'][^>]*>',s,flags=re.I|re.S):
        actions.append(html.unescape(m.group(1)))
    metas=[]
    for m in re.finditer(r'<meta\b[^>]*>',s,flags=re.I):
        tag=m.group(0)
        if re.search(r'(refresh|robots|description)',tag,flags=re.I):
            metas.append(re.sub(r'\s+',' ',tag)[:400])
    text=clean_text(s)
    markers={
        'contains_cloudflare': bool(re.search(r'cloudflare|cf-ray|challenge-platform',s,flags=re.I)),
        'contains_captcha': bool(re.search(r'captcha|turnstile',s,flags=re.I)),
        'contains_rate_limit': bool(re.search(r'rate.?limit|too many requests',text,flags=re.I)),
        'contains_email_capture': bool(re.search(r'email|download',text,flags=re.I) and re.search(r'email',text,flags=re.I)),
        'contains_login': bool(re.search(r'log.?in|sign.?in',text,flags=re.I)),
        'contains_unavailable': bool(re.search(r'unavailable|not available|not found|may not download',text,flags=re.I)),
    }
    return {
        'html_decodable':True,
        'title':title,
        'selected_hrefs':sorted(set(hrefs))[:50],
        'form_actions':sorted(set(actions))[:20],
        'selected_meta_tags':metas[:20],
        'text_prefix':text[:500],
        **markers,
    }


def main():
    ds=api_json(API+DSPATH)
    vh=ds['_links']['stash:version']['href']
    base=vh if vh.startswith('http') else API+vh.removeprefix('/api/v2')
    files=api_json(base.rstrip('/')+'/files?per_page=100')['_embedded']['stash:files']
    wanted={x['path']:x for x in files if x['path'] in {'final_dataset.csv','trees.zip'}}
    assert set(wanted)=={'final_dataset.csv','trees.zip'}, wanted.keys()

    # Emit the complete public API metadata object for the two files. These are file-level
    # metadata only; no file bytes/outcomes are present in this object.
    api_file_metadata={name:wanted[name] for name in sorted(wanted)}

    jar=http.cookiejar.CookieJar()
    op=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    with op.open(urllib.request.Request(LANDING,headers={'User-Agent':UA,'Accept':'text/html'}),timeout=60) as r:
        landing_bytes=r.read()
    landing_diag=structural_html_diagnostic(landing_bytes)

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
                'link_header':r.headers.get('Link'),
                'location_header':r.headers.get('Location'),
                'downloaded_bytes':len(b),
                'downloaded_sha256':hashlib.sha256(b).hexdigest(),
                'digest_match':hashlib.sha256(b).hexdigest().lower()==str(m.get('digest','')).lower(),
                'html_structure': structural_html_diagnostic(b) if 'text/html' in (r.headers.get('Content-Type') or '').lower() else None,
            }
            out.append(row)
    payload={
        'source_doi':DOI,
        'api_file_metadata':api_file_metadata,
        'landing_page_structure':landing_diag,
        'responses':out,
        'outcome_values_emitted':False,
    }
    p=Path('build/flowerclades51_public_download_diagnostic_v0_1.json')
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(payload,indent=2)+'\n')
    print(json.dumps(payload,indent=2))

if __name__=='__main__':
    main()
