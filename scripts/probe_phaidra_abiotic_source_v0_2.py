#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

BASES=[
    "https://services.phaidra.univie.ac.at/api",
    "https://phaidra.univie.ac.at/api",
]
ROOTS=[
    {"pid":"o:2098641","provenance":"article_data_availability_statement"},
    {"pid":"o:2322953","provenance":"current_university_publication_record"},
]
ARTICLE_DOI="10.1002/ajb2.70044"
ARTICLE_TITLE="Does the abiotic environment influence the distribution of flower and fruit colors?"
UA="CHUN-PHAIDRA-abiotic-recovery/0.2"

SEARCH_PATHS=("search/select","solr/select")
MEMBERSHIP_FIELDS=("isPartOf","ismemberof")


def get_json(url:str,timeout:int=60)->tuple[Any|None,dict]:
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/json,*/*"})
    try:
        with urllib.request.urlopen(req,timeout=timeout) as r:
            raw=r.read()
            diag={
                "url":url,
                "http_status":getattr(r,"status",200),
                "bytes":len(raw),
                "content_type":r.headers.get("Content-Type"),
                "final_url":r.geturl(),
            }
            try:
                return json.loads(raw.decode("utf-8")),diag
            except Exception as e:
                diag["parse_error"]=f"{type(e).__name__}: {e}"
                diag["prefix"]=raw[:200].decode("utf-8","replace")
                return None,diag
    except Exception as e:
        return None,{"url":url,"error":f"{type(e).__name__}: {e}"}


def walk(x:Any):
    if isinstance(x,dict):
        for k,v in x.items():
            yield k,v
            yield from walk(v)
    elif isinstance(x,list):
        for v in x:
            yield from walk(v)


def first_string(payload:Any,keys:tuple[str,...])->str|None:
    for k,v in walk(payload):
        if k not in keys:
            continue
        if isinstance(v,str):
            return v
        if isinstance(v,(int,float)):
            return str(v)
        if isinstance(v,list):
            stack=list(v)
            while stack:
                z=stack.pop(0)
                if isinstance(z,str):
                    return z
                if isinstance(z,dict):
                    if "@value" in z and isinstance(z["@value"],str):
                        return z["@value"]
                    stack.extend(z.values())
                elif isinstance(z,list):
                    stack.extend(z)
    return None


def extract_pids(payload:Any)->list[str]:
    found=set()
    def visit(x:Any):
        if isinstance(x,str):
            for m in re.finditer(r"\bo:\d+\b",x):
                found.add(m.group(0))
        elif isinstance(x,dict):
            for k,v in x.items():
                if k.lower()=="pid" and isinstance(v,str) and re.fullmatch(r"o:\d+",v):
                    found.add(v)
                visit(v)
        elif isinstance(x,list):
            for v in x:
                visit(v)
    visit(payload)
    return sorted(found,key=lambda s:int(s.split(":")[1]))


def relevant_text(*parts:Any)->bool:
    text=" ".join(str(x or "") for x in parts).lower()
    tokens=(
        "does the abiotic environment",
        "ajb2.70044",
        "dellinger",
        "flower",
        "fruit",
        "color",
        "colour",
        "temperature",
        "aridity",
        "uv-b",
        "ultraviolet",
        "clim",
        "environment",
        "gbif",
        ".csv",
        ".rds",
        ".rdata",
        ".rda",
        ".zip",
        ".r",
    )
    return any(t in text for t in tokens)


def summarize_payload(pid:str,payload:Any)->dict:
    filename=first_string(payload,("ebucore:filename","filename"))
    title=first_string(payload,("bf:mainTitle","dc_title","title","dce:title"))
    mimetype=first_string(payload,("ebucore:hasMimeType","mimetype","mime"))
    description=first_string(payload,("dc_description","description","dcterms:description","bf:Summary"))
    doi=first_string(payload,("doi","dc_identifier","dcterms:identifier"))
    resource=first_string(payload,("resourcetype","cmodel","type","dcterms:type"))
    pids=extract_pids(payload)
    return {
        "pid":pid,
        "filename":filename,
        "title":title,
        "mimetype":mimetype,
        "description":description,
        "doi_or_identifier":doi,
        "resource_type":resource,
        "related_pids":[x for x in pids if x!=pid],
        "article_or_environment_relevant":relevant_text(filename,title,description,doi),
    }


def object_info(pid:str)->tuple[dict|None,list[dict]]:
    diagnostics=[]
    for base in BASES:
        for token in (pid,urllib.parse.quote(pid,safe="")):
            payload,diag=get_json(f"{base}/object/{token}/info")
            diagnostics.append(diag)
            if payload is not None:
                return summarize_payload(pid,payload),diagnostics
    return None,diagnostics


def search(base:str,path:str,q:str="*:*",fq:str|None=None,rows:int=500)->tuple[Any|None,dict]:
    params={"q":q,"rows":str(rows),"wt":"json"}
    if fq is not None:
        params["fq"]=fq
    return get_json(f"{base}/{path}?{urllib.parse.urlencode(params)}")


def membership_queries(root_pid:str)->tuple[list[str],list[dict]]:
    found=set()
    diagnostics=[]
    values=[
        root_pid,
        f"info:fedora/{root_pid}",
        f"https://phaidra.univie.ac.at/{root_pid}",
    ]
    for base in BASES:
        for path in SEARCH_PATHS:
            for field in MEMBERSHIP_FIELDS:
                for value in values:
                    payload,diag=search(base,path,q="*:*",fq=f'{field}:"{value}"')
                    diag.update({"query_kind":"membership","root_pid":root_pid,"field":field,"value":value})
                    diagnostics.append(diag)
                    if payload is not None:
                        found.update(extract_pids(payload))
    found.discard(root_pid)
    return sorted(found,key=lambda s:int(s.split(":")[1])),diagnostics


def global_discovery()->tuple[list[str],list[dict]]:
    queries=[
        ARTICLE_DOI,
        f'"{ARTICLE_DOI}"',
        '"Does the abiotic environment influence the distribution of flower and fruit colors"',
        "Dellinger flower fruit color",
        "Dellinger abiotic environment flower fruit",
    ]
    found=set()
    diagnostics=[]
    for base in BASES:
        for path in SEARCH_PATHS:
            for q in queries:
                payload,diag=search(base,path,q=q,rows=200)
                diag.update({"query_kind":"global","query":q})
                diagnostics.append(diag)
                if payload is not None:
                    found.update(extract_pids(payload))
    return sorted(found,key=lambda s:int(s.split(":")[1])),diagnostics


def bounded_expand(seed_pids:list[str],limit:int=250)->tuple[list[dict],list[dict]]:
    queue=list(dict.fromkeys(seed_pids))
    seen=set()
    objects=[]
    diagnostics=[]
    while queue and len(seen)<limit:
        pid=queue.pop(0)
        if pid in seen:
            continue
        seen.add(pid)
        info,diags=object_info(pid)
        diagnostics.extend(diags)
        if info is None:
            objects.append({"pid":pid,"metadata_ready":False})
            continue
        info["metadata_ready"]=True
        objects.append(info)
        for rp in info["related_pids"]:
            if rp not in seen and rp not in queue and len(queue)+len(seen)<limit:
                queue.append(rp)
    return objects,diagnostics


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    a.out.parent.mkdir(parents=True,exist_ok=True)

    root_rows=[]
    seed_pids=[r["pid"] for r in ROOTS]
    all_diags=[]
    for root in ROOTS:
        info,diags=object_info(root["pid"])
        members,mdiags=membership_queries(root["pid"])
        all_diags.extend(diags); all_diags.extend(mdiags)
        root_rows.append({
            **root,
            "metadata":info,
            "member_pids":members,
            "member_count":len(members),
        })
        seed_pids.extend(members)

    discovered,gdiags=global_discovery()
    all_diags.extend(gdiags)
    seed_pids.extend(discovered)

    objects,odiags=bounded_expand(seed_pids)
    all_diags.extend(odiags)
    relevant=[x for x in objects if x.get("article_or_environment_relevant")]
    filelike=[
        x for x in relevant
        if x.get("filename") or any(
            z in str(x.get("mimetype") or "").lower()
            for z in ("csv","zip","r-","octet-stream","text/")
        )
    ]

    if filelike:
        status="PHAIDRA_ABIOTIC_RELEVANT_FILE_METADATA_RECOVERED"
        next_gate="FREEZE_EXACT_RELEVANT_MEMBER_IDENTITIES_BEFORE_CONTENT_OPENING"
    elif relevant:
        status="PHAIDRA_ABIOTIC_RELEVANT_OBJECT_METADATA_RECOVERED_NO_FILE_IDENTITY"
        next_gate="FOLLOW_RELEVANT_RELATIONSHIPS_METADATA_ONLY"
    elif any(r["metadata"] or r["member_count"] for r in root_rows) or discovered:
        status="HOLD_PHAIDRA_METADATA_RECOVERED_BUT_ARTICLE_DATA_FILES_NOT_IDENTIFIED"
        next_gate="STOP_HOLD"
    else:
        status="HOLD_PHAIDRA_SOURCE_METADATA_STILL_UNAVAILABLE"
        next_gate="STOP_HOLD"

    out={
        "version":"v0.2",
        "status":status,
        "article_doi":ARTICLE_DOI,
        "article_title":ARTICLE_TITLE,
        "root_candidates":root_rows,
        "global_discovered_pids":discovered,
        "inspected_object_count":len(objects),
        "relevant_objects":relevant,
        "relevant_filelike_objects":filelike,
        "search_contract":{
            "search_paths":list(SEARCH_PATHS),
            "membership_fields":list(MEMBERSHIP_FIELDS),
            "membership_value_forms":["o:PID","info:fedora/o:PID","https://phaidra.univie.ac.at/o:PID"],
            "bounded_object_limit":250,
        },
        "diagnostics":all_diags,
        "next_gate":next_gate,
        "outcome_firewall":{
            "member_file_contents_downloaded":False,
            "environmental_rows_opened":False,
            "flower_memory_outcome_fit":False,
        },
        "paper1_science_changed":False,
        "el_v0_3_science_changed":False,
    }
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "status":status,
        "roots":[{"pid":r["pid"],"metadata_ready":r["metadata"] is not None,"member_count":r["member_count"]} for r in root_rows],
        "global_discovered_pids":discovered,
        "inspected_object_count":len(objects),
        "relevant_objects":relevant,
        "relevant_filelike_objects":filelike,
        "next_gate":next_gate,
    },indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
