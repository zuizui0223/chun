#!/usr/bin/env python3
"""Pirie et al. 2024 *Erica* supplemental tree ZIP: source-only audit.

A distinct, *later* tree source than Pirie 2016 TreeBASE S18291.
Receipt never licenses treating imputed taxa as observed phylogenetic tips.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path
import urllib.request
import zipfile

DOI = "10.3897/phytokeys.244.124565.suppl7"
NAME = "phytokeys-244-127_article-124565__-s007.zip"
URLS = [
  "https://pmc.ncbi.nlm.nih.gov/articles/PMC11255470/bin/" + NAME,
  "https://pmc.ncbi.nlm.nih.gov/articles/instance/11255470/bin/" + NAME,
  "https://phytokeys.pensoft.net/article/124565/download/suppl7",
]
MAX_BYTES = 10_000_000


def inspect_zip(content: bytes) -> dict:
    if not content.startswith(b"PK"):
        raise ValueError("not ZIP bytes")
    with zipfile.ZipFile(io.BytesIO(content)) as z:
        bad = z.testzip()
        if bad:
            raise ValueError("bad archive member: " + bad)
        members = []
        for info in z.infolist():
            if info.is_dir():
                continue
            if info.file_size > 30_000_000:
                raise ValueError("oversize extracted member")
            members.append({"name": info.filename,
                            "bytes": info.file_size,
                            "candidate_tree": info.filename.lower().endswith(
                                (".nex", ".nexus", ".tre", ".tree", ".nwk", ".newick"))})
        return {"members": members, "member_count": len(members),
                "tree_filename_candidates": [x["name"] for x in members if x["candidate_tree"]]}


def acquire(fetcher=None, timeout=14) -> tuple[dict, bytes | None]:
    if fetcher is None:
        fetcher = urllib.request.urlopen
    r = {
        "version": "v0.1", "source": "Pirie et al. 2024 PhytoKeys",
        "supplement_doi": DOI, "expected_filename": NAME,
        "source_role": "ALTERNATIVE_LATER_TREE_NOT_ORIGINAL_2016",
        "status": "HOLD_LATER_PHYLOGENY_SOURCE_BYTES_UNRECOVERED",
        "routes": [], "taxon_crosswalk_checked": False,
        "no_imputed_species_admitted": True,
        "selection_of_phylogenetic_tree": "NOT_PERFORMED",
        "independent_regulatory_memory_replication": False,
        "first_submission_contracts_unchanged": True
    }
    for url in URLS:
        route = {"url": url, "state": "TRANSPORT_HOLD"}
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "CHUN-Erica-2024-tree-source-preflight/0.1",
                "Accept": "application/zip,application/octet-stream,*/*"})
            with fetcher(req, timeout=timeout) as response:
                route["status_code"] = getattr(response, "status", 200)
                if route["status_code"] != 200:
                    raise ValueError("HTTP " + str(route["status_code"]))
                content = response.read(MAX_BYTES + 1)
            if len(content) > MAX_BYTES:
                raise ValueError("too large ZIP download")
            inventory = inspect_zip(content)
            route.update(inventory)
            route["bytes"] = len(content)
            route["sha256"] = hashlib.sha256(content).hexdigest()
            route["state"] = "SOURCE_ZIP_ADMITTED_INVENTORY_ONLY"
            r["routes"].append(route)
            r["status"] = "LATER_TREE_ZIP_RECOVERED_TREE_AND_TIP_CROSSWALK_UNVERIFIED"
            r["received_sha256"] = route["sha256"]
            r["received_bytes"] = len(content)
            r["source_member_inventory"] = inventory
            return r, content
        except (OSError, ValueError, zipfile.BadZipFile, EOFError) as exc:
            route["error"] = type(exc).__name__ + ": " + str(exc)[:300]
            r["routes"].append(route)
    return r, None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--save-zip", type=Path)
    parser.add_argument("--timeout", type=int, default=14)
    args = parser.parse_args()
    r, content = acquire(timeout=args.timeout)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(r, indent=2, sort_keys=True) + "\n")
    if content is not None and args.save_zip:
        args.save_zip.parent.mkdir(parents=True, exist_ok=True)
        args.save_zip.write_bytes(content)
    print("ERICA_ALTERNATIVE_TREE_STATUS", r["status"])
    for route in r["routes"]:
        print("ERICA_ALTERNATIVE_TREE_ROUTE", json.dumps(route, sort_keys=True)[:2400])
    print("NO_IMPUTED_TAXA_AS_EVIDENCE_OR_NEW_MEMORY_TEST")


if __name__ == "__main__":
    main()
