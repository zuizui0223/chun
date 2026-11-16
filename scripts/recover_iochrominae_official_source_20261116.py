#!/usr/bin/env python3
"""One-time source acquisition diagnostic for Iochrominae (2026-11-16).

Only original publisher, author-university and official Dryad URLs are probed.
Original binary bytes are NEVER committed or uploaded. Save only URL-normalized
receipts, content hashes and file-type/structure evidence. If an authoritative
original 2018 supplement is obtained, inspect its PDF structure and whether
numeric seven-gene species matrix text is present; do not fabricate original
HPLC/qPCR data from author plots. A 2018 floral-shape tree is NOT an original
2015 author-used flower-colour tree unless identical bytes are separately proven.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import io
import json
import re
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

from pypdf import PdfReader


URLS = {
    "publisher_article":"https://academic.oup.com/mbe/article/35/9/2159/5034462",
    "publisher_supp_static":"https://oup.silverchair-cdn.com/oup/backfile/Content_public/Journal/mbe/35/9/10.1093_molbev_msy117/1/msy117_supp.pdf",
    "author_institutional_preprint":"https://scholar.colorado.edu/concern/articles/g158bj138",
    "dryad_2015_tree_landing":"https://datadryad.org/dataset/doi%3A10.5061/dryad.0732g",
    "dryad_2018_shape_landing":"https://datadryad.org/dataset/doi%3A10.5061/dryad.5jn7b",
    "dryad_2015_tree_api":"https://api.datadryad.org/api/v2/datasets/doi%3A10.5061%2Fdryad.0732g",
    "dryad_2018_shape_api":"https://api.datadryad.org/api/v2/datasets/doi%3A10.5061%2Fdryad.5jn7b",
    "dryad_2015_tree_samehost_api":"https://datadryad.org/api/v2/datasets/doi%3A10.5061%2Fdryad.0732g",
    "dryad_2018_shape_samehost_api":"https://datadryad.org/api/v2/datasets/doi%3A10.5061%2Fdryad.5jn7b",
    "dryad_2015_tree_version":"https://datadryad.org/api/v2/versions/3567",
    "dryad_2018_shape_version":"https://datadryad.org/api/v2/versions/22139",
    "dryad_2015_tree_files":"https://datadryad.org/api/v2/versions/3567/files",
    "dryad_2018_shape_files":"https://datadryad.org/api/v2/versions/22139/files",
    "dryad_2015_original_file_21811_samehost_download":"https://datadryad.org/api/v2/files/21811/download",
    "dryad_2018_shape_file_76310_samehost_download":"https://datadryad.org/api/v2/files/76310/download",
    "dryad_2018_shape_file_76311_samehost_download":"https://datadryad.org/api/v2/files/76311/download",
    "dryad_2015_tree_version_archive":"https://datadryad.org/api/v2/versions/3567/download",
    "dryad_2018_shape_version_archive":"https://datadryad.org/api/v2/versions/22139/download",
    "dryad_2015_tree_dataset_archive":"https://datadryad.org/api/v2/datasets/doi%3A10.5061%2Fdryad.0732g/download",
    "dryad_2018_shape_dataset_archive":"https://datadryad.org/api/v2/datasets/doi%3A10.5061%2Fdryad.5jn7b/download",
}
VALID_HOSTS={"academic.oup.com","oup.silverchair-cdn.com","scholar.colorado.edu",
             "datadryad.org","api.datadryad.org","www.colorado.edu"}
MAX_BYTES=18*1024*1024
TIMEOUT_SECONDS=22


def sanitized(url:str)->str:
    p=urllib.parse.urlparse(url)
    return p.hostname+p.path if p.hostname else "UNPARSABLE"


def supported_url(url:str)->bool:
    p=urllib.parse.urlparse(url)
    return p.scheme=="https" and p.hostname in VALID_HOSTS


def download(url:str)->tuple[bytes,dict]:
    if not supported_url(url):
        raise ValueError("source URI outside original official provider allowlist")
    req=urllib.request.Request(
        url, headers={"User-Agent":"Mozilla/5.0 (compatible; academic original-source audit/1.0)",
                      "Accept":"application/pdf,text/html,application/json,application/zip,*/*",
                      "Accept-Encoding":"identity","Referer":"https://academic.oup.com/"})
    try:
        with urllib.request.urlopen(req,timeout=TIMEOUT_SECONDS) as response:
            status=int(response.status)
            mime=response.headers.get("Content-Type","").split(";")[0]
            final=response.geturl()
            # Do not follow redirects to nonauthoritative, unknown hosts.
            if not supported_url(final):
                return b"",{"status":"HOLD_UNTRUSTED_REDIRECT","http_status":status,
                             "redirect_host":urllib.parse.urlparse(final).hostname}
            payload=response.read(MAX_BYTES+1)
            if len(payload)>MAX_BYTES:
                return b"",{"status":"HOLD_SOURCE_LARGER_THAN_18MB","http_status":status,
                             "mime":mime}
            return payload,{"status":"OK","http_status":status,"mime":mime,
                            "final_resource":sanitized(final)}
    except urllib.error.HTTPError as exc:
        return b"",{"status":"HTTP_ERROR","http_status":exc.code}
    except Exception as exc:
        return b"",{"status":"FETCH_ERROR","exception_type":type(exc).__name__,
                    "detail":str(exc)[:160]}


def inspect(payload:bytes,tag:str)->dict:
    rec={"payload_bytes":len(payload),"sha256":hashlib.sha256(payload).hexdigest()}
    if payload.startswith(b"%PDF"):
        rec["format"]="PDF"
        try:
            reader=PdfReader(io.BytesIO(payload))
            rec["pdf_pages"]=len(reader.pages)
            txt="\n".join(page.extract_text() or "" for page in reader.pages)
            rec["pdf_text_chars"]=len(txt)
            rec["pdf_has_species_hplc_numeric_table"]=bool(
                re.search(r"(?is)(?:table\s*s\d+).{0,100}(?:pigment|flavonol|anthocyan)",
                          txt))
            rec["pdf_has_gene_expression_numeric_table"]=bool(
                re.search(r"(?is)(?:table\s*s\d+).{0,120}(?:expression|qpcr|fold)",
                          txt))
            rec["pdf_mentions_original_supp_S1"]=bool(re.search(r"(?i)fig(?:ure)?\s*S1",txt))
            rec["pdf_mentions_original_supp_S4"]=bool(re.search(r"(?i)table\s*S4",txt))
            # These are indicators only, never verified 28x7 assay counts.
            rec["pdf_reconstruction_admitted"]=False
        except Exception as exc:
            rec["pdf_parse_error"]=type(exc).__name__
    elif payload.startswith(b"PK\x03\x04"):
        rec["format"]="ZIP"
        try:
            with zipfile.ZipFile(io.BytesIO(payload)) as zf:
                rec["zip_file_list"]=[{"name":f.filename,"uncompressed_bytes":f.file_size}
                                      for f in zf.infolist()[:120]]
        except Exception as exc:
            rec["zip_parse_error"]=type(exc).__name__
    elif payload.startswith(b"{") or payload.startswith(b"["):
        rec["format"]="JSON"
        try:
            item=json.loads(payload)
            if isinstance(item,dict):
                rec["json_top_keys"]=sorted(item.keys())[:45]
                rec["json_links_or_identifier"]={
                    k:str(v)[:260] for k,v in item.items()
                    if k in ("id","identifier","doi","_links","title")}
                embedded=item.get("_embedded",{})
                if isinstance(embedded,dict):
                    inventory=[]
                    for embedded_key,values in embedded.items():
                        if isinstance(values,list):
                            for row in values[:40]:
                                if isinstance(row,dict):
                                    inventory.append({
                                        "group":embedded_key,
                                        **{k:v for k,v in row.items()
                                           if k in ("id","path","filename","size","md5",
                                                    "digest","mimeType","status","description",
                                                    "fileSize","fileName","checksum")}
                                    })
                    rec["json_original_provider_file_inventory"]=inventory
        except Exception:
            rec["json_parse_error"]=True
    else:
        rec["format"]="HTML_OR_OTHER"
        if b"<html" in payload[:1000].lower() or b"<!doctype html" in payload[:1000].lower():
            rec["format"]="HTML"
        rec["contains_relevant_supplement_url"]=b"msy117_supp.pdf" in payload
        # Dryad landing pages sometimes serve index HTML while the separate
        # api.datadryad.org domain fails DNS. Extract original file IDs/links
        # from the *official page bytes*, not from guessed filenames.
        text=html.unescape(payload.decode("utf-8",errors="replace"))
        rawlinks=re.findall(r"""(?is)href=["']([^"']{1,800})["']""",text)
        candidates=[]
        for h in rawlinks:
            u=urllib.parse.urljoin("https://datadryad.org/",h)
            path=urllib.parse.urlparse(u).path
            if supported_url(u) and re.search(
                r"(?i)(download|file.stream|/api/v2/|\.(?:zip|rar|nex|nwk|tre|csv|tsv)$)",path):
                name=sanitized(u)
                if name not in candidates:
                    candidates.append(name)
        rec["html_official_file_links"]=candidates[:35]
        ids=re.findall(r"""(?i)(?:file[_-]?id|fileId|file_id)["'\s:=]+(\d{3,12})""",text)
        rec["html_file_id_candidates"]=sorted(set(ids))[:30]
        rec["html_has_2015_tempo_title"]="Tempo and mode of flower color evolution" in text
        rec["html_has_2018_shape_title"]="Convergent evolution of floral shape" in text
        rec["html_original_archived_filenames"]=[
            f for f in sorted(set(re.findall(
                r"(?i)\b[a-z0-9_\-]{3,100}\.(?:zip|rar|nex|nwk|tre|csv|tsv|txt)\b",text)))
            if not f.startswith(("http","www"))][:50]
    return rec


def signed_publisher_url(page_bytes:bytes)->str|None:
    text=html.unescape(page_bytes.decode("utf-8",errors="replace"))
    # Extract only a URL signed by OUP on the page. Never evaluate arbitrary HTML.
    for match in re.finditer(r"""(?:(?:href|data-href)=["'])([^"']*msy117_supp\.pdf[^"']*)""",text,re.I):
        url=urllib.parse.urljoin("https://academic.oup.com/",match.group(1))
        if urllib.parse.urlparse(url).hostname=="oup.silverchair-cdn.com":
            return url
    return None


def run()->dict:
    records={}
    signed=None
    for name,url in URLS.items():
        data,meta=download(url)
        rec={"source_uri":sanitized(url),**meta}
        if data:
            rec.update(inspect(data,name))
            if name=="publisher_article":
                signed=signed_publisher_url(data)
        records[name]=rec
        print("IOCHROMINAE_SOURCE_PROBE",name,json.dumps(rec,sort_keys=True),flush=True)
    if signed:
        data,meta=download(signed)
        rec={"source_uri":sanitized(signed),"signed_link_discovered_in_official_article":True,**meta}
        if data: rec.update(inspect(data,"signed_publisher_supplement"))
        records["signed_publisher_supplement"]=rec
        print("IOCHROMINAE_SOURCE_PROBE","signed_publisher_supplement",json.dumps(rec,sort_keys=True),flush=True)
    else:
        records["signed_publisher_supplement"]={"status":"NO_PUBLISHER_PAGE_SIGNED_LINK_RECOVERED"}
    pdf_receipts=[v for k,v in records.items() if "supp" in k and v.get("format")=="PDF"]
    records_status=("ORIGINAL_2018_SUPPLEMENT_PDF_BYTES_RECOVERED_NEEDS_TABLE_CHECK"
                    if pdf_receipts else "HOLD_ORIGINAL_2018_PUBLISHER_SUPPLEMENT_BYTES")
    # Even if a PDF is fetched, the original raw 2018 *numeric* HPLC/qPCR
    # matrices and the exact 2015 original dated tree have not been verified.
    summary={
        "version":"v0.1","date":"2026-11-16",
        "status":records_status,
        "original_publication_DOI":"10.1093/molbev/msy117",
        "original_2015_tree_DOI":"10.5061/dryad.0732g",
        "2018_separate_flower_shape_tree_DOI":"10.5061/dryad.5jn7b",
        "sources":records,
        "original_2018_HPLC_species_matrix_admitted":False,
        "original_2018_seven_qPCR_gene_species_matrix_admitted":False,
        "original_2015_author_used_dated_tree_admitted":False,
        "original_2015_tree_binary_archive_recovered":False,
        "original_2018_shape_tree_binary_archive_recovered":False,
        "independent_radiation_source_join_admitted":False,
        "original_pdf_bytes_republished":False,
        "source_absence_or_http_failure_not_biological_result":True,
        "note":"Receipt is primary provider byte/status audit, not a gene-expression-to-pigment prediction or confirmed taxon intersection."
    }
    return summary


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    result=run()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("IOCHROMINAE_OFFICIAL_SOURCE_RECOVERY_TERMINAL",
          json.dumps({"status":result["status"],
                      "pdf_recovered":result["status"].startswith("ORIGINAL_2018_SUPPLEMENT"),
                      "source_join_admitted":result["independent_radiation_source_join_admitted"]},
                     sort_keys=True))


if __name__=="__main__":
    main()
