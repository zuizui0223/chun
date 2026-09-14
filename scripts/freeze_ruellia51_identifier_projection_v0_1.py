#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, io, json, urllib.request
from collections import defaultdict
from pathlib import Path

URL='https://ndownloader.figshare.com/files/58502635'
SIZE=130680
MD5='0e3b9830abb1378f9546cd7d07ae1f97'
ALLOWED=['hplc_id','species','spec_ID','phylo_ID']


def norm(x: str) -> str:
    return ' '.join(x.strip().replace('_',' ').split()).lower()


def main():
    req=urllib.request.Request(URL,headers={'User-Agent':'CHUN-ruellia51-identifiers/0.1'})
    with urllib.request.urlopen(req,timeout=120) as r: raw=r.read()
    assert len(raw)==SIZE,(len(raw),SIZE)
    assert hashlib.md5(raw).hexdigest()==MD5
    reader=csv.reader(io.StringIO(raw.decode('utf-8-sig')))
    header=[x.strip() for x in next(reader)]
    missing=[x for x in ALLOWED if x not in header]
    if missing: raise SystemExit(f'missing identifier columns {missing}')
    idx={x:header.index(x) for x in ALLOWED}
    rows=[]
    for rownum,r in enumerate(reader,start=2):
        if len(r)<len(header): continue
        rows.append({x:r[i].strip() for x,i in idx.items()} | {'source_row':rownum})

    species_to_phylo=defaultdict(set); phylo_to_species=defaultdict(set)
    nonempty_phylo=set(); nonempty_species=set()
    for r in rows:
        sp=norm(r['species']) if r['species'] else ''
        ph=norm(r['phylo_ID']) if r['phylo_ID'] else ''
        if sp: nonempty_species.add(sp)
        if ph: nonempty_phylo.add(ph)
        if sp and ph:
            species_to_phylo[sp].add(ph); phylo_to_species[ph].add(sp)

    sp_multi={k:sorted(v) for k,v in species_to_phylo.items() if len(v)>1}
    ph_multi={k:sorted(v) for k,v in phylo_to_species.items() if len(v)>1}
    mapping=[]
    for ph in sorted(nonempty_phylo):
        spp=sorted(phylo_to_species.get(ph,set()))
        mapping.append({'phylo_id_normalized':ph,'species_normalized':spp[0] if len(spp)==1 else None,'n_species_labels':len(spp)})

    out={
      'version':'v0.1','status':'RUELLIA51_IDENTIFIER_PROJECTION_FROZEN_OUTCOMES_UNOPENED',
      'source_file':'raw_data.csv','figshare_file_id':58502635,'size':SIZE,'md5':MD5,
      'allowed_columns_accessed':ALLOWED,
      'forbidden_hplc_numeric_columns_accessed':False,
      'data_rows_total':len(rows),
      'rows_with_nonempty_species':sum(bool(r['species']) for r in rows),
      'rows_with_nonempty_phylo_id':sum(bool(r['phylo_ID']) for r in rows),
      'unique_species_normalized':len(nonempty_species),
      'unique_phylo_ids_normalized':len(nonempty_phylo),
      'species_mapping_to_multiple_phylo_ids':sp_multi,
      'phylo_id_mapping_to_multiple_species':ph_multi,
      'phylo_id_species_projection':mapping,
      'sample_to_species_rule_changed':False,
      'hplc_outcomes_opened':False,'auc_computed':False,'winner_computed':False,
      'next_gate':'MATCH_FROZEN_PHYLO_ID_KEY_SET_TO_AUTHORITATIVE_TREE_TIPS_BEFORE_HPLC_OUTCOME_OPENING'
    }
    Path('build').mkdir(exist_ok=True)
    Path('build/ruellia51_identifier_projection_v0_1.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in out.items() if k not in {'phylo_id_species_projection'}},indent=2,ensure_ascii=False))

if __name__=='__main__': main()
