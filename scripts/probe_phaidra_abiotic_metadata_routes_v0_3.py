#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

PIDS=["o:2098641","o:2322953"]
UA="CHUN-PHAIDRA-metadata-route-diagnostic/0.3"

def get(url:str,accept:str="*/*",timeout:int=15)->dict:
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":accept})
    try:
        with urllib.request.urlopen(req,timeout=timeout) as r:
            b=r.read()
            return {
                "url":url,"ok":True,"status":getattr(r,"status",200),
                "final_url":r.geturl(),"content_type":r.headers.get("Content-Type"),
                "bytes":len(b),"body":b
            }
    except urllib.error.HTTPError as e:
        try:b=e.read()
        except Exception:b=b""
        return {
            "url":url,"ok":False,"status":e.code,"final_url":e.geturl(),
            "content_type":(e.headers or {}).get("Content-Type"),"bytes":len(b),
            "error":f"HTTPError: {e.reason}","body":b
        }
    except Exception as e:
        return {"url":url,"ok":False,"status":None,"bytes":0,
                "error":f"{type(e).__name__}: {e}","body":b""}

def parse_json(body:bytes):
    try:return json.loads(body.decode("utf-8"))
    except Exception:return None

def body_summary(body:bytes)->dict:
    text=body[:200000].decode("utf-8","replace")
    pids=sorted(set(re.findall(r"\bo:\d+\b",text)),key=lambda s:int(s.split(":")[1]))
    filenames=sorted(set(re.findall(r"""[A-Za-z0-9_.()' -]+\.(?:csv|tsv|txt|zip|rds|rda|rdata|r|xlsx|docx)""",text,re.I)))
    low=text.lower()
    return {
        "contains_target_title": "does the abiotic environment influence the distribution of flower and fruit colors" in low,
        "contains_article_doi": "10.1002/ajb2.70044" in low,
        "pids":pids[:200],
        "filenames":filenames[:200],
        "prefix":text[:500],
    }

def routes(pid:str)->list[tuple[str,str]]:
    enc=urllib.parse.quote(pid,safe="")
    num=pid.split(":")[1]
    return [
        ("services_info",f"https://services.phaidra.univie.ac.at/api/object/{pid}/info"),
        ("services_metadata",f"https://services.phaidra.univie.ac.at/api/object/{pid}/metadata"),
        ("services_jsonld",f"https://services.phaidra.univie.ac.at/api/object/{pid}/datastream/JSON-LD"),
        ("services_info_encoded",f"https://services.phaidra.univie.ac.at/api/object/{enc}/info"),
        ("services_metadata_encoded",f"https://services.phaidra.univie.ac.at/api/object/{enc}/metadata"),
        ("frontend_detail",f"https://phaidra.univie.ac.at/detail/{enc}"),
        ("frontend_object",f"https://phaidra.univie.ac.at/{pid}"),
        ("handle_api",f"https://hdl.handle.net/api/handles/11353/10.{num}"),
        ("handle_resolver",f"https://hdl.handle.net/11353/10.{num}"),
        ("oai_simple",f"https://services.phaidra.univie.ac.at/api/oai?verb=GetRecord&metadataPrefix=oai_dc&identifier={urllib.parse.quote(pid)}"),
        ("oai_prefixed",f"https://services.phaidra.univie.ac.at/api/oai?verb=GetRecord&metadataPrefix=oai_dc&identifier={urllib.parse.quote('oai:phaidra.univie.ac.at:'+pid)}"),
    ]

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args(); a.out.parent.mkdir(parents=True,exist_ok=True)

    per_pid=[]
    any_metadata=False
    discovered=set()
    for pid in PIDS:
        attempts=[]
        for label,url in routes(pid):
            r=get(url)
            body=r.pop("body")
            parsed=parse_json(body)
            summ=body_summary(body)
            if parsed is not None:
                summ["json_top_type"]=type(parsed).__name__
            candidate=bool(
                r.get("ok") and (
                    parsed is not None or summ["contains_target_title"] or summ["contains_article_doi"]
                    or summ["pids"] or summ["filenames"]
                )
            )
            if candidate:
                any_metadata=True
                discovered.update(summ["pids"])
            attempts.append({"label":label,**r,"candidate_metadata_response":candidate,"summary":summ})
        per_pid.append({"pid":pid,"attempts":attempts})

    status=("PHAIDRA_ALTERNATE_METADATA_ROUTE_RECOVERED"
            if any_metadata else "HOLD_PHAIDRA_ALTERNATE_METADATA_ROUTES_UNAVAILABLE")
    out={
        "version":"v0.3",
        "status":status,
        "pids":PIDS,
        "route_results":per_pid,
        "discovered_pids":sorted(discovered,key=lambda s:int(s.split(":")[1])),
        "outcome_firewall":{
            "content_download_routes_called":False,
            "member_file_contents_opened":False,
            "environmental_rows_opened":False,
            "flower_memory_outcome_fit":False
        },
        "next_gate":("INSPECT_RECOVERED_METADATA_RELATIONSHIPS_ONLY" if any_metadata else "STOP_HOLD"),
        "paper1_science_changed":False,
        "el_v0_3_science_changed":False
    }
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "status":status,
        "discovered_pids":out["discovered_pids"],
        "attempts":[
            {"pid":x["pid"],"routes":[
                {"label":z["label"],"status":z.get("status"),"ok":z.get("ok"),
                 "bytes":z.get("bytes"),"content_type":z.get("content_type"),
                 "error":z.get("error"),"candidate":z["candidate_metadata_response"],
                 "contains_doi":z["summary"]["contains_article_doi"],
                 "filenames":z["summary"]["filenames"][:10],
                 "pids":z["summary"]["pids"][:20]}
                for z in x["attempts"]
            ]} for x in per_pid
        ],
        "next_gate":out["next_gate"]
    },indent=2,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
