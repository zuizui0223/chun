#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import ssl
import sys
import tarfile
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from urllib.parse import urljoin, urlparse

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
from fetch_pmc_cloud_media_v0_1 import choose_version, fetch_metadata, list_versions, s3_to_https
PREREG = ROOT / "data/solanaceae_red_biochemical_resolution_profile_prereg_v0_1.json"
UA = "Mozilla/5.0 CHUN-source-preflight/0.2"


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def fetch(url: str, *, timeout: int = 90) -> tuple[bytes, str, str]:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout, context=ssl.create_default_context()) as r:
        return r.read(), r.geturl(), r.headers.get("Content-Type", "")


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def text_content(el: ET.Element) -> str:
    return " ".join("".join(el.itertext()).split())


def norm_species(x: str) -> str | None:
    x = re.sub(r"\s+", " ", x.strip().replace("×", "x"))
    m = re.match(r"^([A-Z][A-Za-z-]+)\s+([a-z][A-Za-z-]+)\b", x)
    return f"{m.group(1).lower()}_{m.group(2).lower()}" if m else None


def inspect_docx_identifiers(docx_bytes: bytes, expected_name: str) -> dict:
    if not docx_bytes.startswith(b"PK"):
        raise RuntimeError("supplement payload is not a DOCX/ZIP")
    with zipfile.ZipFile(io.BytesIO(docx_bytes)) as z:
        if "word/document.xml" not in z.namelist():
            raise RuntimeError("DOCX lacks word/document.xml")
        root = ET.fromstring(z.read("word/document.xml"))

    tables = [x for x in root.iter() if local_name(x.tag) == "tbl"]
    structural = []
    hits = []
    for ti, tbl in enumerate(tables):
        trs = [x for x in list(tbl) if local_name(x.tag) == "tr"]
        rows = [[text_content(tc) for tc in list(tr) if local_name(tc.tag) == "tc"] for tr in trs]
        structural.append({"table_index": ti, "rows": len(rows),
                           "max_columns": max((len(r) for r in rows), default=0)})
        # Inspect at most five initial rows to locate a header, but never emit those data rows.
        for hi, header in enumerate(rows[:5]):
            for ci, cell in enumerate(header):
                c = re.sub(r"\s+", " ", cell.strip().lower())
                if c not in {"species", "taxon", "study species", "species name"}:
                    continue
                vals = []
                for r in rows[hi + 1:]:
                    if ci < len(r):
                        n = norm_species(r[ci])
                        if n:
                            vals.append(n)
                if len(set(vals)) >= 20:
                    hits.append((ti, hi, ci, header, vals))
    if len(hits) != 1:
        raise RuntimeError(f"expected exactly one >=20-species identifier table, found {len(hits)}")
    ti, hi, ci, header, vals = hits[0]
    uniq = sorted(set(vals))
    return {
        "expected_filename": expected_name,
        "docx_bytes": len(docx_bytes),
        "docx_sha256": sha256_bytes(docx_bytes),
        "table_count": len(tables),
        "table_structure": structural,
        "selected_table_index": ti,
        "selected_header_row_index": hi,
        "selected_species_column_index": ci,
        "selected_header": header,
        "species_rows_parsed": len(vals),
        "unique_normalized_species": len(uniq),
        "normalized_species": uniq,
        "outcome_columns_emitted": False,
        "outcome_data_rows_emitted": False,
    }


def supplement_from_oa_package(pmcid: str, filename: str, out_dir: Path) -> tuple[bytes | None, dict]:
    """Recover the exact supplement from the current PMC Cloud media inventory."""
    attempts = []
    try:
        prefixes = list_versions(pmcid)
        metadata = [fetch_metadata(prefix) for prefix in prefixes]
        selected = choose_version(metadata)
        selected_prefix = f"{selected['pmcid']}.{selected['version']}"
        matches = []
        for raw in selected.get("media_urls") or []:
            https_url, expected_md5 = s3_to_https(raw)
            if Path(urlparse(https_url).path).name == filename:
                matches.append((https_url, expected_md5))
        attempts.append({
            "method": "pmc_cloud_metadata",
            "selected_prefix": selected_prefix,
            "available_prefixes": prefixes,
            "matching_media_count": len(matches),
            "matching_media_urls": [u for u, _ in matches],
        })
        if len(matches) != 1:
            return None, {
                "oa_api": None,
                "attempts": attempts,
                "selected_method": None,
            }

        url, expected_md5 = matches[0]
        payload, final_url, content_type = fetch(url, timeout=120)
        actual_md5 = hashlib.md5(payload).hexdigest()
        ok_md5 = expected_md5 is None or actual_md5.lower() == expected_md5.lower()
        rec = {
            "method": "pmc_cloud_media",
            "url": url,
            "final_url": final_url,
            "content_type": content_type,
            "bytes": len(payload),
            "sha256": sha256_bytes(payload),
            "expected_md5": expected_md5,
            "actual_md5": actual_md5,
            "md5_match": ok_md5,
            "supplement_is_zip": payload.startswith(b"PK"),
        }
        attempts.append(rec)
        if not ok_md5:
            raise RuntimeError(
                f"PMC Cloud MD5 mismatch for {filename}: {actual_md5} != {expected_md5}"
            )
        if payload.startswith(b"PK"):
            (out_dir / filename).write_bytes(payload)
            return payload, {
                "oa_api": None,
                "attempts": attempts,
                "selected_method": "pmc_cloud_media",
                "selected_package_url": None,
                "selected_member": filename,
                "selected_url": url,
                "selected_prefix": selected_prefix,
            }
    except Exception as e:
        attempts.append({
            "method": "pmc_cloud_media",
            "error": f"{type(e).__name__}: {e}",
        })
    return None, {
        "oa_api": None,
        "attempts": attempts,
        "selected_method": None,
    }


def supplement_from_article_links(pmcid: str, filename: str, out_dir: Path) -> tuple[bytes | None, dict]:
    article_url = f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/"
    attempts = []
    try:
        html, final, ctype = fetch(article_url)
        text = html.decode("utf-8", errors="replace")
        hrefs = re.findall(r'href=["\']([^"\']+)["\']', text, flags=re.I)
        hits = [urljoin(final, h) for h in hrefs if filename in h]
        attempts.append({"method": "article_html", "article_url": article_url,
                         "article_final_url": final, "content_type": ctype,
                         "matching_href_count": len(hits)})
        for u in hits:
            try:
                b, fu, ct = fetch(u)
                attempts.append({"method": "article_link", "url": u, "final_url": fu,
                                 "content_type": ct, "bytes": len(b),
                                 "sha256": sha256_bytes(b), "is_zip": b.startswith(b"PK")})
                if b.startswith(b"PK"):
                    (out_dir / filename).write_bytes(b)
                    return b, {"article_url": article_url, "attempts": attempts,
                               "selected_method": "article_link", "selected_url": u}
            except Exception as e:
                attempts.append({"method": "article_link", "url": u,
                                 "error": f"{type(e).__name__}: {e}"})
    except Exception as e:
        attempts.append({"method": "article_html", "url": article_url,
                         "error": f"{type(e).__name__}: {e}"})
    return None, {"article_url": article_url, "attempts": attempts, "selected_method": None}


def acquire_pmc_supplement(pmcid: str, filename: str, out_dir: Path) -> tuple[bytes, dict]:
    b, oa = supplement_from_oa_package(pmcid, filename, out_dir)
    if b is not None:
        return b, {"oa_package": oa, "article_fallback": None}
    b, article = supplement_from_article_links(pmcid, filename, out_dir)
    if b is not None:
        return b, {"oa_package": oa, "article_fallback": article}
    raise RuntimeError("could not recover exact PMC supplement; OA + article attempts=" +
                       json.dumps({"oa": oa, "article": article}))


def parse_nexml(payload: bytes) -> dict:
    root = ET.fromstring(payload)
    otus = {}
    for el in root.iter():
        if local_name(el.tag) == "otu" and el.attrib.get("id"):
            otus[el.attrib["id"]] = el.attrib.get("label", "")
    trees = []
    for tr in [x for x in root.iter() if local_name(x.tag) == "tree"]:
        nodes = {n.attrib["id"]: n for n in tr if local_name(n.tag) == "node" and n.attrib.get("id")}
        edges = [e for e in tr if local_name(e.tag) == "edge"]
        source_ids = {e.attrib.get("source") for e in edges}
        tips = [n for nid, n in nodes.items() if nid not in source_ids]
        labels = [otus.get(n.attrib.get("otu"), n.attrib.get("label", "")) for n in tips]
        labels = [x for x in labels if x]
        nlen = sum(e.attrib.get("length") not in (None, "") for e in edges)
        trees.append({"tree_id": tr.attrib.get("id"), "tree_label": tr.attrib.get("label"),
                      "nodes": len(nodes), "edges": len(edges), "tip_labels": labels,
                      "tip_count": len(labels), "edges_with_length": nlen,
                      "all_edges_have_length": bool(edges) and nlen == len(edges)})
    return {"otu_count": len(otus), "tree_count": len(trees), "trees": trees}


def acquire_treebase(study_id: str, out_dir: Path) -> tuple[bytes | None, dict]:
    base = f"TB2:{study_id}"
    urls = [
        f"https://purl.org/phylo/treebase/phylows/study/{base}?format=nexml",
        f"http://purl.org/phylo/treebase/phylows/study/{base}?format=nexml",
        f"https://treebase.org/treebase-web/phylows/study/{base}?format=nexml",
        f"https://treebase.org/treebase-web/phylows/study/{base}",
    ]
    attempts = []
    for u in urls:
        try:
            b, fu, ct = fetch(u)
            rec = {"url": u, "final_url": fu, "content_type": ct,
                   "bytes": len(b), "sha256": sha256_bytes(b)}
            try:
                info = parse_nexml(b)
                rec.update({"parsed_nexml": True, "tree_count": info["tree_count"]})
                attempts.append(rec)
                if info["tree_count"]:
                    (out_dir / f"treebase_{study_id}.xml").write_bytes(b)
                    return b, {"attempts": attempts, "selected_url": u,
                               "selected_final_url": fu, "selected_content_type": ct,
                               "nexml": info}
            except Exception as pe:
                rec.update({"parsed_nexml": False,
                            "parse_error": f"{type(pe).__name__}: {pe}"})
                attempts.append(rec)
        except Exception as e:
            attempts.append({"url": u, "error": f"{type(e).__name__}: {e}"})
    return None, {"attempts": attempts, "selected_url": None, "nexml": None}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--receipt", type=Path, required=True)
    a = ap.parse_args()
    a.out_dir.mkdir(parents=True, exist_ok=True)
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    assert prereg["status"] == "FROZEN_BEFORE_SOLANACEAE_RED_TABLES1_ROW_LEVEL_OUTCOME_OPENING"
    assert prereg["source"]["primary_pigment_pmcid"] == "PMC4804202"
    assert prereg["source"]["treebase_study_id"] == "S16617"
    assert prereg["source"]["row_level_trait_values_opened_for_this_profile_before_freeze"] is False

    filename = prereg["source"]["supplement_file"]
    docx, pmc = acquire_pmc_supplement(prereg["source"]["primary_pigment_pmcid"], filename, a.out_dir)
    doc = inspect_docx_identifiers(docx, filename)
    tree_bytes, tree = acquire_treebase(prereg["source"]["treebase_study_id"], a.out_dir)

    trait_species = set(doc["normalized_species"])
    tree_candidates = []
    if tree_bytes is not None:
        for t in tree["nexml"]["trees"]:
            tree_norm = {n for n in (norm_species(x) for x in t["tip_labels"]) if n}
            exact = sorted(trait_species & tree_norm)
            tree_candidates.append({"tree_id": t["tree_id"], "tree_label": t["tree_label"],
                                    "tip_count": t["tip_count"],
                                    "all_edges_have_length": t["all_edges_have_length"],
                                    "normalized_tip_count": len(tree_norm),
                                    "trait_species_exact_matches": len(exact),
                                    "trait_species_unmatched": sorted(trait_species - tree_norm),
                                    "exact_matches": exact})

    eligible = [t for t in tree_candidates
                if t["all_edges_have_length"] and t["trait_species_exact_matches"] >= 20]
    if tree_bytes is None:
        status = "HOLD_TREE_OBJECT_AMBIGUOUS_OR_UNAVAILABLE"
    elif len(eligible) == 1:
        status = "PASS_SOURCE_SCHEMA_TREE_CROSSWALK_SINGLE_ELIGIBLE_TREE"
    elif not eligible:
        status = "HOLD_NO_TREE_OBJECT_MEETS_FROZEN_CROSSWALK_AND_BRANCH_LENGTH_GATE"
    else:
        status = "HOLD_TREE_OBJECT_AMBIGUOUS_OR_UNAVAILABLE"

    firewall = {k: False for k in [
        "pigment_values_emitted", "pigment_states_computed", "state_frequencies_computed",
        "patristic_distances_computed", "profile_auc_computed", "permutations_computed",
        "winner_class_computed"]}
    receipt = {
        "version": "v0.1", "system": "SOLANACEAE_RED_27", "status": status,
        "prereg_status_verified": prereg["status"], "outcome_firewall": firewall,
        "supplement": {**pmc, **doc},
        "treebase": {"study_id": prereg["source"]["treebase_study_id"],
                     "payload_available": tree_bytes is not None,
                     "payload_sha256": sha256_bytes(tree_bytes) if tree_bytes is not None else None,
                     "retrieval": tree, "tree_candidates": tree_candidates,
                     "eligible_tree_count": len(eligible),
                     "eligible_tree_ids": [t["tree_id"] for t in eligible]},
        "reported_taxa_contract": prereg["source"]["reported_taxa"],
        "parsed_unique_species": doc["unique_normalized_species"],
        "source_gate_pass": status.startswith("PASS_"), "paper1_science_changed": False,
    }
    a.receipt.parent.mkdir(parents=True, exist_ok=True)
    a.receipt.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "supplement_sha256": doc["docx_sha256"],
                      "unique_species": doc["unique_normalized_species"],
                      "treebase_payload_available": tree_bytes is not None,
                      "tree_count": tree["nexml"]["tree_count"] if tree.get("nexml") else 0,
                      "eligible_tree_count": len(eligible),
                      "eligible_tree_ids": [t["tree_id"] for t in eligible],
                      "outcome_firewall": firewall}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
