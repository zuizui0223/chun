#!/usr/bin/env python3
"""Recover organ-specific Angraecinae flower-colour states from the primary S2/S3 matrices.

No author ancestral state or BiSSE terminal coding is imported. Four source organ-colour
characters are retained separately; binary GREEN/WHITE admission is explicit and fail-closed.
"""
from __future__ import annotations
import argparse,csv,json,re
from collections import Counter
from pathlib import Path

CHARACTERS={
    20:('sepal',{'1':'GREEN_YELLOWISH','2':'WHITE_WHITEGREEN','3':'OCHER','4':'OTHER'}),
    23:('petal',{'1':'GREEN_YELLOWISH','2':'WHITE_WHITEGREEN','3':'OCHER','4':'OTHER'}),
    31:('labellum',{'1':'GREEN_YELLOWISH','2':'WHITE_WHITEGREEN','3':'OTHER'}),
    37:('spur',{'1':'GREEN_YELLOWISH','2':'WHITE_WHITEGREEN','3':'OTHER'}),
}
OUTGROUPS={'Acampe ochracea','Aerides odorata','Phalaenopsis cornu-cervi','Vanda tricolor','Polystachya fulvilabia'}

def norm(s):return re.sub(r'\s+',' ',s.strip())
def binary(code):return 'GREEN' if code=='1' else ('WHITE' if code=='2' else 'OUTSIDE_BINARY')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source-dir',type=Path,required=True);ap.add_argument('--out-dir',type=Path,required=True);a=ap.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
    files=a.source_dir/'files';s2=files/'pone.0163194.s008.csv';s3=files/'pone.0163194.s009.csv'
    desc=list(csv.reader(s2.read_text(encoding='latin-1').splitlines(),delimiter=';'))
    observed={}
    current=None
    for r in desc[1:]:
        if r and r[0].strip():current=int(r[0]) if r[0].strip().isdigit() else None
        if current in CHARACTERS and len(r)>=4 and r[2].strip():observed[(current,r[2].strip())]=r[3].strip().lower()
    expected={(20,'1'):'green to yellowish',(20,'2'):'white to white green',(23,'1'):'green to yellowish',(23,'2'):'white to white green',(31,'1'):'greenish to yellowish',(31,'2'):'white to white green',(37,'1'):'green to yellowish',(37,'2'):'white to white green'}
    for k,v in expected.items():
        if observed.get(k)!=v:raise ValueError(f'colour codebook drift {k}: {observed.get(k)!r}')
    matrix=list(csv.reader(s3.read_text(encoding='utf-8-sig').splitlines(),delimiter=';'))
    header=matrix[0]
    if header[20]!='20' or header[23]!='23' or header[31]!='31' or header[37]!='37':raise ValueError('morphology column numbering drift')
    rows=[]
    for i,r in enumerate(matrix[1:],1):
        if len(r)<40:raise ValueError(f'short morphology row {i}')
        taxon=norm(r[0]); raw={organ:r[c].strip() for c,(organ,_) in CHARACTERS.items()}
        for c,(organ,states) in CHARACTERS.items():
            if raw[organ] not in states:raise ValueError(f'unknown {organ} code {raw[organ]} for {taxon}')
        sep,pet=raw['sepal'],raw['petal'];all4=[raw[x] for x in ('sepal','petal','labellum','spur')]
        per='GREEN' if sep==pet=='1' else ('WHITE' if sep==pet=='2' else 'OUTSIDE_BINARY')
        strict='GREEN' if all(v=='1' for v in all4) else ('WHITE' if all(v=='2' for v in all4) else 'OUTSIDE_BINARY')
        rows.append({'morphology_row':i,'source_taxon':taxon,'source_group':'OUTGROUP' if taxon in OUTGROUPS else 'ANGRAECINAE','sepal_code':sep,'sepal_binary':binary(sep),'petal_code':pet,'petal_binary':binary(pet),'labellum_code':raw['labellum'],'labellum_binary':binary(raw['labellum']),'spur_code':raw['spur'],'spur_binary':binary(raw['spur']),'display_perianth_concordant':per,'all4_concordant':strict})
    if len(rows)!=194 or len({r['source_taxon'] for r in rows})!=194:raise ValueError('expected 194 unique morphology taxa')
    fields=list(rows[0]);out=a.out_dir/'terminal_organ_states.csv'
    with out.open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    policies=['sepal_binary','petal_binary','labellum_binary','spur_binary','display_perianth_concordant','all4_concordant']
    summary={'version':'v0.1','source_rows':194,'ingroup_rows':189,'outgroup_rows':5,'policy_counts':{p:dict(Counter(r[p] for r in rows)) for p in policies},'source_character_contract':{str(c):{'organ':o,'states':s} for c,(o,s) in CHARACTERS.items()},'primary_cross_clade_policies':['sepal_binary','petal_binary'],'derived_sensitivity_policies':['display_perianth_concordant','all4_concordant'],'claim_boundary':'Organ-specific source characters are primary. Derived whole-display proxies are sensitivities only; OUTSIDE_BINARY states are never silently recoded to GREEN or WHITE.','atlas_asr_status':'TRAITS_RECOVERED_TREE_NOT_YET_JOINED'}
    (a.out_dir/'trait_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
