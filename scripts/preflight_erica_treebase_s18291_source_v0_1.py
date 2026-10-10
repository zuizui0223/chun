#!/usr/bin/env python3
"""Source-only preflight for Pirie 2016 Erica TreeBASE S18291 phylogeny.

Does not choose a tree, reroot, prune, match taxa, compute distances or outcomes.
Only downloads a published TreeBASE study export and records its raw identity.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request

STUDY_DOI = "10.1186/s12862-016-0764-3"
STUDY_ID = "S18291"
URLS = [
    "https://treebase.org/treebase-web/phylows/study/TB2:S18291?format=nexus",
    "https://treebase.org/treebase-web/phylows/study/TB2:S18291?format=nexml",
    "https://purl.org/phylo/treebase/phylows/study/TB2:S18291?format=nexus",
]
MAX_BYTES = 12_000_000


def classify(content: bytes) -> str:
    head = content[:4096].lstrip().lower()
    if head.startswith(b"#nexus") and b"begin trees" in content.lower():
        return "SOURCE_STUDY_NEXUS_TREE_EXPORT"
    if b"<nex:nexml" in head or b"<nexml" in head:
        return "SOURCE_STUDY_NEXML_EXPORT"
    if b"<html" in head or b"<!doctype html" in head:
        return "HTML_NOT_MACHINE_TREE"
    if head.startswith(b"<?xml") or b"<rdf" in head:
        return "METADATA_XML_NOT_CONFIRMED_TREE"
    return "UNCLASSIFIED_DOCUMENT_NOT_ADMITTED"


def audit(fetcher=None, timeout=18) -> tuple[dict, bytes | None]:
    if fetcher is None:
        fetcher = urllib.request.urlopen
    receipt = {
        "version": "v0.1",
        "study_tree_doi": STUDY_DOI,
        "treebase_study_id": STUDY_ID,
        "status": "HOLD_TREEBASE_SOURCE_TREE_UNRECOVERED",
        "routes": [],
        "selected_evolutionary_tree": False,
        "patristic_distance_matrix_computed": False,
        "taxon_crosswalk_verified": False,
        "pigment_gene_memory_test_performed": False,
        "independent_replication_admitted": False,
        "original_ajb_el_submission_unchanged": True,
    }
    for url in URLS:
        row = {"url": url, "result": "HOLD_TRANSPORT"}
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "CHUN-Erica-TreeBASE-source-only/0.1",
                "Accept": "application/nexus,text/plain,application/xml,*/*",
            })
            with fetcher(req, timeout=timeout) as resp:
                row["http_status"] = getattr(resp, "status", 200)
                if row["http_status"] != 200:
                    raise ValueError("HTTP " + str(row["http_status"]))
                payload = resp.read(MAX_BYTES + 1)
            if len(payload) > MAX_BYTES:
                raise ValueError("source exceeds 12 MB budget")
            row["bytes"] = len(payload)
            row["sha256"] = hashlib.sha256(payload).hexdigest()
            row["source_type"] = classify(payload)
            row["result"] = "SOURCE_RECEIVED"
            receipt["routes"].append(row)
            if row["source_type"] in ("SOURCE_STUDY_NEXUS_TREE_EXPORT", "SOURCE_STUDY_NEXML_EXPORT"):
                receipt["status"] = "SOURCE_TREE_EXPORT_RECOVERED_TAXON_AND_TREE_SELECTION_NOT_YET_ADMITTED"
                receipt["selected_route"] = url
                receipt["raw_tree_export_sha256"] = row["sha256"]
                return receipt, payload
        except (OSError, ValueError) as exc:
            row["error"] = type(exc).__name__ + ": " + str(exc)[:250]
            receipt["routes"].append(row)
    return receipt, None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--save-export", type=Path)
    p.add_argument("--timeout", type=int, default=18)
    args = p.parse_args()
    if not 1 <= args.timeout <= 45:
        raise ValueError("bad timeout")
    result, content = audit(timeout=args.timeout)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if content and args.save_export:
        args.save_export.parent.mkdir(parents=True, exist_ok=True)
        args.save_export.write_bytes(content)
    print("ERICA_TREEBASE_SOURCE_STATUS", result["status"])
    for row in result["routes"]:
        print("ERICA_TREEBASE_ROUTE", row)
    print("NO_SOURCE_CROSSWALK_OR_PHYLOGENETIC_MEMORY_ESTIMATE")


if __name__ == "__main__":
    main()
