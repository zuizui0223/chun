#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import urllib.parse
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
V1=ROOT/"scripts"/"probe_phaidra_abiotic_source_v0_1.py"
spec=importlib.util.spec_from_file_location("v1probe",V1)
v1=importlib.util.module_from_spec(spec)
spec.loader.exec_module(v1)

ROOT_CANDIDATES=v1.ROOT_CANDIDATES
BASES=v1.BASES


def pids_from_root_info(payload, root_pid:str)->list[str]:
    if payload is None:
        return []
    return v1.extract_pids(payload,exclude=(root_pid,))


def search_members_current_fields(root_pid:str)->tuple[list[str],list[dict]]:
    diagnostics=[]
    found=[]
    for base in BASES:
        for field in ("ispartof","ismemberof"):
            q=urllib.parse.quote("*:*")
            fq=urllib.parse.quote(f'{field}:"{root_pid}"')
            url=f"{base}/search/select?q={q}&fq={fq}&rows=1000&wt=json"
            payload,diag=v1.get_json(url)
            diag["membership_field"]=field
            diagnostics.append(diag)
            if payload is not None:
                found.extend(v1.extract_pids(payload,exclude=(root_pid,)))

        # Root search can expose current index fields such as haspart even if
        # object/{pid}/info is unavailable.
        q=urllib.parse.quote(f'pid:"{root_pid}"')
        url=f"{base}/search/select?q={q}&rows=5&wt=json"
        payload,diag=v1.get_json(url)
        diag["membership_field"]="root_pid_search_for_haspart"
        diagnostics.append(diag)
        if payload is not None:
            found.extend(v1.extract_pids(payload,exclude=(root_pid,)))
    return sorted(set(found),key=lambda s:int(s.split(":")[1])),diagnostics


def inventory_root(candidate:dict)->dict:
    pid=candidate["pid"]
    root_payload=None
    root_info_diags=[]
    encoded=urllib.parse.quote(pid,safe="")
    for base in BASES:
        for token in (encoded,pid):
            payload,diag=v1.get_json(f"{base}/object/{token}/info")
            root_info_diags.append(diag)
            if payload is not None and root_payload is None:
                root_payload=payload

    direct=pids_from_root_info(root_payload,pid)
    searched,search_diags=search_members_current_fields(pid)
    member_pids=sorted(set(direct+searched),key=lambda s:int(s.split(":")[1]))

    root_summary=v1.summarize_info(pid,root_payload) if root_payload is not None else None
    members=[]
    for mpid in member_pids:
        row,diags=v1.first_object_info(mpid)
        if row is None:
            row={"pid":mpid,"info_status":"UNAVAILABLE"}
        else:
            row["info_status"]="READY"
        row["diagnostics"]=diags
        members.append(row)

    return {
        "pid":pid,
        "provenance":candidate["provenance"],
        "root_object":root_summary,
        "root_info_ready":root_payload is not None,
        "direct_related_pid_count":len(direct),
        "search_member_pid_count":len(searched),
        "member_count":len(member_pids),
        "members":members,
        "root_info_diagnostics":root_info_diags,
        "current_membership_search_diagnostics":search_diags,
    }


def choose_source(roots:list[dict])->dict|None:
    qualifying=[]
    for root in roots:
        relevant=[
            m for m in root["members"]
            if m.get("candidate_environment_or_code")
        ]
        root_relevant=bool((root.get("root_object") or {}).get("candidate_environment_or_code"))
        if root_relevant or relevant:
            qualifying.append({
                "pid":root["pid"],
                "provenance":root["provenance"],
                "root_relevant":root_relevant,
                "relevant_member_count":len(relevant),
                "relevant_members":[
                    {k:m.get(k) for k in ("pid","filename","title","mimetype","size")}
                    for m in relevant
                ],
            })
    return qualifying[0] if len(qualifying)==1 else None


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    a.out.parent.mkdir(parents=True,exist_ok=True)

    roots=[inventory_root(c) for c in ROOT_CANDIDATES]
    chosen=choose_source(roots)
    if chosen is not None:
        status="PHAIDRA_ABIOTIC_SOURCE_IDENTITY_READY_V0_2"
    elif any(r["root_info_ready"] or r["member_count"]>0 for r in roots):
        status="HOLD_PHAIDRA_SOURCE_IDENTITY_AMBIGUOUS_V0_2"
    else:
        status="HOLD_PHAIDRA_SOURCE_METADATA_UNAVAILABLE_V0_2"

    out={
        "version":"v0.2",
        "status":status,
        "article_doi":"10.1002/ajb2.70044",
        "article_data_availability_pid":"o:2098641",
        "current_record_candidate_pid":"o:2322953",
        "change_from_v0_1":"Recheck current PHAIDRA membership discovery using both ispartof (current indexed field) and legacy ismemberof, plus root-index haspart discovery.",
        "roots":roots,
        "chosen_source":chosen,
        "outcome_firewall":{
            "member_file_contents_downloaded":False,
            "environmental_rows_opened":False,
            "flower_memory_outcome_fit":False,
        },
        "next_gate":(
            "FREEZE_RELEVANT_MEMBER_IDENTITIES_BEFORE_ANY_FILE_CONTENT_OPENING"
            if chosen is not None else "STOP_HOLD"
        ),
        "paper1_science_changed":False,
        "el_v0_3_science_changed":False,
    }
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "status":status,
        "chosen_source":chosen,
        "roots":[{
            "pid":r["pid"],
            "root_info_ready":r["root_info_ready"],
            "direct_related_pid_count":r["direct_related_pid_count"],
            "search_member_pid_count":r["search_member_pid_count"],
            "member_count":r["member_count"],
            "relevant_members":[
                {k:m.get(k) for k in ("pid","filename","title","mimetype","size")}
                for m in r["members"] if m.get("candidate_environment_or_code")
            ],
        } for r in roots]
    },indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
