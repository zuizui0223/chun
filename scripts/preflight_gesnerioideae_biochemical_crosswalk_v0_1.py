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
UA="CHUN-Gesnerioideae-crosswalk/0.2"


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


def source_first_rows(body:bytes)->list[dict]:
    wb=load_workbook(io.BytesIO(body),read_only=True,data_only=False)
    ws=wb[SHEET]
    header=[str(c.value).strip() if c.value is not None else "" for c in ws[HEADER_ROW]]
    required=["Species","Voucher","Living collection ID"]
    missing=[x for x in required if x not in header]
    if missing:
        raise ValueError(f"identifier headers missing: {missing}")
    cols={x:header.index(x)+1 for x in required}
    first=OrderedDict()
    for r in range(HEADER_ROW+1,ws.max_row+1):
        v=ws.cell(r,cols["Species"]).value
        if v is None or not str(v).strip():
            continue
        raw=str(v).strip()
        k=species_key(raw)
        if k not in first:
            first[k]={
                "species":raw,
                "voucher":ws.cell(r,cols["Voucher"]).value,
                "living_collection_id":ws.cell(r,cols["Living collection ID"]).value,
            }
    return list(first.values())


def source_species_first_rows(body:bytes)->list[str]:
    return [x["species"] for x in source_first_rows(body)]


def identifier_token(x)->str:
    if x is None:
        return ""
    return re.sub(r"[^a-z0-9]","",str(x).lower())


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


def resolve_candidate_by_source_identifiers(candidates:list[str], identifiers:dict)->tuple[str|None,str|None]:
    # Outcome-independent priority frozen before chemistry opening:
    # source voucher first, then living-collection identifier.
    for field in ("voucher","living_collection_id"):
        token=identifier_token(identifiers.get(field))
        if len(token)<3:
            continue
        hits=[c for c in candidates if token in identifier_token(c)]
        if len(hits)==1:
            return hits[0],field
    return None,None


def build_crosswalk(source_species:list[str],tree_tips:list[str],identifier_map:dict|None=None)->dict:
    src=OrderedDict()
    for raw in source_species:
        k=species_key(raw)
        if k not in src:
            src[k]=raw
    matches=[]
    unmatched=[]
    ambiguous=[]
    ambiguous_candidates={}
    identifier_resolved=[]
    for k,raw in src.items():
        cand=[t for t in tree_tips if tip_matches_key(t,k)]
        if len(cand)==1:
            matches.append({"source_species":raw,"source_key":k,"tree_tip":cand[0],"resolution":"species_unique"})
        elif len(cand)==0:
            unmatched.append(k)
        else:
            chosen=None
            field=None
            if identifier_map and k in identifier_map:
                chosen,field=resolve_candidate_by_source_identifiers(cand,identifier_map[k])
            if chosen is not None:
                matches.append({
                    "source_species":raw,
                    "source_key":k,
                    "tree_tip":chosen,
                    "resolution":f"source_{field}_suffix",
                })
                identifier_resolved.append(k)
            else:
                ambiguous.append(k)
                ambiguous_candidates[k]=cand
    return {
        "source_unique_species":len(src),
        "tree_tips":len(tree_tips),
        "matched_species":len(matches),
        "matches":matches,
        "identifier_resolved_species":sorted(identifier_resolved),
        "unmatched_source_keys":sorted(unmatched),
        "ambiguous_source_keys":sorted(ambiguous),
        "ambiguous_candidates":ambiguous_candidates,
    }


def pruned_tree(tree, matched_tree_tips:list[str]):
    keep=set(matched_tree_tips)
    for terminal in list(tree.get_terminals()):
        if terminal.name not in keep:
            tree.prune(terminal)
    remaining={str(t.name).strip() for t in tree.get_terminals()}
    if remaining != keep:
        missing=sorted(keep-remaining)
        extra=sorted(remaining-keep)
        raise RuntimeError(f"pruned-tree tip mismatch: missing={missing}, extra={extra}")
    return tree


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--tree",type=Path,required=True)
    ap.add_argument("--out-json",type=Path,required=True)
    ap.add_argument("--out-tree",type=Path,required=True)
    a=ap.parse_args()
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_tree.parent.mkdir(parents=True,exist_ok=True)

    wb=exact_workbook()
    records=source_first_rows(wb)
    source_species=[x["species"] for x in records]
    identifier_map={
        species_key(x["species"]):{
            "voucher":x["voucher"],
            "living_collection_id":x["living_collection_id"],
        }
        for x in records
    }
    tree=Phylo.read(str(a.tree),"nexus")
    tips=[str(t.name).strip() for t in tree.get_terminals()]
    cw=build_crosswalk(source_species,tips,identifier_map)

    if cw["ambiguous_source_keys"]:
        status="HOLD_AMBIGUOUS_IDENTIFIER_CROSSWALK"
    elif cw["matched_species"]<20:
        status="HOLD_CROSSWALK_LT_20"
    else:
        status="GESNERIOIDEAE_BIOCHEMICAL_CROSSWALK_FROZEN_CHEMISTRY_UNOPENED"

    matched_tree_tips=[m["tree_tip"] for m in cw["matches"]]
    tree_for_analysis=pruned_tree(tree,matched_tree_tips)
    Phylo.write(tree_for_analysis,str(a.out_tree),"newick")

    unresolved_identifier_context={
        k:identifier_map.get(k,{}) for k in cw["ambiguous_source_keys"]
    }

    out={
      "version":"v0.2",
      "status":status,
      "source_workbook_sha256":WORKBOOK_SHA,
      "source_tree_exact_sha256":"0aac94ddfad56cff759eb0352aeaebb61b5bd4ebb60fa8c0db857b7f93ab0d50",
      "staged_tree_note":"Input staging text was reconstructed from the separately exact-byte-verified Library source; analysis uses its parsed topology and branch lengths.",
      **cw,
      "unresolved_source_identifiers":unresolved_identifier_context,
      "pruned_tree_path":str(a.out_tree),
      "pruned_tree_tips":len(tree_for_analysis.get_terminals()),
      "crosswalk_rule":"first source row per normalized genus+species; accept one species-matching tree tip directly; if multiple tips match the species key, resolve only by exact normalized source Voucher suffix, then Living collection ID suffix; otherwise HOLD; unmatched source species are excluded before chemistry opening",
      "crosswalk_rule_refinement_note":"v0.1 stopped before chemistry because four species had multiple tree candidates. v0.2 adds a source-identifier-only resolver while chemistry values, state frequencies, and AUC remain unopened.",
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
      "identifier_resolved_species":cw["identifier_resolved_species"],
      "pruned_tree_tips":len(tree_for_analysis.get_terminals()),
      "unmatched_source_count":len(cw["unmatched_source_keys"]),
      "ambiguous_source_keys":cw["ambiguous_source_keys"],
      "ambiguous_candidates":cw["ambiguous_candidates"],
      "unresolved_source_identifiers":unresolved_identifier_context,
    },indent=2,default=str))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
