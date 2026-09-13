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

# Known public/API routes. Only exact-hash bytes are accepted.
add(f'https://datadryad.org/stash/downloads/file_stream/{FILE_ID}', 'known_stash_file_stream')
add(f'https://datadryad.org/api/v2/files/{FILE_ID}/download', 'dryad_api_download')

landing_status=None
landing_len=None
try:
    r=s.get(LANDING, timeout=30)
    landing_status=r.status_code; landing_len=len(r.content)
    text=r.text
    # Scrape hrefs around the exact frozen filename.
    for m in re.finditer(r'href=[\"\']([^\"\']+)[\"\'][^>]*>(.*?)</a>', text, re.I|re.S):
        href=m.group(1); anchor=re.sub('<[^>]+>',' ',m.group(2))
        if FILENAME in href or FILENAME in anchor or FILE_ID in href:
            add(urljoin(r.url, href), 'landing_anchor')
    # Also collect explicit file-stream/download URLs mentioning frozen file id.
    for pat in [rf'https?://[^\"\'<> ]+(?:{FILE_ID}|file_stream)[^\"\'<> ]*', rf'/[^\"\'<> ]*(?:{FILE_ID}|file_stream)[^\"\'<> ]*']:
        for m in re.finditer(pat, text, re.I):
            add(urljoin(r.url, m.group(0).replace('&amp;','&')), 'landing_regex')
except Exception as e:
    landing_status='ERROR:'+repr(e)

attempts=[]
matched=None
for c in candidates:
    rec=dict(c)
    try:
        rr=s.get(c['url'], timeout=60, allow_redirects=True)
        b=rr.content
        rec.update(status=rr.status_code, final_url=rr.url, size=len(b), content_type=rr.headers.get('content-type'), md5=hashlib.md5(b).hexdigest())
        if rr.status_code==200 and len(b)==EXPECTED_SIZE and rec['md5']==EXPECTED_MD5:
            p=OUT/FILENAME; p.write_bytes(b)
            rec['exact_match']=True
            matched=rec
            attempts.append(rec)
            break
        rec['exact_match']=False
    except Exception as e:
        rec.update(error=repr(e), exact_match=False)
    attempts.append(rec)

receipt={
 'status':'PASS_EXACT_FROZEN_TREE_BYTES' if matched else 'HOLD_PUBLIC_FETCH_NO_EXACT_MATCH',
 'filename':FILENAME,'file_id':FILE_ID,'expected_size':EXPECTED_SIZE,'expected_md5':EXPECTED_MD5,
 'landing_status':landing_status,'landing_len':landing_len,
 'attempts':attempts,
 'outcome_values_read':False,'auc_computed':False,'decision_computed':False
}
(OUT/'public_fetch_receipt.json').write_text(json.dumps(receipt,indent=2), encoding='utf-8')
print(json.dumps(receipt,indent=2))
if not matched:
    sys.exit(2)
