#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from Bio import Phylo

DOI="10.5061/dryad.47d7wm3f4"
API="https://datadryad.org/api/v2"
UA="CHUN-Schistanthe-source-recovery/0.1"

COLOR={
    "name":"Vireya_RADsamples_tiplabels_ingroup_color_clade.csv",
    "file_id":3623568,
    "size":6182,
    "sha256":"266045976d6d0b78a74bcf43c90a30a9e52848d0f25cc4a3b96997b080581e4e",
    "mirror_urls":["https://zenodo.org/records/6640376/files/Vireya_RADsamples_tiplabels_ingroup_color_clade.csv?download=1"],
}
TREE={
    "name":"VireyaRADd10m5c91R1_0717_Rdref_min4_raxml_treePLCIs.mean.newick.named",
    "file_id":3623564,
    "size":9700,
    "sha256":"41bc04cdc63032086485c1ce6daf6dedc72fe582e142f7970b72d3143056390b",
    "mirror_urls":["https://zenodo.org/records/6640376/files/VireyaRADd10m5c91R1_0717_Rdref_min4_raxml_treePLCIs.mean.newick.named?download=1"],
}


def exact_sha_match(body:bytes, expected_size:int, expected_sha256:str)->bool:
    return len(body)==int(expected_size) and hashlib.sha256(body).hexdigest()==expected_sha256.lower()


def csv_header_only(body:bytes)->list[str]:
    text=body.decode("utf-8-sig",errors="strict")
    first=text.splitlines()[0] if text.splitlines() else ""
    return next(csv.reader([first])) if first else []


def identifier_column_candidates(header:list[str])->list[str]:
    out=[]
    for x in header:
        n=re.sub(r"[^a-z0-9]+","_",x.strip().lower()).strip("_")
        if any(bad in n for bad in ("color","colour","hue","pigment","clade")):
            continue
        if any(tok in n for tok in ("tip","species","taxon","label","name","id","sample")):
            out.append(x)
    return out


def request(url:str,accept:str="*/*")->dict:
    q=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":accept})
    try:
        with urllib.request.urlopen(q,timeout=120) as r:
            return {"ok":True,"status":r.status,"url":url,"final_url":r.geturl(),
                    "headers":dict(r.headers),"body":r.read()}
    except urllib.error.HTTPError as e:
        try: b=e.read()
        except Exception: b=b""
        return {"ok":False,"status":e.code,"url":url,"final_url":e.geturl(),
                "headers":dict(e.headers or {}),"body":b,"reason":str(e.reason)}
    except Exception as e:
        return {"ok":False,"status":None,"url":url,"final_url":url,
                "headers":{},"body":b"","reason":repr(e)}


def request_json(url:str)->dict:
    r=request(url,"application/json")
    if not r["ok"]:
        raise RuntimeError(f"JSON request failed {url}: {r['status']} {r.get('reason')}")
    return json.loads(r["body"])


def collect_hrefs(x:Any)->list[str]:
    found=[]
    def walk(v:Any):
        if isinstance(v,dict):
            for k,z in v.items():
                if k=="href" and isinstance(z,str):
                    if z.startswith(("http://","https://")):
                        found.append(z)
                    elif z.startswith("/"):
                        found.append("https://datadryad.org"+z)
                walk(z)
        elif isinstance(v,list):
            for z in v: walk(z)
    walk(x)
    return list(dict.fromkeys(found))


def is_html(r:dict)->bool:
    c=str(r.get("headers",{}).get("Content-Type","")).lower()
    b=r.get("body",b"").lstrip().lower()
    return "html" in c or b.startswith(b"<!doctype html") or b.startswith(b"<html")


def recover_one(spec:dict)->tuple[bytes|None,list[dict],dict|None]:
    fid=spec["file_id"]
    detail=None
    try:
        detail=request_json(f"{API}/files/{fid}")
    except Exception:
        detail=None
    urls=[]
    if detail:
        urls.extend(collect_hrefs(detail))
    urls += [
        f"{API}/files/{fid}/download",
        f"https://datadryad.org/stash/downloads/file_stream/{fid}",
        f"https://datadryad.org/downloads/file_stream/{fid}",
    ]
    urls += list(spec.get("mirror_urls",[]))
    urls=list(dict.fromkeys(urls))
    attempts=[]
    for u in urls:
        r=request(u)
        match=bool(r["ok"] and not is_html(r) and exact_sha_match(r["body"],spec["size"],spec["sha256"]))
        attempts.append({
            "url":u,
            "http_status":r["status"],
            "final_url":r["final_url"],
            "content_type":str(r.get("headers",{}).get("Content-Type","")),
            "downloaded_bytes":len(r["body"]),
            "sha256":hashlib.sha256(r["body"]).hexdigest() if r["body"] else None,
            "html_payload":is_html(r),
            "exact_match":match,
            "reason":r.get("reason"),
        })
        if match:
            return r["body"],attempts,detail
    return None,attempts,detail


def tree_diagnostics(body:bytes)->dict:
    tree=Phylo.read(io.StringIO(body.decode("utf-8-sig")),"newick")
    tips=[str(t.name) for t in tree.get_terminals()]
    branches=[c.branch_length for c in tree.find_clades() if c is not tree.root]
    return {
        "tip_count":len(tips),
        "duplicate_tip_labels":len(tips)-len(set(tips)),
        "all_nonroot_branch_lengths_present":bool(branches) and all(x is not None for x in branches),
        "min_nonroot_branch_length":float(min(x for x in branches if x is not None)) if branches else None,
        "max_nonroot_branch_length":float(max(x for x in branches if x is not None)) if branches else None,
    }


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--outdir",type=Path,required=True)
    a=ap.parse_args()
    a.outdir.mkdir(parents=True,exist_ok=True)

    color_body,color_attempts,color_detail=recover_one(COLOR)
    tree_body,tree_attempts,tree_detail=recover_one(TREE)

    color_rec={
        **COLOR,
        "recovered":color_body is not None,
        "attempts":color_attempts,
        "api_detail_available":color_detail is not None,
    }
    tree_rec={
        **TREE,
        "recovered":tree_body is not None,
        "attempts":tree_attempts,
        "api_detail_available":tree_detail is not None,
    }

    header=[]
    id_candidates=[]
    if color_body is not None:
        (a.outdir/COLOR["name"]).write_bytes(color_body)
        header=csv_header_only(color_body)
        id_candidates=identifier_column_candidates(header)
        color_rec["header"]=header
        color_rec["identifier_column_candidates"]=id_candidates

    if tree_body is not None:
        (a.outdir/TREE["name"]).write_bytes(tree_body)
        tree_rec["tree_diagnostics"]=tree_diagnostics(tree_body)

    both=color_body is not None and tree_body is not None
    status="EXACT_SOURCE_BYTES_RECOVERED_IDENTIFIER_CROSSWALK_PENDING" if both else "HOLD_EXACT_SOURCE_BYTES_UNAVAILABLE"
    if both:
        td=tree_rec["tree_diagnostics"]
        if not td["all_nonroot_branch_lengths_present"] or td["duplicate_tip_labels"]!=0:
            status="HOLD_TREE_SCHEMA"

    out={
        "version":"v0.1",
        "status":status,
        "candidate":"RHODODENDRON_SECT_SCHISTANTHE",
        "source_doi":DOI,
        "color":color_rec,
        "chronogram":tree_rec,
        "csv_header":header,
        "identifier_column_candidates":id_candidates,
        "row_level_color_values_interpreted":False,
        "state_frequencies_computed":False,
        "hidden_memory_auc_computed":False,
        "next_gate":("FREEZE_IDENTIFIER_ONLY_CROSSWALK" if status=="EXACT_SOURCE_BYTES_RECOVERED_IDENTIFIER_CROSSWALK_PENDING" else "STOP_HOLD"),
        "el_v0_3_science_changed":False,
        "v0_7_promotion_state_changed":False,
        "paper1_science_changed":False,
    }
    (a.outdir/"source_receipt.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "status":status,
        "color_recovered":color_rec["recovered"],
        "tree_recovered":tree_rec["recovered"],
        "csv_header":header,
        "identifier_column_candidates":id_candidates,
        "tree_diagnostics":tree_rec.get("tree_diagnostics"),
    },indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
