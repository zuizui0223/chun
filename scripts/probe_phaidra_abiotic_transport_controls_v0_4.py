#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

TARGETS=[
    {"pid":"o:2098641","role":"article_data_availability"},
    {"pid":"o:2322953","role":"current_university_record"},
]
CONTROL_OBJECT="o:295002"
CONTROL_COLLECTION="o:295028"
UA="CHUN-PHAIDRA-transport-control/0.4"
SERVICES="https://services.phaidra.univie.ac.at/api"
FRONT_API="https://phaidra.univie.ac.at/api"

def request(url:str,method:str="GET",accept:str="*/*",timeout:int=25)->dict:
    req=urllib.request.Request(url,method=method,headers={"User-Agent":UA,"Accept":accept})
    try:
        with urllib.request.urlopen(req,timeout=timeout) as r:
            body=b"" if method=="HEAD" else r.read()
            return {
                "url":url,"method":method,"ok":True,
                "status":getattr(r,"status",200),"final_url":r.geturl(),
                "content_type":r.headers.get("Content-Type"),
                "content_length":r.headers.get("Content-Length"),
                "content_disposition":r.headers.get("Content-Disposition"),
                "etag":r.headers.get("ETag"),
                "last_modified":r.headers.get("Last-Modified"),
                "location":r.headers.get("Location"),
                "bytes":len(body),"body":body,
            }
    except urllib.error.HTTPError as e:
        try: body=b"" if method=="HEAD" else e.read()
        except Exception: body=b""
        return {
            "url":url,"method":method,"ok":False,"status":e.code,
            "final_url":e.geturl(),"content_type":(e.headers or {}).get("Content-Type"),
            "content_length":(e.headers or {}).get("Content-Length"),
            "content_disposition":(e.headers or {}).get("Content-Disposition"),
            "etag":(e.headers or {}).get("ETag"),
            "last_modified":(e.headers or {}).get("Last-Modified"),
            "location":(e.headers or {}).get("Location"),
            "bytes":len(body),"error":f"HTTPError: {e.reason}","body":body,
        }
    except Exception as e:
        return {"url":url,"method":method,"ok":False,"status":None,"bytes":0,
                "error":f"{type(e).__name__}: {e}","body":b""}

def strip_body(x:dict)->dict:
    y=dict(x); y.pop("body",None); return y

def parse_json(body:bytes):
    try:return json.loads(body.decode("utf-8"))
    except Exception:return None

def handle_urls(pid:str)->list[str]:
    n=pid.split(":")[1]
    return [
        f"https://hdl.handle.net/api/handles/11353/10.{n}",
        f"https://hdl.handle.net/11353/10.{n}",
    ]

def metadata_gets(pid:str)->list[dict]:
    out=[]
    for base in (SERVICES,FRONT_API):
        out.append(request(f"{base}/object/{pid}/info","GET","application/json,*/*"))
        out.append(request(f"{base}/object/{pid}/uwmetadata?format=xml","GET","application/xml,text/xml,*/*"))
    return out

def download_heads(pid:str)->list[dict]:
    enc=urllib.parse.quote(pid,safe="")
    out=[]
    for base in (SERVICES,FRONT_API):
        for token in (pid,enc):
            out.append(request(f"{base}/object/{token}/download","HEAD"))
    return out

def handle_diagnostic(pid:str)->list[dict]:
    out=[]
    for u in handle_urls(pid):
        r=request(u,"GET","application/json,text/html,*/*")
        body=r.pop("body")
        parsed=parse_json(body)
        values=[]
        if isinstance(parsed,dict):
            for v in parsed.get("values",[]) or []:
                data=v.get("data",{}) if isinstance(v,dict) else {}
                values.append({
                    "index":v.get("index"),
                    "type":v.get("type"),
                    "data_type":data.get("format"),
                    "value":data.get("value"),
                })
        r["json_values"]=values
        r["body_prefix"]=body[:500].decode("utf-8","replace")
        out.append(r)
    return out

def control_collection_search()->list[dict]:
    out=[]
    values=[
        CONTROL_COLLECTION,
        f"info:fedora/{CONTROL_COLLECTION}",
        f"https://phaidra.univie.ac.at/{CONTROL_COLLECTION}",
    ]
    for path in ("search/select","solr/select"):
        for field in ("ispartof","ismemberof","isPartOf"):
            for val in values:
                params={"q":"*:*","fq":f'{field}:"{val}"',"rows":"10","wt":"json"}
                r=request(f"{SERVICES}/{path}?{urllib.parse.urlencode(params)}","GET","application/json,*/*")
                body=r.pop("body")
                parsed=parse_json(body)
                num=None
                docs=None
                if isinstance(parsed,dict):
                    resp=parsed.get("response")
                    if isinstance(resp,dict):
                        num=resp.get("numFound")
                        if isinstance(resp.get("docs"),list):
                            docs=len(resp["docs"])
                r.update({"field":field,"value":val,"num_found":num,"docs_returned":docs})
                out.append(r)
    return out

def classify_head(rows:list[dict])->dict:
    informative=[]
    for r in rows:
        ctype=(r.get("content_type") or "").lower()
        disp=r.get("content_disposition") or ""
        clen=r.get("content_length")
        if r.get("ok") and (disp or clen not in (None,"0",0) or ctype not in ("","text/html; charset=utf-8","text/html")):
            informative.append({
                "final_url":r.get("final_url"),"content_type":r.get("content_type"),
                "content_length":clen,"content_disposition":disp,
                "etag":r.get("etag"),"last_modified":r.get("last_modified"),
            })
    return {"informative":bool(informative),"records":informative}

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args(); a.out.parent.mkdir(parents=True,exist_ok=True)

    control_meta=metadata_gets(CONTROL_OBJECT)
    control_search=control_collection_search()

    targets=[]
    for t in TARGETS:
        mh=metadata_gets(t["pid"])
        dh=download_heads(t["pid"])
        hh=handle_diagnostic(t["pid"])
        targets.append({
            **t,
            "metadata_routes":[strip_body(x) for x in mh],
            "download_heads":[strip_body(x) for x in dh],
            "download_head_identity":classify_head(dh),
            "handle_routes":hh,
        })

    control_nonempty=any(x.get("ok") and x.get("bytes",0)>0 for x in control_meta)
    control_members=any(isinstance(x.get("num_found"),int) and x["num_found"]>0 for x in control_search)
    target_head_identity=any(x["download_head_identity"]["informative"] for x in targets)

    if target_head_identity:
        status="PHAIDRA_TARGET_DOWNLOAD_HEAD_IDENTIFIES_ROOT_OBJECT"
        next_gate="FREEZE_ROOT_DOWNLOAD_IDENTITY_BEFORE_ANY_BODY_OPENING"
    elif control_nonempty or control_members:
        status="HOLD_PHAIDRA_TARGET_METADATA_SPECIFICALLY_UNAVAILABLE_CONTROL_WORKS"
        next_gate="STOP_HOLD"
    else:
        status="HOLD_PHAIDRA_API_RESPONSE_LAYER_NONDIAGNOSTIC_TARGET_AND_CONTROL"
        next_gate="STOP_HOLD"

    out={
        "version":"v0.4",
        "status":status,
        "targets":targets,
        "controls":{
            "object_pid":CONTROL_OBJECT,
            "metadata_routes":[strip_body(x) for x in control_meta],
            "metadata_nonempty":control_nonempty,
            "collection_pid":CONTROL_COLLECTION,
            "collection_search":[strip_body(x) for x in control_search],
            "collection_has_members":control_members,
        },
        "outcome_firewall":{
            "download_body_get_called":False,
            "target_file_content_opened":False,
            "environmental_rows_opened":False,
            "flower_memory_outcome_fit":False,
        },
        "next_gate":next_gate,
        "paper1_science_changed":False,
        "el_v0_3_science_changed":False,
    }
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "status":status,
        "control_metadata_nonempty":control_nonempty,
        "control_collection_has_members":control_members,
        "targets":[{
            "pid":x["pid"],
            "download_head_identity":x["download_head_identity"],
            "handle_routes":x["handle_routes"],
            "metadata_routes":x["metadata_routes"],
        } for x in targets],
        "next_gate":next_gate,
    },indent=2,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
