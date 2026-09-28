#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import urllib.request
from pathlib import Path

FIGSHARE_ARTICLE=30282448
FIGSHARE_BASE=f"https://api.figshare.com/v2/articles/{FIGSHARE_ARTICLE}"
GITHUB_REPO="jlwatts98/Ruellia_theoretical_colorspace"
GITHUB_API=f"https://api.github.com/repos/{GITHUB_REPO}"
TARGET_BASENAME="03-Ruellia_phylo.timed.tre"
EXPECTED_AUTHOR_CODE_PATH="color data/color data/phylogeny/03-Ruellia_phylo.timed.tre"
UA="CHUN-Ruellia-tree-recheck/0.2"

TREE_SUFFIXES=(".tre",".tree",".nwk",".newick",".nex",".nexus")


def get_json(url:str):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=90) as r:
        return json.load(r)


def get_text(url:str)->str:
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"text/plain,*/*"})
    with urllib.request.urlopen(req,timeout=90) as r:
        return r.read().decode("utf-8",errors="replace")


def figshare_inventory()->dict:
    current=get_json(FIGSHARE_BASE)
    versions=get_json(FIGSHARE_BASE+"/versions")
    seen=[]
    for v in versions:
        n=v.get("version")
        x=get_json(FIGSHARE_BASE+f"/versions/{n}")
        seen.append({
            "version":n,
            "modified_date":x.get("modified_date"),
            "files":[
                {
                    "id":f.get("id"),
                    "name":f.get("name"),
                    "size":f.get("size"),
                    "supplied_md5":f.get("supplied_md5"),
                    "computed_md5":f.get("computed_md5"),
                    "download_url":f.get("download_url"),
                }
                for f in x.get("files",[])
            ],
        })
    curfiles=[
        {
            "id":f.get("id"),
            "name":f.get("name"),
            "size":f.get("size"),
            "supplied_md5":f.get("supplied_md5"),
            "computed_md5":f.get("computed_md5"),
            "download_url":f.get("download_url"),
        }
        for f in current.get("files",[])
    ]
    allfiles=[]
    for z in seen:
        allfiles.extend(z["files"])
    target=[f for f in allfiles if str(f.get("name") or "").casefold()==TARGET_BASENAME.casefold()]
    tree_like=[f for f in allfiles if str(f.get("name") or "").lower().endswith(TREE_SUFFIXES)]
    return {
        "current_version":current.get("version"),
        "current_modified_date":current.get("modified_date"),
        "current_files":curfiles,
        "versions":seen,
        "exact_target_hits":target,
        "tree_like_hits":tree_like,
    }


def github_inventory()->dict:
    repo=get_json(GITHUB_API)
    default=repo.get("default_branch") or "main"
    branch=get_json(GITHUB_API+f"/branches/{default}")
    head=((branch.get("commit") or {}).get("sha"))
    tree=get_json(GITHUB_API+f"/git/trees/{head}?recursive=1")
    paths=[str(x.get("path") or "") for x in tree.get("tree",[]) if x.get("type")=="blob"]
    target=[p for p in paths if Path(p).name.casefold()==TARGET_BASENAME.casefold()]
    tree_like=[p for p in paths if p.lower().endswith(TREE_SUFFIXES)]
    analysis_url=f"https://raw.githubusercontent.com/{GITHUB_REPO}/{head}/analysis.R"
    analysis=get_text(analysis_url)
    target_path_present=EXPECTED_AUTHOR_CODE_PATH in analysis
    lines=[]
    for i,s in enumerate(analysis.splitlines(),1):
        if "Ruellia_phylo.timed.tre" in s or "read.tree" in s or "phylo_ID" in s:
            lines.append({"line":i,"text":s[:800]})
    return {
        "default_branch":default,
        "head_sha":head,
        "all_blob_count":len(paths),
        "exact_target_hits":target,
        "tree_like_hits":tree_like,
        "analysis_expected_target_path_present":target_path_present,
        "analysis_evidence":lines,
    }


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    a.out.parent.mkdir(parents=True,exist_ok=True)

    errors={}
    try:
        fig=figshare_inventory()
    except Exception as e:
        fig=None
        errors["figshare"]=f"{type(e).__name__}: {e}"
    try:
        gh=github_inventory()
    except Exception as e:
        gh=None
        errors["github"]=f"{type(e).__name__}: {e}"

    fig_target=(fig or {}).get("exact_target_hits",[])
    gh_target=(gh or {}).get("exact_target_hits",[])
    if fig_target or gh_target:
        status="RUELLIA_AUTHORITATIVE_TARGET_TREE_OBJECT_LOCATED_SOURCE_ONLY"
        next_gate="VERIFY_TARGET_TREE_BYTES_HASH_AND_FREEZE_TREE_TIP_CROSSWALK_BEFORE_HPLC"
    elif fig is None and gh is None:
        status="HOLD_RUELLIA_TREE_RECHECK_TRANSPORT_NONDIAGNOSTIC"
        next_gate="STOP_HOLD"
    else:
        status="HOLD_RUELLIA_AUTHORITATIVE_TARGET_TREE_STILL_UNAVAILABLE_OUTCOMES_UNOPENED"
        next_gate="STOP_HOLD"

    out={
        "version":"v0.2",
        "status":status,
        "checked_target_basename":TARGET_BASENAME,
        "checked_author_code_path":EXPECTED_AUTHOR_CODE_PATH,
        "figshare_article_id":FIGSHARE_ARTICLE,
        "author_github_repo":GITHUB_REPO,
        "figshare":fig,
        "github":gh,
        "errors":errors,
        "authoritative_target_tree_located":bool(fig_target or gh_target),
        "next_gate":next_gate,
        "outcome_firewall":{
            "six_HPLC_numeric_values_opened":False,
            "compound_presence_patterns_computed":False,
            "branch_presence_patterns_computed":False,
            "state_frequencies_computed":False,
            "AUC_computed":False,
            "permutations_computed":False,
            "winner_computed":False,
        },
        "ruellia_specific_promotion_rule_changed":False,
        "paper1_science_changed":False,
        "el_v0_3_science_changed":False,
    }
    a.out.write_text(json.dumps(out,indent=2,ensure_ascii=False,sort_keys=True)+"\n")
    print(json.dumps({
        "status":status,
        "figshare_current_version":None if fig is None else fig["current_version"],
        "figshare_current_modified_date":None if fig is None else fig["current_modified_date"],
        "figshare_exact_target_hits":fig_target,
        "figshare_tree_like_hits":[] if fig is None else fig["tree_like_hits"],
        "github_head":None if gh is None else gh["head_sha"],
        "github_exact_target_hits":gh_target,
        "github_tree_like_hits":[] if gh is None else gh["tree_like_hits"],
        "analysis_target_path_present":None if gh is None else gh["analysis_expected_target_path_present"],
        "errors":errors,
    },indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
