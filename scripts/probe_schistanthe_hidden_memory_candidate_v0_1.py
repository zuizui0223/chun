#!/usr/bin/env python3
from __future__ import annotations

import argparse, json, re, urllib.error, urllib.parse, urllib.request
from pathlib import Path

DOI="10.5061/dryad.47d7wm3f4"
COLOR_FILE="Vireya_RADsamples_tiplabels_ingroup_color_clade.xls"
TREE_FILE="VireyaRADd10m5c91R1_0717_Rdref_min4_raxml_treePLCIs.mean.newick"
API="https://datadryad.org/api/v2"
UA="CHUN-Schistanthe-heldout-screen/0.1"
REPORTED_TAXA=114


def req_json(url:str)->dict:
    q=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/json"})
    try:
        with urllib.request.urlopen(q,timeout=120) as r:
            return json.loads(r.read())
    except Exception as e:
        raise RuntimeError(f"metadata request failed: {url}: {e!r}")


def collect_file_id(meta:dict)->int|None:
    def walk(x):
        if isinstance(x,str):
            m=re.search(r"/files/(\d+)(?:$|[/?#])",x)
            if m:return int(m.group(1))
        elif isinstance(x,dict):
            for v in x.values():
                z=walk(v)
                if z is not None:return z
        elif isinstance(x,list):
            for v in x:
                z=walk(v)
                if z is not None:return z
        return None
    return walk(meta)


def coarse_from_source_color(value:str|None)->str|None:
    if value is None:return None
    s=" ".join(str(value).strip().lower().split())
    if not s:return None
    return "WHITE" if s=="white" else "NONWHITE"


def summarize(meta:dict)->dict:
    return {
      "path":meta.get("path"),
      "file_id":collect_file_id(meta),
      "size":meta.get("size"),
      "digest_type":meta.get("digestType"),
      "digest":meta.get("digest"),
      "mime_type":meta.get("mimeType") or meta.get("mime_type"),
    }


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    a.out.parent.mkdir(parents=True,exist_ok=True)

    ds=req_json(API+"/datasets/"+urllib.parse.quote("doi:"+DOI,safe=""))
    vh=ds["_links"]["stash:version"]["href"]
    vurl=vh if vh.startswith("http") else API+vh.removeprefix("/api/v2")
    listing=req_json(vurl.rstrip("/")+"/files?per_page=500")
    files=listing.get("_embedded",{}).get("stash:files",[])
    def basename(x):
        return str(x or "").replace("\\\\","/").split("/")[-1]
    by={basename(f.get("path")):f for f in files}

    color=by.get(COLOR_FILE)
    tree=by.get(TREE_FILE)
    source_complete=color is not None and tree is not None
    status=("ADMIT_SOURCE_COMPLETE_PENDING_ROWLEVEL_STATE_SUPPORT_GATE"
            if source_complete and REPORTED_TAXA>=20
            else "HOLD_SOURCE_METADATA_INCOMPLETE")

    out={
      "version":"v0.1",
      "status":status,
      "candidate":"RHODODENDRON_SECT_SCHISTANTHE",
      "article_doi":"10.1111/nph.18083",
      "source_doi":DOI,
      "reported_taxa":REPORTED_TAXA,
      "reported_taxa_source":"published article metadata; 114 sect. Schistanthe taxa in RAD-seq phylogeny",
      "exact_files":{
        "color":summarize(color) if color else None,
        "chronogram":summarize(tree) if tree else None,
      },
      "trait_semantics_frozen_before_row_values":{
        "fine":"exact source flower-color string after trim/lowercase/collapse whitespace; no semantic merging",
        "coarse":"exact normalized string WHITE if and only if source value equals 'white'; every other nonmissing exact string -> NONWHITE",
        "ambiguous_or_composite_label_rule":"HOLD_SCHEMA rather than reinterpret after row opening",
        "minimum_fine_state_support":5,
        "minimum_common_tips":20
      },
      "tree_semantics":{
        "role":"published chronogram displayed in Soza et al. 2022 Figure 5",
        "branch_length_units":"million years according to Dryad description",
        "tree_file_body_downloaded":False,
        "tree_tip_labels_opened":False
      },
      "next_gate":("DOWNLOAD_EXACT_TREE_AND_COLOR_FILE_THEN_FREEZE_IDENTIFIER_CROSSWALK_AND_STATE_SUPPORT_BEFORE_HIDDEN_MEMORY_AUC"
                   if status.startswith("ADMIT_") else "STOP_HOLD"),
      "row_level_color_values_opened":False,
      "state_frequencies_computed":False,
      "hidden_memory_auc_computed":False,
      "current_v0_7_promotion_rule_changed":False,
      "el_v0_3_science_changed":False,
      "paper1_science_changed":False
    }
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
      "status":status,
      "reported_taxa":REPORTED_TAXA,
      "color_file_found":color is not None,
      "tree_file_found":tree is not None,
      "color":out["exact_files"]["color"],
      "tree":out["exact_files"]["chronogram"],
    },indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
