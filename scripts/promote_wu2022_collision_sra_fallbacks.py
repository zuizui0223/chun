#!/usr/bin/env python3
"""Promote known TPIA checksum-collision taxa to frozen PRJNA665925 SRA fallbacks."""
from __future__ import annotations
import argparse,csv,json
from pathlib import Path

EXPECTED={
    'Camellia euphlebia':'SRR19266673',
    'Camellia pilosperma':'SRR19266674',
}

def read(path):
    with open(path,newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))

def write(path,rows,fields):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n',extrasaction='ignore');w.writeheader();w.writerows(rows)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--manifest-v02',type=Path,required=True)
    ap.add_argument('--run-taxa',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--summary',type=Path,required=True)
    a=ap.parse_args()
    rows=read(a.manifest_v02); runs=read(a.run_taxa)
    run_by_tax={}
    for r in runs:
        tax=r.get('normalized_taxon',''); run=r.get('Run','')
        if tax and run: run_by_tax.setdefault(tax,[]).append(r)
    promoted=[]
    for row in rows:
        tax=row['source_taxon']
        if tax not in EXPECTED: continue
        expected=EXPECTED[tax]
        hits=[r for r in run_by_tax.get(tax,[]) if r.get('Run')==expected]
        if len(hits)!=1: raise SystemExit(f'{tax}: expected frozen run {expected}, observed {hits}')
        r=hits[0]
        old={k:row.get(k,'') for k in ('assembly_source','assembly_file','assembly_url')}
        row.update({
            'assembly_source':'ncbi_sra_raw_fallback',
            'assembly_file':expected,
            'source_data':r.get('BioProject','PRJNA665925'),
            'advertised_size':'',
            'assembly_url':f'https://www.ncbi.nlm.nih.gov/sra/{expected}',
            'payload_identity_risk':'known_tpia_id_bound_checksum_collision_raw_sra_required',
            'analysis_role':'species_level_nuclear_backbone_raw_read_fallback',
            'claim_ceiling':'frozen NCBI SRA provenance after known TPIA checksum collision; transcript/locus recovery required before topology reconstruction',
        })
        promoted.append({'source_taxon':tax,'run':expected,'biosample':r.get('BioSample',''),'old_resource':old})
    if {x['source_taxon']:x['run'] for x in promoted}!=EXPECTED:
        raise SystemExit(f'promotion mismatch: {promoted}')
    fields=list(rows[0]); write(a.output,rows,fields)
    counts={k:sum(r['assembly_source']==k for r in rows) for k in sorted({r['assembly_source'] for r in rows})}
    summary={
        'analysis_version':'v0.3',
        'manifest_rows':len(rows),
        'resource_counts':counts,
        'known_collision_promotions':promoted,
        'expected_authoritative_state':{'tpia_id_bound_allassemblies':93,'ncbi_sra_raw_fallback':5},
        'decision':'known exact TPIA checksum-collision taxa are excluded from assembled-resource admission and reverted to frozen PRJNA665925 raw RNA-seq runs',
        'claim_ceiling':'resource provenance only; five raw-read taxa require transcript/locus recovery before nuclear topology reconstruction',
    }
    assert len(rows)==98, len(rows)
    assert counts.get('tpia_id_bound_allassemblies',0)==93, counts
    assert counts.get('ncbi_sra_raw_fallback',0)==5, counts
    a.summary.parent.mkdir(parents=True,exist_ok=True);a.summary.write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
