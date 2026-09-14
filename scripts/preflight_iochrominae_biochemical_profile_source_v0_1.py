#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, re, urllib.error, urllib.parse, urllib.request
from pathlib import Path

DOI='10.5061/dryad.p5dq84v'
README='README_for_Larter et al 2019 Dvdy Iochrominae development evolution DATA.txt'
ARCHIVE='Larter et al 2019 Dvdy Iochrominae development evolution DATA.rar'
API='https://datadryad.org/api/v2'
UA='CHUN-iochrominae-biochemical-source-preflight/0.1'


def req(url,accept='*/*'):
    r=urllib.request.Request(url,headers={'User-Agent':UA,'Accept':accept})
    try:
        with urllib.request.urlopen(r,timeout=120) as x:
            return {'ok':True,'status':x.status,'final_url':x.geturl(),'headers':dict(x.headers),'body':x.read()}
    except urllib.error.HTTPError as e:
        try:b=e.read()
        except Exception:b=b''
        return {'ok':False,'status':e.code,'final_url':e.geturl(),'headers':dict(e.headers or {}),'body':b,'reason':str(e.reason)}
    except Exception as e:
        return {'ok':False,'status':None,'final_url':url,'headers':{},'body':b'','reason':repr(e)}


def jget(url):
    x=req(url,'application/json')
    if not x['ok']: raise SystemExit(f'JSON fetch failed {url}: {x["status"]} {x.get("reason")}')
    return json.loads(x['body'])


def fid(meta):
    href=((meta.get('_links') or {}).get('self') or {}).get('href','')
    m=re.search(r'/files/(\d+)$',href)
    if not m: raise ValueError(f'cannot parse file id from {href!r}')
    return int(m.group(1))


def digest_check(meta,body):
    typ=str(meta.get('digestType') or '').lower().replace('_','-')
    expected=str(meta.get('digest') or '').lower()
    sha=hashlib.sha256(body).hexdigest(); md5=hashlib.md5(body).hexdigest()
    match=None
    if typ in {'sha-256','sha256'} and expected: match=(sha==expected)
    elif typ=='md5' and expected: match=(md5==expected)
    return {'sha256':sha,'md5':md5,'digest_type':typ or None,'expected_digest':expected or None,'digest_match':match}


def attempt(meta):
    file_id=fid(meta)
    urls=[
      ('public_file_stream',f'https://datadryad.org/stash/downloads/file_stream/{file_id}'),
      ('api_file_download',f'{API}/files/{file_id}/download'),
    ]
    out=[]
    for tag,url in urls:
        x=req(url)
        d=digest_check(meta,x['body'])
        ctype=str(x.get('headers',{}).get('Content-Type',''))
        html=('html' in ctype.lower()) or x['body'].lstrip().lower().startswith(b'<!doctype html')
        out.append({
          'route':tag,'url':url,'ok':x['ok'],'http_status':x['status'],'final_url':x['final_url'],
          'content_type':ctype,'downloaded_bytes':len(x['body']),'html_payload':html,
          'reason':x.get('reason'),**d,
        })
        expected_size=int(meta.get('size') or 0)
        valid=x['ok'] and not html and (not expected_size or len(x['body'])==expected_size) and (d['digest_match'] is True or not d['expected_digest'])
        if valid:
            return out,x['body'],tag
    return out,None,None


def main():
    build=Path('build'); build.mkdir(exist_ok=True)
    ds=jget(API+'/datasets/'+urllib.parse.quote('doi:'+DOI,safe=''))
    vh=ds['_links']['stash:version']['href']
    vurl=vh if vh.startswith('http') else API+vh.removeprefix('/api/v2')
    obj=jget(vurl.rstrip('/')+'/files?per_page=100')
    fs=obj.get('_embedded',{}).get('stash:files',[])
    by={x.get('path'):x for x in fs}
    missing=[x for x in (README,ARCHIVE) if x not in by]
    if missing: raise SystemExit(f'missing expected Dryad objects: {missing}; got={sorted(by)}')

    receipts={}
    recovered={}
    for name in (README,ARCHIVE):
        meta=by[name]
        attempts,body,route=attempt(meta)
        receipts[name]={
          'file_id':fid(meta),'size':meta.get('size'),'digest_type_api':meta.get('digestType'),'digest_api':meta.get('digest'),
          'attempts':attempts,'recovered':body is not None,'recovered_via':route,
        }
        if body is not None:
            recovered[name]=body
            if name==README:(build/'iochrominae_dvdy2019_README.txt').write_bytes(body)
            else:(build/'iochrominae_dvdy2019_DATA.rar').write_bytes(body)

    if README not in recovered:
        status='HOLD_SOURCE_ACCESS_README_AND_ARCHIVE_PROFILE_UNCOMPUTED'
    elif ARCHIVE not in recovered:
        status='HOLD_SOURCE_ACCESS_ARCHIVE_PROFILE_UNCOMPUTED'
    else:
        status='SOURCE_BYTES_ACQUIRED_SCHEMA_INSPECTION_ALLOWED_PROFILE_UNCOMPUTED'

    out={
      'version':'v0.1','status':status,
      'source_doi':DOI,'dataset_version_number':ds.get('versionNumber'),'version_href':vh,
      'expected_objects':[README,ARCHIVE],
      'file_receipts':receipts,
      'allowed_if_archive_recovered':'LIST_ARCHIVE_MEMBER_NAMES_AND_READ_README_ONLY_BEFORE_PROFILE_STATE_MAPPING_FREEZE',
      'archive_data_rows_opened_by_preflight':False,
      'profile_states_computed':False,
      'patristic_distances_computed':False,
      'profile_auc_computed':False,
      'winner_computed':False,
      'paper1_science_changed':False,
    }
    (build/'iochrominae_biochemical_profile_source_preflight_v0_1.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({
      'status':status,
      'objects':{k:{'file_id':v['file_id'],'size':v['size'],'digest_type_api':v['digest_type_api'],'digest_api':v['digest_api'],'recovered':v['recovered']} for k,v in receipts.items()},
      'profile_auc_computed':False,
    },indent=2,ensure_ascii=False))

if __name__=='__main__':main()
