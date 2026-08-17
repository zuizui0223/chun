#!/usr/bin/env python3
"""Query the public TPIA2 Gene ID Convert endpoint across all source namespaces.

No source namespace is assumed from the legacy ID prefix. The same frozen ID
list is submitted to every source type exposed by the TPIA2 web interface.
Raw response bodies and normalized returned rows are retained with checksums.
This is a read-only provenance audit, not an orthology inference.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,time
from pathlib import Path
import requests

SOURCE_TYPES=[
    'Shuchazao1','Shuchazao2','Biyun','Huangdan','Tieguanyin','DASZ',
    'Longjin43','Yunkang10','Oil-tea','C.chekiangoleosa'
]
ENDPOINT='https://tpia.teaplants.cn/gene-id-convert/list'

def sha256(b:bytes)->str:return hashlib.sha256(b).hexdigest()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--ids',type=Path,required=True);ap.add_argument('--out-dir',type=Path,required=True);a=ap.parse_args()
    ids=[x.strip() for x in a.ids.read_text(encoding='utf-8').splitlines() if x.strip() and not x.startswith('#')]
    a.out_dir.mkdir(parents=True,exist_ok=True)
    s=requests.Session();s.headers.update({'User-Agent':'chun-camellia-orthology/0.1 (public TPIA2 read-only audit)','Accept':'application/json','Content-Type':'application/json'})
    normalized=[];attempts=[]
    for typ in SOURCE_TYPES:
        payload={'type':typ,'geneIds':ids}
        r=s.post(ENDPOINT,json=payload,timeout=60)
        raw=r.content
        (a.out_dir/f'{typ.replace(".","_").replace("-","_")}.json').write_bytes(raw)
        rec={'source_type':typ,'http_status':r.status_code,'response_bytes':len(raw),'response_sha256':sha256(raw),'content_type':r.headers.get('content-type',''),'payload':payload}
        try:
            obj=r.json();rec['json_type']=type(obj).__name__
            content=obj.get('content',[]) if isinstance(obj,dict) else []
            rec['returned_rows']=len(content) if isinstance(content,list) else None
            rec['top_level_keys']=sorted(obj.keys()) if isinstance(obj,dict) else []
            if isinstance(content,list):
                for row in content:
                    if not isinstance(row,dict):continue
                    for k,v in row.items():
                        if k=='id':continue
                        normalized.append({'source_type':typ,'returned_column':k,'returned_value':str(v),'row_json':json.dumps(row,sort_keys=True,ensure_ascii=False)})
        except Exception as e:
            rec['json_error']=repr(e);rec['body_preview']=r.text[:1000]
        attempts.append(rec)
        time.sleep(0.2)
    (a.out_dir/'attempts.json').write_text(json.dumps(attempts,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    with (a.out_dir/'normalized_rows.csv').open('w',newline='',encoding='utf-8') as f:
        fields=['source_type','returned_column','returned_value','row_json'];w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(normalized)
    summary={
        'endpoint':ENDPOINT,'input_ids':ids,'source_types_tested':SOURCE_TYPES,
        'successful_http_types':[r['source_type'] for r in attempts if r['http_status']==200],
        'types_with_returned_rows':[r['source_type'] for r in attempts if isinstance(r.get('returned_rows'),int) and r['returned_rows']>0],
        'returned_row_counts':{r['source_type']:r.get('returned_rows') for r in attempts},
        'claim_ceiling':'namespace and database crosswalk evidence only; returned IDs do not by themselves prove sequence orthology or functional equivalence'
    }
    (a.out_dir/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2,ensure_ascii=False))
if __name__=='__main__':main()
