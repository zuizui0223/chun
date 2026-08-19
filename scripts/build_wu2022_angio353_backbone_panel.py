#!/usr/bin/env python3
"""Build the assembled-taxon Angiosperms353 backbone panel from the frozen Wu v0.3 manifest.

The authoritative manifest contains 98 species-level taxa. Only rows whose
``assembly_source`` is ``tpia_id_bound_allassemblies`` are admitted here; raw
SRA fallbacks remain excluded until transcript/locus recovery has been done.
This keeps the topology input mechanically tied to the provenance gate instead
of maintaining a second hand-edited species list.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

OUT_FIELDS = [
    "taxon",
    "colour_state",
    "section",
    "tpia_id",
    "tpia_resource_name",
    "assembly_url",
    "panel_role",
    "admission_status",
    "provenance_note",
]


def parse_tpia_id(assembly_file: str) -> str:
    m = re.match(r"^(\d+)_", assembly_file or "")
    if not m:
        raise ValueError(f"cannot parse TPIA id from assembly_file={assembly_file!r}")
    return m.group(1)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    ap.add_argument("--expected-total", type=int, default=98)
    ap.add_argument("--expected-assembled", type=int, default=93)
    ap.add_argument("--expected-raw", type=int, default=5)
    args = ap.parse_args()

    with args.manifest.open(newline="", encoding="utf-8-sig") as f:
        manifest = list(csv.DictReader(f))

    assembled = [r for r in manifest if r["assembly_source"] == "tpia_id_bound_allassemblies"]
    raw = [r for r in manifest if r["assembly_source"] == "ncbi_sra_raw_fallback"]
    other = [r for r in manifest if r["assembly_source"] not in {"tpia_id_bound_allassemblies", "ncbi_sra_raw_fallback"}]

    assert len(manifest) == args.expected_total, (len(manifest), args.expected_total)
    assert len(assembled) == args.expected_assembled, (len(assembled), args.expected_assembled)
    assert len(raw) == args.expected_raw, (len(raw), args.expected_raw)
    assert not other, [(r.get("source_taxon"), r.get("assembly_source")) for r in other]

    taxa = [r["source_taxon"] for r in assembled]
    assert len(taxa) == len(set(taxa)), "duplicate assembled source_taxon"
    urls = [r["assembly_url"] for r in assembled]
    assert len(urls) == len(set(urls)), "duplicate admitted assembly_url in v0.3 manifest"

    panel = []
    for r in sorted(assembled, key=lambda x: x["source_taxon"]):
        panel.append(
            {
                "taxon": r["source_taxon"],
                "colour_state": "U",
                "section": "unknown",
                "tpia_id": parse_tpia_id(r["assembly_file"]),
                "tpia_resource_name": r["resource_taxon"],
                "assembly_url": r["assembly_url"],
                "panel_role": "genus_nuclear_backbone",
                "admission_status": "admit",
                "provenance_note": f"v0.3:{r['match_basis']}",
            }
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=OUT_FIELDS)
        w.writeheader()
        w.writerows(panel)

    summary = {
        "manifest": str(args.manifest),
        "n_manifest_taxa": len(manifest),
        "n_assembled_admitted": len(panel),
        "n_raw_held_out": len(raw),
        "raw_held_out_taxa": sorted(r["source_taxon"] for r in raw),
        "claim_ceiling": "93 provenance-admitted assembled taxa only; five raw SRA taxa excluded pending independent transcript/locus recovery",
    }
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
