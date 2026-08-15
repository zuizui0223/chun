#!/usr/bin/env python3
"""Build a provenance-safe Wu 2022 species-level TPIA assembly manifest.

Priority is the ID-bound TPIA `All_assemblies` URL because a diagnostic audit
showed that species-named bulk-download URLs can return non-species-specific
payloads. Bulk download is accepted only for taxa lacking an ID-bound ZIP.

Input artifacts are produced by audit_wu2022_tpia_backbone_assets.py.
"""
from __future__ import annotations
import argparse,csv,json
from pathlib import Path
from collections import defaultdict


def read(p):
    with open(p,newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))

def write(p,rows):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--run-taxa',type=Path,required=True)
    ap.add_argument('--allassemblies',type=Path,required=True)
    ap.add_argument('--bulk',type=Path,required=True)
    ap.add_argument('--aliases',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--summary',type=Path,required=True)
    a=ap.parse_args()

    source=sorted({r['normalized_taxon'] for r in read(a.run_taxa) if r.get('normalized_taxon')})
    alias={r['source_archive_taxon']:(r['tpia_resource_taxon'],r['match_basis']) for r in read(a.aliases)}
    byall=defaultdict(list)
    for r in read(a.allassemblies):
        if r.get('normalized_taxon'): byall[r['normalized_taxon']].append(r)
    bybulk=defaultdict(list)
    for r in read(a.bulk):
        if r.get('normalized_taxon') and r.get('is_transcriptome_assembly')=='True':
            bybulk[r['normalized_taxon']].append(r)

    rows=[]; unresolved=[]
    for tax in source:
        query,basis=alias.get(tax,(tax,'exact_archive_tpia_species_name'))
        direct=[r for r in byall.get(query,[]) if r.get('assembly_zip_url')]
        direct=sorted(direct,key=lambda r:(0 if r.get('sourceData')=='PRJNA665925' else 1,r.get('ID','')))
        bulk=sorted(bybulk.get(query,[]),key=lambda r:(0 if r.get('sourceData')=='PRJNA665925' else 1,r.get('no','')))
        if direct:
            r=direct[0]
            source_type='tpia_id_bound_allassemblies'
            file=f"{r.get('ID')}_{r.get('name')}.zip"
            url=r['assembly_zip_url']
            source_data=r.get('sourceData','')
            advertised=''
            risk='preferred_id_bound_url'
        elif bulk:
            r=bulk[0]
            source_type='tpia_bulk_fallback'
            file=r.get('fileName','')
            url=r.get('bulk_download_url','')
            source_data=r.get('sourceData','')
            advertised=r.get('size','')
            risk='bulk_fallback_requires_payload_identity_audit'
        else:
            unresolved.append(tax);continue
        rows.append({
            'source_taxon':tax,'resource_taxon':query,'match_basis':basis,
            'assembly_source':source_type,'assembly_file':file,
            'source_data':source_data,'advertised_size':advertised,
            'assembly_url':url,'payload_identity_risk':risk,
            'analysis_role':'species_level_nuclear_backbone_input',
            'claim_ceiling':'one assembly per PRJNA665925 species-level taxon; not exact reconstruction of all 116 Wu paper tips'
        })
    if unresolved: raise SystemExit(f'unresolved source taxa: {unresolved}')
    write(a.output,rows)
    summary={
        'source_species_level_taxa':len(source),
        'manifest_rows':len(rows),
        'id_bound_allassemblies':sum(r['assembly_source']=='tpia_id_bound_allassemblies' for r in rows),
        'bulk_fallback':sum(r['assembly_source']=='tpia_bulk_fallback' for r in rows),
        'coverage_fraction':len(rows)/len(source),
        'bulk_fallback_taxa':[r['source_taxon'] for r in rows if r['assembly_source']=='tpia_bulk_fallback'],
        'decision':'ID-bound All_assemblies is primary; bulk is fallback only after bulk endpoint payload collision was observed in diagnostic download',
        'claim_ceiling':'resource-provenance manifest only; payload checksums/sequence identity still required before tree reconstruction'
    }
    a.summary.parent.mkdir(parents=True,exist_ok=True);a.summary.write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
