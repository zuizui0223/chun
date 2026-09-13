#!/usr/bin/env python3
import hashlib, io, json, re, zipfile
from pathlib import Path
import requests
from openpyxl import load_workbook
from Bio import Phylo

EPMC_SUPP='https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7767864/supplementaryFiles'
DRYAD_SEARCH='https://datadryad.org/api/v2/search?q=10.5061%2Fdryad.m7589'
TREE_NAME='Gesne_Ago8_simple_combined_CA.tre'
OUT=Path('build/gesnerioideae_source_preflight_v0_1')
HEADER_SCAN_ROWS=20
HEADER_PATTERNS={
 'species':re.compile(r'^(species|species\s*name|taxon|taxon\s*name)$',re.I),
 'voucher':re.compile(r'voucher',re.I),'sample':re.compile(r'(sample|accession|collection)',re.I),
 'anthocyanin':re.compile(r'(anthocyan|pigment)',re.I),'reflectance':re.compile(r'(reflect|colou?r|hue)',re.I)}

def sha256(b): return hashlib.sha256(b).hexdigest()
def absurl(url): return 'https://datadryad.org'+url if url.startswith('/') else url
def get(url):
 r=requests.get(absurl(url),timeout=60); r.raise_for_status(); return r

def norm_binomial(x):
 s=re.sub(r'[_]+',' ',str(x).strip()); s=re.sub(r'\s+',' ',s); t=s.split()
 return (t[0].lower(),t[1].lower()) if len(t)>=2 else None

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
 cand=[]; diagnostics=[]
 for href,url,b in xlsx_rows:
  wb=load_workbook(io.BytesIO(b),read_only=True,data_only=False)
  for ws in wb.worksheets:
   scanned=scan_header_tokens(ws); diagnostics.append({'file':href,'sheet':ws.title,'rows':ws.max_row,'cols':ws.max_column,'header_token_hits':scanned})
   for item in scanned:
    kinds=[k for h in item['hits'] for k in h['kinds']]; sp=[h['col'] for h in item['hits'] if 'species' in h['kinds']]
    if not sp: continue
    score=5+(3 if 170<=ws.max_row<=220 else 0)+(2 if 'voucher' in kinds else 0)+(1 if 'sample' in kinds else 0)+(1 if 'anthocyanin' in kinds else 0)+(1 if 'reflectance' in kinds else 0)
    cand.append({'score':score,'href':href,'url':url,'bytes':b,'sheet':ws.title,'rows':ws.max_row,'cols':ws.max_column,'header_row':item['row'],'header_token_hits':item['hits'],'species_cols':sp})
 OUT.mkdir(parents=True,exist_ok=True)
 (OUT/'header_structure_diagnostic.json').write_text(json.dumps({'status':'OUTCOME_BLIND_HEADER_STRUCTURE_DIAGNOSTIC','outcome_values_retained':False,'scan_rows':HEADER_SCAN_ROWS,'sheets':diagnostics},indent=2,ensure_ascii=False)+'\n')
 cand.sort(key=lambda x:(-x['score'],abs(x['rows']-181),x['href'],x['sheet'],x['header_row']))
 if not cand or cand[0]['score']<8: raise RuntimeError('Could not unambiguously identify S1 from structural metadata')
 return cand[0]

def extract_species_only(s1):
 wb=load_workbook(io.BytesIO(s1['bytes']),read_only=True,data_only=False); ws=wb[s1['sheet']]; c=s1['species_cols'][0]; vals=[]
 for r in range(s1['header_row']+1,ws.max_row+1):
  v=ws.cell(r,c).value
  if v is not None and str(v).strip(): vals.append(str(v).strip())
 return vals,[norm_binomial(v) for v in vals]

def dataset_candidates(x):
 emb=x.get('_embedded',{})
 for k in ('stash:datasets','datasets','stash:dataset'):
  if isinstance(emb.get(k),list): return emb[k]
 return x.get('datasets',[]) if isinstance(x.get('datasets'),list) else []

def dryad_tree_manifest():
 ds=dataset_candidates(get(DRYAD_SEARCH).json())
 if not ds: raise RuntimeError('Dryad DOI search returned no dataset')
 meta=next((d for d in ds if 'dryad.m7589' in json.dumps(d).lower()),ds[0]); links=meta.get('_links',{})
 vh=(links.get('stash:version',{}) or links.get('version',{})).get('href'); fh=(links.get('stash:files',{}) or links.get('files',{})).get('href')
 if not fh and vh: fh=vh.rstrip('/')+'/files'
 if not fh: raise RuntimeError('Dryad files manifest endpoint absent')
 files=get(fh).json(); items=files.get('_embedded',{}).get('stash:files',[]) or files.get('_embedded',{}).get('files',[]) or files.get('files',[])
 m=next((it for it in items if it.get('path')==TREE_NAME or it.get('filename')==TREE_NAME),None)
 if not m: raise RuntimeError(f'{TREE_NAME} absent from Dryad manifest')
 dl=((m.get('_links',{}).get('stash:download',{}) or m.get('_links',{}).get('download',{})).get('href'))
 self_href=(m.get('_links',{}).get('self',{}) or {}).get('href',''); fid=self_href.rstrip('/').split('/')[-1] if self_href else None
 return meta,m,dl,fid

def main():
 OUT.mkdir(parents=True,exist_ok=True)
 xlsxs,zipsha=discover_supplementary_xlsx(); s1=choose_s1_without_outcomes(xlsxs); species_rows,species_keys=extract_species_only(s1)
 unique=[]; seen=set(); malformed=[]
 for raw,key in zip(species_rows,species_keys):
  if key is None: malformed.append(raw); continue
  if key not in seen: seen.add(key); unique.append((raw,key))
 _,m,dl,fid=dryad_tree_manifest()
 tree_manifest={'dryad_doi':'10.5061/dryad.m7589','filename':TREE_NAME,'file_id':fid,'size':m.get('size'),'mimeType':m.get('mimeType'),'digest':m.get('digest'),'digestType':m.get('digestType'),'download_endpoint':absurl(dl) if dl else None}
 tree_b=None; access_status='NOT_ATTEMPTED'
 if dl:
  r=requests.get(absurl(dl),timeout=60)
  if r.status_code==200: tree_b=r.content; access_status='ANONYMOUS_DOWNLOAD_OK'
  elif r.status_code==401: access_status='BEARER_TOKEN_REQUIRED_401'
  else: r.raise_for_status()
 base={'status':'GESNERIOIDEAE_SOURCE_PREFLIGHT_COMPLETE_OUTCOME_BLIND','outcome_values_read':False,'auc_computed':False,'decision_computed':False,'forbidden_columns_read':False,
  'supplementary_source':{'pmcid':'PMC7767864','endpoint':EPMC_SUPP,'supplementary_zip_sha256':zipsha,'selected_href':s1['href'],'selected_url':s1['url'],'sha256':sha256(s1['bytes']),'sheet':s1['sheet'],'max_row':s1['rows'],'max_column':s1['cols'],'header_row':s1['header_row'],'header_token_hits':s1['header_token_hits'],'selection_basis':'workbook shape + whitelisted header-token matches only'},
  'species_identifier_only':{'source_rows_nonempty':len(species_rows),'unique_normalized_binomials':len(unique),'malformed_species_labels':malformed},'tree_source_manifest':tree_manifest,'tree_byte_access':access_status}
 if tree_b is None:
  base.update({'hard_stop':'HOLD_SOURCE_ACCESS','crosswalk_executed':False,'required_external_input':'Dryad tree bytes matching frozen file id/digest, or an authorized DRYAD_TOKEN; do not inspect trait outcomes first'})
  (OUT/'source_preflight_receipt.json').write_text(json.dumps(base,indent=2,ensure_ascii=False)+'\n'); print(json.dumps(base,indent=2,ensure_ascii=False)); return
 tree_path=OUT/TREE_NAME; tree_path.write_bytes(tree_b); tree=Phylo.read(str(tree_path),'newick'); tips=[t.name for t in tree.get_terminals() if t.name]; tip_set={x for x in (norm_binomial(t) for t in tips) if x}
 unmatched=[raw for raw,key in unique if key not in tip_set]
 base['tree_source_manifest'].update({'downloaded_sha256':sha256(tree_b),'tree_tips':len(tips)})
 base.update({'crosswalk_executed':True,'matched_unique_binomials':len(unique)-len(unmatched),'unmatched_source_species':unmatched,'hard_stop':'PASS_CROSSWALK_PREFLIGHT' if not unmatched and not malformed else 'HOLD_CROSSWALK'})
 (OUT/'source_preflight_receipt.json').write_text(json.dumps(base,indent=2,ensure_ascii=False)+'\n'); (OUT/'species_only_crosswalk_preflight.csv').write_text('source_species,normalized_key,in_tree\n'+''.join(f'"{raw}","{key[0]} {key[1]}",{str(key in tip_set).lower()}\n' for raw,key in unique)); print(json.dumps(base,indent=2,ensure_ascii=False))

if __name__=='__main__': main()
