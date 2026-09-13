#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import urllib.parse
import urllib.request
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

from Bio import Phylo

DOI = "10.5061/dryad.r4xgxd2sc"
API = "https://datadryad.org/api/v2"
DATASET_PATH = "/datasets/" + urllib.parse.quote("doi:" + DOI, safe="")
EXPECTED_FILES = {"final_dataset.csv", "trees.zip"}
REQUIRED_HEADER = {"clade", "species", "flower_color", "fruit_color"}
OUTCOME_COLUMNS = {"flower_color", "fruit_color"}


def get_bytes(url: str, timeout: int = 90) -> bytes:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "CHUN-flowerclades51-preflight/0.1 (+https://github.com/zuizui0223/chun)",
            "Accept": "*/*",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def get_json(url: str) -> dict:
    return json.loads(get_bytes(url).decode("utf-8"))


def sha256_bytes(x: bytes) -> str:
    return hashlib.sha256(x).hexdigest()


def norm_label(x: str) -> str:
    x = x.strip().replace("_", " ")
    x = re.sub(r"\s+", " ", x)
    return x.lower()


def compact(x: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", norm_label(x))


def version_href(dataset: dict) -> str:
    try:
        return dataset["_links"]["stash:version"]["href"]
    except Exception as e:
        raise SystemExit(f"Dryad dataset metadata lacks stash:version href: {e}")


def list_files(vhref: str) -> list[dict]:
    base = vhref if vhref.startswith("http") else API + vhref.removeprefix("/api/v2")
    url = base.rstrip("/") + "/files?per_page=100"
    data = get_json(url)
    rows = data.get("_embedded", {}).get("stash:files", [])
    total = int(data.get("total", len(rows)))
    if len(rows) != total:
        raise SystemExit(f"Dryad file list pagination incomplete: {len(rows)} of {total}")
    return rows


def file_id(meta: dict) -> str:
    href = meta.get("_links", {}).get("self", {}).get("href", "")
    m = re.search(r"/files/(\d+)$", href)
    if not m:
        raise SystemExit(f"could not parse Dryad file id from {href!r}")
    return m.group(1)


def download_public_file(meta: dict) -> bytes:
    fid = file_id(meta)
    # Browser/public-file route. The REST file-download endpoint requires an API account
    # even for published content, so it is intentionally not used here.
    url = f"https://datadryad.org/stash/downloads/file_stream/{fid}"
    return get_bytes(url, timeout=180)


def verify_digest(meta: dict, payload: bytes) -> dict:
    observed = sha256_bytes(payload)
    dtype = (meta.get("digestType") or "").lower().replace("_", "-")
    expected = meta.get("digest")
    if dtype in {"sha-256", "sha256"} and expected:
        if observed.lower() != str(expected).lower():
            raise SystemExit(
                f"Dryad digest mismatch for {meta.get('path')}: expected {expected}, observed {observed}"
            )
        status = "PASS_MATCH_DRYAD_SHA256"
    else:
        status = "NO_DRYAD_SHA256_AVAILABLE_LOCAL_SHA256_FROZEN"
    return {
        "path": meta.get("path"),
        "file_id": file_id(meta),
        "size_api": meta.get("size"),
        "size_downloaded": len(payload),
        "digest_type_api": meta.get("digestType"),
        "digest_api": expected,
        "sha256_downloaded": observed,
        "digest_status": status,
    }


def identifier_projection(csv_bytes: bytes) -> tuple[dict, dict[str, list[str]]]:
    # The source bytes necessarily contain all columns, but this preflight's parser stores,
    # groups, emits, and makes decisions from CLade/species identifiers only. Outcome columns
    # are checked for header presence and never accessed by name or retained in output objects.
    text = io.TextIOWrapper(io.BytesIO(csv_bytes), encoding="utf-8-sig", newline="")
    reader = csv.reader(text)
    try:
        header = next(reader)
    except StopIteration:
        raise SystemExit("final_dataset.csv is empty")
    h = [x.strip() for x in header]
    missing = sorted(REQUIRED_HEADER - set(h))
    if missing:
        raise SystemExit(f"final_dataset.csv missing required columns: {missing}; header={h}")
    ci = h.index("clade")
    si = h.index("species")
    if ci == si:
        raise SystemExit("clade/species column indices collide")

    by_clade: dict[str, list[str]] = defaultdict(list)
    rows = 0
    malformed = 0
    for raw in reader:
        rows += 1
        if len(raw) < len(h):
            malformed += 1
            continue
        clade = raw[ci].strip()
        species = raw[si].strip()
        if not clade or not species:
            malformed += 1
            continue
        by_clade[clade].append(species)

    clade_summary = {}
    for clade in sorted(by_clade):
        vals = by_clade[clade]
        normed = [norm_label(x) for x in vals]
        counts = Counter(normed)
        clade_summary[clade] = {
            "rows": len(vals),
            "unique_species_normalized": len(counts),
            "duplicate_rows_after_normalization": sum(n - 1 for n in counts.values() if n > 1),
        }

    summary = {
        "header": h,
        "row_count": rows,
        "malformed_identifier_rows": malformed,
        "clade_count": len(by_clade),
        "unique_species_labels_global_normalized": len({norm_label(s) for xs in by_clade.values() for s in xs}),
        "clades": clade_summary,
        "outcome_columns_present_in_header": sorted(OUTCOME_COLUMNS & set(h)),
        "outcome_columns_accessed_by_preflight": False,
    }
    return summary, by_clade


def parse_tree_members(zip_bytes: bytes) -> tuple[list[dict], dict[str, set[str]]]:
    tree_records: list[dict] = []
    tips_by_member: dict[str, set[str]] = {}
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        members = [m for m in zf.namelist() if not m.endswith("/")]
        if not members:
            raise SystemExit("trees.zip contains no files")
        for member in sorted(members):
            raw = zf.read(member)
            try:
                txt = raw.decode("utf-8-sig")
            except UnicodeDecodeError:
                tree_records.append({
                    "member": member,
                    "parse_status": "NON_UTF8_NOT_PARSED",
                    "bytes": len(raw),
                })
                continue
            parsed = None
            fmt = None
            last_error = None
            for trial in ("newick", "nexus"):
                try:
                    parsed = Phylo.read(io.StringIO(txt), trial)
                    fmt = trial
                    break
                except Exception as e:
                    last_error = str(e)
            if parsed is None:
                tree_records.append({
                    "member": member,
                    "parse_status": "PARSE_FAIL",
                    "bytes": len(raw),
                    "error": last_error,
                })
                continue
            tips = [t.name for t in parsed.get_terminals()]
            if any(t is None for t in tips):
                raise SystemExit(f"tree {member} contains unnamed terminal")
            normtips = {norm_label(str(t)) for t in tips}
            branches = [c.branch_length for c in parsed.find_clades() if c is not parsed.root]
            tips_by_member[member] = normtips
            tree_records.append({
                "member": member,
                "parse_status": "PASS",
                "format": fmt,
                "bytes": len(raw),
                "tip_count": len(tips),
                "unique_tip_count_normalized": len(normtips),
                "duplicate_tip_labels_after_normalization": len(tips) - len(normtips),
                "nonroot_branch_count": len(branches),
                "nonroot_branch_lengths_present": sum(x is not None for x in branches),
                "all_nonroot_branch_lengths_present": bool(branches) and all(x is not None for x in branches),
            })
    return tree_records, tips_by_member


def preliminary_mapping(by_clade: dict[str, list[str]], tips_by_member: dict[str, set[str]]) -> tuple[dict, dict]:
    # Names-only candidate mapping. This is NOT the frozen crosswalk; it only identifies
    # unambiguous candidates for the next branch.
    member_keys = {m: compact(Path(m).stem) for m in tips_by_member}
    mapping = {}
    join = {}
    for clade in sorted(by_clade):
        ck = compact(clade)
        candidates = [m for m, mk in member_keys.items() if ck and (ck in mk or mk in ck)]
        status = "UNMAPPED"
        chosen = None
        if len(candidates) == 1:
            chosen = candidates[0]
            status = "UNIQUE_FILENAME_CANDIDATE"
        elif len(candidates) > 1:
            status = "AMBIGUOUS_FILENAME_CANDIDATES"
        mapping[clade] = {"status": status, "candidates": candidates}
        if chosen:
            data_species = {norm_label(x) for x in by_clade[clade]}
            tree_species = tips_by_member[chosen]
            join[clade] = {
                "candidate_tree_member": chosen,
                "data_unique_species_normalized": len(data_species),
                "tree_unique_tips_normalized": len(tree_species),
                "exact_normalized_intersection": len(data_species & tree_species),
                "data_only": len(data_species - tree_species),
                "tree_only": len(tree_species - data_species),
                "crosswalk_frozen": False,
            }
    return mapping, join


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    dataset_url = API + DATASET_PATH
    dataset = get_json(dataset_url)
    vhref = version_href(dataset)
    files = list_files(vhref)
    by_name = {f.get("path"): f for f in files}
    missing = sorted(EXPECTED_FILES - set(by_name))
    if missing:
        raise SystemExit(f"Dryad version missing expected files {missing}; found {sorted(by_name)}")

    csv_payload = download_public_file(by_name["final_dataset.csv"])
    trees_payload = download_public_file(by_name["trees.zip"])
    csv_receipt = verify_digest(by_name["final_dataset.csv"], csv_payload)
    trees_receipt = verify_digest(by_name["trees.zip"], trees_payload)

    identifiers, by_clade = identifier_projection(csv_payload)
    tree_records, tips_by_member = parse_tree_members(trees_payload)
    prelim, join = preliminary_mapping(by_clade, tips_by_member)

    result = {
        "version": "v0.1",
        "status": "PREFLIGHT_COMPLETE_OUTCOMES_UNOPENED",
        "source_doi": DOI,
        "dataset_identifier_api": dataset.get("identifier"),
        "dataset_version_number": dataset.get("versionNumber"),
        "dataset_publication_date": dataset.get("publicationDate"),
        "dataset_last_modification_date": dataset.get("lastModificationDate"),
        "dataset_storage_size_api": dataset.get("storageSize"),
        "version_href": vhref,
        "api_file_count": len(files),
        "api_files": [
            {
                "path": f.get("path"),
                "size": f.get("size"),
                "file_id": file_id(f),
                "digest_type": f.get("digestType"),
                "digest": f.get("digest"),
            }
            for f in sorted(files, key=lambda x: str(x.get("path")))
        ],
        "download_receipts": [csv_receipt, trees_receipt],
        "identifier_projection": identifiers,
        "tree_members": tree_records,
        "tree_archive_members_total": len(tree_records),
        "tree_members_parsed": sum(r.get("parse_status") == "PASS" for r in tree_records),
        "preliminary_clade_tree_filename_mapping": prelim,
        "preliminary_identifier_join": join,
        "outcome_firewall": {
            "flower_color_values_accessed_or_emitted": False,
            "fruit_color_values_accessed_or_emitted": False,
            "clade_color_frequencies_computed": False,
            "coarse_intermediate_fine_states_materialized": False,
            "AUC_computed": False,
            "profile_winner_computed": False,
            "result_directory_created": False,
        },
        "next_gate": "FREEZE_CLade_TREE_CROSSWALK_AND_DUPLICATE_RULE_FROM_IDENTIFIERS_ONLY_BEFORE_OPENING_FLOWER_COLOR",
        "paper1_science_changed": False,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "dataset_version_number": result["dataset_version_number"],
        "api_file_count": result["api_file_count"],
        "rows": identifiers["row_count"],
        "clades": identifiers["clade_count"],
        "trees_total": result["tree_archive_members_total"],
        "trees_parsed": result["tree_members_parsed"],
        "unique_filename_mappings": sum(v["status"] == "UNIQUE_FILENAME_CANDIDATE" for v in prelim.values()),
        "outcomes_opened": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
