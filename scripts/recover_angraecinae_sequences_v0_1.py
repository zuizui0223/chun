#!/usr/bin/env python3
"""Recover the author-mapped public GenBank sequences for the Angraecinae source rows.

Table S1 is the primary accession-to-sample mapping. GenBank organism metadata are audited
and preserved but are not used to silently rename or reassign source samples.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,re,time,urllib.parse,urllib.request,xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

LOCI=(('matK',4),('rps16',5),('trnL',6),('ITS',7))
ACC=re.compile(r'\b[A-Z]{1,2}\d{5,8}\b')
OUTGROUPS={'Acampe ochracea','Aerides odorata','Phalaenopsis cornu-cervi','Vanda tricolor','Polystachya fulvilabia'}

def norm(s):return re.sub(r'\s+',' ',s.strip())
def get(url):
    for attempt in range(4):
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'CHUN-Angraecinae-public-sequence-audit/0.1'})
            with urllib.request.urlopen(req,timeout=90) as r:return r.read(40_000_000)
        except Exception:
            if attempt==3:raise
            time.sleep(2**(attempt+1))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source-dir',type=Path,required=True);ap.add_argument('--trait-csv',type=Path,required=True);ap.add_argument('--out-dir',type=Path,required=True);a=ap.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
    s1=a.source_dir/'files/pone.0163194.s007.csv'
    raw=list(csv.reader(s1.read_text(encoding='latin-1').splitlines(),delimiter=';'))[2:]
    source=[]
    for r in raw:
        found={g:(ACC.findall(r[i]) if i<len(r) else []) for g,i in LOCI}
        if not any(found.values()):continue
        if any(len(v)>1 for v in found.values()):raise ValueError(f'multiple GenBank accessions in one source cell: {r[0]}')
        source.append((r,found))
    if len(source)!=194:raise ValueError(f'expected 194 source sample rows, got {len(source)}')
    traits=list(csv.DictReader(a.trait_csv.open()))
    trait_names={r['source_taxon'] for r in traits};source_names=Counter(norm(r[0]) for r,_ in source)
    rows=[];all_acc=set()
    for i,(r,found) in enumerate(source,1):
        taxon=norm(r[0]);tip=f'ANG{i:03d}';join='EXACT_UNIQUE' if source_names[taxon]==1 and taxon in trait_names else ('DUPLICATE_SOURCE_NAME_HELD' if source_names[taxon]>1 else 'NO_EXACT_TRAIT_NAME_HELD')
        out={'tip_id':tip,'source_row':i,'source_taxon':taxon,'source_group':'OUTGROUP' if taxon in OUTGROUPS else 'ANGRAECINAE','trait_join_status':join}
        for g,_ in LOCI:
            acc=found[g][0] if found[g] else ''
            out[g+'_accession']=acc
            if acc:all_acc.add(acc)
        rows.append(out)
    cache=a.out_dir/'genbank_xml';cache.mkdir(exist_ok=True);records={};hashes={}
    accs=sorted(all_acc)
    for start in range(0,len(accs),40):
        batch=accs[start:start+40];dest=cache/f'batch_{start//40:02d}.xml'
        if not dest.exists():
            url='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?'+urllib.parse.urlencode({'db':'nuccore','id':','.join(batch),'rettype':'gb','retmode':'xml','tool':'chun_angraecinae'})
            data=get(url);ET.fromstring(data);dest.write_bytes(data);time.sleep(.5)
        data=dest.read_bytes();hashes[dest.name]=hashlib.sha256(data).hexdigest();root=ET.fromstring(data)
        for rec in root.findall('.//GBSeq'):
            records[rec.findtext('GBSeq_primary-accession')]=rec
    audits=[];seqs={g:{} for g,_ in LOCI}
    for r in rows:
        for g,_ in LOCI:
            acc=r[g+'_accession'];audit={'tip_id':r['tip_id'],'source_taxon':r['source_taxon'],'locus':g,'source_accession':acc,'accession_version':'','record_organism':'','sequence_length':0,'status':'SOURCE_MISSING'}
            if acc:
                rec=records.get(acc)
                if rec is None:audit['status']='GENBANK_RECORD_NOT_RECOVERED_HELD'
                else:
                    seq=rec.findtext('GBSeq_sequence','').upper();org=norm(rec.findtext('GBSeq_organism',''))
                    audit.update(accession_version=rec.findtext('GBSeq_accession-version',''),record_organism=org,sequence_length=len(seq))
                    if not seq or re.search('[^ACGTRYSWKMBDHVN]',seq) or len(seq)>12000:audit['status']='INVALID_SEQUENCE_HELD'
                    else:
                        audit['status']='SOURCE_ASSIGNED_SEQUENCE_ADMITTED'
                        seqs[g][r['tip_id']]=seq
            audits.append(audit)
    fields=list(rows[0]);
    with (a.out_dir/'source_sample_manifest.csv').open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    af=list(audits[0]);
    with (a.out_dir/'sequence_audit.csv').open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=af);w.writeheader();w.writerows(audits)
    for g in seqs:(a.out_dir/f'{g}.fasta').write_text(''.join(f'>{tip}\n{s}\n' for tip,s in sorted(seqs[g].items())))
    summary={'version':'v0.1','source_sample_rows':len(rows),'exact_unique_trait_joins':sum(r['trait_join_status']=='EXACT_UNIQUE' for r in rows),'held_trait_joins':[{k:r[k] for k in ('tip_id','source_taxon','trait_join_status')} for r in rows if r['trait_join_status']!='EXACT_UNIQUE'],'unique_genbank_accessions_requested':len(accs),'genbank_records_recovered':len(records),'sequence_status_counts':dict(Counter(x['status'] for x in audits)),'admitted_per_locus':{g:len(v) for g,v in seqs.items()},'tips_with_any_sequence':len(set().union(*(set(v) for v in seqs.values()))),'outgroup_tips':[r['tip_id'] for r in rows if r['source_group']=='OUTGROUP'],'raw_xml_sha256':hashes,'claim_boundary':'Source S1 mapping is primary. GenBank organism labels are audit metadata; no source taxon is silently renamed from GenBank. Trait-name mismatches remain held.'}
    (a.out_dir/'sequence_manifest.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
