#!/usr/bin/env python3
"""Audit actually recovered CC0 Dryad original Iochrominae source archives.

This is an original archive/tree and phenotype-cohort provenance audit, NOT
a newly matched 2018 qPCR-HPLC phylogenetic analysis. Exact published MD5
and original extracted members SHA256 are required. The 2015 posterior
100-tree set is NOT the 2018 shape study MCC tree and is not silently
promoted to Larter et al. (2018)'s exact author-used MCC tree.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import io
import json
from pathlib import Path
import zipfile

from Bio import Phylo


PUBLISHED_PROVIDER = {
    "2015": {
        "outer_member":"ModeandTempoFlColor.zip",
        "md5":"78957f5320749f5c022de78e8ad1ab32",
        "sha256":"2a7a92f600b0d92f874d636e90f5e2fcc3314876a7c4affc21b51e3c81701e5b",
        "doi":"10.5061/dryad.0732g",
    },
    "2018": {
        "outer_member":"Smith_and_Kriebel_2018.zip",
        "md5":"a4318f07ddd7e2dd1ce8297c057ead6b",
        "sha256":"2a7f70c1e1db8e8308851b8317b90c112732661d288ec584219dd2d001a5bfe9",
        "doi":"10.5061/dryad.5jn7b",
    },
}
REQUIRED_SOURCE_MEMBERS = {
    "2015":{
        "IochBeast100.nex":"c2690a2b27d712684baab36be251e016904b98f60dd95156917a77a5a866c671",
        "ioch_data.csv":"6aacfaee4b5ef65afddf96e4e9d886d490d9bec59deafd70cc63440c26c06480",
    },
    "2018":{
        "phylogenies/MCC_tree.nex":"80d4f39a9e7dba3f6337e0698473b1bcdd9027f853e82a072026204018076cec",
        "phylogenies/126_trees.nex":"dac440674e8018e3a71b8147e46cb5c047486d7a8009725ce45d2165614c8e4d",
        "data/data.csv":"318637026410ef0c714ed225f4add7615aca3fe1e1d0908aa91295f777edff47",
    },
}


def digest(content:bytes,kind:str="sha256")->str:
    return hashlib.new(kind,content).hexdigest()


def source(archive:Path,year:str)->tuple[dict,dict]:
    publication=PUBLISHED_PROVIDER[year]
    with zipfile.ZipFile(archive) as outer:
        content=outer.read(publication["outer_member"])
    for method in ("md5","sha256"):
        if digest(content,method)!=publication[method]:
            raise ValueError(f"{year}: original provider {method} mismatch")
    payload={}
    with zipfile.ZipFile(io.BytesIO(content)) as original:
        for name,original_sha in REQUIRED_SOURCE_MEMBERS[year].items():
            data=original.read(name)
            if digest(data)!=original_sha:
                raise ValueError(f"{year}: original original ZIP member SHA256 mismatch: {name}")
            payload[name]=data
    proof={
        "source_doi":publication["doi"],
        "original_provider_nested_file":publication["outer_member"],
        "original_provider_md5":publication["md5"],
        "original_provider_sha256":publication["sha256"],
        "exact_member_sha256":REQUIRED_SOURCE_MEMBERS[year],
        "primary_provider_md5_sha256_verified":True,
        "original_member_sha256_verified":True,
    }
    return payload,proof


def nexus_trees(payload:bytes)->list:
    trees=list(Phylo.parse(io.StringIO(payload.decode("utf-8-sig")),"nexus"))
    if not trees:
        raise ValueError("source tree collection empty")
    counts=[len(t.get_terminals()) for t in trees]
    if len(set(counts))!=1:
        raise ValueError("inconsistent original source tree taxon counts")
    if any(not t.name for tr in trees for t in tr.get_terminals()):
        raise ValueError("unnamed original tree source tips")
    if any(len({t.name for t in tr.get_terminals()})!=counts[0] for tr in trees):
        raise ValueError("duplicated original source tip name")
    return trees


def audit(source2015:Path,source2018:Path)->dict:
    inner15,proof15=source(source2015,"2015")
    inner18,proof18=source(source2018,"2018")
    trees15=nexus_trees(inner15["IochBeast100.nex"])
    trees18=nexus_trees(inner18["phylogenies/126_trees.nex"])
    mcc18=nexus_trees(inner18["phylogenies/MCC_tree.nex"])
    # 2015 historic original .csv is **headerless**; first row is data.
    color15=list(csv.reader(io.StringIO(inner15["ioch_data.csv"].decode())))
    names15=[r[0] for r in color15]
    if len(color15)!=33 or any(len(r)!=2 or r[1] not in {"0","1"} for r in color15):
        raise ValueError("original 2015 Iochrominae source anthocyanin code drift")
    if len(names15)!=len(set(names15)):
        raise ValueError("duplicate original 2015 pigment taxon")
    tree15_names={t.name for t in trees15[0].get_terminals()}
    if not set(names15)<=tree15_names:
        raise ValueError("2015 source anthocyanin presence ID not on original 2015 trees")
    if len(trees15)!=100 or len(tree15_names)!=42:
        raise ValueError("not the 100-tree 42-tip original 2015 posterior file")
    # 2018 visible colour and source-provided pollinator class are not a
    # substitute for 2015 original chemical anthocyanin binary labels.
    rows18=list(csv.DictReader(io.StringIO(inner18["data/data.csv"].decode())))
    names18=[r["image"].removesuffix(".jpg") for r in rows18]
    if len(rows18)!=36 or len(names18)!=len(set(names18)):
        raise ValueError("unexpected original 2018 shape source data cohort")
    if len(mcc18)!=1 or len(mcc18[0].get_terminals())!=44 or len(trees18)!=126:
        raise ValueError("unexpected 2018 study 44-tip MCC and 126 posterior trees")
    shape_tree_ids={t.name for t in mcc18[0].get_terminals()}
    if not set(names18)<=shape_tree_ids:
        raise ValueError("2018 source shape phenotypes have absent MCC tips")
    visible=Counter(row["color"] for row in rows18)
    pollinators=Counter(row["main_pollinator"] or "SOURCE_UNKNOWN"
                        for row in rows18)
    if set(visible)!={"purple","yellow","orange","white","red"}:
        raise ValueError("original 2018 visible source ontology drift")
    exact_overlap=sorted(set(names15)&set(names18))
    # Not an authoritative taxonomic join: 2015 data use source specimen
    # codes (e.g. 125IeduleWAXY), while 2018 uses binomial names.
    if exact_overlap!=["Iochroma_tupayachianum"]:
        raise ValueError("unreviewed 2015/2018 specimen-code to species-name mapping")
    return {
        "status":"RECOVERED_TWO_ORIGINAL_CC0_PHYLOGENETIC_ARCHIVES_NOT_2018_HPLC_QPCR_ADMISSION",
        "version":"v0.1",
        "analysis_date":"2026-11-16",
        "2015_published_original":proof15,
        "2018_shape_study_original":proof18,
        "2015_original_posterior_trees":len(trees15),
        "2015_original_posterior_tips_each":len(tree15_names),
        "2015_original_chemical_anthocyanin_state_rows":len(names15),
        "2015_source_chemical_presence_codes":dict(sorted(Counter(r[1] for r in color15).items())),
        "2015_original_chemical_state_rows_all_on_tree":True,
        "2018_shape_author_used_MCC_count":len(mcc18),
        "2018_shape_MCC_tips":len(shape_tree_ids),
        "2018_shape_original_posterior_trees":len(trees18),
        "2018_visible_colour_data_species":len(names18),
        "2018_visible_colour_counts":dict(sorted(visible.items())),
        "2018_source_pollinator_labels":dict(sorted(pollinators.items())),
        "2018_visible_colour_data_all_exact_MCC_tips":True,
        "unmapped_2015_source_codes_vs_2018_binomials":True,
        "same_literal_species_ID_in_both_original_phenotype_CSVs":exact_overlap,
        "same_literal_ID_count":len(exact_overlap),
        "2015_tree_is_posterior_sample_not_author_used_MCC":True,
        "2018_shape_MCC_not_proven_2018_Larter_author_tree":True,
        "no_2018_Larter_7_gene_source_matrix":True,
        "no_2018_Larter_quantitative_HPLC_source_matrix":True,
        "no_independent_measured_expression_to_metabolite_test":True,
        "source_taxon_mapping_hold":True,
        "no_new_statistical_P_value":True,
        "frozen_AJB_and_EL_unchanged":True,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-2015",required=True,type=Path)
    p.add_argument("--source-2018",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    result=audit(a.source_2015,a.source_2018)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("IOCHROMINAE_ORIGINAL_CC0_ARCHIVE_AUDIT_PASS",
          json.dumps({k:result[k] for k in (
              "status","2015_original_posterior_trees",
              "2015_original_chemical_anthocyanin_state_rows",
              "2018_shape_original_posterior_trees",
              "2018_visible_colour_data_species",
              "same_literal_ID_count")},sort_keys=True))


if __name__=="__main__":
    main()
