#!/usr/bin/env python3
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

DOI="10.1111/plb.12649"
ARTICLE="https://onlinelibrary.wiley.com/doi/10.1111/plb.12649"
FILES={
    "chemistry":{"filename":"plb12649-sup-0001-TableS1-S2.xlsx","kind":"xlsx","publisher_size_label":"19.5 KB"},
    "species":{"filename":"plb12649-sup-0002-TableS3.docx","kind":"docx","publisher_size_label":"35.9 KB"},
}
UA="Mozilla/5.0 CHUN-Rhododendron30-Wiley-recovery/0.6"
TIMEOUT=20


def get(url:str,accept:str="*/*",referer:str|None=None,timeout:int=TIMEOUT)->dict:
    headers={"User-Agent":UA,"Accept":accept,"Accept-Language":"en-US,en;q=0.9"}
    if referer:
        headers["Referer"]=referer
    req=urllib.request.Request(url,headers=headers)
    try:
        with urllib.request.urlopen(req,timeout=timeout) as r:
            return {"ok":True,"status":getattr(r,"status",200),"final_url":r.geturl(),
                    "headers":dict(r.headers),"body":r.read()}
    except urllib.error.HTTPError as e:
        try: body=e.read()
        except Exception: body=b""
        return {"ok":False,"status":e.code,"final_url":e.geturl(),
                "headers":dict(e.headers or {}),"body":body,"reason":str(e.reason)}
    except Exception as e:
        return {"ok":False,"status":None,"final_url":url,"headers":{},
                "body":b"","reason":repr(e)}


def sha256(body:bytes)->str:
    return hashlib.sha256(body).hexdigest()


def valid_office(body:bytes,kind:str)->bool:
    if len(body)<4 or not body.startswith(b"PK\x03\x04"):
        return False
    try:
        with zipfile.ZipFile(io.BytesIO(body)) as z:
            names=set(z.namelist())
    except Exception:
        return False
    if "[Content_Types].xml" not in names:
        return False
    return ("xl/workbook.xml" in names) if kind=="xlsx" else ("word/document.xml" in names)


def extract_filename_urls(text_body:bytes,filename:str,base_url:str)->list[str]:
    text=text_body.decode("utf-8","replace")
    found=[]
    patterns=[
        r'''(?:href|data-url)=["']([^"']*%s[^"']*)["']''' % re.escape(filename),
        r'''https?://[^"'<>\s)]*%s[^"'<>\s)]*''' % re.escape(filename),
    ]
    for pat in patterns:
        for m in re.finditer(pat,text,re.I):
            u=html.unescape(m.group(1) if m.lastindex else m.group(0)).replace("\\/","/")
            found.append(urllib.parse.urljoin(base_url,u))
    return list(dict.fromkeys(found))


def canonical_url(filename:str)->str:
    return (
        "https://onlinelibrary.wiley.com/action/downloadSupplement?"
        f"doi={urllib.parse.quote(DOI,safe='')}&file={urllib.parse.quote(filename,safe='')}"
    )


def direct_candidates(filename:str)->list[str]:
    return list(dict.fromkeys([
        canonical_url(filename),
        f"https://onlinelibrary.wiley.com/doi/suppl/{DOI}/supinfo/{filename}",
        f"https://onlinelibrary.wiley.com/doi/supinfo/{DOI}/supinfo/{filename}",
    ]))


def cdx_url(original:str)->str:
    q=urllib.parse.quote(original,safe="")
    return (
        "https://web.archive.org/cdx/search/cdx?"
        f"url={q}&output=json&fl=timestamp,original,statuscode,mimetype,digest,length"
        "&filter=statuscode:200&collapse=digest"
    )


def parse_cdx(body:bytes)->list[dict]:
    try:
        data=json.loads(body.decode("utf-8"))
    except Exception:
        return []
    if not isinstance(data,list) or len(data)<2 or not isinstance(data[0],list):
        return []
    header=data[0]
    return [dict(zip(header,row)) for row in data[1:] if isinstance(row,list) and len(row)==len(header)]


def bounded_archive_candidates(rows:list[dict])->list[str]:
    if not rows:
        return []
    chosen=[rows[0]]
    if len(rows)>1:
        chosen.append(rows[-1])
    out=[]
    for row in chosen:
        ts=row.get("timestamp"); original=row.get("original")
        if ts and original:
            out.append(f"https://web.archive.org/web/{ts}id_/{original}")
    return list(dict.fromkeys(out))


def recover_one(label:str,spec:dict,article_body:bytes,article_final_url:str)->dict:
    filename=spec["filename"]; kind=spec["kind"]
    discovered=extract_filename_urls(article_body,filename,article_final_url) if article_body else []
    candidates=list(dict.fromkeys(discovered+direct_candidates(filename)))[:4]

    direct_attempts=[]; recovered=None; recovered_from=None
    for url in candidates:
        r=get(url,"*/*",ARTICLE)
        valid=bool(r["ok"] and valid_office(r["body"],kind))
        direct_attempts.append({
            "url":url,"status":r["status"],"final_url":r["final_url"],"bytes":len(r["body"]),
            "content_type":r["headers"].get("Content-Type"),
            "sha256":sha256(r["body"]) if r["body"] else None,
            "valid_office_payload":valid,"reason":r.get("reason"),
        })
        if valid:
            recovered=r["body"]; recovered_from=r["final_url"]; break

    cdx_attempt=None; archive_attempts=[]
    if recovered is None:
        c=get(cdx_url(canonical_url(filename)),"application/json,*/*")
        rows=parse_cdx(c["body"]) if c["ok"] else []
        cdx_attempt={"url":cdx_url(canonical_url(filename)),"status":c["status"],
                     "bytes":len(c["body"]),"snapshot_rows":len(rows),"reason":c.get("reason")}
        for snap in bounded_archive_candidates(rows):
            r=get(snap,"*/*")
            valid=bool(r["ok"] and valid_office(r["body"],kind))
            archive_attempts.append({
                "url":snap,"status":r["status"],"final_url":r["final_url"],"bytes":len(r["body"]),
                "content_type":r["headers"].get("Content-Type"),
                "sha256":sha256(r["body"]) if r["body"] else None,
                "valid_office_payload":valid,"reason":r.get("reason"),
            })
            if valid:
                recovered=r["body"]; recovered_from=r["final_url"]; break

    return {
        "label":label,"filename":filename,"kind":kind,
        "publisher_size_label":spec["publisher_size_label"],
        "discovered_urls":discovered,"candidate_urls":candidates,
        "direct_attempts":direct_attempts,"cdx_attempt":cdx_attempt,
        "archive_attempts":archive_attempts,
        "recovered":recovered is not None,"recovered_from":recovered_from,
        "bytes":len(recovered) if recovered is not None else None,
        "sha256":sha256(recovered) if recovered is not None else None,
        "_body":recovered,
    }


def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("--out",type=Path,required=True); a=ap.parse_args()
    a.out.parent.mkdir(parents=True,exist_ok=True)

    page=get(ARTICLE,"text/html,*/*")
    article_body=page["body"] if page["ok"] else b""
    article_final=page["final_url"] if page["ok"] else ARTICLE
    results={label:recover_one(label,spec,article_body,article_final) for label,spec in FILES.items()}

    chemistry_ready=results["chemistry"]["recovered"]; species_ready=results["species"]["recovered"]
    if chemistry_ready and species_ready:
        status="RHODODENDRON30_WILEY_SUPPLEMENTS_RECOVERED_OUTCOMES_UNOPENED"
        next_gate="FREEZE_RECOVERED_HASHES_THEN_OPEN_SPECIES_IDENTIFIER_COLUMN_ONLY"
    elif chemistry_ready:
        status="HOLD_RHODODENDRON30_TABLE_S3_STILL_UNAVAILABLE"; next_gate="STOP_HOLD"
    elif species_ready:
        status="HOLD_RHODENDRON30_CHEMISTRY_TABLE_STILL_UNAVAILABLE"; next_gate="STOP_HOLD"
    else:
        status="HOLD_RHODODENDRON30_WILEY_SUPPLEMENTS_STILL_UNAVAILABLE"; next_gate="STOP_HOLD"

    for item in results.values():
        body=item.pop("_body")
        if body is not None:
            (a.out.parent/item["filename"]).write_bytes(body)

    firewall={
        "species_rows_opened":False,"chemistry_workbook_opened":False,
        "row_level_anthocyanin_values_opened":False,"compound_states_computed":False,
        "state_frequencies_computed":False,"profile_auc_computed":False,"hidden_memory_auc_computed":False,
    }
    out={
        "version":"v0.6","status":status,"article_doi":DOI,"article_url":ARTICLE,
        "article_probe":{"status":page["status"],"final_url":page["final_url"],"bytes":len(page["body"]),"reason":page.get("reason")},
        "files":results,"outcome_firewall":firewall,
        "primary_tree_already_recovered_exact":True,
        "primary_tree_sha256":"784011d0e2e17df9ea21eb22d31197bad29219a37ac213fda013766e29b51362",
        "next_gate":next_gate,"paper1_science_changed":False,"el_v0_3_science_changed":False,
        "v0_8_promotion_state_changed":False,
    }
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "status":status,"chemistry_recovered":chemistry_ready,"species_recovered":species_ready,
        "chemistry_direct_statuses":[x["status"] for x in results["chemistry"]["direct_attempts"]],
        "chemistry_cdx":results["chemistry"]["cdx_attempt"],
        "chemistry_archive_statuses":[x["status"] for x in results["chemistry"]["archive_attempts"]],
        "species_direct_statuses":[x["status"] for x in results["species"]["direct_attempts"]],
        "species_cdx":results["species"]["cdx_attempt"],
        "species_archive_statuses":[x["status"] for x in results["species"]["archive_attempts"]],
        "next_gate":next_gate,"outcome_firewall":firewall,
    },indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
