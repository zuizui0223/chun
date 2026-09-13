#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,urllib.request
from pathlib import Path
UA='chun-iris-article-api-probe/0.1'; A='569811'
URLS=[
 f'https://www.frontiersin.org/api/v4/articles/{A}',
 f'https://www.frontiersin.org/api/v4/articles/{A}/',
 f'https://www.frontiersin.org/api/v4/articles/{A}/files',
 f'https://www.frontiersin.org/api/v4/articles/{A}/file',
 f'https://www.frontiersin.org/api/v4/articles/{A}/supplementary-materials',
 f'https://www.frontiersin.org/api/v3/articles/{A}',
]
def fetch(u):
 q=urllib.request.Request(u,headers={'User-Agent':UA,'Accept':'application/json,text/plain,*/*'})
 with urllib.request.urlopen(q,timeout=30) as r: return r.geturl(),r.status,(r.headers.get('Content-Type') or '').split(';',1)[0].lower(),r.read()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=[]
 for u in URLS:
  try:
   f,s,ct,b=fetch(u)
   # Metadata probe only. Preserve only a bounded text prefix and parsed structural keys when JSON.
   rec={'url':u,'final_url':f,'status':s,'content_type':ct,'bytes':len(b),'prefix':b[:4000].decode('utf-8','replace')}
   try:
    j=json.loads(b); rec['json_type']=type(j).__name__; rec['json_keys']=list(j)[:100] if isinstance(j,dict) else None
    # recursively collect strings that look like supplementary filenames/URLs, without article science text
    hits=[]
    def walk(x,path=''):
     if isinstance(x,dict):
      for k,v in x.items(): walk(v,f'{path}.{k}' if path else str(k))
     elif isinstance(x,list):
      for i,v in enumerate(x): walk(v,f'{path}[{i}]')
     elif isinstance(x,str) and ('.xlsx' in x.lower() or '.csv' in x.lower() or '/file/' in x.lower()): hits.append({'path':path,'value':x})
    walk(j); rec['file_like_strings']=hits[:200]
   except Exception: pass
   out.append(rec)
  except Exception as e: out.append({'url':u,'error':repr(e)})
R={'version':'v0.1','status':'ARTICLE_METADATA_PROBE_ONLY','probes':out,'row_level_values_emitted':False,'auc_computed':False}
a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(R,indent=2)+'\n');print(json.dumps(R,indent=2));return 0
if __name__=='__main__': raise SystemExit(main())
