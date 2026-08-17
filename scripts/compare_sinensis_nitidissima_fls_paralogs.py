#!/usr/bin/env python3
"""Compare two C. sinensis FLS source loci to named C. nitidissima FLS paralogs.

The tea CDSs are fetched from the public TPIA2 Batch Retrieve endpoint using
SCZ v2 IDs already crosswalked from the source Yunkang10 IDs. Named CnFLS
protein accessions are fetched from NCBI. Pairwise global protein identity and
coverage are reported for all 2x3 comparisons.

The best sequence homolog is a candidate paralog relationship, not a formal
orthology assignment; gene-tree/synteny evidence is still required for that.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,re,zipfile
from pathlib import Path
from urllib.parse import urlencode
import requests
from Bio import Align,SeqIO
from Bio.Seq import Seq

TPIA='https://tpia.teaplants.cn/getGeneSeqByGeneNames'
FLS_TEA={'CSA006950':'CSS0007745','CSA008358':'CSS0045924'}
CNFLS={'CnFLS1':'XP_028071684.1','CnFLS2':'XP_028092149.1','CnFLS3':'XP_028049310.1'}

def sha256(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def parse_fasta(text):
    d={};h=None;s=[]
    for line in text.splitlines():
        line=line.strip()
        if not line:continue
        if line.startswith('>'):
            if h is not None:d[h.split('\t')[0].split()[0]]=''.join(s).upper()
            h=line[1:];s=[]
        elif h is not None:s.append(re.sub(r'\s+','',line))
    if h is not None:d[h.split('\t')[0].split()[0]]=''.join(s).upper()
    return d

def fetch_tpia(session):
    ids=list(FLS_TEA.values());params={'geneNames':','.join(ids),'cds':1,'trans':0,'exon':0,'down':0,'up':0,'teaType':'Shuchazao2'}
    r=session.get(TPIA+'?'+urlencode(params),timeout=120);r.raise_for_status();raw=r.content
    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        seq={}
        for n in zf.namelist():
            if n.lower().endswith('.txt'):seq.update(parse_fasta(zf.read(n).decode('utf-8',errors='replace')))
    return seq,{'response_sha256':sha256(raw),'response_bytes':len(raw),'ids':ids}

def fetch_ncbi(session,acc):
    url='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi'
    r=session.get(url,params={'db':'protein','id':acc,'rettype':'fasta','retmode':'text'},timeout=60);r.raise_for_status();rec=next(SeqIO.parse(io.StringIO(r.text),'fasta'))
    return str(rec.seq).upper(),{'accession':acc,'fasta_sha256':sha256(r.content),'length_aa':len(rec.seq),'header':rec.description}

def clean_translation(cds):
    s=cds[:len(cds)//3*3];p=str(Seq(s).translate(to_stop=False)).rstrip('*')
    return p.replace('*','X')

def metrics(a,b,aligner):
    al=aligner.align(a,b)[0];c=al.counts();nongap=c.identities+c.mismatches;full=nongap+c.gaps
    return c.identities/nongap if nongap else 0,c.identities/full if full else 0,c.gaps

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output-dir',type=Path,required=True);a=ap.parse_args();a.output_dir.mkdir(parents=True,exist_ok=True)
    s=requests.Session();s.headers['User-Agent']='chun-camellia-orthology/0.1 (public sequence comparison)'
    t,tm=fetch_tpia(s);cn={};nmeta=[]
    for name,acc in CNFLS.items():cn[name],m=fetch_ncbi(s,acc);nmeta.append(m)
    tea={src:clean_translation(t[gid]) for src,gid in FLS_TEA.items()}
    aligner=Align.PairwiseAligner();aligner.mode='global';aligner.match_score=1;aligner.mismatch_score=0;aligner.open_gap_score=-1;aligner.extend_gap_score=-0.1
    rows=[]
    for src,p in tea.items():
        for cname,cp in cn.items():
            ni,fi,g=metrics(p,cp,aligner)
            rows.append({'tea_source_id':src,'tea_sczv2_id':FLS_TEA[src],'tea_protein_aa':len(p),'cnfls':cname,'cnfls_accession':CNFLS[cname],'cnfls_aa':len(cp),'protein_nongap_identity':f'{ni:.6f}','protein_full_alignment_identity':f'{fi:.6f}','gap_columns':g})
    # rank candidates independently for each tea source locus.
    for src in tea:
        rr=[r for r in rows if r['tea_source_id']==src];rr.sort(key=lambda r:(-float(r['protein_nongap_identity']),-float(r['protein_full_alignment_identity']),r['cnfls']))
        for rank,r in enumerate(rr,1):r['within_tea_locus_rank']=rank
    fields=list(rows[0])
    with (a.output_dir/'fls_pairwise_identity.csv').open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    best={src:next(r for r in rows if r['tea_source_id']==src and r['within_tea_locus_rank']==1) for src in tea}
    summary={'tpia':tm,'ncbi_proteins':nmeta,'best_candidate_by_tea_locus':{src:{'cnfls':r['cnfls'],'accession':r['cnfls_accession'],'protein_nongap_identity':r['protein_nongap_identity'],'protein_full_alignment_identity':r['protein_full_alignment_identity']} for src,r in best.items()},'same_best_cnfls_for_both_tea_loci':len({r['cnfls'] for r in best.values()})==1,'decision':'pairwise best-homolog screen only; retain one-to-many paralogy and require gene-tree/synteny before formal orthology','claim_ceiling':'sequence similarity can prioritize paralog hypotheses but cannot by itself assign orthology after duplication'}
    (a.output_dir/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
