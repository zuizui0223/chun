#!/usr/bin/env python3
"""Fetch public TPIA2 CDS/transcript sequences for resolved crosswalk rows.

Uses the exact Batch Retrieve endpoint discovered from TPIA2 CustomExport.js.
TPIA2 returns an attachment named Sequences.zip; the script now retains the
raw ZIP checksum, extracts every member in memory, and parses FASTA records
from the member text. Each genome/version and sequence type is queried
separately. This establishes sequence provenance but does not itself infer
orthology.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,re,time,zipfile
from pathlib import Path
from urllib.parse import urlencode
import requests

BASE='https://tpia.teaplants.cn/getGeneSeqByGeneNames'
COL_TO_TYPE={'yk10':'Yunkang10','sczv1':'Shuchazao1','sczv2':'Shuchazao2'}

def sha256(b:bytes)->str:return hashlib.sha256(b).hexdigest()

def parse_fasta(text:str):
    records=[];h=None;seq=[]
    for raw in text.splitlines():
        line=raw.strip()
        if not line:continue
        if line.startswith('>'):
            if h is not None:records.append((h,''.join(seq)))
            h=line[1:].strip();seq=[]
        elif h is not None:
            seq.append(re.sub(r'\s+','',line))
    if h is not None:records.append((h,''.join(seq)))
    return records

def decode_payload(raw:bytes,content_disposition:str):
    members=[]
    is_zip=raw.startswith(b'PK\x03\x04') or 'Sequences.zip' in content_disposition
    if is_zip:
        with zipfile.ZipFile(io.BytesIO(raw)) as zf:
            for info in zf.infolist():
                if info.is_dir():continue
                b=zf.read(info.filename)
                members.append((info.filename,b))
    else:
        members.append(('response.txt',raw))
    return is_zip,members

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--crosswalk',type=Path,required=True);ap.add_argument('--out-dir',type=Path,required=True);a=ap.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
    with a.crosswalk.open(newline='',encoding='utf-8') as f:rows=list(csv.DictReader(f))
    admitted=[r for r in rows if r['crosswalk_status']=='TPIA2_gene_id_convert_exact_row']
    s=requests.Session();s.headers['User-Agent']='chun-camellia-orthology/0.1 (public TPIA2 sequence provenance)'
    audit=[];fasta_rows=[]
    for col,tea_type in COL_TO_TYPE.items():
        ids=[r[col] for r in admitted if r[col]]
        for seq_type in ['cds','transcript']:
            params={'geneNames':','.join(ids),'cds':1 if seq_type=='cds' else 0,'trans':1 if seq_type=='transcript' else 0,'exon':0,'down':0,'up':0,'teaType':tea_type}
            url=BASE+'?'+urlencode(params)
            resp=s.get(url,timeout=120,allow_redirects=True);raw=resp.content
            slug=f'{col}_{seq_type}'
            (a.out_dir/f'{slug}.zip').write_bytes(raw)
            disp=resp.headers.get('content-disposition','')
            is_zip,members=decode_payload(raw,disp)
            records=[];member_meta=[]
            for member_name,b in members:
                safe_name=re.sub(r'[^A-Za-z0-9._-]+','_',member_name)
                (a.out_dir/f'{slug}__{safe_name}').write_bytes(b)
                text=b.decode('utf-8',errors='replace')
                parsed=parse_fasta(text);records.extend((member_name,h,seq) for h,seq in parsed)
                member_meta.append({'name':member_name,'bytes':len(b),'sha256':sha256(b),'n_fasta_records':len(parsed)})
            audit.append({'crosswalk_column':col,'tea_type':tea_type,'sequence_type':seq_type,'http_status':resp.status_code,'final_url':resp.url,'content_type':resp.headers.get('content-type',''),'content_disposition':disp,'response_bytes':len(raw),'response_sha256':sha256(raw),'is_zip':is_zip,'zip_members_json':json.dumps(member_meta,sort_keys=True),'requested_ids':';'.join(ids),'n_fasta_records':len(records)})
            for member_name,header,seq in records:
                fasta_rows.append({'crosswalk_column':col,'tea_type':tea_type,'sequence_type':seq_type,'member_name':member_name,'header':header,'sequence_length':len(seq),'sequence_sha256':sha256(seq.upper().encode()),'sequence':seq.upper()})
            time.sleep(.2)
    with (a.out_dir/'request_audit.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(audit[0]));w.writeheader();w.writerows(audit)
    with (a.out_dir/'fasta_records.csv').open('w',newline='',encoding='utf-8') as f:
        fields=['crosswalk_column','tea_type','sequence_type','member_name','header','sequence_length','sequence_sha256','sequence'];w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(fasta_rows)
    summary={'endpoint':BASE,'resolved_crosswalk_rows':len(admitted),'genome_columns':list(COL_TO_TYPE),'requests':len(audit),'successful_requests':sum(x['http_status']==200 for x in audit),'all_responses_zip':all(x['is_zip'] for x in audit),'total_fasta_records':len(fasta_rows),'fasta_records_by_request':{f"{x['crosswalk_column']}:{x['sequence_type']}":x['n_fasta_records'] for x in audit},'claim_ceiling':'sequence provenance/checksum only; ID-convert row plus sequence recovery does not by itself prove orthology across species'}
    (a.out_dir/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
