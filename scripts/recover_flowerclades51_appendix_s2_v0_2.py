#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import html
import io
import json
import re
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

DOI="10.1002/ajb2.70146"
FILENAME="ajb270146-sup-0002-AJB_SinnottArmstrong_D_24_00358_AppendixS2_ce.docx"
ARTICLE_URLS=[
  "https://bsapubs.onlinelibrary.wiley.com/doi/10.1002/ajb2.70146",
  "https://onlinelibrary.wiley.com/doi/10.1002/ajb2.70146",
]
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
W="{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def sha256_bytes(b:bytes)->str:
    return hashlib.sha256(b).hexdigest()


def valid_docx_bytes(b:bytes)->bool:
    if not b.startswith(b"PK"):
        return False
    try:
        with zipfile.ZipFile(io.BytesIO(b)) as z:
            names=set(z.namelist())
            if "[Content_Types].xml" not in names or "word/document.xml" not in names:
                return False
            return b"wordprocessingml.document.main+xml" in z.read("[Content_Types].xml")
    except Exception:
        return False


def request(url:str,referer:str|None=None,timeout:int=90)->tuple[bytes|None,dict]:
    headers={
      "User-Agent":UA,
      "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,application/vnd.openxmlformats-officedocument.wordprocessingml.document;q=0.9,*/*;q=0.8",
      "Accept-Language":"en-US,en;q=0.9",
      "Cache-Control":"no-cache",
    }
    if referer:
        headers["Referer"]=referer
    req=urllib.request.Request(url,headers=headers)
    try:
        with urllib.request.urlopen(req,timeout=timeout) as r:
            b=r.read()
            return b,{
              "url":url,
              "final_url":r.geturl(),
              "http_status":getattr(r,"status",200),
              "content_type":r.headers.get("Content-Type"),
              "content_disposition":r.headers.get("Content-Disposition"),
              "bytes":len(b),
              "sha256":sha256_bytes(b),
              "valid_docx":valid_docx_bytes(b),
            }
    except Exception as e:
        return None,{"url":url,"error":f"{type(e).__name__}: {e}"}


def discover_article_hrefs()->tuple[list[str],list[dict]]:
    found=[]
    diags=[]
    for article in ARTICLE_URLS:
        b,d=request(article)
        diags.append(d)
        if b is None:
            continue
        s=b.decode("utf-8","replace")
        patterns=[
          r'''href=["']([^"']*''' + re.escape(FILENAME) + r'''[^"']*)["']''',
          r'''https?:\\?/\\?/[^"'<> ]*''' + re.escape(FILENAME) + r'''[^"'<> ]*''',
        ]
        for pat in patterns:
            for m in re.finditer(pat,s,re.I):
                u=html.unescape(m.group(1) if m.lastindex else m.group(0))
                u=u.replace("\\/","/")
                found.append(urllib.parse.urljoin(article,u))
    return list(dict.fromkeys(found)),diags


def static_candidate_urls()->list[str]:
    qdoi=urllib.parse.quote(DOI,safe="")
    qfile=urllib.parse.quote(FILENAME,safe="")
    raw=FILENAME
    bases=[
      "https://bsapubs.onlinelibrary.wiley.com",
      "https://onlinelibrary.wiley.com",
      "https://www.onlinelibrary.wiley.com",
    ]
    urls=[]
    for base in bases:
        urls += [
          f"{base}/action/downloadSupplement?doi={qdoi}&file={qfile}",
          f"{base}/action/downloadSupplement?doi={qdoi}&file={raw}",
          f"{base}/doi/suppl/{DOI}/supinfo/{raw}",
          f"{base}/doi/suppl/{DOI}/supinfo/{qfile}",
        ]
    return list(dict.fromkeys(urls))


def cell_text(tc:ET.Element)->str:
    return " ".join(" ".join(t.text or "" for t in tc.iter(W+"t")).split())


def extract_tables(b:bytes)->list[list[list[str]]]:
    if not valid_docx_bytes(b):
        raise ValueError("not a valid DOCX")
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        root=ET.fromstring(z.read("word/document.xml"))
    tables=[]
    for tbl in root.iter(W+"tbl"):
        rows=[]
        for tr in tbl.findall(W+"tr"):
            rows.append([cell_text(tc) for tc in tr.findall(W+"tc")])
        tables.append(rows)
    return tables


def table_inventory(tables:list[list[list[str]]])->list[dict]:
    out=[]
    for i,rows in enumerate(tables,1):
        preview=rows[:3]
        flat=" | ".join(" | ".join(r) for r in preview)
        out.append({
          "table_index":i,
          "rows":len(rows),
          "max_columns":max((len(r) for r in rows),default=0),
          "first_rows":preview,
          "contains_clade_token":bool(re.search(r"\bclade\b",flat,re.I)),
          "contains_transition_token":bool(re.search(r"transition",flat,re.I)),
        })
    return out


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--outdir",type=Path,required=True)
    a=ap.parse_args()
    a.outdir.mkdir(parents=True,exist_ok=True)

    discovered,article_diags=discover_article_hrefs()
    urls=list(dict.fromkeys(discovered+static_candidate_urls()))
    diagnostics=[{"stage":"article_discovery",**d} for d in article_diags]
    found=None
    found_url=None
    for url in urls:
        b,d=request(url,referer=ARTICLE_URLS[0])
        diagnostics.append({"stage":"supplement_probe",**d})
        if b is not None and valid_docx_bytes(b):
            found=b
            found_url=d.get("final_url") or url
            break

    if found is None:
        out={
          "version":"v0.2",
          "status":"HOLD_WILEY_APPENDIX_S2_BYTES_UNAVAILABLE_V0_2",
          "doi":DOI,
          "expected_filename":FILENAME,
          "article_href_candidates_discovered":discovered,
          "static_candidate_url_count":len(static_candidate_urls()),
          "diagnostics":diagnostics,
          "decision":"HOLD_SOURCE_LABILITY_VALUE_UNRESOLVED",
          "outcome_firewall":{
            "clade_transition_values_extracted":False,
            "transition_counts_reestimated":False,
            "manual_plot_digitization_used":False,
            "chun_bridge_fitted":False,
          },
          "paper1_science_changed":False,
          "el_v0_3_science_changed":False,
        }
        (a.outdir/"source_receipt_v0_2.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
        print(json.dumps({"status":out["status"],"discovered":discovered,"probes":len(diagnostics)},indent=2))
        return 0

    p=a.outdir/FILENAME
    p.write_bytes(found)
    tables=extract_tables(found)
    inv=table_inventory(tables)
    (a.outdir/"appendix_s2_tables_full_v0_2.json").write_text(json.dumps(tables,indent=2,ensure_ascii=False)+"\n")
    out={
      "version":"v0.2",
      "status":"WILEY_APPENDIX_S2_SOURCE_RECOVERED_TABLES_INVENTORIED_V0_2",
      "doi":DOI,
      "filename":FILENAME,
      "recovered_url":found_url,
      "bytes":len(found),
      "sha256":sha256_bytes(found),
      "table_count":len(tables),
      "table_inventory":inv,
      "diagnostics":diagnostics,
      "outcome_firewall":{
        "tables_serialized_verbatim_cell_text":True,
        "clade_transition_predictor_selected_or_transformed":False,
        "transition_counts_reestimated":False,
        "manual_plot_digitization_used":False,
        "chun_bridge_fitted":False,
      },
      "next_gate":"FREEZE_EXACT_APPENDIX_S2_CLADE_TRANSITION_COLUMN_MAPPING_BEFORE_MODEL_FIT",
      "paper1_science_changed":False,
      "el_v0_3_science_changed":False,
    }
    (a.outdir/"source_receipt_v0_2.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
      "status":out["status"],
      "bytes":out["bytes"],
      "sha256":out["sha256"],
      "table_count":out["table_count"],
      "table_inventory":inv,
    },indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
