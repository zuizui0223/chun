#!/usr/bin/env python3
"""Inventory the Wheeler 2023 Petunieae OSF repo and acquire analysis-grade processed files.

The pre-result gate lives in docs/PETUNIEAE_PROSPECTIVE_CROSS_LEVEL_GATE_V0_1.md
and must predate use of this script. This script does not interpret results.
"""
from __future__ import annotations
import argparse, hashlib, json, re, urllib.request
from pathlib import Path

NODE='zg9cu'
BASE=f'https://api.osf.io/v2/nodes/{NODE}/files/osfstorage/'
UA='chun-petunieae-prospective-source-audit/0.1'
MAX_BYTES=50_000_000
KEEP_SUFFIXES={'.csv','.tsv','.txt','.json','.xlsx','.xls','.rds','.rdata','.rda','.nwk','.newick','.tre','.tree','.nex','.nexus','.r','.py'}
SKIP_NAME=re.compile(r'(transcriptome|trinity|assembly|\.fa(sta)?$|\.fq(\.gz)?$|\.fastq(\.gz)?$)',re.I)

def get(url:str, accept='application/vnd.api+json,application/json,*/*'):
    req=urllib.request.Request(url,headers={'User-Agent':UA,'Accept':accept})
    with urllib.request.urlopen(req,timeout=120) as r:
        return r.read(),r.geturl(),dict(r.headers)

def jget(url:str):
    raw,resolved,headers=get(url)
    return json.loads(raw),resolved,headers

def walk(url:str, prefix=''):
    out=[]
    while url:
        obj,resolved,_=jget(url)
        for item in obj.get('data',[]):
            a=item.get('attributes',{}) or {}
            name=str(a.get('name') or item.get('id'))
            path=f'{prefix}/{name}'.strip('/')
            kind=a.get('kind')
            if kind=='folder':
                rel=((item.get('relationships') or {}).get('files') or {}).get('links',{}).get('related',{})
                href=rel.get('href') if isinstance(rel,dict) else rel
                if not href:
                    raise ValueError('folder without related files href: '+path)
                out.extend(walk(href,path))
            elif kind=='file':
                links=item.get('links',{}) or {}
                out.append({
                    'id':item.get('id'),'path':path,'name':name,'size':int(a.get('size') or 0),
                    'date_modified':a.get('date_modified'),'provider':'osfstorage',
                    'download_url':links.get('download'),
                    'md5':((a.get('extra') or {}).get('hashes') or {}).get('md5'),
                    'sha256_osf':((a.get('extra') or {}).get('hashes') or {}).get('sha256'),
                    'api_source':resolved,
                })
        nxt=(obj.get('links') or {}).get('next')
        url=nxt if isinstance(nxt,str) and nxt else None
    return out

def suffix(path:str):
    p=Path(path.lower())
    # Preserve compressed table/script endings only when the underlying suffix is recognized.
    if p.suffix=='.gz' and len(p.suffixes)>=2:
        return p.suffixes[-2]
    return p.suffix

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out-dir',type=Path,required=True);a=ap.parse_args()
    a.out_dir.mkdir(parents=True,exist_ok=True)
    files=walk(BASE)
    if not files: raise ValueError('OSF inventory is empty')
    (a.out_dir/'osf_inventory.json').write_text(json.dumps(files,indent=2)+'\n')
    selected=[]
    data_dir=a.out_dir/'processed';data_dir.mkdir(exist_ok=True)
    for f in files:
        s=suffix(f['path'])
        keep=(s in KEEP_SUFFIXES and f['size']<=MAX_BYTES and not SKIP_NAME.search(f['path']))
        f['selected_for_download']=bool(keep)
        if not keep: continue
        if not f['download_url']: raise ValueError('selected OSF file lacks download URL: '+f['path'])
        raw,resolved,_=get(f['download_url'],'application/octet-stream,*/*')
        if f['size'] and len(raw)!=f['size']:
            raise ValueError(f"size mismatch {f['path']}: {len(raw)} != {f['size']}")
        sha=hashlib.sha256(raw).hexdigest();md5=hashlib.md5(raw).hexdigest()
        if f['sha256_osf'] and sha.lower()!=str(f['sha256_osf']).lower(): raise ValueError('OSF sha256 mismatch: '+f['path'])
        if f['md5'] and md5.lower()!=str(f['md5']).lower(): raise ValueError('OSF md5 mismatch: '+f['path'])
        safe=re.sub(r'[^A-Za-z0-9._-]+','__',f['path'])
        target=data_dir/safe;target.write_bytes(raw)
        selected.append({**f,'local_name':safe,'download_resolved':resolved,'sha256':sha,'md5_computed':md5})
    if not selected: raise ValueError('no processed source files selected from OSF inventory')
    manifest={
        'version':'v0.1','osf_node':NODE,'inventory_count':len(files),'downloaded_count':len(selected),
        'downloaded':selected,'max_download_bytes':MAX_BYTES,'keep_suffixes':sorted(KEEP_SUFFIXES),
        'analysis_status':'SOURCE_INVENTORY_AND_PROCESSED_BYTES_ONLY_NOT_YET_ANALYSED',
        'claim_boundary':'No phenotype-axis or molecular-subspace result is inferred by acquisition.',
        'paper1_science_changed':False,
    }
    (a.out_dir/'source_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'inventory_count':len(files),'downloaded_count':len(selected),'paths':[x['path'] for x in selected]},indent=2))
if __name__=='__main__': main()
