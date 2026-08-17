#!/usr/bin/env python3
"""Discover public TPIA2 form/AJAX endpoints needed for sequence provenance.

This is a provenance diagnostic: it records page checksums, HTML form actions,
input/select names, linked JavaScript and URL-like endpoint strings. It does not
submit gene IDs or infer orthology.
"""
from __future__ import annotations
import argparse,hashlib,json,re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin,urlparse
import requests

PAGES={
 'gene_id_convert':'https://tpia.teaplants.cn/geneIdConvert.html',
 'batch_retrieve':'https://tpia.teaplants.cn/Batch_Retrieve_Data.html',
 'advanced_query':'https://tpia.teaplants.cn/advanceQuery.html',
 'transcriptome':'https://tpia.teaplants.cn/transcriptome.html?tabls=tablist1-tab5',
 'download':'https://tpia.teaplants.cn/download.html',
}

class P(HTMLParser):
    def __init__(self):
        super().__init__();self.forms=[];self.inputs=[];self.selects=[];self.scripts=[];self.links=[]
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if tag=='form':self.forms.append({k:d.get(k,'') for k in ['id','name','action','method']})
        elif tag in {'input','textarea','button'}:self.inputs.append({'tag':tag,**{k:d.get(k,'') for k in ['id','name','type','value','onclick']}})
        elif tag=='select':self.selects.append({k:d.get(k,'') for k in ['id','name']})
        elif tag=='script' and d.get('src'):self.scripts.append(d['src'])
        elif tag=='a' and d.get('href'):self.links.append(d['href'])

def sha256(b:bytes)->str:return hashlib.sha256(b).hexdigest()

def endpoint_strings(text:str):
    pats=[r"['\"]([^'\"]+\.(?:php|json|cgi|html)(?:\?[^'\"]*)?)['\"]",r"url\s*:\s*['\"]([^'\"]+)['\"]",r"ajax\s*\([^)]{0,500}\)"]
    out=set()
    for pat in pats:
        for m in re.finditer(pat,text,re.I|re.S):
            s=m.group(1) if m.lastindex else m.group(0)
            if len(s)<500:out.add(s.strip())
    return sorted(out)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out-dir',type=Path,required=True);a=ap.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
    s=requests.Session();s.headers['User-Agent']='chun-camellia-orthology/0.1 (public TPIA2 audit)'
    result={}
    all_js={}
    for key,url in PAGES.items():
        r=s.get(url,timeout=60);r.raise_for_status();raw=r.content;text=r.text
        (a.out_dir/f'{key}.html').write_bytes(raw)
        p=P();p.feed(text)
        jsrows=[]
        for src in sorted(set(p.scripts)):
            jurl=urljoin(url,src)
            if urlparse(jurl).netloc!=urlparse(url).netloc:continue
            try:
                jr=s.get(jurl,timeout=60)
                jsrows.append({'url':jurl,'status':jr.status_code,'bytes':len(jr.content),'sha256':sha256(jr.content) if jr.ok else '', 'endpoint_strings':endpoint_strings(jr.text) if jr.ok else []})
                if jr.ok:
                    name=re.sub(r'[^A-Za-z0-9._-]+','_',src.strip('/')) or 'script.js'
                    (a.out_dir/f'{key}__{name}').write_bytes(jr.content)
                    all_js[jurl]=jr.text
            except Exception as e:
                jsrows.append({'url':jurl,'error':repr(e)})
        result[key]={'url':url,'status':r.status_code,'bytes':len(raw),'sha256':sha256(raw),'forms':p.forms,'inputs':p.inputs,'selects':p.selects,'scripts':p.scripts,'html_endpoint_strings':endpoint_strings(text),'same_host_js':jsrows}
    # Search all downloaded JS jointly for API-ish strings involving conversion/retrieve/search.
    hits=[]
    for jurl,text in all_js.items():
        for line in text.splitlines():
            ll=line.lower()
            if any(k in ll for k in ['geneid','convert','retrieve','sequence','ajax','ortholog','transcriptome']) and len(line)<2000:
                hits.append({'js_url':jurl,'line':line.strip()})
    result['joint_js_keyword_hits']=hits[:1000]
    (a.out_dir/'tpia_endpoint_audit.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2,ensure_ascii=False)[:120000])
if __name__=='__main__':main()
