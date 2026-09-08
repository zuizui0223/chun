#!/usr/bin/env python3
"""Source/admission audit for the prospectively frozen 51-clade panel.

No Sankoff score, transition count, observed/null ratio, lability result, or
permutation p-value is computed here. This layer only retrieves the public
Dryad files, audits schema/tree identity, and applies the pre-frozen admission
gates.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import shutil
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urljoin

import requests
from Bio import Phylo

DOI = "10.5061/dryad.r4xgxd2sc"
ENCODED = "doi%3A10.5061%2Fdryad.r4xgxd2sc"
BASE = "https://datadryad.org"
API = f"{BASE}/api/v2"
UA = "chun-multiclade-falsification-source-audit/1.1"
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


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def clean(x: str) -> str:
    return re.sub(r"\s+", " ", (x or "").strip())


def norm_species(x: str) -> str:
    # Frozen syntactic comparison boundary only: quotes, underscores/spaces,
    # repeated whitespace and case. Taxonomic tokens are never discarded.
    s = clean(x).strip("'\"").replace("_", " ")
    return clean(s).casefold()


def norm_color(x: str) -> str:
    s = clean(x).casefold().replace("_", " ")
    return s.replace("–", "-").replace("—", "-")


def get_json(url: str) -> dict:
    r = requests.get(
        url,
        headers={"User-Agent": UA, "Accept": "application/json", "X-API-Version": "2.1.0"},
        timeout=120,
    )
    r.raise_for_status()
    return r.json()


def embedded_list(data: dict, preferred_suffix: str) -> list:
    emb = data.get("_embedded") or {}
    preferred = [v for k, v in emb.items() if k.endswith(preferred_suffix) and isinstance(v, list)]
    if len(preferred) == 1:
        return preferred[0]
    lists = [v for v in emb.values() if isinstance(v, list)]
    if len(lists) == 1:
        return lists[0]
    raise SystemExit(f"Dryad HAL schema not uniquely interpretable for {preferred_suffix}: keys={list(emb)}")


def extract_id(record: dict, kind: str) -> int:
    if record.get("id") is not None:
        return int(record["id"])
    href = ((record.get("_links") or {}).get("self") or {}).get("href", "")
    m = re.search(rf"/{re.escape(kind)}/(\d+)(?:$|[/?#])", href)
    if not m:
        raise SystemExit(f"cannot extract {kind} id from record: {record}")
    return int(m.group(1))


def latest_version() -> tuple[dict, dict, list[dict]]:
    dataset_url = f"{API}/datasets/{ENCODED}"
    dataset = get_json(dataset_url)
    versions_data = get_json(f"{dataset_url}/versions")
    versions = embedded_list(versions_data, "versions")
    if not versions:
        raise SystemExit("Dryad returned no dataset versions")

    def vkey(v: dict):
        try:
            vn = int(v.get("versionNumber"))
        except (TypeError, ValueError):
            vn = -1
        try:
            vid = extract_id(v, "versions")
        except SystemExit:
            vid = -1
        return (vn, vid)

    latest = max(versions, key=vkey)
    version_id = extract_id(latest, "versions")
    files_data = get_json(f"{API}/versions/{version_id}/files")
    files = embedded_list(files_data, "files")
    return dataset, latest, files


def public_file_download(file_record: dict, dest: Path) -> dict:
    file_id = extract_id(file_record, "files")
    links = file_record.get("_links") or {}
    href = ((links.get("stash:download") or {}).get("href")) or f"/api/v2/files/{file_id}/download"
    urls = [
        urljoin(BASE, href),
        f"{BASE}/stash/downloads/file_stream/{file_id}",
        f"{BASE}/downloads/file_stream/{file_id}",
    ]
    attempts = []
    for url in urls:
        r = requests.get(
            url,
            headers={"User-Agent": UA, "Accept": "*/*", "X-API-Version": "2.1.0"},
            timeout=180,
            allow_redirects=True,
        )
        attempts.append({
            "requested_url": url,
            "final_url": r.url,
            "status": r.status_code,
            "content_type": r.headers.get("content-type", ""),
            "bytes": len(r.content),
        })
        if not r.ok or not r.content:
            continue
        dest.write_bytes(r.content)
        expected_size = file_record.get("size")
        if expected_size not in (None, "") and int(expected_size) != dest.stat().st_size:
            raise SystemExit(
                f"Dryad file size mismatch for {file_record.get('path')}: expected={expected_size}, got={dest.stat().st_size} via {url}"
            )
        expected_digest = clean(file_record.get("digest", ""))
        actual = sha256_file(dest)
        if expected_digest and clean(file_record.get("digestType", "")).casefold() in {"sha-256", "sha256"}:
            if actual.casefold() != expected_digest.casefold():
                raise SystemExit(
                    f"Dryad SHA-256 mismatch for {file_record.get('path')}: expected={expected_digest}, got={actual}"
                )
        return {
            "file_id": file_id,
            "path": file_record.get("path", ""),
            "size_metadata": expected_size,
            "digest_metadata": expected_digest,
            "digest_type": file_record.get("digestType", ""),
            "download_attempts": attempts,
            "selected_download_url": url,
            "sha256": actual,
            "bytes": dest.stat().st_size,
        }
    raise SystemExit(f"all public Dryad file-download routes failed for id={file_id}: {attempts}")


def choose_named_file(files: list[dict], basename: str) -> dict:
    hits = [f for f in files if Path(str(f.get("path", ""))).name.casefold() == basename.casefold()]
    if len(hits) != 1:
        raise SystemExit(f"expected one Dryad file named {basename}, found {len(hits)}: {[x.get('path') for x in hits]}")
    return hits[0]


def parse_tree_file(path: Path):
    raw = path.read_bytes()
    if not raw:
        return None, "EMPTY"
    text = None
    for enc in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            pass
    if text is None:
        return None, "NON_TEXT"
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
    successes.sort(key=lambda x: 0 if x[0] == "newick" else 1)
    fmt, tree = successes[0]
    tips_raw = [str(t.name or "") for t in tree.get_terminals()]
    return {
        "format": fmt,
        "tip_count": len(tips_raw),
        "tips_norm": [norm_species(x) for x in tips_raw],
    }, "OK"


def normalized_header_map(header: list[str]) -> dict[str, str]:
    out = {}
    for h in header:
        k = clean(h).casefold().replace(" ", "_").replace("-", "_")
        out[k] = h
    return out


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    source_dir = OUT / "source"
    source_dir.mkdir()

    dataset_meta, version_meta, files = latest_version()
    version_id = extract_id(version_meta, "versions")
    csv_rec = choose_named_file(files, "final_dataset.csv")
    trees_rec = choose_named_file(files, "trees.zip")
    csv_path = source_dir / "final_dataset.csv"
    trees_zip = source_dir / "trees.zip"
    csv_dl = public_file_download(csv_rec, csv_path)
    trees_dl = public_file_download(trees_rec, trees_zip)
    if not zipfile.is_zipfile(trees_zip):
        raise SystemExit("downloaded trees.zip is not a ZIP archive")

    source_files = {
        "dataset_doi": DOI,
        "version_id": version_id,
        "version_number": version_meta.get("versionNumber"),
        "published": version_meta.get("publicationDate") or version_meta.get("lastModificationDate"),
        "file_count_in_version": len(files),
        "final_dataset_csv": csv_dl,
        "trees_zip": trees_dl,
        "dataset_self": ((dataset_meta.get("_links") or {}).get("self") or {}).get("href", ""),
    }

    with csv_path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames or []
        hmap = normalized_header_map(header)
        required = {"clade", "species", "flower_color", "fruit_color"}
        if not required.issubset(hmap):
            raise SystemExit(f"CSV schema drift: normalized_header={sorted(hmap)} raw_header={header}")
        rows0 = [dict(r) for r in reader]
    if not rows0:
        raise SystemExit("final_dataset.csv is empty")

    def val(r: dict, key: str) -> str:
        return r.get(hmap[key], "")

    unknown_colors = sorted({
        norm_color(val(r, "flower_color"))
        for r in rows0
        if clean(val(r, "flower_color")) and norm_color(val(r, "flower_color")) not in FINE
    })
    missing_flower = sum(not clean(val(r, "flower_color")) for r in rows0)
    if unknown_colors:
        raise SystemExit(f"HOLD_SCHEMA unknown flower colors: {unknown_colors}")
    if missing_flower:
        raise SystemExit(f"HOLD_SCHEMA missing flower colors: {missing_flower}")

    clade_rows = defaultdict(list)
    for i, r in enumerate(rows0, start=2):
        clade = clean(val(r, "clade"))
        species_raw = clean(val(r, "species"))
        if not clade or not species_raw:
            raise SystemExit(f"missing clade/species at CSV row {i}")
        clade_rows[clade].append({
            "csv_row": i,
            "species_raw": species_raw,
            "species_norm": norm_species(species_raw),
            "fine_state": FINE[norm_color(val(r, "flower_color"))],
            "fruit_color_raw": clean(val(r, "fruit_color")),
        })

    clade_traits = {}
    duplicate_report = {}
    for clade, rows in clade_rows.items():
        by_sp = defaultdict(list)
        for r in rows:
            by_sp[r["species_norm"]].append(r)
        traits, dups, conflicts = {}, [], []
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

    tree_dir = OUT / "trees"
    tree_dir.mkdir()
    with zipfile.ZipFile(trees_zip) as z:
        inner_members = sorted(z.namelist())
        z.extractall(tree_dir)

    tree_records = []
    for p in sorted(x for x in tree_dir.rglob("*") if x.is_file()):
        rec, status = parse_tree_file(p)
        record = {"path": str(p.relative_to(tree_dir)), "bytes": p.stat().st_size, "sha256": sha256_file(p), "parse_status": status}
        if rec:
            norms = rec["tips_norm"]
            record.update({
                "format": rec["format"],
                "tip_count": rec["tip_count"],
                "unique_tip_count": len(set(norms)),
                "duplicate_normalized_tips": sorted(x for x, n in Counter(norms).items() if n > 1),
                "tips_norm": norms,
            })
        tree_records.append(record)

    parsed_trees = [t for t in tree_records if t["parse_status"] == "OK" and not t.get("duplicate_normalized_tips")]
    if not parsed_trees:
        raise SystemExit("no unique-tip machine-readable tree files parsed")

    pair = {}
    for clade, cdat in clade_traits.items():
        trait_set = set(cdat["traits"])
        for tr in parsed_trees:
            tree_set = set(tr["tips_norm"])
            inter = trait_set & tree_set
            denom = min(len(trait_set), len(tree_set))
            pair[(clade, tr["path"])] = {"intersection_n": len(inter), "coverage_smaller": len(inter) / denom if denom else 0.0}

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
        "source_files": source_files,
        "csv_header": header,
        "csv_rows": len(rows0),
        "source_clade_count": len(clade_traits),
        "trees_zip_member_count": len(inner_members),
        "tree_file_count": len(tree_records),
        "parsed_unique_tip_tree_count": len(parsed_trees),
        "admitted_primary_clade_count": len(admitted),
        "panel_minimum_10_clades_gate": len(admitted) >= 10,
        "admitted_clades": [x["clade"] for x in admitted],
        "endpoint_computed": False,
        "signal_fields_computed": [],
        "note": "No Sankoff score, transition count, observed/null ratio, source lability class, or permutation p-value is computed by this audit.",
    }

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
        "version_id": version_id,
        "source_clades": summary["source_clade_count"],
        "parsed_unique_tip_trees": summary["parsed_unique_tip_tree_count"],
        "admitted_primary_clades": summary["admitted_primary_clade_count"],
        "panel_minimum_10_clades_gate": summary["panel_minimum_10_clades_gate"],
        "admitted_clades": summary["admitted_clades"],
        "csv_sha256": csv_dl["sha256"],
        "trees_zip_sha256": trees_dl["sha256"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
