#!/usr/bin/env python3
from __future__ import annotations
import hashlib, http.cookiejar, io, json, re, urllib.error, urllib.parse, urllib.request, zipfile
from pathlib import Path
import xml.etree.ElementTree as ET
from Bio import Phylo

TRAIT_DOI='10.1111/plb.12649'
TABLE_S3='plb12649-sup-0002-TableS3.docx'
TABLE_URL='https://onlinelibrary.wiley.com/action/downloadSupplement?doi=10.1111%2Fplb.12649&file='+TABLE_S3
TREE_DOI='10.5061/dryad.8cz8w9grq'
TREE_FILE='1_WP_RAxML.tre'
API='https://datadryad.org/api/v2'
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/140 Safari/537.36'
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'


def norm(x:str)->str:
    x=x.strip().replace('_',' ')
    x=re.sub(r'\s+',' ',x)
    return x.lower()


def opener():
    jar=http.cookiejar.CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))


def request(op,url,accept='*/*',referer=None,timeout=120):
    h={'User-Agent':UA,'Accept':accept,'Accept-Language':'en-US,en;q=0.9'}
    if referer: h['Referer']=referer
    req=urllib.request.Request(url,headers=h)
    try:
        with op.open(req,timeout=timeout) as r:
            return {'ok':True,'status':r.status,'final_url':r.geturl(),'headers':dict(r.headers),'body':r.read()}
    except urllib.error.HTTPError as e:
        try: body=e.read()
        except Exception: body=b''
        return {'ok':False,'status':e.code,'final_url':e.geturl(),'headers':dict(e.headers or {}),'body':body,'reason':str(e.reason)}
    except Exception as e:
        return {'ok':False,'status':None,'final_url':url,'headers':{},'body':b'','reason':repr(e)}


def jget(op,url):
    r=request(op,url,'application/json')
    if not r['ok']: raise SystemExit(f'JSON request failed {url}: {r["status"]} {r.get("reason")}')
    return json.loads(r['body'])


def first_column_species(docx:bytes):
    # The DOCX necessarily contains all Table S3 cells, but this parser projects ONLY
    # the first cell of each row. Flower colour and CIELAB cells are never read/stored/emitted.
    with zipfile.ZipFile(io.BytesIO(docx)) as z:
        xml=z.read('word/document.xml')
    root=ET.fromstring(xml)
    out=[]
    first_cells=[]
    for tr in root.iter(W+'tr'):
        tcs=list(tr.findall(W+'tc'))
        if not tcs: continue
        txt=''.join((t.text or '') for t in tcs[0].iter(W+'t')).strip()
        first_cells.append(txt)
        if re.match(r'^Rhododendron\b',txt,re.I): out.append(txt)
    # If genus is omitted in a species column, fail rather than inspect other outcome cells to infer structure.
    return out, first_cells[:10]


def dryad_file_id(meta):
    href=meta.get('_links',{}).get('self',{}).get('href','')
    m=re.search(r'/files/(\d+)$',href)
    if not m: raise SystemExit(f'cannot parse file id from {href!r}')
    return int(m.group(1))


def digest_matches(meta,body):
    typ=str(meta.get('digestType') or '').lower().replace('_','-')
    expected=str(meta.get('digest') or '').lower()
    sha=hashlib.sha256(body).hexdigest(); md5=hashlib.md5(body).hexdigest()
    if typ in {'sha-256','sha256'}: match=(sha==expected)
    elif typ=='md5': match=(md5==expected)
    else: match=None
    return sha,md5,match


def main():
    op=opener()
    outcome_firewall={
      'table_s1_chemistry_downloaded':False,
      'row_level_anthocyanin_values_accessed':False,
      'flower_colour_values_accessed':False,
      'CIELAB_values_accessed':False,
      'compound_presence_states_computed':False,
      'state_frequencies_computed':False,
      'AUC_computed':False,
      'winner_computed':False,
    }

    # Trait species identity only from Table S3 first column.
    tr=request(op,TABLE_URL,'application/vnd.openxmlformats-officedocument.wordprocessingml.document,*/*')
    trait_receipt={'url':TABLE_URL,'http_status':tr.get('status'),'ok':tr.get('ok'),'downloaded_bytes':len(tr['body']),
                   'sha256':hashlib.sha256(tr['body']).hexdigest() if tr['body'] else None,
                   'content_type':tr.get('headers',{}).get('Content-Type'),'reason':tr.get('reason')}
    trait_species=[]; first_cells=[]
    if tr['ok'] and tr['body'][:2]==b'PK':
        try: trait_species,first_cells=first_column_species(tr['body'])
        except Exception as e: trait_receipt['parse_error']=repr(e)
    trait_receipt['species_first_column_count']=len(trait_species)
    trait_receipt['first_column_preview_only']=first_cells

    # Frozen primary-tree metadata then public bytes if available.
    ds=jget(op,API+'/datasets/'+urllib.parse.quote('doi:'+TREE_DOI,safe=''))
    vh=ds['_links']['stash:version']['href']
    vurl=vh if vh.startswith('http') else API+vh.removeprefix('/api/v2')
    fl=jget(op,vurl.rstrip('/')+'/files?per_page=100')
    files=fl.get('_embedded',{}).get('stash:files',[])
    by={f.get('path'):f for f in files}
    if TREE_FILE not in by: raise SystemExit(f'{TREE_FILE} absent from Dryad files: {sorted(by)}')
    tm=by[TREE_FILE]; fid=dryad_file_id(tm)
    landing='https://datadryad.org/dataset/'+urllib.parse.quote('doi:'+TREE_DOI,safe='/')
    request(op,landing,'text/html')
    rr=request(op,f'https://datadryad.org/stash/downloads/file_stream/{fid}','*/*',referer=landing)
    sha,md5,match=digest_matches(tm,rr['body'])
    ctype=str(rr.get('headers',{}).get('Content-Type',''))
    treeish=(len(rr['body'])>1000 and b'(' in rr['body'] and b';' in rr['body'] and 'html' not in ctype.lower())
    tree_receipt={
      'doi':TREE_DOI,'dataset_version_number':ds.get('versionNumber'),'version_href':vh,
      'file':TREE_FILE,'file_id':fid,'api_size':tm.get('size'),'digest_type_api':tm.get('digestType'),'digest_api':tm.get('digest'),
      'public_route_http_status':rr.get('status'),'public_route_content_type':ctype,'downloaded_bytes':len(rr['body']),
      'sha256_downloaded':sha,'md5_downloaded':md5,'digest_match':match,'treeish_payload':treeish,
      'reason':rr.get('reason')
    }
    tips=[]; all_bl=False; duplicate_tips=None
    if treeish and (match is True or tm.get('digest') is None):
        tree=Phylo.read(io.StringIO(rr['body'].decode('utf-8-sig')),'newick')
        tips=[str(t.name) for t in tree.get_terminals()]
        branches=[c.branch_length for c in tree.find_clades() if c is not tree.root]
        all_bl=bool(branches) and all(x is not None for x in branches)
        duplicate_tips=len(tips)-len(set(norm(x) for x in tips))
        tree_receipt.update({'tip_count':len(tips),'duplicate_normalized_tips':duplicate_tips,'all_nonroot_branch_lengths_present':all_bl})

    ts={norm(x):x for x in trait_species}
    tt={norm(x):x for x in tips}
    matched=sorted(set(ts)&set(tt))
    trait_only=sorted(set(ts)-set(tt)) if tips else []
    tree_only=sorted(set(tt)-set(ts)) if trait_species and tips else []

    if len(trait_species)!=30:
        status='HOLD_TRAIT_SPECIES_SCHEMA_OR_ACCESS'
    elif not treeish or match is not True:
        status='HOLD_TREE_SOURCE_ACCESS_OUTCOMES_UNOPENED'
    elif duplicate_tips!=0 or not all_bl:
        status='HOLD_TREE_SCHEMA'
    elif len(matched)<20:
        status='HOLD_CROSSWALK_OR_TREE_COVERAGE'
    else:
        status='PASS_CROSSWALK_PREFLIGHT_OUTCOMES_UNOPENED'

    out={
      'version':'v0.1','status':status,
      'trait_source_doi':TRAIT_DOI,'trait_species_supplement':TABLE_S3,
      'trait_receipt':trait_receipt,
      'trait_species_normalized':sorted(ts),
      'tree_receipt':tree_receipt,
      'crosswalk':{
        'trait_species_count':len(ts),'tree_tip_count':len(tt),'exact_normalized_matches':len(matched),
        'matched_normalized':matched,'trait_only_normalized':trait_only,'tree_only_normalized_restricted_report':tree_only[:200],
        'automatic_synonym_substitution':False,'crosswalk_frozen':status=='PASS_CROSSWALK_PREFLIGHT_OUTCOMES_UNOPENED'
      },
      'outcome_firewall':outcome_firewall,
      'next_gate':'FREEZE_HASH_AND_CROSSWALK_THEN_OPEN_TABLE_S1_CHEMISTRY' if status=='PASS_CROSSWALK_PREFLIGHT_OUTCOMES_UNOPENED' else 'STOP_WITHOUT_OPENING_TABLE_S1_CHEMISTRY',
      'paper1_science_changed':False
    }
    Path('build').mkdir(exist_ok=True)
    Path('build/rhododendron30_source_preflight_v0_1.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    if treeish and match is True: Path('build/1_WP_RAxML.tre').write_bytes(rr['body'])
    print(json.dumps({'status':status,'trait_species':len(ts),'tree_tips':len(tt),'matched':len(matched),'trait_http':tr.get('status'),'tree_http':rr.get('status'),'tree_digest_match':match,'treeish':treeish,'outcome_firewall':outcome_firewall},indent=2))

if __name__=='__main__': main()
