#!/usr/bin/env python3
"""Freeze only the pre-admitted runtime91 Angiosperms353 loci from HybPiper output."""
from __future__ import annotations
import argparse,csv,glob,json,re
from pathlib import Path


def read_fasta(path: Path) -> str:
    seq=[]
    with path.open(encoding='utf-8',errors='ignore') as f:
        for line in f:
            if not line.strip() or line.startswith('>'): continue
            seq.append(re.sub(r'[^A-Za-z*]','',line.strip()).upper().replace('*','X'))
    return ''.join(seq)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--taxon',required=True)
    ap.add_argument('--sample-dir',type=Path,required=True)
    ap.add_argument('--occupancy',type=Path,required=True)
    ap.add_argument('--out-dir',type=Path,required=True)
    ap.add_argument('--min-aa',type=int,default=80)
    a=ap.parse_args(); a.out_dir.mkdir(parents=True,exist_ok=True)

    occ=list(csv.DictReader(a.occupancy.open(newline='',encoding='utf-8-sig')))
    frozen={r['locus'] for r in occ if str(r.get('admitted','')).lower() in {'true','1','yes'} and float(r['occupancy'])>=0.80}
    if len(frozen)!=339: raise SystemExit(f'expected 339 frozen loci, got {len(frozen)}')

    protein_files=sorted(Path(p) for p in glob.glob(str(a.sample_dir/'**'/'sequences'/'FAA'/'*.FAA'),recursive=True))
    rows=[]; seen=set()
    for p in protein_files:
        candidates=[p.stem,p.parent.parent.parent.name]
        loc=''
        for x in candidates:
            m=re.search(r'(\d+)$',x)
            if m and m.group(1) in frozen:
                loc=m.group(1); break
        if not loc or loc in seen: continue
        seq=read_fasta(p)
        if len(seq)<a.min_aa: continue
        seen.add(loc)
        rows.append({'taxon':a.taxon,'locus':loc,'protein_aa':len(seq),'protein_seq':seq,'hybpiper_file':str(p)})

    rows.sort(key=lambda r:int(r['locus']))
    with (a.out_dir/'best_hits.csv').open('w',newline='',encoding='utf-8') as f:
        fields=['taxon','locus','protein_aa','protein_seq','hybpiper_file']
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
    with (a.out_dir/'frozen_markers.faa').open('w',encoding='utf-8') as f:
        for r in rows:
            f.write(f">{a.taxon.replace(' ','_')}|locus_{r['locus']}\n{r['protein_seq']}\n")
    summary={'taxon':a.taxon,'frozen_loci':339,'hybpiper_protein_files':len(protein_files),
             'recovered_loci':len(rows),'recovery_fraction':len(rows)/339,
             'missing_loci':sorted(frozen-seen,key=int),
             'claim_ceiling':'same-project nuclear outgroup marker recovery using the frozen runtime91 339-locus definition; no rooting/topology or ecological inference yet'}
    (a.out_dir/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))

if __name__=='__main__': main()
