#!/usr/bin/env python3
"""Audit all public TPIA bulk-download registry categories.

The public download page calls `selectdownload_data?Type=<display label>` and
constructs links under `web/Download/<option value>/<fileName>`. This script
freezes the live registry and highlights resources relevant to pan-transcriptome,
orthogroups/core genes and phylogeny.
"""
from __future__ import annotations
import argparse,csv,json,pathlib,re,requests
from urllib.parse import quote

BASE='https://tpia.teaplants.cn/'
CATS=[
 ('Genomic_data','Genomic data'),('Annotation_data','Annotation data'),
 ('Transcriptome_data','Transcriptome data'),('Expression_data','Expression data'),
 ('Metabolism_data','Metabolism data'),('Germplasm_data','Germplasm data'),
 ('Correlation_data','Correlation data'),('Other_related_data','Other related data')]
PAT=re.compile(r'(?i)(orth|gene.?famil|pan.?transcript|core.?gene|phylogen|tree|species.?tree|astral|raxml|mrbayes|transcriptome|assembly)')

def write(p,rows):
 p=pathlib.Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 if not rows:p.write_text('',encoding='utf-8');return
 fields=[];seen=set()
 for r in rows:
  for k in r:
   if k not in seen:fields.append(k);seen.add(k)
 with p.open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out-dir',type=pathlib.Path,required=True);a=ap.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
 allrows=[];hits=[]
 for value,label in CATS:
  u=BASE+'selectdownload_data';r=requests.get(u,params={'Type':label},timeout=60,headers={'User-Agent':'chun-public-data-audit/0.3','Accept':'application/json,text/plain,*/*'});r.raise_for_status()
  try:data=r.json()
  except Exception: data=json.loads(r.text)
  (a.out_dir/f'{value}.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  for x in data:
   fn=str(x.get('fileName','') or '').strip();desc=str(x.get('description','') or '').strip();typ=str(x.get('type','') or '').strip()
   row={'category_value':value,'category_label':label,'no':x.get('no',''),'type':typ,'description':desc,'fileName':fn,'format':x.get('format',''),'size':x.get('size',''),'download_url':BASE+'web/Download/'+value+'/'+quote(fn,safe='._-()') if fn else ''}
   allrows.append(row)
   if PAT.search(' '.join([fn,desc,typ])):hits.append(row)
 write(a.out_dir/'all_downloads.csv',allrows);write(a.out_dir/'phylogeny_gene_family_hits.csv',hits)
 summary={'n_categories':len(CATS),'n_rows':len(allrows),'n_candidate_hits':len(hits),'candidate_files':[{'category':r['category_value'],'fileName':r['fileName'],'description':r['description'],'size':r['size'],'download_url':r['download_url']} for r in hits]}
 (a.out_dir/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
