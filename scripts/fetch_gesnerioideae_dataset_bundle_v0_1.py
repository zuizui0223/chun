#!/usr/bin/env python3
import requests, zipfile, io, hashlib, json, sys
from pathlib import Path
URL='https://datadryad.org/api/v2/datasets/doi%253A10.5061%252Fdryad.m7589/download'
TARGET='Gesne_Ago8_simple_combined_CA.tre'
SIZE=668933
MD5='94d6f267f5c123d6d875170da1783ffa'
out=Path('build/gesnerioideae_dataset_bundle_v0_1'); out.mkdir(parents=True,exist_ok=True)
r=requests.get(URL,timeout=120,allow_redirects=True,headers={'User-Agent':'Mozilla/5.0 CHUN source verifier'})
rec={'status_code':r.status_code,'final_url':r.url,'content_type':r.headers.get('content-type'),'bundle_size':len(r.content),'outcome_values_read':False,'auc_computed':False,'decision_computed':False}
try:
 z=zipfile.ZipFile(io.BytesIO(r.content))
 names=z.namelist(); rec['zip_entries']=names
 hit=[n for n in names if n.endswith(TARGET)]
 if hit:
  b=z.read(hit[0]); rec['tree_size']=len(b); rec['tree_md5']=hashlib.md5(b).hexdigest(); rec['entry']=hit[0]
  if len(b)==SIZE and rec['tree_md5']==MD5:
   (out/TARGET).write_bytes(b); rec['status']='PASS_EXACT_FROZEN_TREE_BYTES'
  else: rec['status']='HOLD_TREE_HASH_MISMATCH'
 else: rec['status']='HOLD_TREE_NOT_IN_BUNDLE'
except Exception as e:
 rec['status']='HOLD_DATASET_DOWNLOAD_NOT_ZIP'; rec['error']=repr(e); rec['prefix']=r.content[:200].decode('utf-8','replace')
(out/'receipt.json').write_text(json.dumps(rec,indent=2),encoding='utf-8')
print(json.dumps(rec,indent=2))
sys.exit(0 if rec.get('status')=='PASS_EXACT_FROZEN_TREE_BYTES' else 2)
