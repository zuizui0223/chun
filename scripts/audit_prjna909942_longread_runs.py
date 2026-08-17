#!/usr/bin/env python3
"""Identify long-read/PacBio runs in PRJNA909942 using public NCBI metadata.

The script first requests the NCBI SRA RunInfo CSV endpoint for the BioProject.
It records the exact response/checksum, then selects rows by Platform/Model/
LibraryStrategy text containing PACBIO/SMRT. If the endpoint fails or returns no
rows, it exits rather than inventing a run accession.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json
from pathlib import Path
import requests

URL='https://trace.ncbi.nlm.nih.gov/Traces/sra-db-be/runinfo'

def sha256(b:bytes)->str:return hashlib.sha256(b).hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument('--out-dir',type=Path,required=True);a=p.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
    s=requests.Session();s.headers['User-Agent']='chun-cnfls2-recovery/0.1 (public NCBI metadata audit)'
    r=s.get(URL,params={'acc':'PRJNA909942'},timeout=90);r.raise_for_status();raw=r.content;text=r.text
    (a.out_dir/'runinfo.csv').write_bytes(raw)
    rows=list(csv.DictReader(io.StringIO(text)))
    if not rows:raise SystemExit('NCBI RunInfo returned no rows for PRJNA909942')
    long=[]
    for x in rows:
        blob=' '.join(str(x.get(k,'')) for k in ['Platform','Model','LibraryStrategy','LibrarySource','LibrarySelection','ScientificName','SampleName']).upper()
        if any(t in blob for t in ['PACBIO','SMRT','SEQUEL','REVIO']):long.append(x)
    fields=sorted({k for x in rows for k in x})
    with (a.out_dir/'longread_runs.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(long)
    summary={'bioproject':'PRJNA909942','runinfo_url':r.url,'runinfo_sha256':sha256(raw),'total_runs':len(rows),'longread_runs':len(long),'longread_accessions':[x.get('Run') for x in long],'longread_models':sorted({x.get('Model','') for x in long}),'longread_sample_names':sorted({x.get('SampleName','') for x in long}),'decision':'long-read run metadata identified from NCBI RunInfo' if long else 'no long-read run identified; do not start reconstruction','claim_ceiling':'metadata identifies sequencing runs only; F01.PB8395 recovery still requires sequence-level primer/full-length matching'}
    (a.out_dir/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8');print(json.dumps(summary,indent=2))
    if not long:raise SystemExit('No PacBio/SMRT long-read row found')
if __name__=='__main__':main()
