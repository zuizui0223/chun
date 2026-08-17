#!/usr/bin/env python3
"""Compare the source CnFLS2 qRT-PCR amplicon anchor with tea FLS paralogs.

Feng 2024 Supplementary Fig. 8 groups F01.PB8395 with CnFLS2 and Table 4
provides its qRT-PCR primers. This script tests that primer pair against the two
C. sinensis FLS source loci already resolved through TPIA2 (CSA006950 and
CSA008358) and against the published C. nitidissima CnFLS1 cDNA JF343560.1.

Amplicon compatibility can prioritize homolog/paralog hypotheses; it cannot
replace full-length sequence/gene-tree/synteny evidence for formal orthology.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,re,zipfile
from pathlib import Path
from urllib.parse import urlencode
import requests
from Bio import SeqIO

TPIA='https://tpia.teaplants.cn/getGeneSeqByGeneNames'
FWD='AGCAATCACCACCGTCAAAGG'
REV='CTCTTAGACTCAGCATCCTTAGC'
TEA={'CSA006950':'CSS0007745','CSA008358':'CSS0045924'}

def rc(s):return s.translate(str.maketrans('ACGTNacgtn','TGCANtgcan'))[::-1]
def sha256(b):return hashlib.sha256(b).hexdigest()
def parse_fasta(text):
    d={};h=None;seq=[]
    for raw in text.splitlines():
        line=raw.strip()
        if not line:continue
        if line.startswith('>'):
            if h is not None:d[h.split('\t')[0].split()[0]]=''.join(seq).upper()
            h=line[1:];seq=[]
        elif h is not None:seq.append(re.sub(r'\s+','',line))
    if h is not None:d[h.split('\t')[0].split()[0]]=''.join(seq).upper()
    return d

def fetch_tpia(s,seqtype):
    flags={'cds':(1,0,0),'transcript':(0,1,0),'exon':(0,0,1)}[seqtype]
    ids=list(TEA.values());params={'geneNames':','.join(ids),'cds':flags[0],'trans':flags[1],'exon':flags[2],'down':0,'up':0,'teaType':'Shuchazao2'}
    r=s.get(TPIA+'?'+urlencode(params),timeout=120);r.raise_for_status();raw=r.content
    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        seq={}
        for n in zf.namelist():
            if n.lower().endswith('.txt'):seq.update(parse_fasta(zf.read(n).decode('utf-8',errors='replace')))
    return seq,{'type':seqtype,'sha256':sha256(raw),'bytes':len(raw),'records':len(seq)}

def fetch_ncbi(s,acc):
    u='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi';r=s.get(u,params={'db':'nuccore','id':acc,'rettype':'fasta','retmode':'text'},timeout=60);r.raise_for_status();rec=next(SeqIO.parse(io.StringIO(r.text),'fasta'))
    return str(rec.seq).upper(),{'accession':acc,'sha256':sha256(r.content),'bp':len(rec.seq),'header':rec.description}

def best_window(seq,primer):
    L=len(primer);best=None
    for i in range(max(0,len(seq)-L+1)):
        w=seq[i:i+L];m=sum(a!=b for a,b in zip(w,primer));cand=(m,i,w)
        if best is None or cand<best:best=cand
    return best

def paired(seq,maxmis=4,maxproduct=5000):
    rrc=rc(REV);L1=len(FWD);L2=len(rrc);fh=[];rh=[]
    for primer,L,target in [(FWD,L1,fh),(rrc,L2,rh)]:
        for i in range(max(0,len(seq)-L+1)):
            w=seq[i:i+L];m=sum(a!=b for a,b in zip(w,primer))
            if m<=maxmis:target.append((m,i,w))
    out=[]
    for fm,fp,fw in fh:
        for rm,rp,rw in rh:
            if rp<fp:continue
            prod=rp+L2-fp
            if 0<prod<=maxproduct:out.append((fm+rm,fm,rm,prod,fp,rp))
    return min(out) if out else None

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output-dir',type=Path,required=True);a=ap.parse_args();a.output_dir.mkdir(parents=True,exist_ok=True)
    s=requests.Session();s.headers['User-Agent']='chun-camellia-orthology/0.1 (public FLS primer audit)'
    seqs={};fetch=[]
    for st in ['cds','transcript','exon']:
        q,m=fetch_tpia(s,st);fetch.append(m)
        for src,gid in TEA.items():
            if gid in q:seqs[(src,st)]=q[gid]
    cn1,cnmeta=fetch_ncbi(s,'JF343560.1');seqs[('CnFLS1_JF343560.1','cDNA')]=cn1
    rows=[]
    for (target,layer),seq in seqs.items():
        fw=best_window(seq,FWD);rv=best_window(seq,rc(REV));pr=paired(seq)
        rows.append({'target':target,'sequence_layer':layer,'sequence_bp':len(seq),'sequence_sha256':sha256(seq.encode()),'forward_best_mismatch':fw[0] if fw else '', 'reverse_best_mismatch':rv[0] if rv else '', 'paired_total_mismatches':pr[0] if pr else '', 'paired_forward_mismatches':pr[1] if pr else '', 'paired_reverse_mismatches':pr[2] if pr else '', 'predicted_amplicon_bp':pr[3] if pr else '', 'mapping_interpretation':'amplicon-compatible' if pr and pr[0]<=3 else 'not-decisive','claim_boundary':'primer similarity is a local sequence anchor, not formal orthology'})
    with (a.output_dir/'primer_similarity.csv').open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    # choose best local primer support across layers for each target
    best={}
    for t in sorted({r['target'] for r in rows}):
        rr=[r for r in rows if r['target']==t]
        def k(r):
            try:return (0,int(r['paired_total_mismatches']),abs(int(r['predicted_amplicon_bp'])-170))
            except:return (1,int(r['forward_best_mismatch'])+int(r['reverse_best_mismatch']),9999)
        best[t]=min(rr,key=k)
    summary={'source_transcript':'F01.PB8395','source_class':'CnFLS2','forward_primer':FWD,'reverse_primer':REV,'tea_targets':TEA,'cnfls1_reference':cnmeta,'tpia_fetches':fetch,'best_support_by_target':best,'decision':'local primer/homology screen only; no CnFLS2 full-length sequence is available in the current public supplement','claim_ceiling':'do not assign CnFLS2 to a tea paralog without full-length sequence/gene-tree or sufficiently unique amplicon evidence'}
    (a.output_dir/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
