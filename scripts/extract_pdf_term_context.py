#!/usr/bin/env python3
"""Extract text contexts for specified terms from public supplementary PDFs.

Used only for provenance discovery of named source-local transcript IDs. It
writes page-numbered text windows; it does not infer gene identity from primer
or annotation text.
"""
from __future__ import annotations
import argparse,json,re
from pathlib import Path
from pypdf import PdfReader

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--terms',nargs='+',required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    hits=[];pdfs=sorted(a.root.rglob('*.pdf'))
    for pdf in pdfs:
        try:r=PdfReader(str(pdf))
        except Exception as e:
            hits.append({'pdf':str(pdf),'error':repr(e)});continue
        for pno,page in enumerate(r.pages,1):
            text=page.extract_text() or ''
            norm=re.sub(r'\s+',' ',text)
            low=norm.lower()
            for term in a.terms:
                start=0;t=term.lower()
                while True:
                    i=low.find(t,start)
                    if i<0:break
                    hits.append({'pdf':str(pdf.relative_to(a.root)),'page':pno,'term':term,'context':norm[max(0,i-500):min(len(norm),i+len(term)+900)]})
                    start=i+len(t)
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps({'pdf_count':len(pdfs),'terms':a.terms,'hits':hits},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'pdf_count':len(pdfs),'terms':a.terms,'hit_count':len([h for h in hits if 'term' in h])},indent=2))
if __name__=='__main__':main()
