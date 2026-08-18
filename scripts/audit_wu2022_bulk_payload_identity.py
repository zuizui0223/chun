#!/usr/bin/env python3
"""Audit payload identity for Wu2022 TPIA bulk-fallback transcriptome archives.

This is a provenance gate, not a phylogenetic analysis. It downloads only
manifest rows explicitly marked as bulk fallbacks, fingerprints the HTTP ZIP
payloads and extracted FASTA members, and checks whether nominally different
taxa collapse to the same bytes/sequence set.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import time
import zipfile
from pathlib import Path
from urllib.request import Request, urlopen


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize_seq(text: str) -> bytes:
    seq=[]
    for line in text.splitlines():
        line=line.strip()
        if line and not line.startswith('>'):
            seq.append(re.sub(r'\s+','',line).upper())
    return ''.join(seq).encode()


def fasta_stats(text: str) -> tuple[int,int,str]:
    headers=[]; total=0; seq_chunks=[]
    for line in text.splitlines():
        line=line.strip()
        if not line:
            continue
        if line.startswith('>'):
            headers.append(line[1:])
        else:
            s=re.sub(r'\s+','',line).upper()
            total += len(s)
            seq_chunks.append(s)
    # hash only concatenated sequence characters, independent of wrapping/header text
    return len(headers), total, sha256(''.join(seq_chunks).encode())


def download(url: str, attempts: int=5) -> tuple[bytes,str,str]:
    last=None
    for i in range(attempts):
        try:
            req=Request(url,headers={'User-Agent':'chun-wu2022-payload-audit/0.1'})
            with urlopen(req,timeout=240) as r:
                body=r.read(); final=r.geturl(); ctype=r.headers.get('content-type','')
            if len(body)<1000:
                raise RuntimeError(f'payload too small: {len(body)} bytes')
            return body,final,ctype
        except Exception as exc:
            last=exc
            if i+1<attempts: time.sleep(min(2**(i+1),16))
    raise RuntimeError(f'failed download {url}: {last}')


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument('--manifest',type=Path,required=True)
    ap.add_argument('--out-dir',type=Path,required=True)
    args=ap.parse_args(); args.out_dir.mkdir(parents=True,exist_ok=True)

    with args.manifest.open(newline='',encoding='utf-8-sig') as f:
        all_rows=list(csv.DictReader(f))
    rows=[r for r in all_rows if r.get('assembly_source')=='tpia_bulk_fallback']
    if not rows:
        raise SystemExit('no tpia_bulk_fallback rows')

    audit=[]; members=[]
    for row in rows:
        taxon=row['source_taxon']; url=row['assembly_url']
        body,final,ctype=download(url)
        zip_sha=sha256(body)
        is_zip=body[:4]==b'PK\x03\x04'
        if not is_zip:
            raise RuntimeError(f'{taxon}: response is not ZIP ({ctype}; {len(body)} bytes)')
        with zipfile.ZipFile(io.BytesIO(body)) as zf:
            bad=zf.testzip()
            if bad: raise RuntimeError(f'{taxon}: corrupt ZIP member {bad}')
            zinfos=[x for x in zf.infolist() if not x.is_dir()]
            if not zinfos: raise RuntimeError(f'{taxon}: empty ZIP')
            member_hashes=[]; sequence_hashes=[]; n_fasta_records=0; total_nt=0
            for info in zinfos:
                b=zf.read(info.filename)
                text=b.decode('utf-8',errors='replace')
                nrec,nt,seq_sha=fasta_stats(text)
                member_sha=sha256(b)
                member_hashes.append(member_sha); sequence_hashes.append(seq_sha)
                n_fasta_records+=nrec; total_nt+=nt
                members.append({
                    'source_taxon':taxon,'member_name':info.filename,'member_bytes':len(b),
                    'member_sha256':member_sha,'fasta_records':nrec,'total_nt':nt,
                    'sequence_only_sha256':seq_sha,
                })
        sequence_set_sha=sha256('|'.join(sorted(sequence_hashes)).encode())
        member_set_sha=sha256('|'.join(sorted(member_hashes)).encode())
        audit.append({
            'source_taxon':taxon,'requested_url':url,'final_url':final,
            'content_type':ctype,'payload_bytes':len(body),'zip_sha256':zip_sha,
            'n_members':len(zinfos),'member_set_sha256':member_set_sha,
            'fasta_records':n_fasta_records,'total_nt':total_nt,
            'sequence_set_sha256':sequence_set_sha,
            'advertised_size':row.get('advertised_size',''),
        })

    fields=list(audit[0])
    with (args.out_dir/'bulk_payload_audit.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n'); w.writeheader(); w.writerows(audit)
    with (args.out_dir/'bulk_payload_members.csv').open('w',newline='',encoding='utf-8') as f:
        fields2=list(members[0]); w=csv.DictWriter(f,fieldnames=fields2,lineterminator='\n'); w.writeheader(); w.writerows(members)

    zip_unique=len({r['zip_sha256'] for r in audit})
    seq_unique=len({r['sequence_set_sha256'] for r in audit})
    duplicates=[]
    for key in ('zip_sha256','sequence_set_sha256'):
        groups={}
        for r in audit: groups.setdefault(r[key],[]).append(r['source_taxon'])
        duplicates.extend({'level':key,'sha256':h,'taxa':ts} for h,ts in groups.items() if len(ts)>1)

    summary={
        'analysis_version':'v0.1',
        'bulk_fallback_taxa':len(audit),
        'taxa':sorted(r['source_taxon'] for r in audit),
        'successful_zip_payloads':len(audit),
        'unique_zip_payloads':zip_unique,
        'unique_sequence_sets':seq_unique,
        'duplicate_groups':duplicates,
        'payload_identity_gate_pass': zip_unique==len(audit) and seq_unique==len(audit),
        'decision': ('bulk fallback payloads are byte- and sequence-distinct across taxa' if zip_unique==len(audit) and seq_unique==len(audit) else 'one or more bulk fallback taxa share payload/sequence identity; do not admit collided rows to topology reconstruction'),
        'claim_ceiling':'payload/checksum provenance only; distinct archive bytes or sequence sets do not prove biological sample identity or reconstruct the Wu2022 phylogeny',
    }
    (args.out_dir/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':
    main()
