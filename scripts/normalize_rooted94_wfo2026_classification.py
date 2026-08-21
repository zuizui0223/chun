#!/usr/bin/env python3
"""Normalize rooted94 tips using WFO Plant List 2026-06 classification.csv.

The pinned Zenodo R-backbone snapshot contains one ~953 MB classification.csv.
We stream it and retain only Theaceae records, then resolve exact legacy
*species-binomial* inputs using species-rank WFO name records only.

Resolution rules are deliberately narrow:
1. exact species-rank WFO name records that all lead to one accepted species;
2. if a binomial is a nomenclatural homonym, prefer the unique *currently
   accepted record with the same binomial* over synonym homonyms;
3. only for legacy names absent from the WFO species-rank snapshot, allow a
   small curated override registry with an external authority. Every override
   target must itself be verified as a current accepted WFO species.
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

def candidate_tuples(name,records,index):
    out=[]
    for tid in index.get(name,[]):
        src=records[tid]; acc=accepted(src,records)
        if not acc:continue
        spp=species_parent(acc,records)
        if not spp:continue
        s=binomial(spp)
        if s:out.append((s,src,acc,spp))
    return out

def current_accepted_record_for_species(name,records,index):
    candidates=candidate_tuples(name,records,index)
    xs=[x for x in candidates if x[0]==name and x[1]["taxonID"]==x[2]["taxonID"] and "accepted" in x[1]["taxonomicStatus"].casefold()]
    if len(xs)!=1:
        return None
    return xs[0]

def row_from_chosen(name,status,method,candidates,chosen,override=None):
    groups=sorted({x[0] for x in candidates})
    return {
        "legacy_name":name,"match_status":status,"resolution_method":method,
        "n_exact_species_rank_records":len(candidates),"n_resolved_records":len(candidates),
        "accepted_species_candidates":";".join(groups),
        "matched_taxon_id":chosen[1]["taxonID"] if chosen else "",
        "matched_scientific_name":chosen[1]["scientificName"] if chosen else "",
        "matched_taxonomic_status":chosen[1]["taxonomicStatus"] if chosen else "",
        "accepted_taxon_id":chosen[2]["taxonID"] if chosen else "",
        "accepted_name_full":chosen[2]["scientificName"] if chosen else "",
        "accepted_rank":chosen[2]["taxonRank"] if chosen else "",
        "accepted_species_taxon_id":chosen[3]["taxonID"] if chosen else "",
        "accepted_species":chosen[0] if chosen else "",
        "input_record_is_accepted_usage":bool(chosen and chosen[1]["taxonID"]==chosen[2]["taxonID"]),
        "override_reason":(override or {}).get("override_reason",""),
        "override_source_authority":(override or {}).get("source_authority",""),
        "override_source_url":(override or {}).get("source_url",""),
        "override_evidence_note":(override or {}).get("evidence_note",""),
    }

def resolve(name,records,index):
    candidates=candidate_tuples(name,records,index)
    groups=sorted({x[0] for x in candidates})
    if len(groups)==1:
        same=[x for x in candidates if x[0]==groups[0]]
        same.sort(key=lambda x:(0 if x[1]["taxonID"]==x[2]["taxonID"] else 1,x[1]["taxonID"]))
        return row_from_chosen(name,"resolved","exact_species_rank",candidates,same[0])
    if len(groups)>1:
        # Example: Camellia sasanqua Thunb. is accepted, while the later
        # homonym C. sasanqua Blanco is a synonym of C. oleifera. A legacy
        # binomial with no author is deterministically mapped to the unique
        # current accepted same-binomial record, and this decision is explicit.
        preferred=[x for x in candidates if x[0]==name and x[1]["taxonID"]==x[2]["taxonID"] and "accepted" in x[1]["taxonomicStatus"].casefold()]
        if len(preferred)==1:
            return row_from_chosen(name,"resolved","unique_current_accepted_same_binomial_homonym",candidates,preferred[0])
        return row_from_chosen(name,"ambiguous","unresolved_ambiguous_exact_species_rank",candidates,None)
    return row_from_chosen(name,"unresolved","no_exact_species_rank_record",candidates,None)

def read_overrides(path):
    out={}
    with path.open(newline="",encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            name=clean(r.get("legacy_name")); target=clean(r.get("accepted_species"))
            if not name or not target:raise SystemExit(f"bad override row: {r}")
            if name in out:raise SystemExit(f"duplicate override: {name}")
            out[name]={k:clean(v) for k,v in r.items()}
    return out

def apply_override(row,override,records,index):
    if row["match_status"]=="resolved":
        raise SystemExit(f"override supplied for already resolved name {row['legacy_name']}")
    target=override["accepted_species"]
    chosen=current_accepted_record_for_species(target,records,index)
    if chosen is None:
        raise SystemExit(f"override target is not a unique current accepted WFO species: {target}")
    # Preserve automatic candidates in audit while making the external override explicit.
    candidates=candidate_tuples(row["legacy_name"],records,index)
    x=row_from_chosen(row["legacy_name"],"resolved","curated_external_legacy_override",candidates,chosen,override)
    x["accepted_species_candidates"]=(row.get("accepted_species_candidates") or "")
    x["n_exact_species_rank_records"]=row["n_exact_species_rank_records"]
    x["n_resolved_records"]=row["n_resolved_records"]
    return x

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--tree",type=Path,required=True);ap.add_argument("--snapshot",type=Path,required=True);ap.add_argument("--overrides",type=Path,required=True);ap.add_argument("--out-dir",type=Path,required=True);a=ap.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
    tree=Phylo.read(str(a.tree),"newick"); tips=sorted(t.name for t in tree.get_terminals() if t.name)
    if len(tips)!=94:raise SystemExit(f"expected 94 tips, got {len(tips)}")
    names=[tip_name(x) for x in tips]
    records,index,md5,core,delim,scanned=load_theaceae(a.snapshot)
    overrides=read_overrides(a.overrides)
    rows=[]; used_overrides=set()
    for tip,name in zip(tips,names):
        r=resolve(name,records,index)
        if r["match_status"]!="resolved" and name in overrides:
            r=apply_override(r,overrides[name],records,index);used_overrides.add(name)
        r.update({"tree_tip":tip,"backbone":f"WFO Plant List {RELEASE}","release_doi":DOI});rows.append(r);print(name,r["match_status"],r["resolution_method"],"=>",r["accepted_species"])
    unused=set(overrides)-used_overrides
    if unused:raise SystemExit(f"curated overrides were not needed/used: {sorted(unused)}")
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
    methods=defaultdict(int)
    for r in rows:methods[r["resolution_method"]]+=1
    summary={
        "backbone":f"WFO Plant List {RELEASE}","release_doi":DOI,"snapshot_md5":md5,"snapshot_core":core,"snapshot_delimiter":"TAB" if delim=="\t" else "COMMA","n_snapshot_rows_scanned":scanned,"n_theaceae_records":len(records),
        "n_tree_tips":len(rows),"n_camellia_legacy_tips":len(cam),"n_polyspora_legacy_tips":len(poly),"n_unresolved_or_ambiguous":len(unresolved),"unresolved_or_ambiguous":[r["legacy_name"] for r in unresolved],
        "resolution_method_counts":dict(sorted(methods.items())),"curated_override_names":sorted(used_overrides),
        "n_accepted_species_groups_all":len(groups),"n_accepted_camellia_species_groups":len({r["accepted_species"] for r in cam if r["accepted_species"]}),"n_duplicate_accepted_species_groups":len(dup),"duplicate_groups":dup,
        "claim_ceiling":"versioned taxonomy mapping with explicit curated legacy overrides only; no species-tree remapping, trait transfer, or evolutionary claim"
    }
    (a.out_dir/"summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8");print(json.dumps(summary,indent=2))
    if len(cam)!=93 or len(poly)!=1:raise SystemExit("unexpected genus composition")
    if unresolved:raise SystemExit(f"unresolved/ambiguous names: {len(unresolved)}")
if __name__=="__main__":main()
