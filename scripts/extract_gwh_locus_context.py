#!/usr/bin/env python3
"""Resolve an anchored GWH transcript ID to gene/locus context in GFF3."""

from __future__ import annotations

import argparse
import csv
import pathlib


def parse_attrs(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for item in text.strip().strip(";").split(";"):
        if not item:
            continue
        if "=" in item:
            key, value = item.split("=", 1)
            out[key.strip()] = value.strip()
        elif " " in item:
            key, value = item.split(" ", 1)
            out[key.strip()] = value.strip().strip('"')
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gff", required=True, type=pathlib.Path)
    parser.add_argument("--transcript", required=True)
    parser.add_argument("--out", required=True, type=pathlib.Path)
    args = parser.parse_args()

    records: list[dict[str, str]] = []
    id_index: dict[str, list[int]] = {}
    parent_index: dict[str, list[int]] = {}

    with args.gff.open(encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, 1):
            if not line.strip() or line.startswith("#"):
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) != 9:
                continue
            seqid, source, feature, start, end, score, strand, phase, attr_text = parts
            attrs = parse_attrs(attr_text)
            rec = {
                "line_no": str(line_no),
                "seqid": seqid,
                "source": source,
                "feature": feature,
                "start": start,
                "end": end,
                "score": score,
                "strand": strand,
                "phase": phase,
                "ID": attrs.get("ID", ""),
                "Parent": attrs.get("Parent", ""),
                "Name": attrs.get("Name", ""),
                "attributes": attr_text,
            }
            idx = len(records)
            records.append(rec)
            if rec["ID"]:
                id_index.setdefault(rec["ID"], []).append(idx)
            for parent in [p.strip() for p in rec["Parent"].split(",") if p.strip()]:
                parent_index.setdefault(parent, []).append(idx)

    target = args.transcript.strip()
    seed_indices: set[int] = set()
    candidate_ids = {target, target.removesuffix(".1")}
    for candidate in candidate_ids:
        seed_indices.update(id_index.get(candidate, []))
        seed_indices.update(parent_index.get(candidate, []))

    if not seed_indices:
        # GFF conventions sometimes prefix transcript IDs or retain versionless
        # IDs. Allow a deterministic substring recovery, but record the actual
        # matched IDs rather than pretending it was exact.
        for idx, rec in enumerate(records):
            if target in rec["attributes"] or target.removesuffix(".1") in rec["attributes"]:
                seed_indices.add(idx)

    if not seed_indices:
        raise SystemExit(f"No GFF feature references anchored transcript {target}")

    selected: set[int] = set(seed_indices)
    frontier_ids: set[str] = set()
    for idx in seed_indices:
        rec = records[idx]
        if rec["ID"]:
            frontier_ids.add(rec["ID"])
        frontier_ids.update(p.strip() for p in rec["Parent"].split(",") if p.strip())

    # Walk parent chain upward and immediate child chain downward until stable.
    changed = True
    while changed:
        changed = False
        current_ids = set(frontier_ids)
        for ident in current_ids:
            for idx in id_index.get(ident, []):
                if idx not in selected:
                    selected.add(idx); changed = True
                rec = records[idx]
                frontier_ids.update(p.strip() for p in rec["Parent"].split(",") if p.strip())
            for idx in parent_index.get(ident, []):
                if idx not in selected:
                    selected.add(idx); changed = True
                child_id = records[idx]["ID"]
                if child_id:
                    frontier_ids.add(child_id)

    chosen = [records[i] for i in sorted(selected, key=lambda i: (records[i]["seqid"], int(records[i]["start"]), int(records[i]["end"]), records[i]["feature"]))]
    seqids = {r["seqid"] for r in chosen}
    genes = [r for r in chosen if r["feature"].lower() == "gene"]
    transcripts = [r for r in chosen if r["feature"].lower() in {"mrna", "transcript"}]
    if len(seqids) != 1:
        raise SystemExit(f"Anchored context spans multiple seqids unexpectedly: {seqids}")
    if not transcripts:
        raise SystemExit(f"No transcript/mRNA feature recovered for {target}")
    if not genes:
        raise SystemExit(f"No parent gene feature recovered for {target}")

    for rec in chosen:
        rec["anchored_transcript"] = target
        rec["relation"] = (
            "gene" if rec["feature"].lower() == "gene"
            else "transcript" if rec["feature"].lower() in {"mrna", "transcript"}
            else "child_feature"
        )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "anchored_transcript", "relation", "line_no", "seqid", "source", "feature",
        "start", "end", "score", "strand", "phase", "ID", "Parent", "Name", "attributes",
    ]
    with args.out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader(); writer.writerows(chosen)

    gene = genes[0]
    print(
        f"{target}: gene={gene['ID']} seqid={gene['seqid']} "
        f"coordinates={gene['start']}-{gene['end']} strand={gene['strand']} "
        f"features={len(chosen)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
