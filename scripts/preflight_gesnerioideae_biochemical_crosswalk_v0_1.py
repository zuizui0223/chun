#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import urllib.request
import zipfile
from collections import OrderedDict
from pathlib import Path

from Bio import Phylo
from openpyxl import load_workbook

EPMC="https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7767864/supplementaryFiles"
WORKBOOK_SHA="a84abf67da0afb8c0bafd4c1251dbcbb6dc48eb286dca788e6e88ce0176ccbc8"
SHEET="FINAL SAMPLE LIST"
HEADER_ROW=3
UA="CHUN-Gesnerioideae-crosswalk/0.1"


def sha256(b:bytes)->str:
    return hashlib.sha256(b).hexdigest()


def fetch(url:str)->bytes:
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"*/*"})
    with urllib.request.urlopen(req,timeout=120) as r:
        return r.read()


def exact_workbook()->bytes:
    container=fetch(EPMC)
    matches=[]
    with zipfile.ZipFile(io.BytesIO(container)) as z:
        for name in z.namelist():
            if name.lower().endswith(".xlsx"):
                b=z.read(name)
                if sha256(b)==WORKBOOK_SHA:
                    matches.append(b)
    if len(matches)!=1:
        raise RuntimeError(f"expected one frozen workbook, got {len(matches)}")
    return matches[0]


def species_key(x:str)->str:
    s=re.sub(r"[_]+"," ",str(x).strip())
    s=re.sub(r"\s+"," ",s)
    parts=s.split(" ")
    if len(parts)<2:
        raise ValueError(f"malformed binomial: {x!r}")
    return f"{parts[0].lower()}_{parts[1].lower()}"


def source_species_first_rows(body:bytes)->list[str]:
    wb=load_workbook(io.BytesIO(body),read_only=True,data_only=False)
    ws=wb[SHEET]
    header=[str(c.value).strip() if c.value is not None else "" for c in ws[HEADER_ROW]]
    if "Species" not in header:
        raise ValueError("Species header missing")
    c=header.index("Species")+1
    first=OrderedDict()
    for r in range(HEADER_ROW+1,ws.max_row+1):
        v=ws.cell(r,c).value
        if v is None or not str(v).strip():
            continue
        raw=str(v).strip()
        k=species_key(raw)
        if k not in first:
            first[k]=raw
    return list(first.values())


def tip_matches_key(tip:str,key:str)->bool:
    raw=str(tip).strip().strip("'").strip('"')
    low=raw.lower()
    if low==key:
        return True
    if low.startswith(key+"_"):
        return True
    if low.startswith(key):
        suffix=raw[len(key):]
        return bool(suffix) and (suffix[0].isdigit() or suffix[0].isupper())
    return False


def build_crosswalk(source_species:list[str],tree_tips:list[str])->dict:
    src=OrderedDict()
    for raw in source_species:
        k=species_key(raw)
        if k not in src:
            src[k]=raw
    matches=[]
    unmatched=[]
    ambiguous=[]
    for k,raw in src.items():
        cand=[t for t in tree_tips if tip_matches_key(t,k)]
        if len(cand)==1:
            matches.append({"source_species":raw,"source_key":k,"tree_tip":cand[0]})
        elif len(cand)==0:
            unmatched.append(k)
        else:
            ambiguous.append(k)
    return {
        "source_unique_species":len(src),
        "tree_tips":len(tree_tips),
        "matched_species":len(matches),
        "matches":matches,
        "unmatched_source_keys":sorted(unmatched),
        "ambiguous_source_keys":sorted(ambiguous),
    }


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--tree",type=Path,required=True)
    ap.add_argument("--out-json",type=Path,required=True)
    a=ap.parse_args()

    wb=exact_workbook()
    source_species=source_species_first_rows(wb)
    tree=Phylo.read(str(a.tree),"nexus")
    tips=[str(t.name).strip() for t in tree.get_terminals()]
    cw=build_crosswalk(source_species,tips)

    if cw["ambiguous_source_keys"]:
        status="HOLD_AMBIGUOUS_IDENTIFIER_CROSSWALK"
    elif cw["matched_species"]<20:
        status="HOLD_CROSSWALK_LT_20"
    else:
        status="GESNERIOIDEAE_BIOCHEMICAL_CROSSWALK_FROZEN_CHEMISTRY_UNOPENED"


    out={
      "version":"v0.1",
      "status":status,
      "source_workbook_sha256":WORKBOOK_SHA,
      "source_tree_exact_sha256":"0aac94ddfad56cff759eb0352aeaebb61b5bd4ebb60fa8c0db857b7f93ab0d50",
      "staged_tree_note":"Input staging text was reconstructed from the separately exact-byte-verified Library source; analysis uses its parsed topology and branch lengths.",
      **cw,
      "crosswalk_rule":"first source row per normalized genus+species; accept exactly one tree tip matching genus_species exactly, genus_species_*, or genus_species followed by uppercase/digit voucher suffix; exclude unmatched source species before chemistry opening; any multiple tree candidates -> HOLD",
      "chemistry_values_opened":False,
      "state_frequencies_computed":False,
      "hidden_memory_auc_computed":False,
      "next_gate":("OPEN_FROZEN_13_COMPOUND_COLUMNS_FOR_STATE_SUPPORT_ONLY"
                   if status=="GESNERIOIDEAE_BIOCHEMICAL_CROSSWALK_FROZEN_CHEMISTRY_UNOPENED"
                   else "STOP_HOLD"),
      "old_three_level_schema_hold_changed":False,
      "paper1_science_changed":False,
      "el_v0_3_science_changed":False
    }
    a.out_json.write_text(json.dumps(out,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
      "status":status,
      "source_unique_species":cw["source_unique_species"],
      "tree_tips":cw["tree_tips"],
      "matched_species":cw["matched_species"],
      "unmatched_source_count":len(cw["unmatched_source_keys"]),
      "ambiguous_source_keys":cw["ambiguous_source_keys"],
    },indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
