#!/usr/bin/env python3
"""Retrospective named-taxon Erica voucher-averaged developmental-expression correlation.

This is a NEW, explicitly distinct operational estimand, not a repair of the
frozen original 2016-tree same-tip Erica source HOLD and not a direct
cross-radiation replication of Petunieae exact-pigment-state memory.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import io
import itertools
import json
from pathlib import Path
import sys
import zipfile

import numpy as np
from scipy.stats import rankdata
from Bio import Phylo

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from audit_erica_qpcr_source_keys_v0_1 import (
    extract_rows, source_key_audit, ID_PATTERN)
from preflight_erica_qpcr_xlsx_source_v0_1 import inventory_xlsx


def fixed_expression(xlsx:bytes, taxon_rows:list[dict], design:dict):
    audit=source_key_audit(xlsx)
    if audit["status"]!="SOURCE_KEYS_ADMITTED_FOR_SCHEMA_ONLY":
        raise ValueError("original 2019 qPCR source keys unavailable")
    tabs={x["name"]:x["sheet_xml"] for x in inventory_xlsx(xlsx)["sheets"]}
    source=extract_rows(xlsx,tabs["Fold Change"])
    if len(source)!=721 or source[0]["A"]!="ID_REF":
        raise ValueError("original Fold Change worksheet differs")
    stages=design["support"]["three_developmental_stages"]
    genes=design["support"]["full_fixed_gene_panel"]
    n=len(taxon_rows)
    labels=[r["qpcr_source_taxon"] for r in taxon_rows]
    if n!=22 or len(set(labels))!=22:
        raise ValueError("changed 22 independent named-taxon frame")
    values={}
    for row in source[1:]:
        m=ID_PATTERN.fullmatch(row["A"].strip())
        if not m:
            raise ValueError("invalid original source gene+stage identifier")
        name=m.group("taxon")
        stage=m.group("stage").lower()
        gene=m.group("gene")
        if gene=="PTB1_REF":
            continue
        key=(name,stage,gene)
        if key in values:raise ValueError("duplicate original qPCR measurement")
        try:
            v=float(row.get("B",""))
        except ValueError as exc:
            raise ValueError("non-numeric original qPCR pathway fold change") from exc
        if not np.isfinite(v) or v<0:
            raise ValueError("invalid negative or nonfinite fold change")
        values[key]=v
    features=[(stage,gene) for stage in stages for gene in genes]
    if len(features)!=21:
        raise ValueError("21 prespecified age-by-gene coordinates changed")
    X=np.empty((n,21),dtype=float)
    for i,name in enumerate(labels):
        for j,(stage,gene) in enumerate(features):
            key=(name,stage,gene)
            if key not in values:raise ValueError("missing full fixed 21-gene-stage measurement")
            X[i,j]=values[key]
    transformed=np.log1p(X)
    sd=transformed.std(axis=0,ddof=0)
    if not np.isfinite(transformed).all() or np.any(sd<=1e-12):
        raise ValueError("unidentified nonvariable expression feature")
    standardized=(transformed-transformed.mean(axis=0))/sd
    return standardized,features,audit


def frozen_taxon_frame(support:dict,design:dict):
    files=support["trees"]
    if len(files)!=3:raise ValueError("three original molecular source partitions missing")
    orig=files[0]
    rows=sorted((x for x in orig["source_taxa"] if x["remaining_count"]>0),
                key=lambda x:x["qpcr_source_taxon"])
    counts=dict(sorted(collections.Counter(x["visible_colour"] for x in rows).items()))
    if len(rows)!=22 or counts!=dict(sorted(design["support"]["expected_by_colour"].items())):
        raise ValueError("molecular taxon source support changed")
    for other in files[1:]:
        b={x["qpcr_source_taxon"]:x for x in other["source_taxa"]}
        for a in rows:
            k=a["qpcr_source_taxon"]
            if sorted(b[k]["remaining_tip_candidates"])!=sorted(a["remaining_tip_candidates"]):
                # IQ-TREE data subsets sometimes replace molecular marker
                # vouchers. Keep each specific source set separately;
                # no assumption that all partitions have same tips.
                if b[k]["remaining_count"]==0:
                    raise ValueError("taxon absent from a molecular sensitivity source")
    return rows


def source_tip_mean_distances(zip_bytes:bytes, support:dict,
                              taxon_order:list[str])->dict[str,np.ndarray]:
    if hashlib.md5(zip_bytes).hexdigest()!=support["trees"][0].get("published_archive_md5",
                                                               "d4363c6e604784b58c91d8a1d824a1f1"):
        raise ValueError("original Hoekstra 2025 molecular tree archive MD5 mismatch")
    if len(support["trees"])!=3:raise ValueError("source trees missing")
    result={}
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        members={Path(s).name:s for s in z.namelist()
                 if s.endswith(".treefile") and "Phylogenetic analysis results/" in s}
        if len(members)!=3:raise ValueError("archive original treefile count changed")
        for record in support["trees"]:
            key=record["tree"]
            if key not in members:raise ValueError("frozen IQ-TREE result not in archive")
            source_by={r["qpcr_source_taxon"]:r for r in record["source_taxa"]}
            phylo=Phylo.read(io.StringIO(z.read(members[key]).decode("utf-8-sig")),"newick")
            tips={x.name:x for x in phylo.get_terminals()}
            if len(tips)!=record["original_tree_tips"]:
                raise ValueError("original molecular terminal count drift")
            sets={k:source_by[k]["remaining_tip_candidates"] for k in taxon_order}
            if any(not vv or any(t not in tips for t in vv) for vv in sets.values()):
                raise ValueError("unresolved taxon or voucher source")
            dm=np.zeros((len(taxon_order),len(taxon_order)),dtype=float)
            for i in range(len(taxon_order)):
                for j in range(i+1,len(taxon_order)):
                    a,b=taxon_order[i],taxon_order[j]
                    vals=[float(phylo.distance(tips[x],tips[y]))
                          for x,y in itertools.product(sets[a],sets[b])]
                    if not vals or not all(np.isfinite(v) and v>0 for v in vals):
                        raise ValueError("invalid molecular voucher distances")
                    dm[i,j]=dm[j,i]=np.mean(vals)
            result[key]=dm
    return result


def same_hue_pairs(colour:list[str]):
    ii,jj=np.triu_indices(len(colour),1)
    c=np.asarray(colour)
    select=c[ii]==c[jj]
    return ii[select],jj[select]


def rank_corr(dist:np.ndarray,x:np.ndarray,ii:np.ndarray,jj:np.ndarray):
    a=rankdata(dist[ii,jj]).astype(float)
    y=np.sqrt(np.mean((x[ii]-x[jj])**2,axis=1))
    b=rankdata(y).astype(float)
    aa=a-a.mean();bb=b-b.mean()
    den=np.sqrt(float(np.dot(aa,aa)*np.dot(bb,bb)))
    if den<=1e-12:raise ValueError("uninformative rank association")
    return float(np.dot(aa,bb)/den)


def analyze(xlsx:bytes, zip_bytes:bytes, support:dict, design:dict,
            *,permutations:int|None=None):
    taxa=frozen_taxon_frame(support,design)
    names=[r["qpcr_source_taxon"] for r in taxa]
    colours=[r["visible_colour"] for r in taxa]
    ii,jj=same_hue_pairs(colours)
    if len(ii)!=design["support"]["unordered_within_colour_taxon_pairs"]:
        raise ValueError("changed within-colour source pair count")
    expression,features,audit=fixed_expression(xlsx,taxa,design)
    sources=source_tip_mean_distances(zip_bytes,support,names)
    primary=design["operational_distance"]["primary_tree_filename"]
    if primary not in sources:raise ValueError("chosen source partition not admitted")
    dist=sources[primary]
    observed=rank_corr(dist,expression,ii,jj)
    permutations=permutations if permutations is not None else design["main_test"]["n_permutations"]
    if permutations<9:raise ValueError("not enough permutations")
    seed=design["main_test"]["seed"]
    rng=np.random.default_rng(seed)
    groups=[np.flatnonzero(np.asarray(colours)==key) for key in sorted(set(colours))]
    null=np.empty(permutations)
    for b in range(permutations):
        perm=np.arange(len(names))
        for g in groups:
            perm[g]=rng.permutation(g)
        null[b]=rank_corr(dist,expression[perm],ii,jj)
    mean=float(null.mean())
    p=float((1+np.count_nonzero(null>=observed))/(permutations+1))
    passed=observed>mean and p<=0.05
    others={}
    for tree,dm in sources.items():
        others[tree]={"rho":rank_corr(dm,expression,ii,jj),
                      "role":"DESCRIPTIVE" if tree!=primary else "PRIMARY"}
    leave_one=[]
    for excluded in range(len(names)):
        keep=np.arange(len(names))!=excluded
        labels=np.asarray(colours)[keep].tolist()
        aa,bb=same_hue_pairs(labels)
        r=rank_corr(dist[np.ix_(keep,keep)],expression[keep],aa,bb)
        leave_one.append(r)
    return {
        "version":"v0.1",
        "status":"SUPPORTED_EXPLORATORY_TAXON_NAME_LEVEL" if passed else "NOT_SUPPORTED_EXPLORATORY_TAXON_NAME_LEVEL",
        "design_status":design["status"],
        "design_role":"RETROSPECTIVE_DISTINCT_FROM_FROZEN_2016_TREE_DIRECT_TIP_ERICA_HOLD",
        "n_taxa":len(names),
        "n_source_same_visible_colour_pairs":len(ii),
        "n_features":len(features),
        "source_taxa":names,
        "visible_colour_counts":dict(sorted(collections.Counter(colours).items())),
        "n_original_qpcr_measurements":audit["quantitative_pathway_measurements"],
        "primary_combined_tree":primary,
        "observed_rho":observed,
        "null_mean_rho":mean,
        "null_centered_rho":observed-mean,
        "null_q025":float(np.quantile(null,0.025)),
        "null_q975":float(np.quantile(null,0.975)),
        "p_one_sided":p,
        "n_permutations":permutations,
        "seed":seed,
        "descriptive_tree_partition_results":others,
        "leave_one_taxon_out_descriptive":{
            "positive":sum(v>0 for v in leave_one),
            "n":len(leave_one),
            "min_rho":min(leave_one),
            "median_rho":float(np.median(leave_one)),
            "max_rho":max(leave_one)
        },
        "source_md5_verified":True,
        "qPCR_and_DNA_same_specimens":False,
        "voucher_uncertainty_integrated_uniformly":True,
        "independent_exact_pigment_chemical_memory_replication":False,
        "no_causal_molecular_or_selection_claim":True,
        "original_2016_Erica_primary_test_HOLD":True,
        "original_Petunieae_result_untouched":True,
        "original_AJB_EL_science_unchanged":True
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-xlsx",type=Path,required=True)
    p.add_argument("--source-phylogeny-zip",type=Path,required=True)
    p.add_argument("--source-candidates",type=Path,required=True)
    p.add_argument("--design",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--permutations",type=int)
    a=p.parse_args()
    des=json.loads(a.design.read_text())
    report=analyze(a.source_xlsx.read_bytes(),a.source_phylogeny_zip.read_bytes(),
                   json.loads(a.source_candidates.read_text()),des,
                   permutations=a.permutations)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print("ERICA_VOUCHER_AVERAGED_RETROSPECTIVE_RESULT",json.dumps({
        key:report[key] for key in (
            "status","n_taxa","n_source_same_visible_colour_pairs","n_features",
            "observed_rho","null_mean_rho","null_centered_rho","p_one_sided",
            "n_permutations","descriptive_tree_partition_results",
            "leave_one_taxon_out_descriptive")},sort_keys=True))
    print("DOES_NOT_OVERRIDE_FROZEN_ORIGINAL_ERICA_EVIDENCE_HOLD")

if __name__=="__main__":
    main()
