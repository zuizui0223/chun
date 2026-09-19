#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FREEZE=ROOT/"data"/"cross_radiation_el_v0_3_science_freeze_v0_1.json"


def git_blob_sha(data:bytes)->str:
    header=f"blob {len(data)}\0".encode("utf-8")
    return hashlib.sha1(header+data).hexdigest()


def validate_freeze(x:dict, root:Path=ROOT)->dict:
    if x.get("status")!="EL_V0_3_SCIENCE_FROZEN":
        raise ValueError("freeze status drift")
    if x.get("current_candidate")!="Evolution Letters v0.3":
        raise ValueError("current candidate drift")
    if x.get("fallback_candidate")!="Evolution Letters v0.2":
        raise ValueError("fallback candidate drift")
    if x.get("science_changes_require_new_candidate_version") is not True:
        raise ValueError("science-change versioning rule disabled")
    if x.get("paper1_science_changed") is not False:
        raise ValueError("Paper 1 firewall drift")

    assets=x.get("protected_assets")
    if not isinstance(assets,list) or not assets:
        raise ValueError("protected_assets must be a non-empty list")

    seen=set()
    mismatches=[]
    missing=[]
    actual=[]
    for row in assets:
        if not isinstance(row,dict):
            raise ValueError("protected asset row must be an object")
        path=row.get("path")
        expected=row.get("git_blob_sha")
        if not isinstance(path,str) or not path:
            raise ValueError("protected asset path missing")
        if path in seen:
            raise ValueError(f"duplicate protected asset path: {path}")
        seen.add(path)
        if not isinstance(expected,str) or len(expected)!=40:
            raise ValueError(f"invalid frozen git blob SHA for {path}")
        p=root/path
        if not p.is_file():
            missing.append(path)
            continue
        got=git_blob_sha(p.read_bytes())
        actual.append({"path":path,"git_blob_sha":got})
        if got!=expected:
            mismatches.append({"path":path,"expected":expected,"actual":got})

    mutable=x.get("allowed_mutable_submission_assets")
    if not isinstance(mutable,list):
        raise ValueError("allowed_mutable_submission_assets must be a list")
    overlap=seen.intersection(mutable)
    if overlap:
        raise ValueError(f"asset cannot be both protected and mutable: {sorted(overlap)}")

    status="EL_V0_3_SCIENCE_FREEZE_VALID" if not missing and not mismatches else "EL_V0_3_SCIENCE_FREEZE_BROKEN"
    return {
        "status":status,
        "protected_assets":len(assets),
        "missing":missing,
        "mismatches":mismatches,
        "allowed_mutable_submission_assets":mutable,
        "paper1_science_changed":False,
    }


def main()->int:
    x=json.loads(FREEZE.read_text(encoding="utf-8"))
    summary=validate_freeze(x,ROOT)
    print(json.dumps(summary,indent=2))
    if summary["status"]!="EL_V0_3_SCIENCE_FREEZE_VALID":
        raise SystemExit("EL v0.3 science freeze validation failed")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
