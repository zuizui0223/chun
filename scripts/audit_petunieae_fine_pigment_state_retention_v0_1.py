#!/usr/bin/env python3
"""Audit how the frozen Petunieae rare-state gate changes biochemical coverage.

Descriptive source-support audit only. No change to prior cohort, p-values,
state thresholds, or the frozen nested molecular-memory result.
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from analyze_petunieae_nested_regulatory_memory_v0_1 import fine_sixbit, sha256

def audit(source:Path, design_path:Path)->dict:
    design=json.loads(design_path.read_text(encoding="utf-8"))
    spec=design["source"]
    table=source/spec["processed_csv_path"]
    tree=source/spec["tree_path"]
    original_script=source/"processed/phyloCCA__phyloCCA_expression_HPLC-with-flavs-final.r"
    for path,key in [(table,"processed_csv_sha256"),(tree,"tree_sha256"),
                     (original_script,"source_script_sha256")]:
        if sha256(path)!=spec[key]:
            raise ValueError("frozen source SHA256 mismatch: "+key)
    source_manifest=json.loads((source/"source_manifest.json").read_text())
    if source_manifest["authoritative_prefix"]!="phyloCCA" or source_manifest["required_duplicate_identity"]!="PASS_PHYLOCCA_PHYLOPCA_CSV_AND_TREE_OSF_METADATA_IDENTICAL":
        raise ValueError("source manifest duplicate identity mismatch")
    df=pd.read_csv(table)
    if len(df)!=60 or df["key_0"].duplicated().any() or int((df["key_0"]=="BROW").sum())!=1:
        raise ValueError("source row frame invalid")
    d=df[df["key_0"]!="BROW"].copy()
    cols=design["frame"]["fine_six_compounds_order"]
    codes=fine_sixbit(d,cols)
    count=collections.Counter(codes)
    k=[count[c]>=5 for c in codes]
    kept=d.loc[k];excluded=d.loc[[not v for v in k]]
    retained=collections.Counter(c for c,keep in zip(codes,k) if keep)
    if len(kept)!=47 or len(excluded)!=12 or len(retained)!=6:
        raise ValueError("rare state frame drift")
    if dict(sorted(retained.items()))!={"000000":6,"000010":6,"000011":6,"000100":10,"000110":6,"000111":13}:
        raise ValueError("frozen six-bit fine class occupancy drift")
    def positive_counts(frame):
        return {col:int((frame[col]>0).sum()) for col in cols}
    a=positive_counts(kept)
    b=positive_counts(excluded)
    varying=[col for col in cols if 0<a[col]<len(kept)]
    invariant_absent=[col for col in cols if a[col]==0]
    return {
      "version":"v0.1",
      "status":"PETUNIEAE_FROZEN_RARE_STATE_FILTER_COVERAGE_AUDITED",
      "source_verified":True,
      "unfiltered_ingroup_tips":len(d),
      "retained_tips":len(kept),
      "excluded_tips":len(excluded),
      "fine_states_unfiltered":len(count),
      "fine_states_retained":len(retained),
      "unfiltered_sixbit_state_counts":dict(sorted(count.items())),
      "retained_sixbit_state_counts":dict(sorted(retained.items())),
      "retained_compound_positive_tips":a,
      "excluded_compound_positive_tips":b,
      "retained_variable_anthocyanidin_compounds":varying,
      "retained_constant_zero_anthocyanidin_compounds":invariant_absent,
      "all_rare_branch_positive_removed":all(b[col]>0 for col in invariant_absent),
      "three_bit_reduction_preserves_fine_partition":len({c[3:] for c in retained})==len(retained) and all(c.startswith("000") for c in retained),
      "primary_cohort_or_result_changed":False,
      "claim_boundary":"The 47-tip molecular-memory result conditions on the six-source-compound assay, but only the Del/Pet/Malv derivatives vary after its frozen rare-state filtering. No tested inference covers within-class regulatory memory for retained Pel/Cyan/Peon-positive species.",
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--design",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    d=audit(a.source,a.design)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(d,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
