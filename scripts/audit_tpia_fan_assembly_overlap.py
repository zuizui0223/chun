#!/usr/bin/env python3
"""Audit public TPIA transcriptome assemblies against Fan 2026 species colours.

TPIA's public transcriptome page obtains assembly metadata from
`selectAllassemblies` and downloads zip files from
`web/All_assemblies/Fasta/{ID}_{name}.zip`. This script freezes that live public
metadata and joins it to the deterministic Fan species-colour seed.
"""
from __future__ import annotations
import argparse,csv,json,pathlib,re,requests
from urllib.parse import quote

BASE='https://tpia.teaplants.cn/'
ENDPOINT=BASE+'selectAllassemblies'

def clean(s):return re.sub(r'\s+',' ',str(s or '').replace('\xa0',' ').strip())
def base_species(s):
    s=clean(s); s=re.sub(r'^C\.\s*','Camellia ',s); s=re.sub(r"\bcv\.\s+.*$",'',s,flags=re.I); s=re.sub(r"'[^']+'$",'',s).strip(); s=re.split(r'\s+(?:var\.|subsp\.|ssp\.|f\.|forma)\s+',s,maxsplit=1,flags=re.I)[0]; p=s.split(); return ' '.join(p[:2]) if len(p)>=2 and p[0]=='Camellia' else ''
def read(p):
    with open(p,newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))
def write(p,rows):
    p=pathlib.Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    if not rows:p.write_text('',encoding='utf-8');return
    with p.open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--fan-seed',type=pathlib.Path,required=True);ap.add_argument('--out-dir',type=pathlib.Path,required=True);a=ap.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
    r=requests.get(ENDPOINT,timeout=120,headers={'User-Agent':'chun-public-data-audit/0.1'});r.raise_for_status();data=r.json() if r.headers.get('content-type','').startswith('application/json') else json.loads(r.text)
    (a.out_dir/'selectAllassemblies.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    fan={x['taxon']:x for x in read(a.fan_seed)};rows=[]
    for d in data:
        name=clean(d.get('name'));sp=base_species(name);ID=clean(d.get('ID'));has=bool(d.get('hasZipFile'))
        # Website JS concatenates name literally; quote only URL-reserved characters for a valid HTTP request.
        zip_url=BASE+'web/All_assemblies/Fasta/'+quote(f'{ID}_{name}.zip',safe='._-()') if has else ''
        row={'tpia_ID':ID,'tpia_name':name,'species_base':sp,'cultivar':clean(d.get('cultivar')),'prjnaNumber':clean(d.get('prjnaNumber')),'hasZipFile':has,'unigeneSize':d.get('unigeneSize',''),'n50':d.get('n50',''),'complete':d.get('complete',''),'fragmented':d.get('fragmented',''),'missing':d.get('missing',''),'zip_url':zip_url,'fan_overlap':sp in fan,'fan_colour_state':fan.get(sp,{}).get('colour_state',''),'fan_section':fan.get(sp,{}).get('section','')}
        if has:
            try:
                h=requests.head(zip_url,allow_redirects=True,timeout=30,headers={'User-Agent':'chun-public-data-audit/0.1'});row['http_status']=h.status_code;row['content_length']=h.headers.get('content-length','')
            except Exception as e:row['http_status']='error';row['content_length']='';row['head_error']=str(e)
        rows.append(row)
    write(a.out_dir/'tpia_assemblies.csv',rows);over=[x for x in rows if x['fan_overlap'] and x['hasZipFile']];write(a.out_dir/'fan_overlap_assemblies.csv',over)
    uniq=sorted({x['species_base'] for x in over});sizes=[]
    for x in over:
        try:sizes.append(int(x['content_length']))
        except:pass
    summary={'n_tpia_rows':len(rows),'n_has_zip':sum(bool(x['hasZipFile']) for x in rows),'n_fan_overlap_rows_with_zip':len(over),'n_unique_fan_species_with_zip':len(uniq),'fan_state_counts':{s:sum(1 for sp in uniq if fan[sp]['colour_state']==s) for s in ('A','W','Y')},'known_content_length_files':len(sizes),'known_total_bytes':sum(sizes),'known_median_bytes':sorted(sizes)[len(sizes)//2] if sizes else None,'overlap_species':uniq,'endpoint':ENDPOINT}
    (a.out_dir/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
