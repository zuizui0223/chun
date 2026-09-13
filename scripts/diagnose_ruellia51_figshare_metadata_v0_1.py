#!/usr/bin/env python3
import json, urllib.request
from pathlib import Path

ARTICLE_ID=30282448
URL=f'https://api.figshare.com/v2/articles/{ARTICLE_ID}'
req=urllib.request.Request(URL,headers={'User-Agent':'CHUN-ruellia51-preflight/0.1','Accept':'application/json'})
with urllib.request.urlopen(req,timeout=60) as r:
    x=json.load(r)
files=[]
for f in x.get('files',[]):
    files.append({
        'id':f.get('id'),'name':f.get('name'),'size':f.get('size'),
        'is_link_only':f.get('is_link_only'),'download_url':f.get('download_url'),
        'supplied_md5':f.get('supplied_md5'),'computed_md5':f.get('computed_md5')
    })
out={
    'status':'FIGSHARE_METADATA_ONLY_OUTCOMES_UNOPENED',
    'article_id':ARTICLE_ID,
    'doi':x.get('doi'),
    'title':x.get('title'),
    'version':x.get('version'),
    'modified_date':x.get('modified_date'),
    'files':files,
    'row_level_HPLC_values_read':False,
    'AUC_computed':False,
    'winner_computed':False
}
p=Path('build/ruellia51_figshare_metadata_v0_1.json'); p.parent.mkdir(parents=True,exist_ok=True)
p.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
print(json.dumps(out,indent=2,ensure_ascii=False))
