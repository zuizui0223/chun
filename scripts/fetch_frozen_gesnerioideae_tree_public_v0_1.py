#!/usr/bin/env python3
import hashlib, json, re, sys
from pathlib import Path
from urllib.parse import urljoin
import requests

LANDING='https://datadryad.org/dataset/doi:10.5061/dryad.m7589'
FILENAME='Gesne_Ago8_simple_combined_CA.tre'
FILE_ID='72407'
EXPECTED_SIZE=668933
EXPECTED_MD5='94d6f267f5c123d6d875170da1783ffa'
OUT=Path('build/gesnerioideae_dryad_public_fetch_v0_1')
OUT.mkdir(parents=True, exist_ok=True)

s=requests.Session()
s.headers.update({'User-Agent':'Mozilla/5.0 CHUN prospective source verifier/0.1'})

candidates=[]
def add(u, basis):
    if u and u not in [x['url'] for x in candidates]:
        candidates.append({'url':u,'basis':basis})

add(f'https://datadryad.org/stash/downloads/file_stream/{FILE_ID}', 'known_stash_file_stream')
add(f'https://datadryad.org/api/v2/files/{FILE_ID}/download', 'dryad_api_download')

landing_status=None; landing_len=None; text=''
try:
    r=s.get(LANDING, timeout=30)
    landing_status=r.status_code; landing_len=len(r.content); text=r.text
    (OUT/'landing.html').write_text(text, encoding='utf-8', errors='replace')
    for m in re.finditer(r'href=[\"\']([^\"\']+)[\"\'][^>]*>(.*?)</a>', text, re.I|re.S):
        href=m.group(1); anchor=re.sub('<[^>]+>',' ',m.group(2))
        if FILENAME in href or FILENAME in anchor or FILE_ID in href:
            add(urljoin(r.url, href), 'landing_anchor')
    for pat in [rf'https?://[^\"\'<> ]+(?:{FILE_ID}|file_stream)[^\"\'<> ]*', rf'/[^\"\'<> ]*(?:{FILE_ID}|file_stream)[^\"\'<> ]*']:
        for m in re.finditer(pat, text, re.I):
            add(urljoin(r.url, m.group(0).replace('&amp;','&')), 'landing_regex')
except Exception as e:
    landing_status='ERROR:'+repr(e)

attempts=[]; matched=None; html_diagnostics=[]
for i,c in enumerate(candidates):
    rec=dict(c)
    try:
        rr=s.get(c['url'], timeout=60, allow_redirects=True, headers={'Referer':LANDING,'Accept':'application/octet-stream,text/plain;q=0.9,*/*;q=0.8'})
        b=rr.content; md5=hashlib.md5(b).hexdigest(); ct=rr.headers.get('content-type')
        rec.update(status=rr.status_code, final_url=rr.url, size=len(b), content_type=ct, md5=md5)
        if rr.status_code==200 and len(b)==EXPECTED_SIZE and md5==EXPECTED_MD5:
            (OUT/FILENAME).write_bytes(b); rec['exact_match']=True; matched=rec; attempts.append(rec); break
        rec['exact_match']=False
        if 'html' in (ct or '').lower() and len(b) < 20000:
            p=OUT/f'wrapper_{i}.html'; p.write_bytes(b)
            t=b.decode('utf-8','replace')
            links=sorted(set(urljoin(rr.url,x.replace('&amp;','&')) for x in re.findall(r'(?:href|src|action)=[\"\']([^\"\']+)',t,re.I)))
            forms=re.findall(r'<form[^>]*action=[\"\']([^\"\']+)',t,re.I)
            title=(re.search(r'<title[^>]*>(.*?)</title>',t,re.I|re.S).group(1).strip() if re.search(r'<title[^>]*>(.*?)</title>',t,re.I|re.S) else None)
            html_diagnostics.append({'candidate':c['url'],'saved':str(p),'title':title,'links':links[:50],'forms':forms[:20]})
            for u in links:
                if any(k in u.lower() for k in ['download','file_stream','storage','amazonaws','s3']) or FILE_ID in u:
                    add(u,'wrapper_link')
    except Exception as e:
        rec.update(error=repr(e), exact_match=False)
    attempts.append(rec)

receipt={
 'status':'PASS_EXACT_FROZEN_TREE_BYTES' if matched else 'HOLD_PUBLIC_FETCH_NO_EXACT_MATCH',
 'filename':FILENAME,'file_id':FILE_ID,'expected_size':EXPECTED_SIZE,'expected_md5':EXPECTED_MD5,
 'landing_status':landing_status,'landing_len':landing_len,'attempts':attempts,'html_diagnostics':html_diagnostics,
 'outcome_values_read':False,'auc_computed':False,'decision_computed':False
}
(OUT/'public_fetch_receipt.json').write_text(json.dumps(receipt,indent=2), encoding='utf-8')
print(json.dumps(receipt,indent=2))
if not matched: sys.exit(2)
