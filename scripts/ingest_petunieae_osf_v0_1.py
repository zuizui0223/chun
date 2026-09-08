#!/usr/bin/env python3
"""Acquire only analysis-grade Wheeler 2023 Petunieae OSF files needed by the frozen gate.

The pre-result gate predates all OSF inspection. Root-only and one-level metadata diagnostics
identified the exact processed-analysis folders below; no phenotype/expression values were
inspected before this scope was fixed. Large raw/transcriptome hierarchies are never traversed.
"""
from __future__ import annotations
import argparse, hashlib, json, re, urllib.request
from pathlib import Path

NODE='zg9cu'
BASE=f'https://api.osf.io/v2/nodes/{NODE}/files/osfstorage/'
UA='chun-petunieae-prospective-source-audit/0.4'
MAX_BYTES=5_000_000
TARGET_ROOTS={'phyloCCA','phyloPCA','stochastic_mapping'}
KEEP_SUFFIXES={'.csv','.tsv','.txt','.json','.xlsx','.xls','.rds','.rdata','.rda','.nwk','.newick','.tre','.tree','.nex','.nexus','.r','.py','.ipynb'}

def get(url:str, accept='application/vnd.api+json,application/json,*/*'):
    req=urllib.request.Request(url,headers={'User-Agent':UA,'Accept':accept})
    with urllib.request.urlopen(req,timeout=120) as r:return r.read(),r.geturl(),dict(r.headers)

def jget(url:str):
    raw,resolved,headers=get(url);return json.loads(raw),resolved,headers

def folder_href(item):
    rel=((item.get('relationships') or {}).get('files') or {}).get('links',{}).get('related',{})
    return rel.get('href') if isinstance(rel,dict) else rel

def list_one_level(url:str,prefix:str):
    out=[]
    while url:
        obj,resolved,_=jget(url)
        for item in obj.get('data',[]):
            a=item.get('attributes',{}) or {};name=str(a.get('name') or item.get('id'));path=f'{prefix}/{name}'
            if a.get('kind')!='file':
                raise ValueError('unexpected nested folder in frozen analysis root: '+path)
            links=item.get('links',{}) or {};hashes=((a.get('extra') or {}).get('hashes') or {})
            out.append({'id':item.get('id'),'path':path,'name':name,'size':int(a.get('size') or 0),'date_modified':a.get('date_modified'),'provider':'osfstorage','download_url':links.get('download'),'md5':hashes.get('md5'),'sha256_osf':hashes.get('sha256'),'api_source':resolved})
        nxt=(obj.get('links') or {}).get('next');url=nxt if isinstance(nxt,str) and nxt else None
    return out

def root_targets():
    obj,resolved,_=jget(BASE+'?page[size]=100');rows=[];found={}
    for item in obj.get('data',[]):
        a=item.get('attributes',{}) or {};name=str(a.get('name') or item.get('id'));href=folder_href(item)
        rows.append({'name':name,'kind':a.get('kind'),'id':item.get('id'),'files_href':href,'size':a.get('size')})
        if a.get('kind')=='folder' and name in TARGET_ROOTS:found[name]=href
    missing=TARGET_ROOTS-set(found)
    if missing:raise ValueError('target OSF root folders missing: '+','.join(sorted(missing)))
    if any(not found[x] for x in TARGET_ROOTS):raise ValueError('target root missing files href')
    return rows,found,resolved

def suffix(path:str):return Path(path.lower()).suffix

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out-dir',type=Path,required=True);a=ap.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
    roots,found,root_resolved=root_targets();(a.out_dir/'osf_root_inventory.json').write_text(json.dumps(roots,indent=2)+'\n')
    files=[]
    for tag in sorted(TARGET_ROOTS):files.extend(list_one_level(found[tag],tag))
    if not files:raise ValueError('targeted OSF inventory is empty')
    (a.out_dir/'osf_target_inventory.json').write_text(json.dumps(files,indent=2)+'\n')
    selected=[];data_dir=a.out_dir/'processed';data_dir.mkdir(exist_ok=True)
    for f in files:
        s=suffix(f['path']);keep=s in KEEP_SUFFIXES and 0 < f['size'] <= MAX_BYTES
        f['selected_for_download']=bool(keep)
        if not keep:continue
        if not f['download_url']:raise ValueError('selected OSF file lacks download URL: '+f['path'])
        raw,resolved,_=get(f['download_url'],'application/octet-stream,*/*')
        if len(raw)!=f['size']:raise ValueError(f"size mismatch {f['path']}: {len(raw)} != {f['size']}")
        sha=hashlib.sha256(raw).hexdigest();md5=hashlib.md5(raw).hexdigest()
        if f['sha256_osf'] and sha.lower()!=str(f['sha256_osf']).lower():raise ValueError('OSF sha256 mismatch: '+f['path'])
        if f['md5'] and md5.lower()!=str(f['md5']).lower():raise ValueError('OSF md5 mismatch: '+f['path'])
        safe=re.sub(r'[^A-Za-z0-9._-]+','__',f['path']);(data_dir/safe).write_bytes(raw)
        selected.append({**f,'local_name':safe,'download_resolved':resolved,'sha256':sha,'md5_computed':md5})
    required_names={'tpm10k-mgg-combined-with-flavs.csv','11genestre_dated_pruned.tre'}
    for tag in ('phyloCCA','phyloPCA'):
        names={x['name'] for x in selected if x['path'].startswith(tag+'/')}
        if not required_names <= names:raise ValueError(f'{tag} missing required processed source files: {sorted(required_names-names)}')
    # Two independent OSF analysis folders must expose byte-identical data/tree before one copy is authoritative.
    for name in sorted(required_names):
        copies=[x for x in selected if x['name']==name and x['path'].split('/')[0] in {'phyloCCA','phyloPCA'}]
        if len(copies)!=2 or len({x['sha256'] for x in copies})!=1:raise ValueError('phyloCCA/phyloPCA duplicate drift: '+name)
    manifest={'version':'v0.4','osf_node':NODE,'root_api_resolved':root_resolved,'target_roots':sorted(TARGET_ROOTS),'target_inventory_count':len(files),'downloaded_count':len(selected),'downloaded':selected,'required_duplicate_identity':'PASS_PHYLOCCA_PHYLOPCA_CSV_AND_TREE_BYTE_IDENTICAL','authoritative_prefix':'phyloCCA','max_download_bytes':MAX_BYTES,'analysis_status':'SOURCE_BYTES_ACQUIRED_READY_FOR_FROZEN_ANALYSIS','claim_boundary':'No phenotype-axis or molecular-subspace result is inferred by acquisition.','paper1_science_changed':False}
    (a.out_dir/'source_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'target_inventory_count':len(files),'downloaded_count':len(selected),'paths':[x['path'] for x in selected]},indent=2))
if __name__=='__main__':main()
