#!/usr/bin/env python3
"""Filter an audited accepted-species colour seed to taxa present in a frozen tree."""
import argparse,csv,json,re
from pathlib import Path
from Bio import Phylo

def key(x): return re.sub(r'\s+',' ',(x or '').strip().replace('_',' ')).casefold()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--tree',type=Path,required=True);ap.add_argument('--seed',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--summary',type=Path,required=True);a=ap.parse_args()
    tree=Phylo.read(str(a.tree),'newick');tips={key(x.name):x.name for x in tree.get_terminals() if x.name}
    with a.seed.open(newline='',encoding='utf-8-sig') as f:rows=list(csv.DictReader(f));fields=list(rows[0]) if rows else ['accepted_species','colour_state']
    kept=[];missing=[]
    for r in rows:
        k=key(r.get('accepted_species') or r.get('taxon'))
        if k in tips: kept.append(r)
        else: missing.append(r.get('accepted_species') or r.get('taxon'))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    with a.out.open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(kept)
    counts={s:sum((r.get('colour_state') or '').strip()==s for r in kept) for s in ['A','W','Y']}
    out={'tree_tips':len(tips),'input_seed_n':len(rows),'kept_seed_n':len(kept),'state_counts':counts,'missing_seed_taxa':sorted(missing)}
    a.summary.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
