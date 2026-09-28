#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FREEZE=ROOT/"data"/"cross_radiation_el_v0_3_science_freeze_v0_1.json"

SUBMISSION_ASSETS=[
  "submission/CROSS_RADIATION_EL_SUBMISSION_METADATA_V0_2.json",
  "submission/CROSS_RADIATION_EL_V0_3_COVER_LETTER_V0_1.md",
  "submission/CROSS_RADIATION_EL_V0_3_UPLOAD_MANIFEST_V0_1.json",
  "data/cross_radiation_el_v0_3_submission_readiness_v0_1.json",
  "docs/CROSS_RADIATION_EL_CURRENT_SUBMISSION_CANDIDATE_V0_3.md",
  "docs/CROSS_RADIATION_EL_V0_3_SUBMISSION_READINESS_V0_1.md",
  "scripts/export_cross_radiation_el_v0_3_submission_figures_v0_1.py",
  "scripts/audit_cross_radiation_el_v0_3_submission_readiness_v0_1.py",
  "scripts/build_cross_radiation_el_v0_3_submission_docx_v0_1.py",
  "scripts/build_cross_radiation_el_v0_3_snapshot_v0_1.py",
]


def run(*args)->str:
    return subprocess.check_output(args,cwd=ROOT,text=True).strip()


def sha256(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()


def git_blob(path:str)->str:
    return run("git","hash-object",path)


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--out-dir",type=Path,required=True)
    ap.add_argument("--zip",type=Path,required=True)
    a=ap.parse_args()
    a.out_dir.mkdir(parents=True,exist_ok=True)
    a.zip.parent.mkdir(parents=True,exist_ok=True)

    freeze=json.loads(FREEZE.read_text())
    science=freeze["protected_assets"]
    mismatches=[]
    entries=[]
    for row in science:
        p=row["path"]
        path=ROOT/p
        observed=git_blob(p)
        if observed!=row["git_blob_sha"]:
            mismatches.append({"path":p,"expected":row["git_blob_sha"],"observed":observed})
        entries.append({
          "path":p,
          "role":"frozen_science",
          "git_blob_sha":observed,
          "sha256":sha256(path),
          "bytes":path.stat().st_size
        })
    if mismatches:
        raise RuntimeError(f"frozen science mismatch: {mismatches}")

    for p in SUBMISSION_ASSETS:
        path=ROOT/p
        if not path.exists():
            raise RuntimeError(f"missing submission asset: {p}")
        entries.append({
          "path":p,
          "role":"submission_tooling_or_metadata",
          "git_blob_sha":git_blob(p),
          "sha256":sha256(path),
          "bytes":path.stat().st_size
        })

    commit=run("git","rev-parse","HEAD")
    manifest={
      "version":"v0.1",
      "status":"EL_V0_3_REPRODUCIBILITY_SNAPSHOT_CANDIDATE_READY",
      "repository":"zuizui0223/chun",
      "source_commit":commit,
      "frozen_science_origin_commit":freeze["frozen_from_main_commit"],
      "frozen_science_asset_count":len(science),
      "submission_asset_count":len(SUBMISSION_ASSETS),
      "entries":entries,
      "archive_identifier":{"doi":None,"version":None,"url":None},
      "archive_identifier_pending":True,
      "note":"This filtered snapshot contains the frozen v0.3 science contract plus submission tooling and metadata. Third-party source datasets remain referenced by their original repository identifiers and are not redistributed here.",
      "scientific_results_changed":False
    }

    mp=a.out_dir/"SNAPSHOT_MANIFEST.json"
    readme=a.out_dir/"README.md"
    readme.write_text(
      "# CHUN cross-radiation Evolution Letters v0.3 reproducibility snapshot\n\n"
      "This package is generated from the frozen Evolution Letters v0.3 science contract. "
      "It contains the protected manuscript, results, validators, and submission tooling. "
      "Third-party datasets are not redistributed; use the persistent source identifiers cited in the manuscript.\n\n"
      "Source commit: "+commit+"\n\n"
      "The archive DOI, version, and URL are intentionally unset until a persistent repository mints them.\n"
    )

    with zipfile.ZipFile(a.zip,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        z.write(readme,"README.md")
        for row in entries:
            z.write(ROOT/row["path"],row["path"])

    manifest["snapshot_zip"]={
      "filename":a.zip.name,
      "bytes":a.zip.stat().st_size,
      "sha256":sha256(a.zip)
    }
    mp.write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")

    with zipfile.ZipFile(a.zip,"a",compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        z.write(mp,"SNAPSHOT_MANIFEST.json")

    print(json.dumps({
      "status":manifest["status"],
      "source_commit":commit,
      "entries":len(entries),
      "zip":manifest["snapshot_zip"]
    },indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
