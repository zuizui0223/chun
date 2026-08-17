#!/usr/bin/env python3
"""Map public CSNG qRT-PCR primer pairs to predeclared TPIA2 candidate CDSs.

Candidate panels are frozen independently of the mapping result. The script
fetches candidate CDS sequences from the public TPIA2 Batch Retrieve endpoint,
then scores the published forward primer and reverse-complement of the reverse
primer against each CDS. Exact paired matches are preferred; if none exist,
best <=2-mismatch windows are reported with amplicon-length deviation.

A primer match can crosswalk a de novo transcript to a candidate locus/family;
it does not prove that all sequence outside the amplicon is identical.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,re,zipfile
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlencode
import requests

ENDPOINT='https://tpia.teaplants.cn/getGeneSeqByGeneNames'

def rc(s:str)->str:
    tab=str.maketrans('ACGTNacgtn','TGCANtgcan')
    return s.translate(tab)[::-1]

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

def fetch_cds(session,tea_type,ids):
    params={'geneNames':','.join(ids),'cds':1,'trans':0,'exon':0,'down':0,'up':0,'teaType':tea_type}
    r=session.get(ENDPOINT+'?'+urlencode(params),timeout=120);r.raise_for_status();raw=r.content
    if not raw.startswith(b'PK\x03\x04'):raise RuntimeError(f'expected TPIA ZIP for {tea_type}, got {r.headers.get("content-type")}')
    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        texts=[]
        for n in zf.namelist():
            if n.lower().endswith('.txt'):texts.append(zf.read(n).decode('utf-8',errors='replace'))
    seq={}
    for t in texts:seq.update(parse_fasta(t))
    return seq,{'tea_type':tea_type,'requested_ids':ids,'response_bytes':len(raw),'response_sha256':sha256(raw),'n_sequences':len(seq),'content_disposition':r.headers.get('content-disposition','')}

def windows(seq,primer,max_mis=2):
    L=len(primer);hits=[]
    for i in range(0,len(seq)-L+1):
        w=seq[i:i+L];m=sum(a!=b for a,b in zip(w,primer))
        if m<=max_mis:hits.append((m,i,w))
    return sorted(hits)

def best_pair(seq,fwd,rev,expected):
    revrc=rc(rev)
    fh=windows(seq,fwd,2);rh=windows(seq,revrc,2);pairs=[]
    for fm,fp,fw in fh:
        for rm,rp,rw in rh:
            if rp < fp:continue
            product=(rp+len(revrc))-fp
            if product<=0 or product>1000:continue
            pairs.append((fm+rm,abs(product-expected),fm,rm,fp,rp,product,fw,rw))
    if not pairs:
        return {'paired_hit':False,'forward_best_mismatch':fh[0][0] if fh else '', 'reverse_best_mismatch':rh[0][0] if rh else ''}
    p=min(pairs)
    return {'paired_hit':True,'total_primer_mismatches':p[0],'product_length_deviation':p[1],'forward_mismatches':p[2],'reverse_mismatches':p[3],'forward_start_0based':p[4],'reverse_rc_start_0based':p[5],'predicted_product_bp':p[6],'forward_matched_window':p[7],'reverse_rc_matched_window':p[8]}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--primers',type=Path,required=True);ap.add_argument('--candidates',type=Path,required=True);ap.add_argument('--out-dir',type=Path,required=True);a=ap.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
    with a.primers.open(newline='',encoding='utf-8') as f:prim={r['source_unigene']:r for r in csv.DictReader(f)}
    with a.candidates.open(newline='',encoding='utf-8') as f:cands=list(csv.DictReader(f))
    bytype=defaultdict(list)
    for r in cands:bytype[r['tpia_type']].append(r['candidate_id'])
    s=requests.Session();s.headers['User-Agent']='chun-camellia-orthology/0.1 (public primer-to-TPIA audit)'
    seq={};fetch=[]
    for typ,ids in bytype.items():
        q,meta=fetch_cds(s,typ,ids);fetch.append(meta)
        for gid,ss in q.items():seq[(typ,gid)]=ss
    out=[]
    for c in cands:
        p=prim[c['source_unigene']];gid=c['candidate_id'];ss=seq.get((c['tpia_type'],gid),'')
        m=best_pair(ss,p['forward_primer'].upper(),p['reverse_primer'].upper(),int(p['reported_product_bp'])) if ss else {'paired_hit':False}
        row={**c,'candidate_cds_bp':len(ss),'candidate_cds_sha256':sha256(ss.encode()) if ss else '',**m}
        row['mapping_decision']='exact_or_near_paired_primer_match' if m.get('paired_hit') and m.get('total_primer_mismatches',99)<=2 and m.get('product_length_deviation',999)<=10 else ('paired_candidate_but_not_decisive' if m.get('paired_hit') else 'no_paired_match')
        row['claim_boundary']='primer mapping identifies an amplicon-compatible candidate locus; full-length de novo transcript identity still requires transcript/assembly sequence'
        out.append(row)
    # rank within source unigene, preserving all candidates
    for u in prim:
        rr=[r for r in out if r['source_unigene']==u]
        rr.sort(key=lambda r:(0 if r.get('paired_hit') else 1,int(r.get('total_primer_mismatches') or 99),int(r.get('product_length_deviation') or 999),r['candidate_id']))
        for rank,r in enumerate(rr,1):r['within_unigene_rank']=rank
    fields=list(out[0].keys())
    with (a.out_dir/'primer_candidate_mapping.csv').open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(out)
    summary={}
    for u in prim:
        rr=sorted([r for r in out if r['source_unigene']==u],key=lambda r:r['within_unigene_rank']);best=rr[0]
        decisive=[r for r in rr if r['mapping_decision']=='exact_or_near_paired_primer_match']
        summary[u]={'candidate_count':len(rr),'decisive_candidate_count':len(decisive),'best_candidate':best['candidate_id'],'best_class':best['candidate_class'],'best_paired_hit':best.get('paired_hit'), 'best_total_primer_mismatches':best.get('total_primer_mismatches'),'best_predicted_product_bp':best.get('predicted_product_bp'),'reported_product_bp':int(prim[u]['reported_product_bp']),'decision':'unique_decisive_candidate' if len(decisive)==1 else ('multiple_amplicon_compatible_candidates' if len(decisive)>1 else 'no_decisive_candidate')}
    meta={'endpoint':ENDPOINT,'fetches':fetch,'unigene_results':summary,'claim_ceiling':'qRT-PCR amplicon compatibility can narrow de novo unigene mapping but is not full-length orthology evidence'}
    (a.out_dir/'summary.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8');print(json.dumps(meta,indent=2))
if __name__=='__main__':main()
