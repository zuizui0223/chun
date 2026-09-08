#!/usr/bin/env python3
"""Summarize the already generated Epimedium access layer; no signal computation."""
import csv, hashlib, json
from pathlib import Path

BASE=Path('analysis/_generated/epimedium_fine_state_access_v1')

def main():
    matches=json.loads((BASE/'tnrs_matches.json').read_text(encoding='utf-8'))
    exact=sorted((m['query'],int(m['ott_id'])) for m in matches if m['status']=='EXACT' and m['ott_id'] is not None)
    rejected=sorted(m['query'] for m in matches if m['status']!='EXACT')
    tree=(BASE/'opentree_raw.nwk').read_bytes()
    rows=list(csv.DictReader((BASE/'source_rebuild'/'source_taxon_summary.csv').open(encoding='utf-8')))
    by={r['taxon_normalized']:r for r in rows}
    states=[]
    for name,ott in exact:
        r=by[name]
        states.append({'taxon':name,'ott_id':ott,'sepal':r['sepal_codes'],'spur':r['spur_codes'],'joint':r['joint_codes']})
    out={'exact_taxa_n':len(exact),'exact_taxa':states,'rejected_taxa':rejected,
         'opentree_raw_newick_sha256':hashlib.sha256(tree).hexdigest(),
         'state_rows_sha256':hashlib.sha256(json.dumps(states,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
         'sankoff_computed':False,'permutation_computed':False}
    (BASE/'admission_candidate.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print('EPIMEDIUM_ADMISSION_CANDIDATE='+json.dumps(out,ensure_ascii=False,separators=(',',':')))
if __name__=='__main__': main()
