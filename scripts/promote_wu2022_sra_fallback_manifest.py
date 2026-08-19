#!/usr/bin/env python3
"""Replace unavailable Wu2022 TPIA bulk fallbacks with frozen NCBI SRA runs.

This is a provenance correction. It does not assemble reads or reconstruct a tree.
"""
from __future__ import annotations
import argparse,csv,json
from pathlib import Path


def read(path):
    with open(path,newline='',encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def write(path,rows,fields):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n',extrasaction='ignore')
        w.writeheader(); w.writerows(rows)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--manifest-v01',type=Path,required=True)
    ap.add_argument('--run-taxa',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--summary',type=Path,required=True)
    a=ap.parse_args()

    rows=read(a.manifest_v01)
    runs=read(a.run_taxa)
    bytax={}
    for r in runs:
        tax=r.get('normalized_taxon','')
        run=r.get('Run','')
        if tax and run:
            bytax.setdefault(tax,[]).append(r)

    corrected=[]
    replaced=[]
    for row in rows:
        row=dict(row)
        if row.get('assembly_source')=='tpia_bulk_fallback':
            tax=row['source_taxon']
            candidates=bytax.get(tax,[])
            if not candidates:
                raise SystemExit(f'no frozen PRJNA665925 RunInfo row for {tax}')
            # These species have one run each in the frozen species-level table.
            chosen=sorted(candidates,key=lambda r:r['Run'])[0]
            row.update({
                'assembly_source':'ncbi_sra_raw_fallback',
                'assembly_file':chosen['Run'],
                'source_data':chosen.get('BioProject','PRJNA665925'),
                'advertised_size':'',
                'assembly_url':f"https://www.ncbi.nlm.nih.gov/sra/{chosen['Run']}",
                'payload_identity_risk':'raw_sra_run_requires_transcriptome_assembly_before_backbone_use',
                'analysis_role':'species_level_nuclear_backbone_raw_read_fallback',
                'claim_ceiling':'frozen NCBI SRA run provenance only; de novo transcriptome assembly and locus recovery required before topology reconstruction',
            })
            replaced.append({
                'source_taxon':tax,
                'run':chosen['Run'],
                'biosample':chosen.get('BioSample',''),
                'bioproject':chosen.get('BioProject',''),
                'library_strategy':chosen.get('LibraryStrategy',''),
            })
        corrected.append(row)

    expected={
        'Camellia lipoensis':'SRR19266662',
        'Camellia campanisepala':'SRR19266763',
        'Camellia salicifolia':'SRR19266758',
    }
    observed={r['source_taxon']:r['run'] for r in replaced}
    if observed!=expected:
        raise SystemExit(f'unexpected raw fallback mapping: {observed}')

    fields=list(corrected[0])
    write(a.output,corrected,fields)
    summary={
        'analysis_version':'v0.2',
        'manifest_rows':len(corrected),
        'tpia_id_bound_assemblies':sum(r['assembly_source']=='tpia_id_bound_allassemblies' for r in corrected),
        'ncbi_sra_raw_fallbacks':sum(r['assembly_source']=='ncbi_sra_raw_fallback' for r in corrected),
        'tpia_bulk_fallbacks_remaining':sum(r['assembly_source']=='tpia_bulk_fallback' for r in corrected),
        'raw_fallbacks':replaced,
        'decision':'retire unavailable TPIA bulk fallback URLs and use the frozen PRJNA665925 SRA runs for the three affected taxa',
        'claim_ceiling':'resource provenance only; the three raw-read fallbacks must be assembled and passed through the same locus-recovery pipeline before inclusion in the nuclear topology',
    }
    a.summary.parent.mkdir(parents=True,exist_ok=True)
    a.summary.write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    main()
