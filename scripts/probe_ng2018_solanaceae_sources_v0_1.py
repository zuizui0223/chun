#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ARTICLE="https://academic.oup.com/evolut/article/72/12/2792/6726798"
SUPP_TOKEN="evo13589-sup-0002"
TREEBASE_ID="S23063"
UA="Mozilla/5.0 CHUN-Ng2018-source-probe/0.1"


def get(url:str,accept:str="*/*")->dict:
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":accept})
    try:
        with urllib.request.urlopen(req,timeout=120) as r:
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


def xlsxish(body:bytes)->bool:
    return bool(body.startswith(b"PK\x03\x04") and b"<html" not in body[:200].lower())


def extract_supplement_urls(body:bytes)->list[str]:
    text=body.decode("utf-8","replace")
    found=[]
    for m in re.finditer(r'''(?:href|data-url)=["']([^"']*%s[^"']*)["']''' % re.escape(SUPP_TOKEN),text,re.I):
        u=html.unescape(m.group(1))
        found.append(urllib.parse.urljoin(ARTICLE,u))
    # Some Silverchair pages JSON-escape URLs.
    for m in re.finditer(r'''https?:\\?/\\?/[^"'<> ]*%s[^"'<> ]*''' % re.escape(SUPP_TOKEN),text,re.I):
        u=html.unescape(m.group(0).replace("\\/","/"))
        found.append(u)
    return list(dict.fromkeys(found))


def treebase_candidate_urls(study_id:str)->list[str]:
    tb=f"TB2:{study_id}"
    q=urllib.parse.quote(tb,safe=":")
    return [
      f"https://treebase.org/treebase-web/phylows/study/{q}?format=nexml",
      f"https://treebase.org/treebase-web/phylows/study/{q}?format=nexus",
      f"http://purl.org/phylo/treebase/phylows/study/{q}?format=nexml",
      f"http://purl.org/phylo/treebase/phylows/study/{q}?format=nexus",
    ]


def treebase_payload(body:bytes)->bool:
    x=body.lstrip().lower()
    return bool(
      x.startswith(b"<?xml") or x.startswith(b"<nex") or x.startswith(b"#nexus")
    ) and b"<html" not in x[:500]


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    a.out.parent.mkdir(parents=True,exist_ok=True)

    article_attempts=[]
    supp_urls=[]
    for u in [ARTICLE,ARTICLE+"?login=false",ARTICLE+"?searchresult=1"]:
        r=get(u,"text/html,*/*")
        article_attempts.append({
          "url":u,"status":r["status"],"final_url":r["final_url"],
          "bytes":len(r["body"]),"reason":r.get("reason")
        })
        if r["ok"]:
            supp_urls.extend(extract_supplement_urls(r["body"]))
    supp_urls=list(dict.fromkeys(supp_urls))

    # Conservative static candidates are attempted only as source transport routes.
    supp_urls += [
      "https://academic.oup.com/evolut/article-supplement/doi/10.1111/evo.13589/suppl_file/evo13589-sup-0002-tables1.xlsx",
      "https://academic.oup.com/evolut/article-supplement/doi/10.1111/evo.13589/suppl_file/evo13589-sup-0002-TableS1.xlsx",
    ]
    supp_urls=list(dict.fromkeys(supp_urls))
    supp_attempts=[]
    supp_body=None
    supp_url=None
    for u in supp_urls:
        r=get(u)
        ok=bool(r["ok"] and xlsxish(r["body"]))
        supp_attempts.append({
          "url":u,"status":r["status"],"final_url":r["final_url"],
          "bytes":len(r["body"]),
          "sha256":hashlib.sha256(r["body"]).hexdigest() if r["body"] else None,
          "xlsxish":xlsxish(r["body"]),
          "accepted":ok,
          "reason":r.get("reason")
        })
        if ok:
            supp_body=r["body"]; supp_url=r["final_url"]; break

    tree_attempts=[]
    tree_body=None
    tree_url=None
    for u in treebase_candidate_urls(TREEBASE_ID):
        r=get(u,"application/xml,application/nexml+xml,text/plain,*/*")
        ok=bool(r["ok"] and treebase_payload(r["body"]))
        tree_attempts.append({
          "url":u,"status":r["status"],"final_url":r["final_url"],
          "bytes":len(r["body"]),
          "sha256":hashlib.sha256(r["body"]).hexdigest() if r["body"] else None,
          "treebase_payload":treebase_payload(r["body"]),
          "accepted":ok,
          "reason":r.get("reason")
        })
        if ok:
            tree_body=r["body"]; tree_url=r["final_url"]; break

    if supp_body is not None:
        (a.out.parent/"ng2018_TableS1_source.xlsx").write_bytes(supp_body)
    if tree_body is not None:
        (a.out.parent/"ng2018_TreeBASE_S23063_source").write_bytes(tree_body)

    if supp_body is not None and tree_body is not None:
        status="NG2018_EXACT_PUBLIC_SOURCE_OBJECTS_RECOVERED_SCHEMA_PREFLIGHT_PENDING"
    elif supp_body is not None:
        status="HOLD_NG2018_TREEBASE_SOURCE_UNAVAILABLE"
    elif tree_body is not None:
        status="HOLD_NG2018_TRAIT_SUPPLEMENT_SOURCE_UNAVAILABLE"
    else:
        status="HOLD_NG2018_PUBLIC_SOURCE_OBJECTS_UNAVAILABLE"

    out={
      "version":"v0.1",
      "status":status,
      "article_doi":"10.1111/evo.13589",
      "trait_supplement":{
        "expected_label":"evo13589-sup-0002-TableS1",
        "expected_format":"xlsx",
        "recovered":supp_body is not None,
        "recovered_url":supp_url,
        "bytes":len(supp_body) if supp_body is not None else None,
        "sha256":hashlib.sha256(supp_body).hexdigest() if supp_body is not None else None,
        "article_attempts":article_attempts,
        "candidate_urls":supp_urls,
        "attempts":supp_attempts
      },
      "phylogeny":{
        "repository":"TreeBASE",
        "submission_id":TREEBASE_ID,
        "recovered_study_object":tree_body is not None,
        "recovered_url":tree_url,
        "bytes":len(tree_body) if tree_body is not None else None,
        "sha256":hashlib.sha256(tree_body).hexdigest() if tree_body is not None else None,
        "attempts":tree_attempts
      },
      "trait_rows_opened":False,
      "trait_column_names_opened":False,
      "trait_state_frequencies_computed":False,
      "tree_labels_opened":False,
      "tree_selected_from_submission":False,
      "hidden_memory_auc_computed":False,
      "next_gate":("INSPECT_XLSX_SHEET_AND_HEADER_PLUS_TREEBASE_TREE_METADATA_ONLY"
                   if status=="NG2018_EXACT_PUBLIC_SOURCE_OBJECTS_RECOVERED_SCHEMA_PREFLIGHT_PENDING"
                   else "STOP_HOLD"),
      "el_v0_3_science_changed":False,
      "v0_8_promotion_state_changed":False,
      "paper1_science_changed":False
    }
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
      "status":status,
      "trait_recovered":supp_body is not None,
      "treebase_recovered":tree_body is not None,
      "trait_bytes":out["trait_supplement"]["bytes"],
      "treebase_bytes":out["phylogeny"]["bytes"]
    },indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
