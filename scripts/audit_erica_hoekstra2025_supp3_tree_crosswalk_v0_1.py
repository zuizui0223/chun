#!/usr/bin/env python3
"""Inspect *real* molecular tree files in Hoekstra et al. 2025 Erica Supplement 3.

The DOI-linked Zenodo file is from a distinct 2025 taxonomic study, NOT
the original 2016 TreeBASE S18291 nor the 2024 PhytoKeys sup7 source.
Reports purely lexical tip overlap against the previously frozen 27
single-colour expression/taxon labels; does not select or analyse a tree.
"""
from __future__ import annotations
import argparse, hashlib, io, json, pathlib, urllib.request, zipfile
from Bio import Phylo

RECORD_ID=15606575
DOI="10.3897/phytokeys.257.139457.suppl3"
FILENAME="oo_1344866.zip"
MD5="d4363c6e604784b58c91d8a1d824a1f1"
SOURCES=[
    f"https://zenodo.org/api/records/{RECORD_ID}/files/{FILENAME}/content",
    f"https://zenodo.org/records/{RECORD_ID}/files/{FILENAME}?download=1",
    f"https://zenodo.org/api/records/{RECORD_ID}/files/{FILENAME}",
]
MAX_DOWNLOAD=9_000_000
TREE_SUFFIXES={".nex": "nexus", ".nexus":"nexus", ".nwk":"newick",
               ".newick":"newick", ".tre":"newick", ".tree":"newick",
               ".treefile":"newick"}

def source_admission(data:bytes):
    if hashlib.md5(data).hexdigest()!=MD5:
        raise ValueError("2025 supplementary zip MD5 does not match original published archive")
    if not data.startswith(b"PK"):
        raise ValueError("not ZIP bytes")
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        bad=z.testzip()
        if bad:raise ValueError("ZIP member CRC failure: "+bad)
        members=[]
        for m in z.infolist():
            if m.is_dir():continue
            if m.file_size>28_000_000:
                raise ValueError("ZIP has oversized extraction entry")
            members.append({"name":m.filename,"bytes":m.file_size,
                            "format":TREE_SUFFIXES.get(pathlib.PurePosixPath(m.filename).suffix.lower())})
    return members

def voucher_prefix_candidates(tips:list[str], reference:dict)->dict:
    """Source-label prefix candidates only; never voucher-verified taxa.

    E.g. qPCR Erica_abietina vs tree abietina_KG123. Published Table2
    spellings are tested independently, not silently substituted as synonyms.
    """
    rows=[r for r in reference["taxa"] if r["phenotypically_fixed_sample"]]
    if len(rows)!=27 or len(set(r["collapsed_species_lineage"] for r in rows))!=27:
        raise ValueError("original fixed-colour source lineage gate changed")
    out=[]
    colour_counts={}
    for r in rows:
        qname=r["collapsed_species_lineage"].removeprefix("Erica_")
        printed=r["table2_taxon"].replace(" ","_")
        def matches(key):
            return sorted({t for t in tips if t==key or t.startswith(key+"_")})
        literal=matches(qname)
        published=matches(printed)
        any_candidates=sorted(set(literal+published))
        out.append({
            "source_qpcr_taxon":r["qpcr_label"],
            "table2_published_name":r["table2_taxon"],
            "visible_colour":r["table2_visible_colour"],
            "raw_qpcr_epithet_tip_candidates":literal,
            "published_table2_epithet_tip_candidates":published,
            "union_unverified_voucher_candidates":any_candidates,
            "requires_taxon_and_sequence_voucher_verification":True,
            "no_taxonomic_synonym_automatically_applied":True
        })
        if any_candidates:
            c=r["table2_visible_colour"]
            colour_counts[c]=colour_counts.get(c,0)+1
    total=sum(bool(x["union_unverified_voucher_candidates"]) for x in out)
    potential={c:n*(n-1)//2 for c,n in sorted(colour_counts.items())}
    return {
        "candidate_source_lineages":total,
        "candidate_lineages_by_visible_colour":dict(sorted(colour_counts.items())),
        "potential_within_colour_unordered_lineage_pairs_not_admitted":potential,
        "possible_pair_upper_bound_for_these_label_candidates":sum(potential.values()),
        "candidate_rows":out,
        "not_a_voucher_or_sequenced_tip_crosswalk":True,
        "not_a_final_sample_or_inference_denominator":True
    }

def lexical_tip_overlap(data:bytes, member:list[dict], reference:dict)->list[dict]:
    rows=reference["taxa"]
    names=sorted({r["collapsed_species_lineage"] for r in rows
                  if r["phenotypically_fixed_sample"]})
    if len(names)!=27:
        raise ValueError("source single-colour lineage count changed")
    results=[]
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        for e in member:
            if e["format"] is None:
                continue
            if e["bytes"]>10_000_000:continue
            try:
                raw=archive.read(e["name"])
                txt=raw.decode("utf-8-sig")
                trees=Phylo.parse(io.StringIO(txt),e["format"])
                observed=[]
                for i,t in enumerate(trees):
                    if i>=30:break
                    tips=[str(x.name or "") for x in t.get_terminals()]
                    # Lexical name-identity only: no taxonomic synonyms,
                    # typo repair, accessions stripped or morphology inferred.
                    distinct=set(tips)
                    exact=sorted(distinct.intersection(names))
                    obs_branch=sum(x.branch_length is not None for x in t.get_terminals())
                    candidates=voucher_prefix_candidates(tips,reference)
                    observed.append({
                        "ordinal":i+1,"tip_count":len(tips),
                        "source_tip_name_sample":tips[:20],
                        "tip_name_exact_match_count":len(exact),
                        "exact_2019_qpcr_lineage_names":exact,
                        "tips_with_branch_lengths":obs_branch,
                        "unverified_voucher_prefix_candidates":candidates,
                        "has_both_expected_taxa_and_tree":bool(exact) and obs_branch>0,
                        "no_sequence_sampling_or_imputation_status_inferred":True
                    })
                results.append({"archive_member":e["name"],"parse_status":"PARSED",
                                "trees_examined_max_30":observed})
            except Exception as exc:
                # Some original NEXUS alignments end in .nex and contain
                # malformed/alternative character definitions for Bio.Nexus.
                # Preserve source identity and diagnose per-member rather than
                # aborting the entire independently verified ZIP archive.
                results.append({"archive_member":e["name"],"parse_status":"HOLD_PARSE",
                                "error":type(exc).__name__+": "+str(exc)[:240],
                                "no_tree_information_inferred":True})
    return results

def run(reference:dict, timeout:int=20, fetcher=None):
    fetcher=fetcher or urllib.request.urlopen
    receipt={"version":"v0.1","source_doi":DOI,"original_zenodo_record":RECORD_ID,
        "expected_original_zip_md5":MD5,
        "classification":"DISTINCT_2025_PHYLOGENY_SOURCE_ONLY",
        "status":"HOLD_ZENODO_TREE_BYTES_UNAVAILABLE",
        "routes":[],"file_source_verified":False,"observed_sequence_tips_admitted":False,
        "original_2016_tree_substituted":False,
        "tree_chosen_for_memory_estimator":False,
        "visible_colour_expression_tree_admission":False,
        "independent_gene_memory_replication":False,
        "frozen_AJB_and_EL_unchanged":True}
    for url in SOURCES:
        route={"url":url,"status":"HOLD"}
        try:
            req=urllib.request.Request(url,headers={
                "User-Agent":"CHUN-Erica-Hoekstra2025-Sup3/0.1",
                "Accept":"application/zip,application/octet-stream,*/*"})
            with fetcher(req,timeout=timeout) as response:
                route["http_status"]=getattr(response,"status",200)
                if route["http_status"]!=200:
                    raise ValueError("HTTP "+str(route["http_status"]))
                data=response.read(MAX_DOWNLOAD+1)
            if len(data)>MAX_DOWNLOAD:
                raise ValueError("source bytes exceed fixed budget")
            members=source_admission(data)
            receipt["status"]="PASS_EXACT_2025_ZIP_SOURCE_NO_EVOLUTIONARY_MEMORY_INFERENCE"
            receipt["file_source_verified"]=True
            receipt["source_sha256"]=hashlib.sha256(data).hexdigest()
            receipt["original_zip_size_bytes"]=len(data)
            receipt["members"]=members
            receipt["parsed_tree_candidates"]=lexical_tip_overlap(data,members,reference)
            route["status"]="PASS_EXACT_ARCHIVE"
            receipt["routes"].append(route)
            return receipt,data
        except (OSError,ValueError,zipfile.BadZipFile) as exc:
            route["error"]=type(exc).__name__+": "+str(exc)[:280]
            receipt["routes"].append(route)
    return receipt,None

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--crosswalk",type=pathlib.Path,required=True)
    p.add_argument("--out",type=pathlib.Path,required=True)
    p.add_argument("--zip-out",type=pathlib.Path)
    p.add_argument("--timeout",type=int,default=20)
    a=p.parse_args()
    if not 1<=a.timeout<=45:raise ValueError("bad timeout")
    reference=json.loads(a.crosswalk.read_text(encoding="utf-8"))
    result,data=run(reference,a.timeout)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    if data and a.zip_out:
        a.zip_out.parent.mkdir(parents=True,exist_ok=True)
        a.zip_out.write_bytes(data)
    print("ERICA_HOEKSTRA2025_STATUS",result["status"])
    for route in result["routes"]:print("ERICA_SOURCE_ROUTE",route)
    for m in result.get("members",[]):print("ERICA_TREE_ARCHIVE_MEMBER",m)
    for tree in result.get("parsed_tree_candidates",[]):
        print("ERICA_TREE_TIP_LEXICAL_CROSSWALK",json.dumps(tree)[:12000])
    print("NO_NEW_PHYLOGENETIC_MEMORY_TEST")

if __name__=="__main__":main()
