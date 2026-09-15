#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import ssl
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "data/solanaceae_red_biochemical_resolution_profile_prereg_v0_1.json"

UA = "Mozilla/5.0 CHUN-source-preflight/0.1"


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def fetch(url: str, *, timeout: int = 60) -> tuple[bytes, str, str]:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
        data = r.read()
        return data, r.geturl(), r.headers.get("Content-Type", "")


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def text_content(el: ET.Element) -> str:
    return " ".join("".join(el.itertext()).split())


def norm_species(x: str) -> str | None:
    x = x.strip().replace("×", "x")
    x = re.sub(r"\s+", " ", x)
    # Preserve only a conservative genus + specific epithet projection.
    m = re.match(r"^([A-Z][A-Za-z-]+)\s+([a-z][A-Za-z-]+)\b", x)
    if not m:
        return None
    return f"{m.group(1).lower()}_{m.group(2).lower()}"


def inspect_docx_identifiers(docx_bytes: bytes, expected_name: str) -> dict:
    if not docx_bytes.startswith(b"PK"):
        raise RuntimeError("supplement download is not a DOCX/ZIP payload")
    with zipfile.ZipFile(Path("/dev/null"), "r") if False else zipfile.ZipFile(__import__('io').BytesIO(docx_bytes)) as z:
        names = z.namelist()
        if "word/document.xml" not in names:
            raise RuntimeError("DOCX lacks word/document.xml")
        xml = z.read("word/document.xml")
    root = ET.fromstring(xml)
    tables = [el for el in root.iter() if local_name(el.tag) == "tbl"]
    table_summaries = []
    candidate_species: list[str] = []
    chosen_table = None
    chosen_species_col = None
    chosen_header: list[str] = []
    for ti, tbl in enumerate(tables):
        trs = [el for el in list(tbl) if local_name(el.tag) == "tr"]
        if not trs:
            continue
        rows = []
        for tr in trs:
            cells = [text_content(tc) for tc in list(tr) if local_name(tc.tag) == "tc"]
            rows.append(cells)
        max_cols = max((len(r) for r in rows), default=0)
        header_scan = rows[:5]
        table_summaries.append({"table_index": ti, "rows": len(rows), "max_columns": max_cols,
                                "header_scan": header_scan})
        # Locate a species/taxon header using only the first five rows.
        for hi, header in enumerate(header_scan):
            for ci, cell in enumerate(header):
                c = cell.strip().lower()
                if c in {"species", "taxon", "study species", "species name"} or "species" == c.replace("study ", ""):
                    vals = []
                    for r in rows[hi + 1:]:
                        if ci < len(r):
                            n = norm_species(r[ci])
                            if n:
                                vals.append(n)
                    if len(set(vals)) >= 20:
                        if chosen_table is not None:
                            raise RuntimeError("multiple DOCX tables contain >=20 parsable species identifiers")
                        chosen_table = ti
                        chosen_species_col = ci
                        chosen_header = header
                        candidate_species = vals
    if chosen_table is None:
        raise RuntimeError("no DOCX table yielded a >=20-species identifier column")
    uniq = sorted(set(candidate_species))
    return {
        "expected_filename": expected_name,
        "docx_bytes": len(docx_bytes),
        "docx_sha256": sha256_bytes(docx_bytes),
        "table_count": len(tables),
        "table_summaries": table_summaries,
        "selected_table_index": chosen_table,
        "selected_species_column_index": chosen_species_col,
        "selected_header": chosen_header,
        "species_rows_parsed": len(candidate_species),
        "unique_normalized_species": len(uniq),
        "normalized_species": uniq,
        "outcome_columns_emitted": False,
    }


def acquire_pmc_supplement(pmcid: str, filename: str, out_dir: Path) -> tuple[bytes, dict]:
    article_url = f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/"
    html, final_url, ctype = fetch(article_url)
    text = html.decode("utf-8", errors="replace")
    hrefs = re.findall(r'href=["\']([^"\']+)["\']', text, flags=re.I)
    hits = [h for h in hrefs if filename in h]
    attempts = []
    candidates = []
    for h in hits:
        candidates.append(urljoin(final_url, h))
    # Stable PMC supplementary route seen in article markup/search surfaces.
    candidates.extend([
        f"https://pmc.ncbi.nlm.nih.gov/articles/instance/4804202/bin/{filename}",
        f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/bin/{filename}",
    ])
    seen = set()
    for u in candidates:
        if u in seen:
            continue
        seen.add(u)
        try:
            b, fu, ct = fetch(u)
            attempts.append({"url": u, "final_url": fu, "content_type": ct, "bytes": len(b),
                             "sha256": sha256_bytes(b), "ok_zip": b.startswith(b"PK")})
            if b.startswith(b"PK") and len(b) > 10000:
                (out_dir / filename).write_bytes(b)
                return b, {"article_url": article_url, "article_final_url": final_url,
                           "article_content_type": ctype, "href_hits": hits, "attempts": attempts}
        except Exception as e:
            attempts.append({"url": u, "error": f"{type(e).__name__}: {e}"})
    raise RuntimeError("could not recover exact PMC supplementary DOCX: " + json.dumps(attempts))


def parse_nexml(payload: bytes) -> dict:
    root = ET.fromstring(payload)
    otus = {}
    for el in root.iter():
        if local_name(el.tag) == "otu":
            oid = el.attrib.get("id")
            lab = el.attrib.get("label", "")
            if oid:
                otus[oid] = lab
    tree_records = []
    for tr in [el for el in root.iter() if local_name(el.tag) == "tree"]:
        nodes = {n.attrib.get("id"): n for n in tr if local_name(n.tag) == "node" and n.attrib.get("id")}
        edges = [e for e in tr if local_name(e.tag) == "edge"]
        source_ids = {e.attrib.get("source") for e in edges}
        tip_nodes = [n for nid, n in nodes.items() if nid not in source_ids]
        labels = []
        for n in tip_nodes:
            otu = n.attrib.get("otu")
            lab = otus.get(otu, n.attrib.get("label", ""))
            if lab:
                labels.append(lab)
        nonempty_lengths = sum(bool(e.attrib.get("length")) for e in edges)
        tree_records.append({
            "tree_id": tr.attrib.get("id"),
            "tree_label": tr.attrib.get("label"),
            "nodes": len(nodes),
            "edges": len(edges),
            "tip_labels": labels,
            "tip_count": len(labels),
            "edges_with_length": nonempty_lengths,
            "all_edges_have_length": bool(edges) and nonempty_lengths == len(edges),
        })
    return {"otu_count": len(otus), "tree_count": len(tree_records), "trees": tree_records}


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
            b, fu, ct = fetch(u, timeout=90)
            rec = {"url": u, "final_url": fu, "content_type": ct, "bytes": len(b),
                   "sha256": sha256_bytes(b)}
            try:
                info = parse_nexml(b)
                rec["parsed_nexml"] = True
                rec["tree_count"] = info["tree_count"]
                attempts.append(rec)
                if info["tree_count"] >= 1:
                    (out_dir / f"treebase_{study_id}.xml").write_bytes(b)
                    return b, {"attempts": attempts, "selected_url": u, "selected_final_url": fu,
                               "selected_content_type": ct, "nexml": info}
            except Exception as pe:
                rec["parsed_nexml"] = False
                rec["parse_error"] = f"{type(pe).__name__}: {pe}"
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
            tree_norm = {x for x in (norm_species(l) for l in t["tip_labels"]) if x}
            exact = sorted(trait_species & tree_norm)
            tree_candidates.append({
                "tree_id": t["tree_id"],
                "tree_label": t["tree_label"],
                "tip_count": t["tip_count"],
                "all_edges_have_length": t["all_edges_have_length"],
                "normalized_tip_count": len(tree_norm),
                "trait_species_exact_matches": len(exact),
                "trait_species_unmatched": sorted(trait_species - tree_norm),
                "exact_matches": exact,
            })

    eligible = [t for t in tree_candidates if t["all_edges_have_length"] and t["trait_species_exact_matches"] >= 20]
    if tree_bytes is None:
        status = "HOLD_TREE_OBJECT_AMBIGUOUS_OR_UNAVAILABLE"
    elif len(eligible) == 1:
        status = "PASS_SOURCE_SCHEMA_TREE_CROSSWALK_SINGLE_ELIGIBLE_TREE"
    elif len(eligible) == 0:
        status = "HOLD_NO_TREE_OBJECT_MEETS_FROZEN_CROSSWALK_AND_BRANCH_LENGTH_GATE"
    else:
        status = "HOLD_TREE_OBJECT_AMBIGUOUS_OR_UNAVAILABLE"

    receipt = {
        "version": "v0.1",
        "system": "SOLANACEAE_RED_27",
        "status": status,
        "prereg_status_verified": prereg["status"],
        "outcome_firewall": {
            "pigment_values_emitted": False,
            "pigment_states_computed": False,
            "state_frequencies_computed": False,
            "patristic_distances_computed": False,
            "profile_auc_computed": False,
            "permutations_computed": False,
            "winner_class_computed": False,
        },
        "supplement": {**pmc, **doc},
        "treebase": {
            "study_id": prereg["source"]["treebase_study_id"],
            "payload_available": tree_bytes is not None,
            "payload_sha256": sha256_bytes(tree_bytes) if tree_bytes is not None else None,
            "retrieval": tree,
            "tree_candidates": tree_candidates,
            "eligible_tree_count": len(eligible),
            "eligible_tree_ids": [t["tree_id"] for t in eligible],
        },
        "reported_taxa_contract": prereg["source"]["reported_taxa"],
        "parsed_unique_species": doc["unique_normalized_species"],
        "source_gate_pass": status.startswith("PASS_"),
        "paper1_science_changed": False,
    }
    a.receipt.parent.mkdir(parents=True, exist_ok=True)
    a.receipt.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": status,
        "supplement_sha256": doc["docx_sha256"],
        "unique_species": doc["unique_normalized_species"],
        "treebase_payload_available": tree_bytes is not None,
        "tree_count": tree["nexml"]["tree_count"] if tree.get("nexml") else 0,
        "eligible_tree_count": len(eligible),
        "eligible_tree_ids": [t["tree_id"] for t in eligible],
        "outcome_firewall": receipt["outcome_firewall"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
