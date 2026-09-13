#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from Bio import SeqIO

LOCI = ["matK", "trnL", "ndhF", "trnK", "rbcL", "ITS"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree-input-dir", type=Path, required=True)
    ap.add_argument("--trimmed-dir", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()
    out=args.out_dir; out.mkdir(parents=True, exist_ok=True)

    receipt=json.loads((args.tree_input_dir/'tree_input_receipt.json').read_text())
    assert receipt['trait_file_read'] is False
    taxa=(args.tree_input_dir/'tree_taxa.txt').read_text().splitlines()
    if len(taxa)!=227 or len(set(taxa))!=227:
        raise SystemExit(f'expected 227 unique tree taxa, got {len(taxa)}')

    pieces={t:[] for t in taxa}
    coords=[]; start=1
    per_locus={}
    for loc in LOCI:
        path=args.trimmed_dir/f'{loc}.trimmed.fasta'
        records={r.id:str(r.seq).upper() for r in SeqIO.parse(str(path),'fasta')}
        if not records:
            raise SystemExit(f'empty trimmed alignment for {loc}')
        lengths={len(s) for s in records.values()}
        if len(lengths)!=1:
            raise SystemExit(f'nonrectangular alignment for {loc}: {lengths}')
        L=next(iter(lengths))
        end=start+L-1
        coords.append((loc,start,end,L,len(records)))
        per_locus[loc]={'alignment_length':L,'taxa_with_sequence':len(records)}
        for t in taxa:
            pieces[t].append(records.get(t,'-'*L))
        start=end+1

    concat=out/'iris_primary_concatenated.fasta'
    with concat.open('w') as fh:
        for t in taxa:
            seq=''.join(pieces[t])
            fh.write(f'>{t}\n{seq}\n')
    total=start-1

    part=out/'iris_primary_partitions.nex'
    lines=['#nexus','begin sets;']
    for loc,s,e,_,_ in coords:
        lines.append(f'  charset {loc} = {s}-{e};')
    lines.append('end;')
    part.write_text('\n'.join(lines)+'\n')

    summary={
      'version':'v0.1',
      'status':'IRIS_PRIMARY_TREE_ALIGNMENT_CONCATENATED_TRAIT_BLIND',
      'taxa':len(taxa),
      'loci':LOCI,
      'per_locus':per_locus,
      'total_alignment_length':total,
      'partition_coordinates':{loc:[s,e] for loc,s,e,_,_ in coords},
      'trait_values_used':False,
      'auc_computed':False,
      'decision_computed':False,
      'paper1_science_changed':False,
    }
    (out/'concat_receipt.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
