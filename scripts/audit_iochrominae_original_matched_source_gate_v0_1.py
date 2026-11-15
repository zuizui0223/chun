#!/usr/bin/env python3
"""Fail-closed admission of independent original Iochrominae matched raw data.

No download or substitution. Requires the investigator to supply *verified*
2018 HPLC and qPCR species-level numerical tables and the *author-used*
dated tree, plus immutable original-source SHA256 receipts. This gate does
not calculate or expose a gene-to-metabolite association.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path
from Bio import Phylo


def sha256(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()


def numeric_table(path:Path,taxon_col:str,quant_cols:list[str])->dict:
    if not quant_cols or len(quant_cols)!=len(set(quant_cols)):
        raise ValueError("original measured numerical columns must be explicitly identified")
    with path.open(newline="",encoding="utf-8-sig") as f:
        reader=csv.DictReader(f)
        if reader.fieldnames is None or taxon_col not in reader.fieldnames:
            raise ValueError("original species ID column absent")
        if any(k not in reader.fieldnames for k in quant_cols):
            raise ValueError("original HPLC/qPCR numeric column absent")
        rows=list(reader)
    if not rows:
        raise ValueError("empty original measured data")
    names=[]
    finite_by_species={}
    for row in rows:
        name=row[taxon_col].strip()
        if not name:
            raise ValueError("original taxon name missing")
        names.append(name)
        finite_by_species[name]=all(
            _isfinite_number(row[k]) for k in quant_cols)
    if len(names)!=len(set(names)):
        raise ValueError("replicate rows cannot be silently collapsed to species means")
    return {"n_rows":len(rows),"species":names,
            "finite_by_species":finite_by_species,
            "columns":quant_cols}


def _isfinite_number(value:str|None)->bool:
    if value is None or not value.strip():
        return False
    try:
        return math.isfinite(float(value))
    except ValueError:
        return False


def audit(manifest:dict)->dict:
    required=("hplc","qpcr","dated_tree")
    if not all(k in manifest for k in required):
        raise ValueError("three independently sourced original input types required")
    source={}
    for key in required:
        item=manifest[key]
        path=Path(item["path"])
        digest=item.get("original_sha256")
        if not digest or len(digest)!=64:
            raise ValueError(f"{key}: original provider SHA256 receipt required")
        if not path.is_file() or sha256(path)!=digest:
            raise ValueError(f"{key}: original bytes missing or provider hash mismatch")
        if not item.get("original_source_url") or not item.get("source_publication"):
            raise ValueError(f"{key}: authoritative original provenance required")
        source[key]={"sha256":digest,"original_source_url":item["original_source_url"],
                     "source_publication":item["source_publication"]}
    if manifest["dated_tree"].get("original_author_used_tree_verified") is not True:
        raise ValueError("different study tree is not the 2018 author-used original")
    h=numeric_table(Path(manifest["hplc"]["path"]),
                    manifest["hplc"]["species_column"],manifest["hplc"]["numeric_columns"])
    q=numeric_table(Path(manifest["qpcr"]["path"]),
                    manifest["qpcr"]["species_column"],manifest["qpcr"]["numeric_columns"])
    tree=Phylo.read(manifest["dated_tree"]["path"],"newick")
    tips=[t.name for t in tree.get_terminals()]
    if not tips or any(not t for t in tips) or len(tips)!=len(set(tips)):
        raise ValueError("dated tree has missing/duplicate source tip labels")
    if any(t.branch_length is not None and
           (not math.isfinite(t.branch_length) or t.branch_length<0)
           for t in tree.find_clades()):
        raise ValueError("original tree branch lengths invalid")
    if not any((t.branch_length or 0)>0 for t in tree.find_clades()):
        raise ValueError("original dated tree branch lengths absent")
    shared=sorted(set(h["species"])&set(q["species"])&set(tips))
    complete=[s for s in shared if h["finite_by_species"][s] and q["finite_by_species"][s]]
    if len(complete)<5:
        return {"status":"HOLD_TOO_FEW_COMPLETE_SOURCE_TIPS",
                "n_shared_tips":len(shared),"n_complete_tips":len(complete),
                "n_hplc_species":len(h["species"]),"n_qpcr_species":len(q["species"]),
                "n_tree_tips":len(tips),"sources":source}
    return {"status":"ADMIT_RAW_MATCHED_SOURCE_FRAME_NOT_AN_EFFECT_RESULT",
            "n_shared_tips":len(shared),"n_complete_tips":len(complete),
            "complete_original_tip_names":complete,
            "n_hplc_species":len(h["species"]),"n_qpcr_species":len(q["species"]),
            "n_tree_tips":len(tips),"sources":source,
            "original_2018_tree_verified":True,
            "no_gene_to_metabolite_prediction_computed":True}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    d=audit(json.loads(args.manifest.read_text(encoding="utf-8")))
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("IOCHROMINAE_ORIGINAL_SOURCE_ADMISSION",d["status"],d["n_complete_tips"])


if __name__=="__main__":
    main()
