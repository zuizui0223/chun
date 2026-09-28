#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

DOI="10.5061/dryad.95x69p8k4"
UA="CHUN-Polemoniaceae-Rose2021-source-first/0.2"
REQUIRED={"README.txt","general.scripts.zip","phylogeny.zip","SuppData_2.xlsx"}

def fetch(url:str,accept:str="*/*")->tuple[bytes,str,dict]:
    last=None
    for attempt in range(5):
        req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":accept})
        try:
            with urllib.request.urlopen(req,timeout=90) as r:
                return r.read(),r.geturl(),dict(r.headers)
        except Exception as e:
            last=e
            if attempt==4: raise
            time.sleep(min(2**attempt,8))
    raise RuntimeError(str(last))

def jget(url:str)->dict:
    b,_,_=fetch(url,"application/json,*/*")
    return json.loads(b.decode("utf-8"))

def md5(b:bytes)->str: return hashlib.md5(b).hexdigest()
def sha256(b:bytes)->str: return hashlib.sha256(b).hexdigest()

def collect_urls(x)->list[str]:
    out=[]
    if isinstance(x,dict):
        for v in x.values(): out.extend(collect_urls(v))
    elif isinstance(x,list):
        for v in x: out.extend(collect_urls(v))
    elif isinstance(x,str) and x.startswith(("http://","https://","/")):
        out.append(urllib.parse.urljoin("https://datadryad.org",x))
    return out

def metadata()->tuple[dict,list[dict]]:
    enc=urllib.parse.quote("doi:"+DOI,safe="")
    ds=None
    diagnostics=[]
    for u in [
      f"https://datadryad.org/api/v2/datasets/{enc}",
      f"https://datadryad.org/api/v2/datasets/doi%3A10.5061%2Fdryad.95x69p8k4",
    ]:
        try:
            ds=jget(u); diagnostics.append({"url":u,"ok":True}); break
        except Exception as e:
            diagnostics.append({"url":u,"ok":False,"error":f"{type(e).__name__}: {e}"})
    if ds is None: raise RuntimeError("dataset metadata unavailable")
    urls=collect_urls(ds)
    vids=[]
    for u in urls:
        m=re.search(r"/versions/(\d+)",u)
        if m: vids.append(m.group(1))
    if not vids:
        # Some dataset records expose latestVersion as an integer.
        for k in ("latestVersion","version"):
            v=ds.get(k)
            if isinstance(v,(int,str)) and str(v).isdigit(): vids.append(str(v))
    inventories=[]
    for vid in sorted(set(vids)):
        for u in [
          f"https://datadryad.org/api/v2/versions/{vid}/files",
          f"https://datadryad.org/api/v2/versions/{vid}",
        ]:
            try:
                x=jget(u); diagnostics.append({"url":u,"ok":True})
            except Exception as e:
                diagnostics.append({"url":u,"ok":False,"error":f"{type(e).__name__}: {e}"}); continue
            candidates=[]
            if isinstance(x,list): candidates=x
            elif isinstance(x,dict):
                for key in ("files","_embedded","stash:files"):
                    v=x.get(key)
                    if isinstance(v,list): candidates+=v
                    elif isinstance(v,dict):
                        for vv in v.values():
                            if isinstance(vv,list): candidates+=vv
            for o in candidates:
                if isinstance(o,dict) and (o.get("path") or o.get("filename") or o.get("name")):
                    inventories.append(o)
    # de-duplicate by file id/name
    uniq={}
    for o in inventories:
        key=str(o.get("id") or o.get("file_id") or o.get("path") or o.get("filename") or o.get("name"))
        uniq[key]=o
    return ds,list(uniq.values()),diagnostics

def name(o:dict)->str:
    return str(o.get("path") or o.get("filename") or o.get("file_name") or o.get("name") or "")

def expected_md5(o:dict)->str|None:
    for k,v in o.items():
        lk=str(k).lower()
        if lk in {"digest","checksum","md5"} or "digest" in lk or "checksum" in lk:
            s=str(v).lower().strip()
            if s.startswith("md5:"): s=s.split(":",1)[1]
            if re.fullmatch(r"[0-9a-f]{32}",s): return s
    return None

def candidate_download_urls(o:dict)->list[str]:
    urls=collect_urls(o)
    fid=o.get("id") or o.get("file_id")
    if fid:
        urls += [
          f"https://datadryad.org/api/v2/files/{fid}/download",
          f"https://datadryad.org/stash/downloads/file_stream/{fid}",
        ]
    ranked=[]
    for u in urls:
        low=u.lower(); score=0
        if "download" in low or "file_stream" in low: score+=5
        if "/files/" in low: score+=2
        ranked.append((score,u))
    seen=set(); out=[]
    for _,u in sorted(ranked,reverse=True):
        if u not in seen:
            seen.add(u); out.append(u)
    return out

def exact_file(o:dict)->tuple[bytes,dict]:
    exp=expected_md5(o)
    size=o.get("size") or o.get("file_size")
    attempts=[]
    for u in candidate_download_urls(o):
        try:
            b,final,h=fetch(u)
            ok_size=True if size is None else int(size)==len(b)
            ok_md5=True if exp is None else md5(b)==exp
            attempts.append({"url":u,"ok":True,"final_url":final,"bytes":len(b),"size_match":ok_size,"md5_match":ok_md5})
            if ok_size and ok_md5:
                return b,{"attempts":attempts,"expected_md5":exp,"metadata_size":size,"sha256":sha256(b),"md5":md5(b)}
        except Exception as e:
            attempts.append({"url":u,"ok":False,"error":f"{type(e).__name__}: {e}"})
    raise RuntimeError(json.dumps(attempts))

def zip_members(b:bytes)->list[dict]:
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        return [{"path":n,"bytes":z.getinfo(n).file_size} for n in z.namelist() if not n.endswith("/")]

def code_evidence(b:bytes)->list[dict]:
    out=[]
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        for n in z.namelist():
            if n.endswith("/") or Path(n).suffix.lower() not in {".r",".rmd",".txt"}: continue
            txt=z.read(n).decode("utf-8",errors="replace")
            hits=[]
            for i,s in enumerate(txt.splitlines(),1):
                low=s.lower()
                if (
                  "suppdata_2" in low or "corolla" in low and ("color" in low or "colour" in low)
                  or "read.tree" in low or "read.nexus" in low or "phylogeny" in low
                  or "mcc" in low
                ):
                    hits.append({"line":i,"text":s[:700]})
            if hits: out.append({"path":n,"hits":hits[:100]})
    return out

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args(); a.out.parent.mkdir(parents=True,exist_ok=True)
    try:
        ds,inv,mdiag=metadata()
    except Exception as e:
        out={"version":"v0.2","status":"HOLD_POLEMONIACEAE_ROSE2021_DRYAD_METADATA_UNAVAILABLE","error":f"{type(e).__name__}: {e}",
             "outcome_firewall":{"trait_rows_opened":False,"colour_values_opened":False,"tree_tip_labels_emitted":False,"hidden_memory_auc_computed":False}}
        a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n"); print(json.dumps(out,indent=2)); return 0
    by={name(o):o for o in inv}
    file_meta=[{"name":name(o),"size":o.get("size") or o.get("file_size"),"md5":expected_md5(o)} for o in inv]
    missing=sorted(REQUIRED-set(by))
    recovered={}
    bodies={}
    if not missing:
        for fn in sorted(REQUIRED):
            try:
                b,d=exact_file(by[fn]); bodies[fn]=b; recovered[fn]={"ready":True,**d}
            except Exception as e:
                recovered[fn]={"ready":False,"error":f"{type(e).__name__}: {e}"}
    all_ready=not missing and all(recovered.get(fn,{}).get("ready") for fn in REQUIRED)
    readme_lines=[]
    code=[]
    phy_members=[]
    if all_ready:
        txt=bodies["README.txt"].decode("utf-8",errors="replace")
        for i,s in enumerate(txt.splitlines(),1):
            low=s.lower()
            if "suppdata" in low or "phylogen" in low or "corolla" in low or "color" in low or "colour" in low:
                readme_lines.append({"line":i,"text":s[:800]})
        code=code_evidence(bodies["general.scripts.zip"])
        phy_members=zip_members(bodies["phylogeny.zip"])
    # Publication-level source-defined schema is frozen before any rows:
    schema={
      "fine_states":["blue/pink","red","white","yellow"],
      "coarse_state":"WHITE iff exact published state is white; otherwise NONWHITE",
      "source":"Rose & Sytsma 2021 Table 1",
      "trait_object_expected":"SuppData_2.xlsx (Data S2 floral/reproductive trait matrix)"
    }
    if missing:
        status="HOLD_POLEMONIACEAE_ROSE2021_REQUIRED_OBJECT_METADATA_MISSING"
    elif not all_ready:
        status="HOLD_POLEMONIACEAE_ROSE2021_REQUIRED_OBJECT_TRANSPORT"
    elif not phy_members:
        status="HOLD_POLEMONIACEAE_ROSE2021_PHYLOGENY_ARCHIVE_EMPTY"
    else:
        status="PASS_POLEMONIACEAE_SOURCE_FIRST_ROSE2021_EXACT_OBJECTS_READY"
    out={
      "version":"v0.2",
      "status":status,
      "candidate":"POLEMONIACEAE",
      "candidate_order":3,
      "source_revision":"Use the 2021 Rose & Sytsma comprehensive Polemoniaceae source for the already selected radiation; no target outcome was opened under the failed 2018 Zenodo search probe.",
      "dataset_doi":DOI,
      "file_metadata":file_meta,
      "required_objects":sorted(REQUIRED),
      "missing_required_objects":missing,
      "recovered":recovered,
      "readme_schema_evidence":readme_lines,
      "author_code_evidence":code,
      "phylogeny_archive_members":phy_members,
      "pre_row_colour_schema":schema,
      "outcome_firewall":{
        "SuppData_2_species_rows_opened":False,
        "corolla_lobe_colour_values_opened":False,
        "colour_state_frequencies_computed":False,
        "tree_tip_labels_emitted":False,
        "hidden_memory_auc_computed":False
      },
      "metadata_diagnostics":mdiag,
      "next_gate":"STOP_SCREEN_AND_FREEZE_POLEMONIACEAE_ADMISSION" if status.startswith("PASS_") else "CONTINUE_SOURCE_FIRST_SCREEN_IF_BUDGET_REMAINS",
      "paper1_science_changed":False,
      "el_v0_3_science_changed":False
    }
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":status,"missing":missing,"recovered":{k:v.get("ready") for k,v in recovered.items()},
                      "phylogeny_members":phy_members[:30],"readme":readme_lines,"code_files":[x["path"] for x in code]},indent=2))
    return 0
if __name__=="__main__": raise SystemExit(main())
