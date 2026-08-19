#!/usr/bin/env python3
"""Build the currently runnable assembled Angiosperms353 backbone panel from the frozen Wu v0.3 manifest.

The frozen v0.3 manifest remains the provenance authority. Runtime exclusions
record TPIA ID-bound URLs that were live when frozen but are no longer retrievable.
Those taxa are held out rather than silently dropped or reclassified in-place.
"""
from __future__ import annotations
import argparse,csv,json,re
from pathlib import Path

OUT_FIELDS=["taxon","colour_state","section","tpia_id","tpia_resource_name","assembly_url","panel_role","admission_status","provenance_note"]

def parse_tpia_id(assembly_file:str)->str:
    m=re.match(r"^(\d+)_",assembly_file or "")
    if not m: raise ValueError(f"cannot parse TPIA id from assembly_file={assembly_file!r}")
    return m.group(1)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--manifest',type=Path,required=True)
    ap.add_argument('--runtime-exclusions',type=Path)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--summary',type=Path,required=True)
    ap.add_argument('--expected-total',type=int,default=98)
    ap.add_argument('--expected-frozen-assembled',type=int,default=93)
    ap.add_argument('--expected-frozen-raw',type=int,default=5)
    ap.add_argument('--expected-runtime-assembled',type=int,default=91)
    args=ap.parse_args()

    manifest=list(csv.DictReader(args.manifest.open(newline='',encoding='utf-8-sig')))
    assembled=[r for r in manifest if r['assembly_source']=='tpia_id_bound_allassemblies']
    raw=[r for r in manifest if r['assembly_source']=='ncbi_sra_raw_fallback']
    other=[r for r in manifest if r['assembly_source'] not in {'tpia_id_bound_allassemblies','ncbi_sra_raw_fallback'}]
    assert len(manifest)==args.expected_total
    assert len(assembled)==args.expected_frozen_assembled
    assert len(raw)==args.expected_frozen_raw
    assert not other

    excluded={}
    if args.runtime_exclusions:
        rows=list(csv.DictReader(args.runtime_exclusions.open(newline='',encoding='utf-8-sig')))
        excluded={r['source_taxon']:r for r in rows}
        missing=sorted(set(excluded)-{r['source_taxon'] for r in assembled})
        assert not missing, missing
    runnable=[r for r in assembled if r['source_taxon'] not in excluded]
    assert len(runnable)==args.expected_runtime_assembled, (len(runnable),args.expected_runtime_assembled)
    assert len({r['source_taxon'] for r in runnable})==len(runnable)
    assert len({r['assembly_url'] for r in runnable})==len(runnable)

    panel=[]
    for r in sorted(runnable,key=lambda x:x['source_taxon']):
        panel.append({'taxon':r['source_taxon'],'colour_state':'U','section':'unknown','tpia_id':parse_tpia_id(r['assembly_file']),'tpia_resource_name':r['resource_taxon'],'assembly_url':r['assembly_url'],'panel_role':'genus_nuclear_backbone','admission_status':'admit','provenance_note':f"v0.3:{r['match_basis']}"})
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=OUT_FIELDS);w.writeheader();w.writerows(panel)
    held=sorted([r['source_taxon'] for r in raw]+list(excluded))
    summary={'manifest':str(args.manifest),'n_manifest_taxa':len(manifest),'n_frozen_tpia_assembled':len(assembled),'n_frozen_raw':len(raw),'n_runtime_tpia_excluded':len(excluded),'runtime_exclusions':excluded,'n_runtime_assembled_admitted':len(panel),'n_total_held_out':len(held),'held_out_taxa':held,'claim_ceiling':'91 currently retrievable provenance-admitted TPIA assemblies; seven taxa held out pending raw transcript/locus recovery or restored ID-bound resources'}
    args.summary.parent.mkdir(parents=True,exist_ok=True);args.summary.write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))
if __name__=='__main__': main()
