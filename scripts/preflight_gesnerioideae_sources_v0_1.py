#!/usr/bin/env python3
import hashlib, io, json, re, sys, zipfile
from pathlib import Path
import requests
from openpyxl import load_workbook
from Bio import Phylo

EPMC_SUPP = 'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7767864/supplementaryFiles'
DRYAD_SEARCH = 'https://datadryad.org/api/v2/search?q=10.5061%2Fdryad.m7589'
TREE_NAME = 'Gesne_Ago8_simple_combined_CA.tre'
OUT = Path('build/gesnerioideae_source_preflight_v0_1')
HEADER_SCAN_ROWS = 20
HEADER_PATTERNS = {
    'species': re.compile(r'^(species|species\s*name|taxon|taxon\s*name)$', re.I),
    'voucher': re.compile(r'voucher', re.I),
    'sample': re.compile(r'(sample|accession|collection)', re.I),
    'anthocyanin': re.compile(r'(anthocyan|pigment)', re.I),
    'reflectance': re.compile(r'(reflect|colou?r|hue)', re.I),
}

def sha256(b): return hashlib.sha256(b).hexdigest()
def get(url):
    r=requests.get(url,timeout=60); r.raise_for_status(); return r

def norm_binomial(x):
    s=re.sub(r'[_]+',' ',str(x).strip()); s=re.sub(r'\s+',' ',s); toks=s.split()
    return (toks[0].lower(),toks[1].lower()) if len(toks)>=2 else None

def discover_supplementary_xlsx():
    zbytes=get(EPMC_SUPP).content; rows=[]
    with zipfile.ZipFile(io.BytesIO(zbytes)) as z:
        for name in z.namelist():
            if name.lower().endswith('.xlsx'): rows.append((name,EPMC_SUPP+'#'+name,z.read(name)))
    if not rows: raise RuntimeError('No XLSX files found in Europe PMC supplementaryFiles ZIP')
    return rows,sha256(zbytes)

def scan_header_tokens(ws):
    hits=[]
    for r in range(1,min(ws.max_row,HEADER_SCAN_ROWS)+1):
        row=[]
        for c in range(1,min(ws.max_column,100)+1):
            v=ws.cell(r,c).value
            if not isinstance(v,str): continue
            s=re.sub(r'\s+',' ',v.strip()); kinds=[k for k,p in HEADER_PATTERNS.items() if p.search(s)]
            if kinds: row.append({'col':c,'kinds':kinds,'token':s})
        if row: hits.append({'row':r,'hits':row})
    return hits

def choose_s1_without_outcomes(xlsx_rows):
    candidates=[]; diagnostics=[]
    for href,url,b in xlsx_rows:
        wb=load_workbook(io.BytesIO(b),read_only=True,data_only=False)
        for ws in wb.worksheets:
            scanned=scan_header_tokens(ws)
            diagnostics.append({'file':href,'sheet':ws.title,'rows':ws.max_row,'cols':ws.max_column,'header_token_hits':scanned})
            for item in scanned:
                kinds=[k for h in item['hits'] for k in h['kinds']]; species_cols=[h['col'] for h in item['hits'] if 'species' in h['kinds']]
                if not species_cols: continue
                score=5+(3 if 170<=ws.max_row<=220 else 0)+(2 if 'voucher' in kinds else 0)+(1 if 'sample' in kinds else 0)+(1 if 'anthocyanin' in kinds else 0)+(1 if 'reflectance' in kinds else 0)
                candidates.append({'score':score,'href':href,'url':url,'bytes':b,'sheet':ws.title,'rows':ws.max_row,'cols':ws.max_column,'header_row':item['row'],'header_token_hits':item['hits'],'species_cols':species_cols})
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'header_structure_diagnostic.json').write_text(json.dumps({'status':'OUTCOME_BLIND_HEADER_STRUCTURE_DIAGNOSTIC','outcome_values_retained':False,'scan_rows':HEADER_SCAN_ROWS,'sheets':diagnostics},indent=2,ensure_ascii=False)+'\n')
    candidates.sort(key=lambda x:(-x['score'],abs(x['rows']-181),x['href'],x['sheet'],x['header_row']))
    if not candidates: raise RuntimeError('Could not identify a species header within first 20 rows using header-token whitelist')
    if candidates[0]['score']<8: raise RuntimeError(f'Ambiguous S1 structural identification: top score={candidates[0]["score"]}')
    return candidates[0],candidates

def extract_species_only(s1):
    wb=load_workbook(io.BytesIO(s1['bytes']),read_only=True,data_only=False); ws=wb[s1['sheet']]; c=s1['species_cols'][0]; vals=[]
    for r in range(s1['header_row']+1,ws.max_row+1):
        v=ws.cell(r,c).value
        if v is not None and str(v).strip(): vals.append(str(v).strip())
    return vals,[norm_binomial(v) for v in vals]

def _dataset_candidates(search_json):
    emb=search_json.get('_embedded',{})
    for key in ('stash:datasets','datasets','stash:dataset'):
        vals=emb.get(key)
        if isinstance(vals,list): return vals
    vals=search_json.get('datasets')
    return vals if isinstance(vals,list) else []

def download_dryad_tree():
    search=get(DRYAD_SEARCH).json(); candidates=_dataset_candidates(search)
    if not candidates: raise RuntimeError('Dryad search returned no dataset for DOI 10.5061/dryad.m7589')
    meta=None
    for d in candidates:
        text=json.dumps(d).lower()
        if 'dryad.m7589' in text: meta=d; break
    if meta is None: meta=candidates[0]
    links=meta.get('_links',{})
    version_href=(links.get('stash:version',{}) or links.get('version',{})).get('href')
    files_href=(links.get('stash:files',{}) or links.get('files',{})).get('href')
    if not files_href and version_href: files_href=version_href.rstrip('/')+'/files'
    if not files_href:
        self_href=(links.get('self',{}) or {}).get('href')
        if self_href:
            detail=get(self_href).json(); links=detail.get('_links',{})
            files_href=(links.get('stash:files',{}) or links.get('files',{})).get('href')
            version_href=(links.get('stash:version',{}) or links.get('version',{})).get('href')
            if not files_href and version_href: files_href=version_href.rstrip('/')+'/files'
    if not files_href: raise RuntimeError('Dryad files endpoint absent after DOI search resolution')
    files=get(files_href).json(); items=files.get('_embedded',{}).get('stash:files',[]) or files.get('_embedded',{}).get('files',[]) or files.get('files',[])
    match=next((it for it in items if it.get('path')==TREE_NAME or it.get('filename')==TREE_NAME),None)
    if not match: raise RuntimeError(f'{TREE_NAME} not found in Dryad file listing')
    l=match.get('_links',{}); dl=(l.get('stash:download',{}) or l.get('download',{})).get('href') or match.get('downloadURL') or match.get('url')
    if not dl: raise RuntimeError('Dryad tree download URL absent')
    b=get(dl).content; return meta,match,dl,b

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    xlsxs,supp_zip_sha=discover_supplementary_xlsx(); s1,_=choose_s1_without_outcomes(xlsxs); species_rows,species_keys=extract_species_only(s1)
    _,_,tree_url,tree_b=download_dryad_tree(); tree_path=OUT/TREE_NAME; tree_path.write_bytes(tree_b); tree=Phylo.read(str(tree_path),'newick')
    tips=[t.name for t in tree.get_terminals() if t.name]; tip_set={x for x in (norm_binomial(t) for t in tips) if x}
    source_unique=[]; seen=set(); malformed=[]
    for raw,key in zip(species_rows,species_keys):
        if key is None: malformed.append(raw); continue
        if key not in seen: seen.add(key); source_unique.append((raw,key))
    matched=[(raw,key) for raw,key in source_unique if key in tip_set]; unmatched=[raw for raw,key in source_unique if key not in tip_set]
    receipt={'status':'GESNERIOIDEAE_SOURCE_PREFLIGHT_COMPLETE_OUTCOME_BLIND','outcome_values_read':False,'auc_computed':False,'decision_computed':False,
      'supplementary_source':{'pmcid':'PMC7767864','endpoint':EPMC_SUPP,'supplementary_zip_sha256':supp_zip_sha,'selected_href':s1['href'],'selected_url':s1['url'],'sha256':sha256(s1['bytes']),'sheet':s1['sheet'],'max_row':s1['rows'],'max_column':s1['cols'],'header_row':s1['header_row'],'header_token_hits':s1['header_token_hits'],'selection_basis':'workbook shape + whitelisted header-token matches only'},
      'species_identifier_only':{'source_rows_nonempty':len(species_rows),'unique_normalized_binomials':len(source_unique),'malformed_species_labels':malformed,'tree_tips':len(tips),'matched_unique_binomials':len(matched),'unmatched_source_species':unmatched},
      'tree_source':{'dryad_doi':'10.5061/dryad.m7589','filename':TREE_NAME,'download_url':tree_url,'sha256':sha256(tree_b),'tree_tips':len(tips)},
      'hard_stop':'PASS_CROSSWALK_PREFLIGHT' if not unmatched and not malformed else 'HOLD_CROSSWALK','forbidden_columns_read':False}
    (OUT/'source_preflight_receipt.json').write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+'\n')
    (OUT/'species_only_crosswalk_preflight.csv').write_text('source_species,normalized_key,in_tree\n'+''.join(f'"{raw}","{key[0]} {key[1]}",{str(key in tip_set).lower()}\n' for raw,key in source_unique))
    print(json.dumps(receipt,indent=2,ensure_ascii=False))
    if receipt['hard_stop']!='PASS_CROSSWALK_PREFLIGHT': sys.exit(2)
if __name__=='__main__': main()
