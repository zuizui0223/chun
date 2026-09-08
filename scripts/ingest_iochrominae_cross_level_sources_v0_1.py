#!/usr/bin/env python3
"""Acquire three public Dryad datasets needed for an Iochrominae cross-level bridge.

Source acquisition only: no colour recoding, mechanistic alignment or evolutionary
claim is made here. Public Dryad DOI endpoints are resolved through API v2 and
all downloaded bytes/member hashes are preserved.
"""
from __future__ import annotations
import argparse,hashlib,json,urllib.parse,urllib.request,zipfile
from pathlib import Path

DATASETS={
 'TEMPO_MODE':('10.5061/dryad.0732g','Tempo and mode of flower color evolution'),
 'SPECTRAL_COLOUR':('10.5061/dryad.36v4b','Competition for hummingbird pollination shapes flower color variation'),
 'DEVELOPMENT_EXPRESSION':('10.5061/dryad.p5dq84v','Developmental control of convergent floral pigmentation across evolutionary timescales'),
}
UA='chun-iochrominae-cross-level-source-audit/0.1'

def get(url:str)->tuple[bytes,str,dict]:
    req=urllib.request.Request(url,headers={'User-Agent':UA,'Accept':'application/json,application/zip,*/*'})
    with urllib.request.urlopen(req,timeout=120) as r:
        return r.read(),r.geturl(),dict(r.headers)

def safe_extract(zpath:Path,dest:Path):
    dest.mkdir(parents=True,exist_ok=True);members=[]
    with zipfile.ZipFile(zpath) as z:
        for info in z.infolist():
            if info.is_dir(): continue
            target=(dest/info.filename).resolve()
            if not target.is_relative_to(dest.resolve()): raise ValueError('unsafe zip member '+info.filename)
            raw=z.read(info.filename);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
            members.append({'name':info.filename,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'suffix':target.suffix.lower()})
    return members

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out-dir',type=Path,required=True);a=ap.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
    results=[]
    for key,(doi,title) in DATASETS.items():
        encoded=urllib.parse.quote('doi:'+doi,safe='')
        api=f'https://datadryad.org/api/v2/datasets/{encoded}'
        raw,meta_resolved,_=get(api);meta=json.loads(raw)
        identifier=str(meta.get('identifier','')).lower()
        if doi.lower() not in identifier: raise ValueError(f'{key}: DOI identity mismatch {identifier!r}')
        ddir=a.out_dir/key.lower();ddir.mkdir(parents=True,exist_ok=True)
        (ddir/'dataset_metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
        bundle,bundle_resolved,headers=get(api+'/download')
        zpath=ddir/'dryad_dataset.zip';zpath.write_bytes(bundle)
        if not zipfile.is_zipfile(zpath): raise ValueError(f'{key}: Dryad /download did not return ZIP ({len(bundle)} bytes; {bundle_resolved})')
        members=safe_extract(zpath,ddir/'extracted')
        suffix_counts={}
        for m in members:suffix_counts[m['suffix']]=suffix_counts.get(m['suffix'],0)+1
        result={
          'dataset_id':key,'doi':doi,'title_expected':title,'identifier':meta.get('identifier'),
          'api_requested':api,'metadata_resolved':meta_resolved,'download_resolved':bundle_resolved,
          'license':meta.get('license'),'versionNumber':meta.get('versionNumber'),
          'storageSize':meta.get('storageSize'),'bundle_bytes':len(bundle),
          'bundle_sha256':hashlib.sha256(bundle).hexdigest(),'member_count':len(members),
          'suffix_counts':suffix_counts,'members':members}
        (ddir/'source_manifest.json').write_text(json.dumps(result,indent=2)+'\n')
        results.append(result)
    summary={
      'version':'v0.1','datasets':results,
      'all_three_acquired':len(results)==3,
      'analysis_status':'SOURCE_BYTES_ACQUIRED_NOT_YET_TRAIT_MECHANISM_JOINED',
      'claim_boundary':'Acquisition/inventory only. No taxon overlap, phenotype hierarchy, molecular recurrence or causal alignment is inferred.',
      'paper1_science_changed':False}
    (a.out_dir/'source_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps([{k:r[k] for k in ('dataset_id','doi','bundle_bytes','bundle_sha256','member_count','suffix_counts')} for r in results],indent=2))
if __name__=='__main__':main()
