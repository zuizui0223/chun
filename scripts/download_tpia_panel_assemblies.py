#!/usr/bin/env python3
"""Download ID-bound TPIA panel assemblies, checksum them, and unwrap FASTA.gz.

Distinct taxa are required to have distinct outer ZIP SHA256 checksums. This hard
provenance gate prevents the species-name bulk-endpoint collision discovered in
the Wu/TPIA audit from silently entering the phylogeny pilot.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,json,re,sys,zipfile
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
import requests

def slug(t): return re.sub(r'[^A-Za-z0-9]+','_',t).strip('_')
def read_panel(p):
    with open(p,newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))
def fetch(row,outdir,read_timeout,retries):
    tax=row['taxon'];url=row['assembly_url'];dest=outdir/(slug(tax)+'.zip')
    s=requests.Session();s.headers['User-Agent']='Mozilla/5.0 chun-angio353-pilot/0.2'
    last=None
    for attempt in range(1,retries+1):
        try:
            print(f'DOWNLOAD_START\t{tax}\tattempt={attempt}\t{url}',flush=True)
            with s.get(url,stream=True,timeout=(15,read_timeout)) as r:
                r.raise_for_status();h=hashlib.sha256();n=0
                with dest.open('wb') as f:
                    for chunk in r.iter_content(1024*1024):
                        if chunk:f.write(chunk);h.update(chunk);n+=len(chunk)
            with zipfile.ZipFile(dest) as z:
                members=[i for i in z.infolist() if not i.is_dir()]
                if len(members)!=1: raise RuntimeError(f'expected one archive member, got {len(members)}')
                info=members[0]
                with z.open(info) as raw:
                    if info.filename.lower().endswith('.gz'):
                        with gzip.GzipFile(fileobj=raw,mode='rb') as dec: head=dec.read(4096)
                    else: head=raw.read(4096)
                if not head.lstrip().startswith(b'>'):raise RuntimeError('inner payload is not FASTA')
            print(f'DOWNLOAD_OK\t{tax}\tbytes={n}\tsha256={h.hexdigest()}',flush=True)
            return {'taxon':tax,'tip':slug(tax),'colour_state':row['colour_state'],'section':row['section'],'tpia_id':row['tpia_id'],'resource_name':row['tpia_resource_name'],'url':url,'zip_file':dest.name,'zip_bytes':n,'zip_sha256':h.hexdigest(),'inner_member':info.filename,'status':'ok'}
        except Exception as e:
            last=e
            print(f'DOWNLOAD_FAIL\t{tax}\tattempt={attempt}\t{type(e).__name__}: {e}',file=sys.stderr,flush=True)
            try:dest.unlink(missing_ok=True)
            except Exception:pass
    raise RuntimeError(f'{tax}: {last}')

def unwrap(rec,download,outdir):
    zp=download/rec['zip_file'];out=outdir/(rec['tip']+'.fna')
    with zipfile.ZipFile(zp) as z:
        info=[i for i in z.infolist() if not i.is_dir()][0]
        with z.open(info) as raw:
            src=gzip.GzipFile(fileobj=raw,mode='rb') if info.filename.lower().endswith('.gz') else raw
            with out.open('wb') as f:
                while True:
                    b=src.read(1024*1024)
                    if not b:break
                    f.write(b)
            if src is not raw:src.close()
    with out.open('rb') as f:head=f.read(4096)
    if not head.lstrip().startswith(b'>'):raise RuntimeError(f'unwrapped payload not FASTA: {out}')
    rec['fasta_file']=out.name;rec['fasta_bytes']=out.stat().st_size
    print(f'UNWRAP_OK\t{rec["taxon"]}\tfasta_bytes={rec["fasta_bytes"]}',flush=True)
    return rec

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--panel',type=Path,required=True);ap.add_argument('--out-dir',type=Path,required=True);ap.add_argument('--workers',type=int,default=8);ap.add_argument('--read-timeout',type=int,default=60);ap.add_argument('--retries',type=int,default=2);a=ap.parse_args()
    panel=read_panel(a.panel);download=a.out_dir/'zips';fastas=a.out_dir/'fastas';download.mkdir(parents=True,exist_ok=True);fastas.mkdir(parents=True,exist_ok=True)
    rows=[]; errors=[]
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        fut={ex.submit(fetch,r,download,a.read_timeout,a.retries):r for r in panel}
        for f in as_completed(fut):
            try: rows.append(f.result())
            except Exception as e:
                errors.append({'taxon':fut[f]['taxon'],'url':fut[f]['assembly_url'],'error':str(e)})
    if errors:
        (a.out_dir/'download_failures.json').write_text(json.dumps(errors,indent=2)+'\n')
        raise SystemExit('TPIA panel download failures: '+json.dumps(errors))
    rows.sort(key=lambda r:r['taxon'])
    byhash={}
    for r in rows:
        byhash.setdefault(r['zip_sha256'],[]).append(r['taxon'])
    collisions={h:t for h,t in byhash.items() if len(t)>1}
    if collisions:raise SystemExit('distinct-taxon ZIP checksum collision: '+json.dumps(collisions))
    rows=[unwrap(r,download,fastas) for r in rows]
    with (a.out_dir/'archive_provenance.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    summary={'n_taxa':len(rows),'unique_zip_sha256':len(byhash),'checksum_collisions':collisions,'total_zip_bytes':sum(r['zip_bytes'] for r in rows),'total_fasta_bytes':sum(r['fasta_bytes'] for r in rows),'read_timeout_seconds':a.read_timeout,'retries':a.retries,'claim_ceiling':'ID-bound TPIA panel payload provenance; no biological inference'}
    (a.out_dir/'download_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
