#!/usr/bin/env python3
"""Fast TPIA assembly-registry x Fan species-colour overlap audit (no file HEADs)."""
from __future__ import annotations
import argparse,csv,json,pathlib,re,requests
from collections import Counter,defaultdict

ENDPOINT='https://tpia.teaplants.cn/selectAllassemblies'

def clean(s):return re.sub(r'\s+',' ',str(s or '').replace('\xa0',' ').strip())
def base_species(s):
    s=clean(s);s=re.sub(r'^C\.\s*','Camellia ',s);s=re.sub(r"\bcv\.\s+.*$",'',s,flags=re.I);s=re.sub(r"'[^']+'$",'',s).strip();s=re.split(r'\s+(?:var\.|subsp\.|ssp\.|f\.|forma)\s+',s,maxsplit=1,flags=re.I)[0];p=s.split();return ' '.join(p[:2]) if len(p)>=2 and p[0]=='Camellia' else ''
def read(p):
    with open(p,newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))
def write(p,rows):
    p=pathlib.Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    if not rows:p.write_text('',encoding='utf-8');return
    with p.open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--fan-seed',type=pathlib.Path,required=True);ap.add_argument('--out-dir',type=pathlib.Path,required=True);a=ap.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
    fan={r['taxon']:r for r in read(a.fan_seed)}
    r=requests.get(ENDPOINT,timeout=90,headers={'User-Agent':'chun-public-data-audit/0.2','Accept':'application/json,text/plain,*/*'});r.raise_for_status();raw=r.json()
    (a.out_dir/'selectAllassemblies.json').write_text(json.dumps(raw,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    rows=[];by=defaultdict(list)
    for x in raw:
        name=clean(x.get('name'));sp=base_species(name);has=bool(x.get('hasZipFile'));rec={'tpia_ID':clean(x.get('ID')),'tpia_name':name,'species_base':sp,'prjnaNumber':clean(x.get('prjnaNumber')),'cultivar':clean(x.get('cultivar')),'hasZipFile':has,'fan_overlap':sp in fan,'fan_colour_state':fan.get(sp,{}).get('colour_state',''),'fan_section':fan.get(sp,{}).get('section',''),'unigeneSize':x.get('unigeneSize',''),'n50':x.get('n50',''),'complete':x.get('complete',''),'fragmented':x.get('fragmented',''),'missing':x.get('missing','')};rows.append(rec)
        if sp and has:by[sp].append(rec)
    write(a.out_dir/'tpia_registry.csv',rows)
    overlap=[]
    for sp in sorted(set(fan)&set(by)):
        for rec in by[sp]:overlap.append(rec)
    write(a.out_dir/'fan_overlap_registry.csv',overlap)
    uniq=sorted(set(fan)&set(by));summary={'n_registry_rows':len(rows),'n_rows_with_zip':sum(bool(r['hasZipFile']) for r in rows),'n_unique_species_with_zip':len(by),'n_fan_species':len(fan),'n_unique_fan_species_with_zip':len(uniq),'fan_state_counts':dict(Counter(fan[s]['colour_state'] for s in uniq)),'overlap_species':uniq,'n_overlap_registry_rows':len(overlap),'endpoint':ENDPOINT}
    (a.out_dir/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
