#!/usr/bin/env python3
"""Recover source accession assignments, then admit by sequence metadata, not table position."""
from __future__ import annotations
import argparse,collections,csv,hashlib,json,re,time,urllib.request,urllib.parse,xml.etree.ElementTree as ET
from pathlib import Path
import fitz
GENERA={'Hugonia','Anisadenia','Cliococca','Hesperolinon','Radiola','Reinwardtia','Sclerolinon','Tirpitzia','Linum'}
GENES=('ndhF','matK','trnLF','ITS')
def write_csv(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def clean(s):return re.sub(r'\s+',' ',s.replace('*','')).strip().lower()
def taxon_key(genus,species):
    t=clean(genus+' '+species);t=re.sub(r' [ab]$','',t)
    return t.replace(' subsp. ',' ').replace(' subsp ',' ').replace('flos carmini','flos-carmini')
def parse_source(path):
    d=fitz.open(path);rows=[]
    for pg in range(4):
        words=d[pg].get_text('words')
        anchors=sorted((y,x,t) for x,y,x1,y1,t,*_ in words if 45<x<110 and t in GENERA)
        for index,(y,x,genus) in enumerate(anchors):
            next_y=anchors[index+1][0] if index+1<len(anchors) else y+17
            selected=sorted([(round(yy,1),xx,t) for xx,yy,_,_,t,*_ in words if y-2<=yy<min(next_y-2,y+32) and 45<=xx<560])
            col=lambda a,b:' '.join(t for yy,xx,t in selected if a<=xx<b)
            r=dict(source_row=len(rows)+1,source_page=pg+1,source_y=round(y,3),genus=genus,species=col(115,208),section=col(208,290),ndhF=col(290,360),matK=col(360,426),trnLF=col(426,490),ITS=col(490,560))
            r['tip_id']=f'LINO{len(rows)+1:03d}';r['source_taxon']=clean(genus+' '+r['species']);r['taxon_key']=taxon_key(genus,r['species']);rows.append(r)
    if len(rows)!=121 or rows[0]['genus']!='Hugonia':raise ValueError('unexpected source-table shape')
    if len({r['source_taxon'] for r in rows})!=121:raise ValueError('duplicate source name')
    if rows[63]['species']!='hirsutum subsp. spathulatum':raise ValueError(f'multiline taxon check: {rows[63]}')
    return rows

def get(url):
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'CHUN-public-sequence-audit/0.2'}),timeout=75) as r:data=r.read(30000000)
            return data
        except Exception:
            if attempt==3:raise
            time.sleep(2**(attempt+1))

def genes_in_record(rec):
    features=rec.findall('.//GBFeature');quals=[]
    for f in features:
        for q in f.findall('.//GBQualifier'):
            if q.findtext('GBQualifier_name') in ('gene','product','note'):quals.append(q.findtext('GBQualifier_value',''))
    text=' '.join([rec.findtext('GBSeq_definition','')]+quals).lower();found=[]
    if re.search(r'\bndhf\b|nadh.dehydrogenase subunit f',text):found.append('ndhF')
    if re.search(r'\bmatk\b|maturase k',text):found.append('matK')
    if re.search(r'\btrnl\b|\btrnf\b|trnl.?trnf|trnl-f',text):found.append('trnLF')
    if re.search(r'internal transcribed spacer|\bits[12]?\b',text):found.append('ITS')
    return found,text

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source-dir',type=Path,required=True);ap.add_argument('--out-dir',type=Path,required=True);ap.add_argument('--parse-only',action='store_true');a=ap.parse_args()
    a.out_dir.mkdir(parents=True,exist_ok=True)
    rows=parse_source(a.source_dir/'files/plants-11-01579-s001/Supplementary material.pdf');write_csv(a.out_dir/'source_accessions.csv',rows)
    accs=sorted({r[g] for r in rows for g in GENES if re.fullmatch('[A-Z]{2}[0-9]{6}',r[g])})
    if a.parse_only:print(json.dumps({'rows':len(rows),'unique_valid_accessions':len(accs),'taxon_units':len(set(r['taxon_key'] for r in rows))}));return
    cache=a.out_dir/'genbank_xml';cache.mkdir(exist_ok=True);records={};rawhashes={}
    for i in range(0,len(accs),40):
        dest=cache/f'batch_{i//40:02d}.xml'
        if not dest.exists():
            url='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?'+urllib.parse.urlencode({'db':'nuccore','id':','.join(accs[i:i+40]),'rettype':'gb','retmode':'xml','tool':'chun_linoideae'})
            data=get(url);ET.fromstring(data);dest.write_bytes(data);time.sleep(0.5)
        data=dest.read_bytes();root=ET.fromstring(data);rawhashes[dest.name]=hashlib.sha256(data).hexdigest()
        for rec in root.findall('.//GBSeq'):
            acc=rec.findtext('GBSeq_primary-accession');records[acc]=rec
    absent=sorted(set(accs)-set(records))
    if absent:raise ValueError(f'missing requested records: {absent}')
    audits=[];admitted=collections.defaultdict(dict)
    for r in rows:
        for source_gene in GENES:
            acc=r[source_gene];rec=records.get(acc)
            audit={'tip_id':r['tip_id'],'source_taxon':r['source_taxon'],'source_gene':source_gene,'accession':acc,'accession_version':'','record_organism':'','record_definition':'','record_gene':'','sequence_length':0,'status':'SOURCE_MISSING'}
            if acc and rec is None:audit['status']='INVALID_SOURCE_ACCESSION'
            if rec is not None:
                actual_genes,text=genes_in_record(rec);seq=rec.findtext('GBSeq_sequence','').upper();org=rec.findtext('GBSeq_organism','')
                audit.update(accession_version=rec.findtext('GBSeq_accession-version'),record_organism=org,record_definition=rec.findtext('GBSeq_definition'),record_gene='|'.join(actual_genes),sequence_length=len(seq))
                want=r['taxon_key'];got=clean(org).replace(' subsp. ',' ').replace(' subsp ',' ')
                if got!=want:audit['status']='TAXON_MISMATCH_HELD'
                elif len(actual_genes)!=1:audit['status']='GENE_UNRESOLVED_HELD'
                elif not seq or re.search('[^ACGTRYSWKMBDHVN]',seq):audit['status']='INVALID_SEQUENCE_HELD'
                elif len(seq)>12000:audit['status']='LONG_RECORD_HELD'
                else:
                    g=actual_genes[0];audit['status']='EXACT_SOURCE_MATCH' if g==source_gene else 'SOURCE_COLUMN_REASSIGNED_BY_RECORD'
                    old=admitted[g].get(r['tip_id'])
                    if old is not None and old['sequence']!=seq:raise ValueError(f'duplicate gene assignments for {r["tip_id"]}:{g}')
                    admitted[g][r['tip_id']]={'sequence':seq,'accession_version':audit['accession_version'],'status':audit['status']}
            audits.append(audit)
    write_csv(a.out_dir/'sequence_assignment_audit.csv',audits)
    for g in GENES:
        path=a.out_dir/f'{g}.fasta';path.write_text(''.join(f'>{tip}\n{v["sequence"]}\n' for tip,v in sorted(admitted[g].items())))
    summary={'source_rows':len(rows),'source_ingroup_rows':sum(r['genus']!='Hugonia' for r in rows),'source_unique_taxon_units':len(set(r['taxon_key'] for r in rows)),'valid_unique_accessions':len(accs),'records_recovered':len(records),'status_counts':dict(collections.Counter(r['status'] for r in audits)),'admitted_per_locus':{g:len(v) for g,v in admitted.items()},'admitted_tips':len(set().union(*(set(v) for v in admitted.values()))),'raw_xml_sha256':rawhashes,'claim_boundary':'Metadata-validated public source reconstruction; not an author alignment or accepted-species tree.'}
    (a.out_dir/'sequence_manifest.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
