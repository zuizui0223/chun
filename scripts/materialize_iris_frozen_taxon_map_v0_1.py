#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import io
import re
import urllib.request
from pathlib import Path

import pandas as pd
from Bio import Phylo

TRAIT_URL = "https://pmc-oa-opendata.s3.amazonaws.com/PMC7588356.1/Table_1.xlsx"
UA = "chun-iris-frozen-taxon-map/0.1"


def clean(x: object) -> str:
    if pd.isna(x):
        return ""
    return re.sub(r"\s+", " ", str(x)).strip()


def binomial_key(raw: str) -> str:
    # Byte-for-byte semantic copy of the already-frozen source-crosswalk validator rule.
    s = clean(raw).lower().replace("×", "x").replace("_", " ")
    s = re.sub(r"\b(subsp|subs|ssp|var|cf)\.?\b", " ", s)
    s = re.sub(r"\b(l|mill|auct)\.?\b", " ", s)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    toks = s.split()
    if not toks:
        return ""
    if toks[0].startswith("irisx") and len(toks[0]) > 5:
        return "iris " + toks[0][5:]
    if toks[0] == "iris" and len(toks) > 1:
        if toks[1] == "x" and len(toks) > 2:
            return "iris " + toks[2]
        return "iris " + toks[1]
    return " ".join(toks[:2])


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", type=Path, required=True)
    ap.add_argument("--frozen-explicit-crosswalk", type=Path, default=Path("data/iris_source_taxon_crosswalk_v0_1.csv"))
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    traits = pd.read_excel(io.BytesIO(fetch(TRAIT_URL)), sheet_name="Source of data", engine="openpyxl")
    trait_labels = [clean(x) for x in traits["Species"] if clean(x)]

    tree = Phylo.read(str(args.tree), "newick")
    tips = [t.name for t in tree.get_terminals()]
    if len(tips) != 227 or len(set(tips)) != 227:
        raise SystemExit(f"unexpected frozen tree tips: {len(tips)} / {len(set(tips))}")

    with args.frozen_explicit_crosswalk.open(newline="", encoding="utf-8-sig") as fh:
        explicit_rows = list(csv.DictReader(fh))
    explicit = {clean(r["trait_source_label"]): clean(r["accession_source_label"]) for r in explicit_rows}
    if len(explicit) != 5 or any(r["status"] != "ADMITTED" for r in explicit_rows):
        raise SystemExit("frozen explicit crosswalk contract drifted")

    reserved = set(explicit.values())
    tip_by_key: dict[str, list[str]] = {}
    for tip in tips:
        if tip in reserved or tip in {"Iris_cedretii", "Iris_darwasica"}:
            continue
        tip_by_key.setdefault(binomial_key(tip), []).append(tip)

    mapped: list[tuple[str, str, str]] = []
    used: set[str] = set()
    for src in trait_labels:
        if src in explicit:
            target = explicit[src]
            mode = "FROZEN_EXPLICIT_OVERRIDE"
        else:
            candidates = tip_by_key.get(binomial_key(src), [])
            if len(candidates) != 1:
                raise SystemExit(f"frozen generic join is not one-to-one for {src!r}: {candidates}")
            target = candidates[0]
            mode = "FROZEN_BINOMIAL_KEY_RULE"
        if target in used:
            raise SystemExit(f"duplicate mapped tree tip: {target}")
        used.add(target)
        mapped.append((src, target, mode))

    if len(mapped) != 226 or len(used) != 226:
        raise SystemExit(f"expected 226 one-to-one trait mappings, got {len(mapped)} / {len(used)}")
    if sorted(set(tips) - used) != ["Iris_cedretii"]:
        # Iris_darwasica was already excluded from the frozen primary tree.
        raise SystemExit(f"unexpected tree-only tip set: {sorted(set(tips)-used)}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["trait_source_label", "accession_source_label", "rule", "status", "notes"])
        for src, target, mode in mapped:
            w.writerow([src, target, mode, "ADMITTED", "Materialized from frozen pre-outcome species-label mapping rule only; no colour/pigment value used."])
    print({"status":"IRIS_FROZEN_FULL_TAXON_MAP_MATERIALIZED","mapped":len(mapped),"trait_values_used":False})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
