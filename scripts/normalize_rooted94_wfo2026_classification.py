#!/usr/bin/env python3
"""Normalize rooted94 tips using WFO Plant List 2026-06 classification.csv.

The pinned Zenodo R-backbone snapshot contains one ~953 MB classification.csv.
We stream it and retain only Theaceae records, then resolve exact legacy
*species-binomial* inputs using species-rank WFO name records only. Accepted
usage links and parent links are then followed to the accepted species group.

Restricting lookup to species-rank records is essential: a species binomial such
as Camellia japonica must not be made artificially ambiguous by also indexing
all varieties/subspecies that share its genus + specific epithet.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,re,zipfile
from collections import defaultdict
from pathlib import Path
from Bio import Phylo

RELEASE="2026-06"
DOI="10.5281/zenodo.20782718"
MD5="0e4486945cd9f7af548ca87eb9a870ed"

def clean(x): return re.sub(r"\s+"," ",(x or "").strip())
def tip_name(x): return clean(x.replace("_"," "))

def binomial(r):
    g=clean(r.get("genus")); e=clean(r.get("specificEpithet"))
    if g and e:return f"{g} {e}"
    t=clean(r.get("scientificName")).replace("× ","").split()
    return " ".join(t[:2]) if len(t)>=2 else ""

def open_classification(zf):
    names=[n for n in zf.namelist() if Path(n).name.lower()=="classification.csv"]
    if len(names)!=1: raise SystemExit(f"expected classification.csv, got {names[:20]}")
    raw=zf.open(names[0]); text=io.TextIOWrapper(raw,encoding="utf-8-sig",errors="replace",newline="")
    header=text.readline()
    if not header: raise SystemExit("empty classification.csv")
    delim="\t" if header.count("\t")>header.count(",") else ","
    fields=next(csv.reader([header],delimiter=delim))
    need={"taxonID","scientificName","taxonRank","taxonomicStatus","family","acceptedNameUsageID","parentNameUsageID"}
    missing=need-set(fields)
    if missing: raise SystemExit(f"classification.csv missing fields {sorted(missing)}; fields={fields}")
    return csv.DictReader(text,fieldnames=fields,delimiter=delim),names[0],delim

def load_theaceae(path):
    md5=hashlib.md5(path.read_bytes()).hexdigest()
    if md5!=MD5:raise SystemExit(f"MD5 mismatch {md5} != {MD5}")
    records={}; index=defaultdict(list); scanned=0
    with zipfile.ZipFile(path) as zf:
        reader,core,delim=open_classification(zf)
        for r in reader:
            scanned+=1
            if clean(r.get("family")).casefold()!="theaceae":continue
            tid=clean(r.get("taxonID"))
            if not tid:continue
            rec={k:clean(r.get(k)) for k in (
                "taxonID","scientificName","taxonRank","taxonomicStatus",
                "family","genus","specificEpithet","acceptedNameUsageID","parentNameUsageID"
            )}
            records[tid]=rec
            # Inputs are species-level binomials. Index only WFO species-rank
            # name records so infraspecific records cannot create false ambiguity.
            if rec["taxonRank"].casefold()=="species":
                b=binomial(rec)
                if b:index[b].append(tid)
    return records,index,md5,core,delim,scanned

def accepted(rec,records):
    aid=rec.get("acceptedNameUsageID","")
    if aid:return records.get(aid)
    if "accepted" in rec.get("taxonomicStatus","").casefold():return rec
    return None

def species_parent(rec,records):
    seen=set(); cur=rec
    while cur:
        tid=cur.get("taxonID","")
        if not tid or tid in seen:return None
        seen.add(tid)
        if cur.get("taxonRank","").casefold()=="species":return cur
        pid=cur.get("parentNameUsageID","")
        cur=records.get(pid) if pid else None
    return None

def resolve(name,records,index):
    candidates=[]
    for tid in index.get(name,[]):
        src=records[tid]; acc=accepted(src,records)
        if not acc:continue
        spp=species_parent(acc,records)
        if not spp:continue
        s=binomial(spp)
        if s:candidates.append((s,src,acc,spp))
    groups=sorted({x[0] for x in candidates})
    status="resolved" if len(groups)==1 else ("unresolved" if not groups else "ambiguous")
    chosen=None
    if status=="resolved":
        same=[x for x in candidates if x[0]==groups[0]]
        same.sort(key=lambda x:(0 if x[1]["taxonID"]==x[2]["taxonID"] else 1,x[1]["taxonID"]))
        chosen=same[0]
    return {
        "legacy_name":name,"match_status":status,"n_exact_species_rank_records":len(index.get(name,[])),
        "n_resolved_records":len(candidates),"accepted_species_candidates":";".join(groups),
        "matched_taxon_id":chosen[1]["taxonID"] if chosen else "",
        "matched_scientific_name":chosen[1]["scientificName"] if chosen else "",
        "matched_taxonomic_status":chosen[1]["taxonomicStatus"] if chosen else "",
        "accepted_taxon_id":chosen[2]["taxonID"] if chosen else "",
        "accepted_name_full":chosen[2]["scientificName"] if chosen else "",
        "accepted_rank":chosen[2]["taxonRank"] if chosen else "",
        "accepted_species_taxon_id":chosen[3]["taxonID"] if chosen else "",
        "accepted_species":chosen[0] if chosen else "",
        "input_record_is_accepted_usage":bool(chosen and chosen[1]["taxonID"]==chosen[2]["taxonID"]),
    }

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--tree",type=Path,required=True);ap.add_argument("--snapshot",type=Path,required=True);ap.add_argument("--out-dir",type=Path,required=True);a=ap.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
    tree=Phylo.read(str(a.tree),"newick"); tips=sorted(t.name for t in tree.get_terminals() if t.name)
    if len(tips)!=94:raise SystemExit(f"expected 94 tips, got {len(tips)}")
    names=[tip_name(x) for x in tips]
    records,index,md5,core,delim,scanned=load_theaceae(a.snapshot)
    rows=[]
    for tip,name in zip(tips,names):
        r=resolve(name,records,index);r.update({"tree_tip":tip,"backbone":f"WFO Plant List {RELEASE}","release_doi":DOI});rows.append(r);print(name,r["match_status"],r["accepted_species_candidates"],"=>",r["accepted_species"])
    unresolved=[r for r in rows if r["match_status"]!="resolved"]
    cam=[r for r in rows if r["legacy_name"].startswith("Camellia ")]; poly=[r for r in rows if r["legacy_name"]=="Polyspora speciosa"]
    groups=defaultdict(list)
    for r in rows:
        if r["accepted_species"]:groups[r["accepted_species"]].append(r["tree_tip"])
    dup={k:sorted(v) for k,v in groups.items() if len(v)>1}
    with (a.out_dir/"wfo2026_06_taxonomy_registry.csv").open("w",newline="",encoding="utf-8") as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    with (a.out_dir/"astral_species_mapping.tsv").open("w",encoding="utf-8") as f:
        for r in rows:
            if r["accepted_species"]:f.write(f"{r['tree_tip']} {r['accepted_species'].replace(' ','_')}\n")
    drows=[{"accepted_species":k,"n_legacy_tips":len(v),"legacy_tips":";".join(v)} for k,v in sorted(dup.items())]
    with (a.out_dir/"duplicate_accepted_species_groups.csv").open("w",newline="",encoding="utf-8") as f:w=csv.DictWriter(f,fieldnames=["accepted_species","n_legacy_tips","legacy_tips"]);w.writeheader();w.writerows(drows)
    summary={
        "backbone":f"WFO Plant List {RELEASE}","release_doi":DOI,"snapshot_md5":md5,"snapshot_core":core,"snapshot_delimiter":"TAB" if delim=="\t" else "COMMA","n_snapshot_rows_scanned":scanned,"n_theaceae_records":len(records),
        "n_tree_tips":len(rows),"n_camellia_legacy_tips":len(cam),"n_polyspora_legacy_tips":len(poly),"n_unresolved_or_ambiguous":len(unresolved),"unresolved_or_ambiguous":[r["legacy_name"] for r in unresolved],
        "unresolved_details":[{k:r[k] for k in ("legacy_name","match_status","accepted_species_candidates","n_exact_species_rank_records")} for r in unresolved],
        "n_accepted_species_groups_all":len(groups),"n_accepted_camellia_species_groups":len({r["accepted_species"] for r in cam if r["accepted_species"]}),"n_duplicate_accepted_species_groups":len(dup),"duplicate_groups":dup,
        "claim_ceiling":"versioned taxonomy mapping only; no species-tree remapping, trait transfer, or evolutionary claim"
    }
    (a.out_dir/"summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8");print(json.dumps(summary,indent=2))
    if len(cam)!=93 or len(poly)!=1:raise SystemExit("unexpected genus composition")
    if unresolved:raise SystemExit(f"unresolved/ambiguous names: {len(unresolved)}")
if __name__=="__main__":main()
