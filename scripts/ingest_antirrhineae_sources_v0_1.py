#!/usr/bin/env python3
"""Acquire and inventory the CC0 Ellis & Field Antirrhineae source bundle.

The dataset DOI and published MD5 are treated as the source contract. Candidate
file URLs are discovered from DOI/record HTML; a payload is admitted only if it
matches the published MD5. No flower-colour state or phylogenetic conclusion is
inferred in this acquisition step.
"""
from __future__ import annotations
import argparse,hashlib,html,json,re,urllib.parse,urllib.request,zipfile
from pathlib import Path

DOI='10.15479/AT:ISTA:34'
RECORD_ID='5550'
FILENAME='IST-2016-34-v1+1_tellis_flower_colour_data.zip'
EXPECTED_MD5='950f85b80427d357bfeff09608ba02e9'
PAGES=[
    'https://doi.org/'+DOI,
    'https://research-explorer.ista.ac.at/record/5550',
    'https://research-explorer-playground.test.ista.ac.at/record/5550',
]

def get(url:str)->tuple[bytes,str]:
    req=urllib.request.Request(url,headers={'User-Agent':'chun-antirrhineae-source-audit/0.1'})
    with urllib.request.urlopen(req,timeout=60) as r:
        return r.read(),r.geturl()

def discover()->tuple[list[str],list[dict]]:
    urls=[];pages=[]
    for page in PAGES:
        try:
            raw,final=get(page); text=raw.decode('utf-8','replace'); pages.append({'requested':page,'resolved':final,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
        except Exception as e:
            pages.append({'requested':page,'error':type(e).__name__+': '+str(e)});continue
        hrefs=re.findall(r'''href\s*=\s*["']([^"']+)["']''',text,re.I)
        for href in hrefs:
            href=html.unescape(href)
            if FILENAME in href or ('.zip' in href.lower() and ('5550' in href or 'flower' in href.lower())):
                urls.append(urllib.parse.urljoin(final,href))
    # Conservative fallback patterns for the record's declared filename.
    for base in ('https://research-explorer.ista.ac.at','https://research-explorer-playground.test.ista.ac.at'):
        urls += [
          f'{base}/record/{RECORD_ID}/files/{FILENAME}',
          f'{base}/record/{RECORD_ID}/files/{FILENAME}?download=1',
          f'{base}/record/{RECORD_ID}/files/{urllib.parse.quote(FILENAME,safe="+")}',
        ]
    return list(dict.fromkeys(urls)),pages

def acquire(urls:list[str],out:Path):
    attempts=[]
    for url in urls:
        try:
            raw,final=get(url); md5=hashlib.md5(raw).hexdigest(); rec={'requested':url,'resolved':final,'bytes':len(raw),'md5':md5,'sha256':hashlib.sha256(raw).hexdigest()}
            if md5==EXPECTED_MD5:
                out.write_bytes(raw);rec['admitted']=True;attempts.append(rec);return rec,attempts
            rec['admitted']=False;rec['reason']='PUBLISHED_MD5_MISMATCH';attempts.append(rec)
        except Exception as e:
            attempts.append({'requested':url,'admitted':False,'error':type(e).__name__+': '+str(e)})
    raise RuntimeError('no discovered candidate matched the published source MD5; attempts='+json.dumps(attempts))

def inventory(zpath:Path,outdir:Path):
    extracted=outdir/'extracted';extracted.mkdir(parents=True,exist_ok=True);members=[]
    with zipfile.ZipFile(zpath) as z:
        for info in z.infolist():
            if info.is_dir(): continue
            # Reject path traversal.
            target=(extracted/info.filename).resolve()
            if not target.is_relative_to(extracted.resolve()): raise ValueError('unsafe archive path: '+info.filename)
            raw=z.read(info.filename);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
            rec={'name':info.filename,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'suffix':Path(info.filename).suffix.lower()}
            if rec['suffix'] in ('.nex','.nexus','.txt','.csv','.tsv','.r','.tre','.tree','.nwk'):
                text=raw.decode('utf-8','replace');rec['text_lines']=len(text.splitlines());rec['text_preview']=text[:600]
            members.append(rec)
    return members

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out-dir',type=Path,required=True);a=ap.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
    urls,pages=discover();zpath=a.out_dir/'source_bundle.zip';admitted,attempts=acquire(urls,zpath);members=inventory(zpath,a.out_dir)
    ext_counts={}
    for r in members: ext_counts[r['suffix']]=ext_counts.get(r['suffix'],0)+1
    result={
      'version':'v0.1','source_doi':DOI,'source_record_id':RECORD_ID,'declared_filename':FILENAME,
      'published_license':'CC0-1.0','published_md5':EXPECTED_MD5,
      'admitted_download':admitted,'page_audit':pages,'download_attempts':attempts,
      'archive_member_count':len(members),'extension_counts':ext_counts,'members':members,
      'trait_history_status':'SOURCE_ACQUIRED_NOT_YET_REANALYSED',
      'claim_boundary':'Source acquisition/inventory only. No terminal-state recoding, ancestral reconstruction, transition estimate or cross-clade replication is claimed.'}
    (a.out_dir/'source_manifest.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'admitted':admitted,'member_count':len(members),'extension_counts':ext_counts},indent=2))
if __name__=='__main__':main()
