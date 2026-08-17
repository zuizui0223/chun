#!/usr/bin/env python3
"""Map public CSNG qRT-PCR primers to predeclared TPIA2 candidate loci.

Candidate panels are frozen independently of the mapping result. The script
queries CDS, transcript/genomic-transcript and exon exports. Exact or near
paired amplicon matches are scored on CDS/exon sequence; transcript sequence is
also searched for individual primer support because introns can inflate the
apparent genomic product length.

Primer compatibility can narrow a de novo transcript mapping. It is not
full-length orthology evidence.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,re,zipfile
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlencode
import requests

ENDPOINT='https://tpia.teaplants.cn/getGeneSeqByGeneNames'
SEQ_PARAMS={'cds':{'cds':1,'trans':0,'exon':0},'transcript':{'cds':0,'trans':1,'exon':0},'exon':{'cds':0,'trans':0,'exon':1}}

def rc(s:str)->str:
    return s.translate(str.maketrans('ACGTNacgtn','TGCANtgcan'))[::-1]
def sha256(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def parse_fasta(text:str):
    out={};h=None;seq=[]
    for raw in text.splitlines():
        line=raw.strip()
        if not line:continue
        if line.startswith('>'):
            if h is not None:out[h.split('\t')[0].split()[0]]=''.join(seq).upper()
            h=line[1:].strip();seq=[]
        elif h is not None:seq.append(re.sub(r'\s+','',line))
    if h is not None:out[h.split('\t')[0].split()[0]]=''.join(seq).upper()
    return out

def fetch_sequences(session,tea_type,ids,seq_type):
    flags=SEQ_PARAMS[seq_type];params={'geneNames':','.join(ids),**flags,'down':0,'up':0,'teaType':tea_type}
    r=session.get(ENDPOINT+'?'+urlencode(params),timeout=120);r.raise_for_status();raw=r.content
    if not raw.startswith(b'PK\x03\x04'):raise RuntimeError(f'expected TPIA ZIP for {tea_type}/{seq_type}')
    seq={}
    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        for n in zf.namelist():
            if n.lower().endswith('.txt'):seq.update(parse_fasta(zf.read(n).decode('utf-8',errors='replace')))
    return seq,{'tea_type':tea_type,'sequence_type':seq_type,'requested_ids':ids,'response_bytes':len(raw),'response_sha256':sha256(raw),'n_sequences':len(seq)}

def best_window(seq,primer):
    L=len(primer);best=None
    for i in range(max(0,len(seq)-L+1)):
        w=seq[i:i+L];m=sum(a!=b for a,b in zip(w,primer))
        cand=(m,i,w)
        if best is None or cand<best:best=cand
    return best

def paired(seq,fwd,rev,expected,max_mis=3,max_product=1000):
    revrc=rc(rev);fh=[];rh=[]
    for primer,target in [(fwd,fh),(revrc,rh)]:
        L=len(primer)
        for i in range(max(0,len(seq)-L+1)):
            w=seq[i:i+L];m=sum(a!=b for a,b in zip(w,primer))
            if m<=max_mis:target.append((m,i,w))
    pairs=[]
    for fm,fp,fw in fh:
        for rm,rp,rw in rh:
            if rp<fp:continue
            prod=rp+len(revrc)-fp
            if 0<prod<=max_product:pairs.append((fm+rm,abs(prod-expected),fm,rm,fp,rp,prod,fw,rw))
    if not pairs:return None
    p=min(pairs);return {'total_mismatches':p[0],'product_deviation':p[1],'forward_mismatches':p[2],'reverse_mismatches':p[3],'forward_start':p[4],'reverse_start':p[5],'product_bp':p[6]}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--primers',type=Path,required=True);ap.add_argument('--candidates',type=Path,required=True);ap.add_argument('--out-dir',type=Path,required=True);a=ap.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
    with a.primers.open(newline='',encoding='utf-8') as f:prim={r['source_unigene']:r for r in csv.DictReader(f)}
    with a.candidates.open(newline='',encoding='utf-8') as f:cands=list(csv.DictReader(f))
    bytype=defaultdict(list)
    for r in cands:bytype[r['tpia_type']].append(r['candidate_id'])
    s=requests.Session();s.headers['User-Agent']='chun-camellia-orthology/0.2 (public primer-to-TPIA audit)'
    seq={};fetch=[]
    for typ,ids in bytype.items():
        for st in SEQ_PARAMS:
            q,meta=fetch_sequences(s,typ,ids,st);fetch.append(meta)
            for gid,ss in q.items():seq[(typ,st,gid)]=ss
    out=[]
    for c in cands:
        p=prim[c['source_unigene']];gid=c['candidate_id'];fwd=p['forward_primer'].upper();rev=p['reverse_primer'].upper();expected=int(p['reported_product_bp'])
        row={**c}
        decisive=[]
        for st in SEQ_PARAMS:
            ss=seq.get((c['tpia_type'],st,gid),'');row[f'{st}_bp']=len(ss);row[f'{st}_sha256']=sha256(ss.encode()) if ss else ''
            if not ss:
                row[f'{st}_forward_best_mismatch']='';row[f'{st}_reverse_best_mismatch']='';row[f'{st}_paired']='';continue
            fw=best_window(ss,fwd);rw=best_window(ss,rc(rev));row[f'{st}_forward_best_mismatch']=fw[0] if fw else '';row[f'{st}_reverse_best_mismatch']=rw[0] if rw else ''
            pr=paired(ss,fwd,rev,expected,max_mis=3,max_product=5000)
            if pr:
                row[f'{st}_paired']=json.dumps(pr,sort_keys=True)
                if pr['total_mismatches']<=2 and ((st in {'cds','exon'} and pr['product_deviation']<=10) or st=='transcript'):decisive.append((st,pr))
            else:row[f'{st}_paired']=''
        row['decisive_layers']=';'.join(st for st,_ in decisive)
        row['mapping_decision']='amplicon_compatible_candidate' if decisive else 'no_decisive_match_across_cds_transcript_exon'
        row['claim_boundary']='primer compatibility is locus support only; full-length de novo transcript sequence is required for strict ortholog assignment'
        out.append(row)
    # Rank by best combined individual-primer mismatch across all layers, then decisive status.
    for u in prim:
        rr=[r for r in out if r['source_unigene']==u]
        def key(r):
            vals=[]
            for st in SEQ_PARAMS:
                try:vals.append(int(r[f'{st}_forward_best_mismatch'])+int(r[f'{st}_reverse_best_mismatch']))
                except Exception:pass
            return (0 if r['mapping_decision']=='amplicon_compatible_candidate' else 1,min(vals) if vals else 999,r['candidate_id'])
        rr.sort(key=key)
        for rank,r in enumerate(rr,1):r['within_unigene_rank']=rank
    fields=list(out[0].keys())
    with (a.out_dir/'primer_candidate_mapping.csv').open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(out)
    summary={}
    for u in prim:
        rr=sorted([r for r in out if r['source_unigene']==u],key=lambda r:r['within_unigene_rank']);dec=[r for r in rr if r['mapping_decision']=='amplicon_compatible_candidate'];best=rr[0]
        summary[u]={'candidate_count':len(rr),'amplicon_compatible_candidates':[r['candidate_id'] for r in dec],'best_candidate_by_primer_distance':best['candidate_id'],'best_class':best['candidate_class'],'decision':'unique_amplicon_candidate' if len(dec)==1 else ('multiple_amplicon_candidates' if len(dec)>1 else 'no_decisive_candidate_across_three_sequence_layers')}
    meta={'endpoint':ENDPOINT,'fetches':fetch,'unigene_results':summary,'claim_ceiling':'absence of primer compatibility across the predeclared CDS/transcript/exon panel rejects only a simple mapping to those candidates; it does not prove the de novo unigene is a novel gene'}
    (a.out_dir/'summary.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8');print(json.dumps(meta,indent=2))
if __name__=='__main__':main()
