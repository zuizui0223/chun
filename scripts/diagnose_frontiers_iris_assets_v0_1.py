#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ARTICLE_ID = "569811"
PMC_NUMERIC = "7588356"
XML_URL = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={PMC_NUMERIC}&retmode=xml"
XLINK = "{http://www.w3.org/1999/xlink}href"
UA = "chun-iris-asset-diagnostic/0.1"
HOSTS = [
    "https://www.frontiersin.org/api/v4/articles",
    "https://public-pages-files-2025.frontiersin.org/articles",
]


def fetch(url: str) -> tuple[str, str, bytes]:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.geturl(), (r.headers.get("Content-Type") or "").split(";",1)[0].lower(), r.read()


def is_html(ct: str, b: bytes) -> bool:
    p=b[:300].lstrip().lower()
    return ct in {"text/html","application/xhtml+xml"} or p.startswith(b"<html") or p.startswith(b"<!doctype html") or b"<html" in p


def text(el):
    return " ".join("".join(el.itertext()).split()) if el is not None else ""


def supplements(xml: bytes):
    root=ET.fromstring(xml)
    out=[]
    for sm in root.findall(".//supplementary-material"):
        desc=f"{text(sm.find('label'))} {text(sm.find('caption'))}".strip()
        hrefs=[]
        for e in sm.iter():
            h=e.attrib.get(XLINK)
            if h: hrefs.append(h)
        out.append({"description":desc,"hrefs":hrefs})
    return out


def slug_variants(filename: str) -> list[str]:
    name=Path(filename).name
    stem=Path(name).stem
    ext=Path(name).suffix.lower().lstrip(".")
    s=re.sub(r"[^a-z0-9]+","_",stem.lower()).strip("_")
    variants=[
        f"{ARTICLE_ID}_{s}",
        f"{ARTICLE_ID}_supplementary-materials_{s}_{ext}",
    ]
    m=re.fullmatch(r"table[_-]?(\d+)", stem, flags=re.I)
    if m:
        n=m.group(1)
        variants += [
            f"{ARTICLE_ID}_table_{n}",
            f"{ARTICLE_ID}_supplementary-materials_tables_{n}_{ext}",
            f"{ARTICLE_ID}_supplementary-materials_table_{n}_{ext}",
        ]
    m=re.fullmatch(r"data[_-]?sheet[_-]?(\d+)", stem, flags=re.I)
    if m:
        n=m.group(1)
        variants += [
            f"{ARTICLE_ID}_data-sheet_{n}",
            f"{ARTICLE_ID}_supplementary-materials_datasheets_{n}_{ext}",
            f"{ARTICLE_ID}_supplementary-materials_data-sheet_{n}_{ext}",
        ]
    m=re.fullmatch(r"supplementary[_-]?material[_-]?(\d+)", stem, flags=re.I)
    if m:
        n=m.group(1)
        variants += [
            f"{ARTICLE_ID}_supplementary-material_{n}",
            f"{ARTICLE_ID}_supplementary-materials_{n}_{ext}",
        ]
    return list(dict.fromkeys(variants))


def diagnose(filename: str):
    attempts=[]
    successes=[]
    for host in HOSTS:
        for slug in slug_variants(filename):
            for ordinal in (1,2,3,4):
                url=f"{host}/{ARTICLE_ID}/file/{Path(filename).name}/{slug}/{ordinal}"
                try:
                    final,ct,b=fetch(url)
                    record={"url":url,"final_url":final,"content_type":ct,"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest(),"magic_hex":b[:16].hex(),"html":is_html(ct,b)}
                    attempts.append(record)
                    if len(b)>100 and not record["html"]:
                        successes.append(record)
                except Exception as e:
                    attempts.append({"url":url,"error":repr(e)})
    return {"filename":filename,"successes":successes,"attempts":attempts}


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    _,_,xml=fetch(XML_URL)
    supp=supplements(xml)
    target=[]
    for x in supp:
        if re.search(r"Supplementary\s+Table\s*1|Data table",x["description"],re.I) or re.search(r"Supplementary\s+Material\s*1|Accession numbers",x["description"],re.I):
            target.append(x)
    filenames=[]
    for x in target:
        for h in x["hrefs"]:
            filenames.append(Path(h).name)
    filenames=list(dict.fromkeys(filenames))
    result={
        "version":"v0.1",
        "status":"ASSET_ROUTE_DIAGNOSTIC_ONLY_NO_ROW_VALUES",
        "xml_supplement_targets":target,
        "filenames":filenames,
        "diagnostics":[diagnose(f) for f in filenames],
        "auc_computed":False,
        "row_level_values_emitted":False,
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
