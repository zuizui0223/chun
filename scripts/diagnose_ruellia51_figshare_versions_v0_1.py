#!/usr/bin/env python3
import json, urllib.request
from pathlib import Path

BASE='https://api.figshare.com/v2/articles/30282448'
def get(url):
    req=urllib.request.Request(url,headers={'User-Agent':'CHUN-ruellia51-tree-recovery/0.1','Accept':'application/json'})
    with urllib.request.urlopen(req,timeout=60) as r: return json.load(r)
versions=get(BASE+'/versions')
out=[]
for v in versions:
    n=v.get('version')
    x=get(BASE+f'/versions/{n}')
    out.append({
      'version':n,'doi':x.get('doi'),'modified_date':x.get('modified_date'),
      'files':[{'id':f.get('id'),'name':f.get('name'),'size':f.get('size'),'supplied_md5':f.get('supplied_md5'),'computed_md5':f.get('computed_md5')} for f in x.get('files',[])]
    })
res={'status':'FIGSHARE_VERSION_HISTORY_METADATA_ONLY_OUTCOMES_UNOPENED','versions':out,'row_level_HPLC_values_read':False,'AUC_computed':False,'winner_computed':False}
p=Path('build/ruellia51_figshare_versions_v0_1.json');p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res,indent=2))
