#!/usr/bin/env python3
"""Normalize frozen rooted94 tips against WFO Plant List 2026-06 DwC.

The nuclear tree is read only. Taxonomy comes from the immutable June 2026 WFO
Plant List Darwin Core snapshot on Zenodo (DOI 10.5281/zenodo.20782718).

For every legacy binomial we find exact genus+specific-epithet name records,
follow acceptedNameUsageID, and then climb parentNameUsageID until species rank.
If exact records resolve to zero or multiple accepted species groups, the gate
fails rather than guessing.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import xml.etree.ElementTree as ET
import zipfile
from collections import defaultdict
from pathlib import Path, PurePosixPath

from Bio import Phylo

RELEASE = "2026-06"
RELEASE_DOI = "10.5281/zenodo.20782718"
EXPECTED_MD5 = "0e4486945cd9f7af548ca87eb9a870ed"


def norm_space(x: str | None) -> str:
    return re.sub(r"\s+", " ", (x or "").strip())


def tip_to_name(x: str) -> str:
    return norm_space(x.replace("_", " "))


def term_local(term: str) -> str:
    return term.rsplit("/", 1)[-1].rsplit("#", 1)[-1]


def decode_sep(x: str | None, default: str) -> str:
    if x is None or x == "":
        return default
    return bytes(x, "utf-8").decode("unicode_escape")


def parse_meta(zf: zipfile.ZipFile):
    metas = [n for n in zf.namelist() if PurePosixPath(n).name == "meta.xml"]
    if len(metas) != 1:
        raise SystemExit(f"expected one meta.xml, got {metas}")
    meta_name = metas[0]
    root = ET.fromstring(zf.read(meta_name))
    core = next((x for x in root.iter() if x.tag.endswith("core")), None)
    if core is None:
        raise SystemExit("DwC meta.xml has no core")
    location = next((x.text for x in core.iter() if x.tag.endswith("location") and x.text), None)
    if not location:
        raise SystemExit("DwC core has no file location")
    base = PurePosixPath(meta_name).parent
    core_name = str(base / location) if str(base) != "." else location
    fields = {}
    id_index = None
    for x in core:
        if x.tag.endswith("id"):
            id_index = int(x.attrib["index"])
        elif x.tag.endswith("field"):
            fields[term_local(x.attrib.get("term", ""))] = int(x.attrib["index"])
    attrs = {
        "delimiter": decode_sep(core.attrib.get("fieldsTerminatedBy"), "\t"),
        "quotechar": decode_sep(core.attrib.get("fieldsEnclosedBy"), '"') or '"',
        "ignore_header": int(core.attrib.get("ignoreHeaderLines", "0") or 0),
        "encoding": core.attrib.get("encoding", "UTF-8"),
    }
    if id_index is not None and "taxonID" not in fields:
        fields["taxonID"] = id_index
    need = {"taxonID", "scientificName", "taxonRank", "taxonomicStatus"}
    missing = sorted(need - set(fields))
    if missing:
        raise SystemExit(f"DwC core lacks required fields: {missing}; available={sorted(fields)}")
    return core_name, fields, attrs


def get(row, fields, key):
    i = fields.get(key)
    return row[i].strip() if i is not None and i < len(row) else ""


def binomial_from_record(rec: dict[str, str]) -> str:
    genus = norm_space(rec.get("genus"))
    epithet = norm_space(rec.get("specificEpithet"))
    if genus and epithet:
        return f"{genus} {epithet}"
    toks = norm_space(rec.get("scientificName")).replace("× ", "").split()
    return " ".join(toks[:2]) if len(toks) >= 2 else ""


def load_dwc(path: Path):
    md5 = hashlib.md5(path.read_bytes()).hexdigest()
    if md5 != EXPECTED_MD5:
        raise SystemExit(f"WFO DwC MD5 mismatch: {md5} != {EXPECTED_MD5}")
    zf = zipfile.ZipFile(path)
    core_name, fields, attrs = parse_meta(zf)
    records = {}
    binomial_index = defaultdict(list)
    with zf.open(core_name) as raw:
        text = io.TextIOWrapper(raw, encoding=attrs["encoding"], errors="replace", newline="")
        reader = csv.reader(text, delimiter=attrs["delimiter"], quotechar=attrs["quotechar"])
        for _ in range(attrs["ignore_header"]):
            next(reader, None)
        for row in reader:
            taxon_id = get(row, fields, "taxonID")
            if not taxon_id:
                continue
            rec = {
                "taxonID": taxon_id,
                "acceptedNameUsageID": get(row, fields, "acceptedNameUsageID"),
                "parentNameUsageID": get(row, fields, "parentNameUsageID"),
                "scientificName": get(row, fields, "scientificName"),
                "taxonRank": get(row, fields, "taxonRank"),
                "taxonomicStatus": get(row, fields, "taxonomicStatus"),
                "genus": get(row, fields, "genus") or get(row, fields, "genericName"),
                "specificEpithet": get(row, fields, "specificEpithet"),
            }
            records[taxon_id] = rec
            b = binomial_from_record(rec)
            if b.startswith("Camellia ") or b == "Polyspora speciosa":
                binomial_index[b].append(taxon_id)
    return records, binomial_index, md5, core_name


def accepted_record(rec, records):
    aid = rec.get("acceptedNameUsageID") or ""
    status = (rec.get("taxonomicStatus") or "").casefold()
    if aid:
        return records.get(aid)
    if "accepted" in status:
        return rec
    return None


def species_ancestor(rec, records):
    seen = set()
    cur = rec
    while cur:
        tid = cur.get("taxonID", "")
        if not tid or tid in seen:
            return None
        seen.add(tid)
        if (cur.get("taxonRank") or "").casefold() == "species":
            return cur
        pid = cur.get("parentNameUsageID") or ""
        cur = records.get(pid) if pid else None
    return None


def resolve_legacy(legacy, records, index):
    ids = index.get(legacy, [])
    resolved = []
    for tid in ids:
        source = records[tid]
        accepted = accepted_record(source, records)
        if not accepted:
            continue
        species = species_ancestor(accepted, records)
        if not species:
            continue
        species_name = binomial_from_record(species)
        if species_name:
            resolved.append((species_name, source, accepted, species))
    groups = sorted({x[0] for x in resolved})
    status = "resolved" if len(groups) == 1 else ("unresolved" if not groups else "ambiguous")
    chosen = None
    if status == "resolved":
        same = [x for x in resolved if x[0] == groups[0]]
        same.sort(key=lambda x: (
            0 if x[1]["taxonID"] == x[2]["taxonID"] else 1,
            x[1]["taxonID"],
        ))
        chosen = same[0]
    return {
        "legacy_name": legacy,
        "match_status": status,
        "n_exact_binomial_records": len(ids),
        "n_resolved_exact_records": len(resolved),
        "accepted_species_candidates": ";".join(groups),
        "matched_taxon_id": chosen[1]["taxonID"] if chosen else "",
        "matched_scientific_name": chosen[1]["scientificName"] if chosen else "",
        "matched_taxonomic_status": chosen[1]["taxonomicStatus"] if chosen else "",
        "accepted_taxon_id": chosen[2]["taxonID"] if chosen else "",
        "accepted_name_full": chosen[2]["scientificName"] if chosen else "",
        "accepted_rank": chosen[2]["taxonRank"] if chosen else "",
        "accepted_species_taxon_id": chosen[3]["taxonID"] if chosen else "",
        "accepted_species": chosen[0] if chosen else "",
        "input_record_is_accepted_usage": bool(chosen and chosen[1]["taxonID"] == chosen[2]["taxonID"]),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", type=Path, required=True)
    ap.add_argument("--dwca", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    tree = Phylo.read(str(args.tree), "newick")
    tips = sorted(t.name for t in tree.get_terminals() if t.name)
    if len(tips) != 94:
        raise SystemExit(f"expected 94 rooted tips, got {len(tips)}")
    legacy = [tip_to_name(x) for x in tips]
    if len(set(legacy)) != 94:
        raise SystemExit("duplicate normalized rooted tips")

    records, index, md5, core_name = load_dwc(args.dwca)
    rows = []
    for tip, name in zip(tips, legacy):
        r = resolve_legacy(name, records, index)
        r.update({
            "tree_tip": tip,
            "backbone": f"WFO Plant List {RELEASE}",
            "release_doi": RELEASE_DOI,
        })
        rows.append(r)
        print(name, r["match_status"], "=>", r["accepted_species"])

    unresolved = [r for r in rows if r["match_status"] != "resolved"]
    cam = [r for r in rows if r["legacy_name"].startswith("Camellia ")]
    poly = [r for r in rows if r["legacy_name"] == "Polyspora speciosa"]
    groups = defaultdict(list)
    for r in rows:
        if r["accepted_species"]:
            groups[r["accepted_species"]].append(r["tree_tip"])
    duplicates = {k: sorted(v) for k, v in groups.items() if len(v) > 1}

    with (args.out_dir / "wfo2026_06_taxonomy_registry.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    with (args.out_dir / "astral_species_mapping.tsv").open("w", encoding="utf-8") as f:
        for r in rows:
            if r["accepted_species"]:
                f.write(f"{r['tree_tip']} {r['accepted_species'].replace(' ', '_')}\n")
    dup_rows = [
        {"accepted_species": k, "n_legacy_tips": len(v), "legacy_tips": ";".join(v)}
        for k, v in sorted(duplicates.items())
    ]
    with (args.out_dir / "duplicate_accepted_species_groups.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["accepted_species", "n_legacy_tips", "legacy_tips"]); w.writeheader(); w.writerows(dup_rows)

    summary = {
        "backbone": f"WFO Plant List {RELEASE}",
        "release_doi": RELEASE_DOI,
        "dwca_md5": md5,
        "dwca_core_file": core_name,
        "n_dwc_records_loaded": len(records),
        "n_tree_tips": len(rows),
        "n_camellia_legacy_tips": len(cam),
        "n_polyspora_legacy_tips": len(poly),
        "n_unresolved_or_ambiguous": len(unresolved),
        "unresolved_or_ambiguous": [r["legacy_name"] for r in unresolved],
        "n_accepted_species_groups_all": len(groups),
        "n_accepted_camellia_species_groups": len({r["accepted_species"] for r in cam if r["accepted_species"]}),
        "n_duplicate_accepted_species_groups": len(duplicates),
        "duplicate_groups": duplicates,
        "claim_ceiling": "versioned taxonomic mapping gate only; no topology collapse, colour-state transfer, or evolutionary interpretation",
    }
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if len(cam) != 93 or len(poly) != 1:
        raise SystemExit("unexpected rooted genus composition")
    if unresolved:
        raise SystemExit(f"WFO normalization unresolved/ambiguous for {len(unresolved)} names")


if __name__ == "__main__":
    main()
