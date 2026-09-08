#!/usr/bin/env python3
"""Acquire the minimal Wheeler 2023 Petunieae inputs needed by the frozen prospective gate.

The pre-result gate predates all OSF inspection. Metadata-only diagnostics identified the two
processed analysis folders and their duplicate CSV/tree copies. We verify duplicate identity
from OSF-provided size/hash metadata, then download only the authoritative phyloCCA CSV/tree/R
script. No phenotype/expression values are interpreted here.
"""
from __future__ import annotations
import argparse, hashlib, json, re, urllib.request
from pathlib import Path

NODE='zg9cu';BASE=f'https://api.osf.io/v2/nodes/{NODE}/files/osfstorage/';UA='chun-petunieae-prospective-source-audit/0.6'
TARGET_ROOTS={'phyloCCA','phyloPCA'}
AUTHORITATIVE_ROOT='phyloCCA'
AUTHORITATIVE_NAMES={'tpm10k-mgg-combined-with-flavs.csv','11genestre_dated_pruned.tre','phyloCCA_expression_HPLC-with-flavs-final.r'}
DUPLICATE_NAMES={'tpm10k-mgg-combined-with-flavs.csv','11genestre_dated_pruned.tre'}

def get(url:str,accept='application/vnd.api+json,application/json,*/*'):
    req=urllib.request.Request(url,headers={'User-Agent':UA,'Accept':accept})
    with urllib.request.urlopen(req,timeout=90) as r:return r.read(),r.geturl(),dict(r.headers)

def jget(url:str):raw,resolved,h=get(url);return json.loads(raw),resolved,h

def folder_href(item):
    rel=((item.get('relationships') or {}).get('files') or {}).get('links',{}).get('related',{})
    return rel.get('href') if isinstance(rel,dict) else rel

def list_one_level(url,prefix):
    out=[]
    while url:
        obj,resolved,_=jget(url)
        for item in obj.get('data',[]):
            a=item.get('attributes') or {};name=str(a.get('name') or item.get('id'))
            if a.get('kind')!='file':raise ValueError(f'unexpected nested item in {prefix}: {name}')
            hashes=((a.get('extra') or {}).get('hashes') or {});links=item.get('links') or {}
            out.append({'id':item.get('id'),'root':prefix,'name':name,'path':f'{prefix}/{name}','size':int(a.get('size') or 0),'md5':hashes.get('md5'),'sha256_osf':hashes.get('sha256'),'download_url':links.get('download'),'api_source':resolved})
        url=(obj.get('links') or {}).get('next') or None
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out-dir',type=Path,required=True);a=ap.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
    root_obj,root_resolved,_=jget(BASE+'?page[size]=100');found={};roots=[]
    for item in root_obj.get('data',[]):
        at=item.get('attributes') or {};name=str(at.get('name') or item.get('id'));href=folder_href(item)
        roots.append({'name':name,'kind':at.get('kind'),'id':item.get('id'),'files_href':href,'size':at.get('size')})
        if at.get('kind')=='folder' and name in TARGET_ROOTS:found[name]=href
    if set(found)!=TARGET_ROOTS or any(not found[x] for x in TARGET_ROOTS):raise ValueError('missing required OSF analysis roots')
    files=[]
    for tag in sorted(TARGET_ROOTS):files.extend(list_one_level(found[tag],tag))
    (a.out_dir/'osf_root_inventory.json').write_text(json.dumps(roots,indent=2)+'\n')
    (a.out_dir/'osf_target_inventory.json').write_text(json.dumps(files,indent=2)+'\n')
    # Verify the two analysis folders expose the same processed data and dated tree before choosing one copy.
    duplicate_audit={}
    for name in sorted(DUPLICATE_NAMES):
        copies=[x for x in files if x['name']==name and x['root'] in TARGET_ROOTS]
        if len(copies)!=2:raise ValueError('missing duplicate copy: '+name)
        sigs={(x['size'],x['sha256_osf'],x['md5']) for x in copies}
        if len(sigs)!=1:raise ValueError('OSF metadata duplicate drift: '+name)
        duplicate_audit[name]={'status':'PASS_OSF_METADATA_IDENTICAL','size':copies[0]['size'],'sha256_osf':copies[0]['sha256_osf'],'md5':copies[0]['md5']}
    chosen=[x for x in files if x['root']==AUTHORITATIVE_ROOT and x['name'] in AUTHORITATIVE_NAMES]
    if {x['name'] for x in chosen}!=AUTHORITATIVE_NAMES:raise ValueError('authoritative processed inputs incomplete')
    data_dir=a.out_dir/'processed';data_dir.mkdir(exist_ok=True);downloaded=[]
    for f in sorted(chosen,key=lambda x:x['name']):
        if not f['download_url']:raise ValueError('missing download URL: '+f['path'])
        raw,resolved,_=get(f['download_url'],'application/octet-stream,*/*')
        if len(raw)!=f['size']:raise ValueError('download size mismatch: '+f['path'])
        sha=hashlib.sha256(raw).hexdigest();md5=hashlib.md5(raw).hexdigest()
        if f['sha256_osf'] and sha.lower()!=str(f['sha256_osf']).lower():raise ValueError('download sha mismatch: '+f['path'])
        if f['md5'] and md5.lower()!=str(f['md5']).lower():raise ValueError('download md5 mismatch: '+f['path'])
        safe=re.sub(r'[^A-Za-z0-9._-]+','__',f['path']);(data_dir/safe).write_bytes(raw)
        downloaded.append({**f,'local_name':safe,'download_resolved':resolved,'sha256':sha,'md5_computed':md5})
    manifest={'version':'v0.6','osf_node':NODE,'root_api_resolved':root_resolved,'target_roots':sorted(TARGET_ROOTS),'target_inventory_count':len(files),'downloaded_count':len(downloaded),'downloaded':downloaded,'duplicate_audit':duplicate_audit,'required_duplicate_identity':'PASS_PHYLOCCA_PHYLOPCA_CSV_AND_TREE_OSF_METADATA_IDENTICAL','authoritative_prefix':AUTHORITATIVE_ROOT,'analysis_status':'SOURCE_BYTES_ACQUIRED_READY_FOR_FROZEN_ANALYSIS','claim_boundary':'Acquisition and source-identity audit only; no phenotype-axis or molecular-subspace result inferred.','paper1_science_changed':False}
    (a.out_dir/'source_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'target_inventory_count':len(files),'downloaded_count':len(downloaded),'downloaded':[x['path'] for x in downloaded],'duplicate_audit':duplicate_audit},indent=2))
if __name__=='__main__':main()
