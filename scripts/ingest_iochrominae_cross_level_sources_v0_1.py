#!/usr/bin/env python3
"""Acquire three public Dryad datasets needed for an Iochrominae cross-level bridge.

Source acquisition only: no colour recoding, mechanistic alignment or evolutionary
claim is made here. Public Dryad DOI endpoints are resolved through API v2 and
all downloaded bytes/member hashes are preserved.
"""
from __future__ import annotations
import argparse,hashlib,json,urllib.parse,urllib.request,zipfile,io
from pathlib import Path

DATASETS={
 'TEMPO_MODE':('10.5061/dryad.0732g','Tempo and mode of flower color evolution'),
 'SPECTRAL_COLOUR':('10.5061/dryad.36v4b','Competition for hummingbird pollination shapes flower color variation'),
 'DEVELOPMENT_EXPRESSION':('10.5061/dryad.p5dq84v','Developmental control of convergent floral pigmentation across evolutionary timescales'),
}
UA='chun-iochrominae-cross-level-source-audit/0.1'

def get(url:str,accept='application/json,*/*')->tuple[bytes,str,dict]:
    req=urllib.request.Request(url,headers={'User-Agent':UA,'Accept':accept})
    with urllib.request.urlopen(req,timeout=120) as r:
        return r.read(),r.geturl(),dict(r.headers)

def json_get(url:str):
    raw,resolved,headers=get(url)
    return json.loads(raw),resolved,headers

def hrefs(obj):
    out=[]
    if isinstance(obj,dict):
        for k,v in obj.items():
            if k=='href' and isinstance(v,str): out.append(v)
            else: out.extend(hrefs(v))
    elif isinstance(obj,list):
        for v in obj: out.extend(hrefs(v))
    return out

def choose_href(obj,needle):
    hs=[h for h in hrefs(obj) if needle.lower() in h.lower()]
    return hs[0] if hs else None

def normalize(url:str):
    if url.startswith('/'): return 'https://datadryad.org'+url
    return url

def latest_version(meta,api):
    # Prefer advertised HAL links. Fall back to the public versions collection.
    h=choose_href(meta,'versions')
    candidates=[]
    for url in ([normalize(h)] if h else [])+[api+'/versions']:
        try:
            obj,resolved,_=json_get(url)
        except Exception:
            continue
        vals=[]
        if isinstance(obj,list): vals=obj
        elif isinstance(obj,dict):
            for key in ('_embedded','versions','stash:versions'):
                v=obj.get(key)
                if isinstance(v,list): vals.extend(v)
                elif isinstance(v,dict):
                    for vv in v.values():
                        if isinstance(vv,list): vals.extend(vv)
        if vals:
            def rank(x):
                for k in ('versionNumber','version','id'):
                    v=x.get(k)
                    if isinstance(v,(int,float)): return float(v)
                    if isinstance(v,str) and v.replace('.','',1).isdigit(): return float(v)
                return 0.0
            return max(vals,key=rank),resolved
        if isinstance(obj,dict) and any(k in obj for k in ('versionNumber','version')):
            return obj,resolved
    # Some Dryad dataset metadata directly exposes the latest version links.
    return meta,meta.get('_links',{}).get('self',{}).get('href',api) if isinstance(meta.get('_links'),dict) else api

def file_records(version):
    h=choose_href(version,'files')
    if not h: return None,None
    obj,resolved,_=json_get(normalize(h))
    vals=[]
    if isinstance(obj,list): vals=obj
    elif isinstance(obj,dict):
        for key in ('_embedded','files','stash:files'):
            v=obj.get(key)
            if isinstance(v,list): vals.extend(v)
            elif isinstance(v,dict):
                for vv in v.values():
                    if isinstance(vv,list): vals.extend(vv)
    return vals,resolved

def download_public_files(meta,api,ddir):
    version,vresolved=latest_version(meta,api)
    files,fresolved=file_records(version)
    if files is None:
        # Last-resort conventional latest-version endpoint.
        vid=version.get('id') or version.get('versionNumber')
        if vid is None: raise ValueError('Dryad metadata has no discoverable public files link/version id')
        files,fresolved,_=json_get(f'https://datadryad.org/api/v2/versions/{vid}/files')
        if isinstance(files,dict):
            vals=[]
            for v in files.values():
                if isinstance(v,list): vals.extend(v)
            files=vals
    if not files: raise ValueError('Dryad public file collection is empty')
    extracted=ddir/'extracted';extracted.mkdir(parents=True,exist_ok=True)
    members=[]
    for i,f in enumerate(files):
        name=str(f.get('path') or f.get('filename') or f.get('name') or f'file_{i:03d}')
        dl=choose_href(f,'download') or choose_href(f,'files')
        if not dl:
            # File metadata commonly has a direct download link whose href does not contain the word download.
            hs=hrefs(f); dl=hs[-1] if hs else None
        if not dl: raise ValueError(f'no public download href for Dryad file {name!r}')
        raw,resolved,_=get(normalize(dl),'application/octet-stream,*/*')
        target=(extracted/name).resolve()
        if not target.is_relative_to(extracted.resolve()): raise ValueError('unsafe Dryad file path '+name)
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
        members.append({'name':name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'suffix':target.suffix.lower(),'download_resolved':resolved})
    return members,vresolved,fresolved

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out-dir',type=Path,required=True);a=ap.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
    results=[]
    for key,(doi,title) in DATASETS.items():
        encoded=urllib.parse.quote('doi:'+doi,safe='')
        api=f'https://datadryad.org/api/v2/datasets/{encoded}'
        meta,meta_resolved,_=json_get(api)
        identifier=str(meta.get('identifier','')).lower()
        if doi.lower() not in identifier: raise ValueError(f'{key}: DOI identity mismatch {identifier!r}')
        ddir=a.out_dir/key.lower();ddir.mkdir(parents=True,exist_ok=True)
        (ddir/'dataset_metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
        members,vresolved,fresolved=download_public_files(meta,api,ddir)
        suffix_counts={}
        total_bytes=0
        bundle_hash=hashlib.sha256()
        for m in sorted(members,key=lambda x:x['name']):
            suffix_counts[m['suffix']]=suffix_counts.get(m['suffix'],0)+1
            raw=(ddir/'extracted'/m['name']).read_bytes();total_bytes+=len(raw)
            bundle_hash.update(m['name'].encode()+b'\0'+raw)
        result={
          'dataset_id':key,'doi':doi,'title_expected':title,'identifier':meta.get('identifier'),
          'api_requested':api,'metadata_resolved':meta_resolved,'version_resolved':vresolved,'files_resolved':fresolved,
          'license':meta.get('license'),'versionNumber':meta.get('versionNumber'),
          'storageSize':meta.get('storageSize'),'bundle_bytes':total_bytes,
          'bundle_sha256':bundle_hash.hexdigest(),'member_count':len(members),
          'suffix_counts':suffix_counts,'members':members}
        (ddir/'source_manifest.json').write_text(json.dumps(result,indent=2)+'\n')
        results.append(result)
    summary={
      'version':'v0.1','datasets':results,
      'all_three_acquired':len(results)==3,
      'analysis_status':'SOURCE_BYTES_ACQUIRED_NOT_YET_TRAIT_MECHANISM_JOINED',
      'claim_boundary':'Acquisition/inventory only. No taxon overlap, phenotype hierarchy, molecular recurrence or causal alignment is inferred.',
      'paper1_science_changed':False}
    (a.out_dir/'source_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps([{k:r[k] for k in ('dataset_id','doi','bundle_bytes','bundle_sha256','member_count','suffix_counts')} for r in results],indent=2))
if __name__=='__main__':main()
