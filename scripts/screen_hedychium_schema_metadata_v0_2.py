#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import time
import urllib.request
from pathlib import Path

DATA_RECORD=6757645
CODE_RECORD=6694682
UA="CHUN-Hedychium-schema-metadata/0.2"

EXPECTED={
  "Discrete_13.csv":"eac3262d6bde7a2efc484088c17c199e",
  "HEDYCHIUM_2022__DATA_README.txt":"b1816d7a71efacabb7c11a22f00f84da",
  "README_Ashokan_etal_AJB.txt":"441ec7ed75038886cc10412cc3ead96c",
}
CODE_NAME="STOCHASTIC_MAPPING_ARD_labellum_09January2021.R"
CODE_MD5="60360c9e41b3033adfa85433b84a1bef"

def fetch(url:str,accept:str="*/*")->bytes:
    last=None
    for attempt in range(4):
        req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":accept})
        try:
            with urllib.request.urlopen(req,timeout=30) as r:
                return r.read()
        except Exception as e:
            last=e
            if attempt==3:
                raise
            time.sleep(min(2**attempt,4))
    raise RuntimeError(str(last))

def md5(b:bytes)->str:
    return hashlib.md5(b).hexdigest()

def meta(record_id:int)->dict:
    return json.loads(fetch(f"https://zenodo.org/api/records/{record_id}","application/json").decode("utf-8"))

def file_map(x:dict)->dict[str,dict]:
    return {str(f.get("key")):f for f in x.get("files",[])}

def content_url(f:dict)->str:
    links=f.get("links") or {}
    u=links.get("content") or links.get("self")
    if not u:
        raise RuntimeError(f"missing content URL for {f.get('key')}")
    return u

def exact_file(record_id:int,name:str,expected_md5:str)->bytes:
    fm=file_map(meta(record_id))
    if name not in fm:
        raise RuntimeError(f"{name} absent from Zenodo record {record_id}")
    b=fetch(content_url(fm[name]))
    if md5(b)!=expected_md5:
        raise RuntimeError(f"{name} md5 mismatch")
    return b

def header_only(body:bytes)->list[str]:
    first=body.decode("utf-8-sig",errors="replace").splitlines()[0]
    return [str(x).strip() for x in next(csv.reader([first]))]

def block(text:str,needle:str,n:int=120)->list[dict]:
    lines=text.splitlines()
    idx=next((i for i,s in enumerate(lines) if needle.lower() in s.lower()),None)
    if idx is None:
        return []
    out=[]
    for j in range(idx,min(len(lines),idx+n)):
        s=lines[j]
        # README-only metadata. Suppress lines that look like species data tables.
        if s.count(",")>=5:
            continue
        out.append({"line":j+1,"text":s[:800]})
    return out

def selected_lines(text:str)->list[dict]:
    terms=("labellum","colour","color","white","pale","bright","red","orange","pink","yellow","character 11","character11","state","code")
    out=[]
    for i,s in enumerate(text.splitlines(),1):
        low=s.lower()
        if any(t in low for t in terms) and s.count(",")<5:
            out.append({"line":i,"text":s[:800]})
    return out[:250]

def mapping_eval(records:list[dict],header:list[str])->dict:
    text="\n".join(x["text"].lower() for x in records)
    explicit_patterns=[
      r"(?:state|code|character\s*11)[^\n]{0,180}(?:0\s*[:=\-]|1\s*[:=\-])",
      r"(?:0\s*[:=]\s*(?:white|pale|red|orange|pink|yellow))",
      r"(?:1\s*[:=]\s*(?:white|pale|red|orange|pink|yellow))",
      r"(?:white|pale|red|orange|pink|yellow)[^\n]{0,100}(?:0\s*[:=]|1\s*[:=]|2\s*[:=]|3\s*[:=])",
    ]
    hits=[p for p in explicit_patterns if re.search(p,text,re.I)]
    literal_header=any(
        ("colour" in h.lower() or "color" in h.lower())
        and ("labellum" in h.lower() or "flower" in h.lower())
        for h in header
    )
    tokens=sorted({t for t in ("white","pale","red","orange","pink","yellow") if t in text})
    return {
      "explicit_code_to_colour_mapping":bool(hits),
      "mapping_patterns_matched":hits,
      "literal_named_colour_header":literal_header,
      "colour_tokens_found":tokens,
      "established":bool(hits or literal_header),
    }

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    a.out.parent.mkdir(parents=True,exist_ok=True)

    discrete=exact_file(DATA_RECORD,"Discrete_13.csv",EXPECTED["Discrete_13.csv"])
    readme1=exact_file(DATA_RECORD,"HEDYCHIUM_2022__DATA_README.txt",EXPECTED["HEDYCHIUM_2022__DATA_README.txt"])
    readme2=exact_file(DATA_RECORD,"README_Ashokan_etal_AJB.txt",EXPECTED["README_Ashokan_etal_AJB.txt"])
    code=exact_file(CODE_RECORD,CODE_NAME,CODE_MD5)

    header=header_only(discrete)
    r1=readme1.decode("utf-8",errors="replace")
    r2=readme2.decode("utf-8",errors="replace")
    rc=code.decode("utf-8",errors="replace")

    discrete_block=block(r1,"DATA-SPECIFIC INFORMATION FOR: Discrete_13.csv",140)
    labellum_block=block(r1,"DATA-SPECIFIC INFORMATION FOR: STOCHASTIC_MAPPING_ER_labellum",90)
    records=discrete_block+labellum_block+selected_lines(r2)+selected_lines(rc)
    ev=mapping_eval(records,header)

    status=(
      "PASS_HEDYCHIUM_PRE_ROW_COLOUR_SCHEMA_MAPPING"
      if ev["established"]
      else "HOLD_HEDYCHIUM_PRE_ROW_COLOUR_SCHEMA_MAPPING_NOT_ESTABLISHED"
    )
    out={
      "version":"v0.2",
      "status":status,
      "candidate":"HEDYCHIUM",
      "exact_objects":{
        "Discrete_13.csv":EXPECTED["Discrete_13.csv"],
        "HEDYCHIUM_2022__DATA_README.txt":EXPECTED["HEDYCHIUM_2022__DATA_README.txt"],
        "README_Ashokan_etal_AJB.txt":EXPECTED["README_Ashokan_etal_AJB.txt"],
        CODE_NAME:CODE_MD5,
      },
      "trait_header":header,
      "discrete13_readme_block":discrete_block,
      "labellum_readme_block":labellum_block,
      "mapping_evaluation":ev,
      "outcome_firewall":{
        "discrete_trait_bytes_downloaded_for_hash_and_header_only":True,
        "species_rows_parsed":False,
        "species_level_colour_values_opened":False,
        "colour_state_frequencies_computed":False,
        "hidden_memory_auc_computed":False,
      },
      "next_gate":"ADMIT_HEDYCHIUM_SOURCE_FIRST" if ev["established"] else "CONTINUE_SOURCE_FIRST_SCREEN_IF_BUDGET_REMAINS",
      "paper1_science_changed":False,
      "el_v0_3_science_changed":False
    }
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
      "status":status,
      "trait_header":header,
      "mapping_evaluation":ev,
      "discrete13_readme_block":discrete_block,
      "labellum_readme_block":labellum_block,
    },indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
