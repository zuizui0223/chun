#!/usr/bin/env python3
"""Access-only probe for the Polemoniaceae candidate; no source content is parsed."""
from __future__ import annotations
import json, re
from pathlib import Path
from urllib.parse import urljoin
import requests

DOI='10.5061/dryad.2710pk5'
ENC='doi%3A10.5061%2Fdryad.2710pk5'
BASE='https://datadryad.org'
API=f'{BASE}/api/v2'
UA='chun-polemoniaceae-access-probe/1.0'
OUT=Path('analysis/_generated/polemoniaceae_access_v1')


def getj(url):
    r=requests.get(url,headers={'User-Agent':UA,'Accept':'application/json','X-API-Version':'2.1.0'},timeout=120)
    r.raise_for_status(); return r.json()


def emb_list(x):
    vals=[v for v in (x.get('_embedded') or {}).values() if isinstance(v,list)]
    if len(vals)!=1: raise SystemExit(f'ambiguous HAL list keys={list((x.get("_embedded") or {}))}')
    return vals[0]


def rid(rec,kind):
    if rec.get('id') is not None: return int(rec['id'])
    href=(((rec.get('_links') or {}).get('self') or {}).get('href',''))
    m=re.search(rf'/{kind}/(\d+)',href)
    if not m: raise SystemExit(f'no {kind} id in {href}')
    return int(m.group(1))


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    dsurl=f'{API}/datasets/{ENC}'
    ds=getj(dsurl)
    vs=emb_list(getj(dsurl+'/versions'))
    latest=max(vs,key=lambda v:(int(v.get('versionNumber') or -1),rid(v,'versions')))
    vid=rid(latest,'versions')
    files=emb_list(getj(f'{API}/versions/{vid}/files'))
    wanted={Path(str(f.get('path',''))).name:f for f in files if Path(str(f.get('path',''))).name in {'Data_files.zip','Tree_files.zip','Alignment_files.zip'}}
    if set(wanted)!={'Data_files.zip','Tree_files.zip','Alignment_files.zip'}:
        raise SystemExit(f'missing expected files: {list(wanted)} all={[f.get("path") for f in files]}')
    probes=[]
    for name in ('Data_files.zip','Tree_files.zip'):
        f=wanted[name]; fid=rid(f,'files')
        href=((((f.get('_links') or {}).get('stash:download') or {}).get('href')) or f'/api/v2/files/{fid}/download')
        urls=[urljoin(BASE,href),f'{BASE}/api/v2/files/{fid}/download',f'{BASE}/downloads/file_stream/{fid}']
        attempts=[]; success=False
        for u in dict.fromkeys(urls):
            r=requests.get(u,headers={'User-Agent':UA,'Accept':'*/*','X-API-Version':'2.1.0','Range':'bytes=0-1023'},timeout=120,allow_redirects=True)
            attempts.append({'url':u,'final':r.url,'status':r.status_code,'content_type':r.headers.get('content-type',''),'bytes':len(r.content),'prefix_hex':r.content[:4].hex()})
            if r.status_code in (200,206) and len(r.content)>0 and r.content[:2]==b'PK':
                success=True; break
        probes.append({'name':name,'file_id':fid,'metadata_size':f.get('size'),'attempts':attempts,'zip_prefix_accessible':success})
    result={'doi':DOI,'version_id':vid,'files_metadata':[{'name':n,'id':rid(f,'files'),'size':f.get('size'),'digest':f.get('digest'),'digestType':f.get('digestType')} for n,f in wanted.items()],'probes':probes,'source_content_parsed':False,'signal_computed':False,'candidate_access_gate':all(p['zip_prefix_accessible'] for p in probes)}
    (OUT/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print('POLEMONIACEAE_ACCESS_PROBE='+json.dumps(result))

if __name__=='__main__': main()
