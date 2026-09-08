#!/usr/bin/env python3
"""Acquire and inventory the CC0 Ellis & Field Antirrhineae source bundle.

The data DOI, record identity, declared filename and historical published MD5 are
preserved separately. Exact MD5 agreement is preferred. If the published MD5 has
drifted, current bytes may be opened for *source-content audit only* when two
ISTA-operated record hosts independently return identical bytes from the same
record/file identifier. Such a payload is explicitly marked checksum-drifted and
is not silently described as historical-hash verified.
"""
from __future__ import annotations
import argparse,hashlib,html,json,re,urllib.parse,urllib.request,zipfile
from pathlib import Path

DOI='10.15479/AT:ISTA:34'
RECORD_ID='5550'
FILE_ID='5594'
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
    # The record HTML currently resolves to /download/5550/5594/<filename>.
    for base in ('https://research-explorer.ista.ac.at','https://research-explorer-playground.test.ista.ac.at'):
        urls.append(f'{base}/download/{RECORD_ID}/{FILE_ID}/{urllib.parse.quote(FILENAME)}')
    return list(dict.fromkeys(urls)),pages

def acquire(urls:list[str],out:Path):
    attempts=[];payloads=[]
    for url in urls:
        try:
            raw,final=get(url); md5=hashlib.md5(raw).hexdigest(); sha=hashlib.sha256(raw).hexdigest()
            rec={'requested':url,'resolved':final,'bytes':len(raw),'md5':md5,'sha256':sha}
            payloads.append((raw,rec));attempts.append(rec)
            if md5==EXPECTED_MD5:
                out.write_bytes(raw);rec['admitted_for_content_audit']=True;rec['integrity_status']='PUBLISHED_MD5_MATCH'
                return rec,attempts
            rec['admitted_for_content_audit']=False;rec['integrity_status']='PUBLISHED_MD5_MISMATCH'
        except Exception as e:
            attempts.append({'requested':url,'admitted_for_content_audit':False,'error':type(e).__name__+': '+str(e)})
    # Explicit drift gate: require matching current bytes from both ISTA-operated hosts,
    # resolving the declared record/file identifier. This permits inspection, not a
    # claim that the historical checksum is satisfied.
    official=[]
    for raw,rec in payloads:
        host=urllib.parse.urlparse(rec['resolved']).hostname or ''
        if host in ('research-explorer.ista.ac.at','research-explorer-playground.test.ista.ac.at') and f'/download/{RECORD_ID}/{FILE_ID}/' in rec['resolved']:
            official.append((raw,rec))
    hosts={urllib.parse.urlparse(r['resolved']).hostname for _,r in official}
    shas={r['sha256'] for _,r in official};sizes={r['bytes'] for _,r in official}
    if {'research-explorer.ista.ac.at','research-explorer-playground.test.ista.ac.at'}<=hosts and len(shas)==1 and len(sizes)==1:
        raw,chosen=official[0];out.write_bytes(raw)
        chosen=dict(chosen);chosen.update(admitted_for_content_audit=True,integrity_status='CURRENT_ISTA_MIRRORS_IDENTICAL_PUBLISHED_MD5_DRIFT',published_md5_match=False,independent_current_hosts=sorted(hosts))
        return chosen,attempts
    raise RuntimeError('source integrity gate failed; attempts='+json.dumps(attempts))

def inventory(zpath:Path,outdir:Path):
    extracted=outdir/'extracted';extracted.mkdir(parents=True,exist_ok=True);members=[]
    with zipfile.ZipFile(zpath) as z:
        for info in z.infolist():
            if info.is_dir(): continue
            target=(extracted/info.filename).resolve()
            if not target.is_relative_to(extracted.resolve()): raise ValueError('unsafe archive path: '+info.filename)
            raw=z.read(info.filename);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
            rec={'name':info.filename,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'suffix':Path(info.filename).suffix.lower()}
            if rec['suffix'] in ('.nex','.nexus','.txt','.csv','.tsv','.r','.tre','.tree','.nwk'):
                text=raw.decode('utf-8','replace');rec['text_lines']=len(text.splitlines());rec['text_preview']=text[:800]
            members.append(rec)
    return members

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out-dir',type=Path,required=True);a=ap.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
    urls,pages=discover();zpath=a.out_dir/'source_bundle.zip';admitted,attempts=acquire(urls,zpath);members=inventory(zpath,a.out_dir)
    ext_counts={}
    for r in members: ext_counts[r['suffix']]=ext_counts.get(r['suffix'],0)+1
    result={
      'version':'v0.1','source_doi':DOI,'source_record_id':RECORD_ID,'source_file_id':FILE_ID,'declared_filename':FILENAME,
      'published_license':'CC0-1.0','historical_published_md5':EXPECTED_MD5,
      'current_source_integrity_status':admitted['integrity_status'],'admitted_download':admitted,
      'page_audit':pages,'download_attempts':attempts,
      'archive_member_count':len(members),'extension_counts':ext_counts,'members':members,
      'trait_history_status':'SOURCE_CONTENT_AUDIT_ONLY_NOT_YET_REANALYSED',
      'claim_boundary':'Source acquisition/inventory only. A historical published-MD5 mismatch is retained explicitly if present. No terminal-state recoding, ancestral reconstruction, transition estimate or cross-clade replication is claimed.'}
    (a.out_dir/'source_manifest.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'integrity_status':admitted['integrity_status'],'current_sha256':admitted['sha256'],'member_count':len(members),'extension_counts':ext_counts},indent=2))
if __name__=='__main__':main()
