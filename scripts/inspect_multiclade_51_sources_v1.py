#!/usr/bin/env python3
"""Source/admission audit for the prospectively frozen 51-clade panel.

This script deliberately does NOT compute Sankoff scores, permutation p-values,
or any other phylogenetic-signal endpoint. It retrieves the public Dryad dataset,
audits schema, associates source clades to machine-readable trees using species-ID
overlap only, and applies the pre-frozen observation gates.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import shutil
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

import requests
from Bio import Phylo

DOI = "10.5061/dryad.r4xgxd2sc"
ENCODED = "doi%3A10.5061%2Fdryad.r4xgxd2sc"
DOWNLOAD = f"https://datadryad.org/api/v2/datasets/{ENCODED}/download"
UA = "chun-multiclade-falsification-source-audit/1.0"
OUT = Path("analysis/_generated/multiclade_51_source_v1")

FINE = {
    "black/dark": "BLACK_DARK",
    "blue/purple": "BLUE_PURPLE",
    "green": "GREEN",
    "orange": "ORANGE",
    "pink": "PINK",
    "red": "RED",
    "white": "WHITE",
    "yellow": "YELLOW",
}


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def clean(x: str) -> str:
    return re.sub(r"\s+", " ", (x or "").strip())


def norm_species(x: str) -> str:
    # Frozen syntactic/lossless comparison boundary: quotes, underscores/spaces,
    # repeated whitespace and case only. Do not drop taxonomic tokens.
    s = clean(x).strip("'\"")
    s = s.replace("_", " ")
    s = clean(s)
    return s.casefold()


def norm_color(x: str) -> str:
    s = clean(x).casefold().replace("_", " ").replace("–", "-").replace("—", "-")
    return s


def locate_unique(root: Path, name: str) -> Path:
    hits = [p for p in root.rglob("*") if p.is_file() and p.name.casefold() == name.casefold()]
    if len(hits) != 1:
        raise SystemExit(f"expected exactly one {name!r}, found {len(hits)}: {[str(x) for x in hits]}")
    return hits[0]


def download_dataset() -> tuple[Path, dict]:
    OUT.mkdir(parents=True, exist_ok=True)
    archive = OUT / "dryad_latest.zip"
    r = requests.get(DOWNLOAD, headers={"User-Agent": UA, "Accept": "application/zip,application/octet-stream,*/*"}, timeout=180, allow_redirects=True)
    r.raise_for_status()
    archive.write_bytes(r.content)
    if not zipfile.is_zipfile(archive):
        preview = r.content[:200]
        raise SystemExit(f"Dryad /download did not return a ZIP; status={r.status_code} content_type={r.headers.get('content-type')} preview={preview!r}")
    meta = {
        "requested_url": DOWNLOAD,
        "final_url": r.url,
        "status_code": r.status_code,
        "content_type": r.headers.get("content-type", ""),
        "content_length": len(r.content),
        "sha256": sha256_bytes(r.content),
    }
    return archive, meta


def parse_tree_file(path: Path):
    raw = path.read_bytes()
    if not raw:
        return None, "EMPTY"
    text = None
    for enc in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            pass
    if text is None:
        return None, "NON_TEXT"
    # Try formats without using file extension as a scientific choice.
    successes = []
    for fmt in ("newick", "nexus"):
        try:
            trees = list(Phylo.parse(io.StringIO(text), fmt))
            if len(trees) == 1 and len(trees[0].get_terminals()) >= 2:
                successes.append((fmt, trees[0]))
        except Exception:
            continue
    if not successes:
        return None, "UNPARSEABLE_OR_NOT_SINGLE_TREE"
    # If the same text parses both ways, prefer Newick deterministically. This is
    # a parser choice only; tip identity is audited below.
    successes.sort(key=lambda x: (0 if x[0] == "newick" else 1))
    fmt, tree = successes[0]
    tips = [str(t.name or "") for t in tree.get_terminals()]
    return {"format": fmt, "tree": tree, "tips_raw": tips, "tips_norm": [norm_species(x) for x in tips]}, "OK"


def main():
    if OUT.exists():
        # Generated only; clearing prevents stale files from a previous CI run.
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    archive, dlmeta = download_dataset()
    extracted = OUT / "dataset"
    extracted.mkdir()
    with zipfile.ZipFile(archive) as z:
        z.extractall(extracted)
        members = sorted(z.namelist())

    csv_path = locate_unique(extracted, "final_dataset.csv")
    trees_zip = locate_unique(extracted, "trees.zip")

    source_files = {
        "dataset_archive": dlmeta,
        "final_dataset_csv": {"path": str(csv_path.relative_to(extracted)), "bytes": csv_path.stat().st_size, "sha256": sha256_file(csv_path)},
        "trees_zip": {"path": str(trees_zip.relative_to(extracted)), "bytes": trees_zip.stat().st_size, "sha256": sha256_file(trees_zip)},
        "outer_members": members,
    }

    # Trait layer.
    with csv_path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames or []
        required = {"clade", "species", "flower_color", "fruit_color"}
        if not required.issubset(header):
            raise SystemExit(f"CSV schema drift: header={header}")
        raw_rows = [dict(r) for r in reader]
    if not raw_rows:
        raise SystemExit("final_dataset.csv is empty")

    unknown_colors = sorted({norm_color(r["flower_color"]) for r in raw_rows if clean(r["flower_color"]) and norm_color(r["flower_color"]) not in FINE})
    missing_flower = sum(not clean(r["flower_color"]) for r in raw_rows)
    if unknown_colors:
        raise SystemExit(f"HOLD_SCHEMA unknown flower colors: {unknown_colors}")
    if missing_flower:
        raise SystemExit(f"HOLD_SCHEMA missing flower colors: {missing_flower}")

    clade_rows = defaultdict(list)
    for i, r in enumerate(raw_rows, start=2):
        clade = clean(r["clade"])
        species_raw = clean(r["species"])
        if not clade or not species_raw:
            raise SystemExit(f"missing clade/species at CSV row {i}")
        clade_rows[clade].append({
            "csv_row": i,
            "species_raw": species_raw,
            "species_norm": norm_species(species_raw),
            "fine_state": FINE[norm_color(r["flower_color"])],
            "fruit_color_raw": clean(r["fruit_color"]),
        })

    # Collapse only exact duplicate normalized species with identical flower state.
    clade_traits = {}
    duplicate_report = {}
    for clade, rows in clade_rows.items():
        by_sp = defaultdict(list)
        for r in rows:
            by_sp[r["species_norm"]].append(r)
        traits = {}
        dups = []
        conflicts = []
        for sp, rs in by_sp.items():
            states = sorted({x["fine_state"] for x in rs})
            if len(states) != 1:
                conflicts.append({"species_norm": sp, "states": states, "rows": [x["csv_row"] for x in rs]})
                continue
            traits[sp] = {"state": states[0], "source_labels": [x["species_raw"] for x in rs], "rows": [x["csv_row"] for x in rs]}
            if len(rs) > 1:
                dups.append({"species_norm": sp, "state": states[0], "rows": [x["csv_row"] for x in rs]})
        clade_traits[clade] = {"traits": traits, "conflicts": conflicts, "raw_n": len(rows)}
        duplicate_report[clade] = dups

    # Tree layer.
    tree_dir = OUT / "trees"
    tree_dir.mkdir()
    with zipfile.ZipFile(trees_zip) as z:
        z.extractall(tree_dir)
        inner_members = sorted(z.namelist())

    tree_records = []
    for p in sorted(x for x in tree_dir.rglob("*") if x.is_file()):
        rec, status = parse_tree_file(p)
        record = {
            "path": str(p.relative_to(tree_dir)),
            "bytes": p.stat().st_size,
            "sha256": sha256_file(p),
            "parse_status": status,
        }
        if rec:
            norms = rec["tips_norm"]
            record.update({
                "format": rec["format"],
                "tip_count": len(norms),
                "unique_tip_count": len(set(norms)),
                "duplicate_normalized_tips": sorted([x for x, n in Counter(norms).items() if n > 1]),
                "tips_norm": norms,
            })
        tree_records.append(record)

    parsed_trees = [t for t in tree_records if t["parse_status"] == "OK" and not t.get("duplicate_normalized_tips")]
    if not parsed_trees:
        raise SystemExit("no unique-tip machine-readable tree files parsed")

    # Build overlap matrix; signal-free species identities only.
    pair = {}
    for clade, cdat in clade_traits.items():
        trait_set = set(cdat["traits"])
        for tr in parsed_trees:
            tree_set = set(tr["tips_norm"])
            inter = trait_set & tree_set
            pair[(clade, tr["path"])] = {
                "intersection_n": len(inter),
                "coverage_smaller": len(inter) / min(len(trait_set), len(tree_set)) if trait_set and tree_set else 0.0,
            }

    # Deterministic mutual-unique-best association by intersection count, then
    # coverage. Ties at the scientific association level are rejected, not broken
    # by downstream signal.
    clade_best = {}
    for clade in sorted(clade_traits):
        vals = [(pair[(clade, t["path"])]["intersection_n"], pair[(clade, t["path"])]["coverage_smaller"], t["path"]) for t in parsed_trees]
        vals.sort(reverse=True)
        top = vals[0]
        tied = [v for v in vals if v[:2] == top[:2]]
        clade_best[clade] = {"tree_path": top[2], "intersection_n": top[0], "coverage_smaller": top[1], "unique_best": len(tied) == 1, "ties": [x[2] for x in tied]}

    tree_best = {}
    for tr in parsed_trees:
        path = tr["path"]
        vals = [(pair[(c, path)]["intersection_n"], pair[(c, path)]["coverage_smaller"], c) for c in clade_traits]
        vals.sort(reverse=True)
        top = vals[0]
        tied = [v for v in vals if v[:2] == top[:2]]
        tree_best[path] = {"clade": top[2], "intersection_n": top[0], "coverage_smaller": top[1], "unique_best": len(tied) == 1, "ties": [x[2] for x in tied]}

    tree_by_path = {t["path"]: t for t in parsed_trees}
    admissions = []
    for clade in sorted(clade_traits):
        cdat = clade_traits[clade]
        b = clade_best[clade]
        tr = tree_by_path[b["tree_path"]]
        reciprocal = tree_best[b["tree_path"]]
        mutual_unique = bool(b["unique_best"] and reciprocal["unique_best"] and reciprocal["clade"] == clade)
        trait_set = set(cdat["traits"])
        tree_set = set(tr["tips_norm"])
        matched = sorted(trait_set & tree_set) if mutual_unique else []
        counts = Counter(cdat["traits"][sp]["state"] for sp in matched)
        white = counts.get("WHITE", 0)
        nonwhite = len(matched) - white
        nonwhite_states = sorted(s for s, n in counts.items() if s != "WHITE" and n > 0)
        gates = {
            "unique_machine_readable_tree_association": mutual_unique,
            "no_conflicting_duplicate_trait_rows": len(cdat["conflicts"]) == 0,
            "matched_n_ge_30": len(matched) >= 30,
            "coverage_ge_80pct": b["coverage_smaller"] >= 0.80 if mutual_unique else False,
            "white_ge_5": white >= 5,
            "nonwhite_ge_15": nonwhite >= 15,
            "nonwhite_fine_states_ge_3": len(nonwhite_states) >= 3,
        }
        admissions.append({
            "clade": clade,
            "trait_raw_rows": cdat["raw_n"],
            "trait_unique_species": len(trait_set),
            "trait_conflict_count": len(cdat["conflicts"]),
            "tree_path": b["tree_path"],
            "tree_tip_count": tr["tip_count"],
            "tree_unique_tip_count": tr["unique_tip_count"],
            "mutual_unique_best": mutual_unique,
            "best_intersection_n_before_mutual_gate": b["intersection_n"],
            "coverage_smaller_before_mutual_gate": b["coverage_smaller"],
            "matched_n": len(matched),
            "fine_state_counts": dict(sorted(counts.items())),
            "white_n": white,
            "nonwhite_n": nonwhite,
            "nonwhite_fine_states": nonwhite_states,
            "gates": gates,
            "admitted_primary": all(gates.values()),
            "matched_species_norm": matched,
        })

    admitted = [x for x in admissions if x["admitted_primary"]]
    summary = {
        "source_doi": DOI,
        "download": dlmeta,
        "source_files": source_files,
        "csv_header": header,
        "csv_rows": len(raw_rows),
        "source_clade_count": len(clade_traits),
        "trees_zip_member_count": len(inner_members),
        "tree_file_count": len(tree_records),
        "parsed_unique_tip_tree_count": len(parsed_trees),
        "admitted_primary_clade_count": len(admitted),
        "panel_minimum_10_clades_gate": len(admitted) >= 10,
        "admitted_clades": [x["clade"] for x in admitted],
        "endpoint_computed": False,
        "signal_fields_computed": [],
        "note": "No Sankoff score, transition count, observed/null ratio, lability class, or permutation p-value is computed by this audit.",
    }

    # Save complete machine-readable source audit.
    (OUT / "source_inventory.json").write_text(json.dumps({"summary": summary, "tree_records": tree_records, "duplicate_trait_rows": duplicate_report}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (OUT / "clade_admission.json").write_text(json.dumps(admissions, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (OUT / "clade_admission.tsv").open("w", encoding="utf-8", newline="") as f:
        fields = ["clade", "trait_unique_species", "tree_path", "tree_tip_count", "mutual_unique_best", "matched_n", "coverage", "white_n", "nonwhite_n", "nonwhite_state_n", "admitted_primary", "failed_gates"]
        w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
        w.writeheader()
        for x in admissions:
            w.writerow({
                "clade": x["clade"],
                "trait_unique_species": x["trait_unique_species"],
                "tree_path": x["tree_path"],
                "tree_tip_count": x["tree_tip_count"],
                "mutual_unique_best": x["mutual_unique_best"],
                "matched_n": x["matched_n"],
                "coverage": f"{x['coverage_smaller_before_mutual_gate']:.6f}",
                "white_n": x["white_n"],
                "nonwhite_n": x["nonwhite_n"],
                "nonwhite_state_n": len(x["nonwhite_fine_states"]),
                "admitted_primary": x["admitted_primary"],
                "failed_gates": ";".join(k for k, v in x["gates"].items() if not v),
            })

    print("MULTICLADE51_SOURCE_AUDIT=" + json.dumps({
        "source_clades": summary["source_clade_count"],
        "parsed_unique_tip_trees": summary["parsed_unique_tip_tree_count"],
        "admitted_primary_clades": summary["admitted_primary_clade_count"],
        "panel_minimum_10_clades_gate": summary["panel_minimum_10_clades_gate"],
        "admitted_clades": summary["admitted_clades"],
        "csv_sha256": source_files["final_dataset_csv"]["sha256"],
        "trees_zip_sha256": source_files["trees_zip"]["sha256"],
    }, ensure_ascii=False))

    # Source audit itself succeeds even if the biological panel would HOLD; a
    # later validator interprets the frozen admission result.


if __name__ == "__main__":
    main()
