#!/usr/bin/env python3
"""Resolve the tea ANR source anchor against reference-mapped ANR/K08695 copies.

This script deliberately distinguishes a tea-reference copy used by a C. reticulata
mapping analysis from a species-native C. reticulata locus.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Iterable

from Bio import AlignIO, SeqIO
from Bio.Align import PairwiseAligner
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord


def open_text(path: Path):
    return gzip.open(path, "rt", encoding="utf-8", errors="replace") if path.suffix == ".gz" else path.open(encoding="utf-8", errors="replace")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def aliases(row: dict[str, str]) -> list[str]:
    vals = [row["target_id"]]
    vals.extend(x.strip() for x in row.get("aliases", "").split(";") if x.strip())
    return list(dict.fromkeys(vals))


def fasta_records(path: Path) -> list[SeqRecord]:
    with open_text(path) as handle:
        return list(SeqIO.parse(handle, "fasta"))


def parse_attrs(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for item in text.strip().split(";"):
        if not item:
            continue
        if "=" in item:
            key, value = item.split("=", 1)
        elif " " in item:
            key, value = item.split(" ", 1)
            value = value.strip('"')
        else:
            continue
        out[key.strip()] = value.strip()
    return out


def gff_candidates(path: Path, target_aliases: Iterable[str]) -> set[str]:
    needles = [x.lower() for x in target_aliases]
    proteins: set[str] = set()
    parents: set[str] = set()
    matching_lines: list[tuple[str, dict[str, str]]] = []
    with open_text(path) as handle:
        for line in handle:
            if not line or line.startswith("#"):
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 9:
                continue
            attrs = parse_attrs(parts[8])
            hay = (parts[8] + " " + " ".join(attrs.values())).lower()
            if any(n in hay for n in needles):
                matching_lines.append((parts[2], attrs))
                for key in ("ID", "Parent", "gene", "gene_id", "Name", "locus_tag", "transcript_id"):
                    if attrs.get(key):
                        parents.update(x.strip() for x in attrs[key].split(","))
                for key in ("protein_id", "proteinId", "protein"):
                    if attrs.get(key):
                        proteins.update(x.strip() for x in attrs[key].split(","))
    if parents:
        with open_text(path) as handle:
            for line in handle:
                if not line or line.startswith("#"):
                    continue
                parts = line.rstrip("\n").split("\t")
                if len(parts) < 9:
                    continue
                attrs = parse_attrs(parts[8])
                relation = set()
                for key in ("ID", "Parent", "gene", "gene_id", "Name", "locus_tag", "transcript_id"):
                    if attrs.get(key):
                        relation.update(x.strip() for x in attrs[key].split(","))
                if relation & parents:
                    for key in ("protein_id", "proteinId", "protein"):
                        if attrs.get(key):
                            proteins.update(x.strip() for x in attrs[key].split(","))
    return {p.split(".")[0] for p in proteins} | proteins


def choose_protein(records: list[SeqRecord], target_aliases: list[str], gff_ids: set[str]) -> tuple[SeqRecord | None, str]:
    exact: list[SeqRecord] = []
    description_hits: list[SeqRecord] = []
    needles = [a.lower() for a in target_aliases]
    gff_lower = {x.lower() for x in gff_ids}
    for rec in records:
        rid = rec.id.lower()
        desc = rec.description.lower()
        if rid in gff_lower or rid.split(".")[0] in gff_lower:
            exact.append(rec)
        elif any(n in desc or n in rid for n in needles):
            description_hits.append(rec)
    pool = exact or description_hits
    if not pool:
        return None, "not_found"
    pool.sort(key=lambda r: (len(r.seq), r.id), reverse=True)
    return pool[0], "gff_link" if exact else "fasta_description"


def global_metrics(a: str, b: str) -> dict[str, float | int]:
    aligner = PairwiseAligner()
    aligner.mode = "global"
    aligner.match_score = 2.0
    aligner.mismatch_score = -1.0
    aligner.open_gap_score = -6.0
    aligner.extend_gap_score = -0.5
    aln = aligner.align(a, b)[0]
    coords = aln.coordinates
    matches = 0
    compared = 0
    a_used = 0
    b_used = 0
    gap_columns = 0
    for i in range(coords.shape[1] - 1):
        a0, a1 = int(coords[0, i]), int(coords[0, i + 1])
        b0, b1 = int(coords[1, i]), int(coords[1, i + 1])
        da, db = a1 - a0, b1 - b0
        if da and db:
            span = min(da, db)
            sa = a[a0:a0 + span]
            sb = b[b0:b0 + span]
            matches += sum(x == y for x, y in zip(sa, sb))
            compared += span
            a_used += span
            b_used += span
            if da != db:
                gap_columns += abs(da - db)
                a_used += max(0, da - span)
                b_used += max(0, db - span)
        elif da:
            gap_columns += da
            a_used += da
        elif db:
            gap_columns += db
            b_used += db
    return {
        "matches": matches,
        "compared_non_gap": compared,
        "nongap_identity": matches / compared if compared else 0.0,
        "query_coverage": a_used / len(a) if a else 0.0,
        "subject_coverage": b_used / len(b) if b else 0.0,
        "gap_columns": gap_columns,
        "query_length": len(a),
        "subject_length": len(b),
        "alignment_score": float(aln.score),
    }


def load_effects(path: Path | None, target_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    if path is None or not path.exists():
        return []
    rows = read_csv(path)
    ids = {r["target_id"]: set(aliases(r)) for r in target_rows if r["role"] == "reference_copy"}
    id_col = next((c for c in ("gene_id", "gene", "feature", "source_feature") if rows and c in rows[0]), None)
    if not id_col:
        return []
    out = []
    for row in rows:
        raw = str(row.get(id_col, ""))
        target = next((tid for tid, als in ids.items() if raw == tid or raw in als or any(a in raw for a in als)), None)
        if not target:
            continue
        effect_col = next((c for c in ("red_minus_white_log2fpkm", "red_minus_white", "log2fc_red_white", "reported_log2FC") if c in row), None)
        value = row.get(effect_col, "") if effect_col else ""
        try:
            x = float(value)
            direction = "red_directed" if x > 0 else ("white_directed" if x < 0 else "neutral")
        except Exception:
            direction = "unresolved"
        out.append({
            "target_id": target,
            "source_feature": raw,
            "red_minus_white_log2fpkm": value,
            "direction": direction,
            "red_gt_white": row.get("red_gt_white", ""),
            "red_gt_pink_gt_white": row.get("red_gt_pink_gt_white", ""),
            "evidence_scope": "tea-reference-mapped C. reticulata contrast",
            "claim_boundary": "direction applies to the mapped tea reference feature, not a recovered species-native C. reticulata locus",
        })
    unique = {r["target_id"]: r for r in out}
    return [unique[k] for k in sorted(unique)]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--targets", type=Path, required=True)
    parser.add_argument("--longjing43-gff", type=Path, required=True)
    parser.add_argument("--longjing43-proteins", type=Path, required=True)
    parser.add_argument("--refseq-gff", type=Path, required=True)
    parser.add_argument("--refseq-proteins", type=Path, required=True)
    parser.add_argument("--effects", type=Path)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    targets = read_csv(args.targets)
    lj_records = fasta_records(args.longjing43_proteins)
    ref_records = fasta_records(args.refseq_proteins)
    mapped: dict[str, SeqRecord] = {}
    mapping_rows = []

    for row in targets:
        als = aliases(row)
        if row["role"] == "anchor":
            gids = gff_candidates(args.longjing43_gff, als)
            rec, route = choose_protein(lj_records, als, gids)
            source = "Longjing43 GWH/TPIA2 crosswalk"
        else:
            gids = gff_candidates(args.refseq_gff, als)
            rec, route = choose_protein(ref_records, als, gids)
            source = "NCBI tea reference assembly"
        if rec is not None:
            mapped[row["target_id"]] = rec
        mapping_rows.append({
            "role": row["role"],
            "target_id": row["target_id"],
            "source_cluster": row["source_cluster"],
            "mapping_route": route,
            "protein_accession": rec.id if rec else "",
            "protein_length_aa": len(rec.seq) if rec else "",
            "sequence_sha256": hashlib.sha256(str(rec.seq).encode()).hexdigest() if rec else "",
            "sequence_source": source,
            "species_native_target_sequence": "yes" if row["role"] == "anchor" else "no",
            "claim_boundary": row["claim_boundary"],
        })

    anchor_row = next(r for r in targets if r["role"] == "anchor")
    anchor_id = anchor_row["target_id"]
    if anchor_id not in mapped:
        raise RuntimeError(f"failed to recover ANR anchor {anchor_id}")

    anchor = str(mapped[anchor_id].seq).rstrip("*")
    identity_rows = []
    for row in targets:
        if row["role"] != "reference_copy" or row["target_id"] not in mapped:
            continue
        tid = row["target_id"]
        metrics = global_metrics(anchor, str(mapped[tid].seq).rstrip("*"))
        identity_rows.append({
            "anchor_id": anchor_id,
            "anchor_protein_accession": mapped[anchor_id].id,
            "reference_target_id": tid,
            "reference_protein_accession": mapped[tid].id,
            **metrics,
            "reference_sequence_scope": "tea reference copy used by C. reticulata mapping analysis",
            "strict_crossspecies_exact_node_ready": "no",
        })
    identity_rows.sort(key=lambda r: (-float(r["nongap_identity"]), r["reference_target_id"]))

    pair_rows = []
    ref_ids = [r["target_id"] for r in targets if r["role"] == "reference_copy" and r["target_id"] in mapped]
    for i, x in enumerate(ref_ids):
        for y in ref_ids[i + 1:]:
            metrics = global_metrics(str(mapped[x].seq).rstrip("*"), str(mapped[y].seq).rstrip("*"))
            pair_rows.append({"target_id_1": x, "target_id_2": y, **metrics})

    effects = load_effects(args.effects, targets)
    effect_by_id = {r["target_id"]: r for r in effects}
    for row in identity_rows:
        effect = effect_by_id.get(row["reference_target_id"], {})
        row["red_minus_white_log2fpkm"] = effect.get("red_minus_white_log2fpkm", "")
        row["direction"] = effect.get("direction", "unresolved")

    best = identity_rows[0] if identity_rows else None
    runner_up = identity_rows[1] if len(identity_rows) > 1 else None
    margin = (float(best["nongap_identity"]) - float(runner_up["nongap_identity"])) if best and runner_up else None
    if best and float(best["nongap_identity"]) >= 0.90 and float(best["query_coverage"]) >= 0.90 and (margin is None or margin >= 0.03):
        anchor_resolution = "one_reference_copy_is_ANR_source_lineage_like"
    elif best and float(best["nongap_identity"]) >= 0.75:
        anchor_resolution = "ANR_family_resolved_but_same_paralog_unresolved"
    else:
        anchor_resolution = "ANR_anchor_to_reference_mapping_unresolved"

    directions = {r.get("direction") for r in identity_rows if r.get("direction") not in (None, "", "unresolved")}
    summary = {
        "analysis_version": "v0.1-diagnostic",
        "anchor": {
            "source_id": anchor_id,
            "protein_accession": mapped[anchor_id].id,
            "protein_length_aa": len(anchor),
            "resolution": anchor_resolution,
            "best_reference_target": best["reference_target_id"] if best else None,
            "best_reference_protein": best["reference_protein_accession"] if best else None,
            "best_nongap_identity": float(best["nongap_identity"]) if best else None,
            "identity_margin_over_runner_up": margin,
        },
        "counts": {
            "requested_reference_copies": sum(r["role"] == "reference_copy" for r in targets),
            "recovered_reference_copies": len(ref_ids),
            "effect_rows_recovered": len(effects),
            "strict_crossspecies_exact_node_recurrence_clusters": 0,
        },
        "reference_copy_direction_heterogeneity": len(directions) > 1,
        "observed_reference_copy_directions": sorted(directions),
        "decision": "Compare the exact tea ANR source lineage with all reference-mapped K08695 copies before treating ANR-family recurrence as exact-node recurrence.",
        "claim_boundary": {
            "supported": [
                "sequence relationship between the exact tea ANR source anchor and tea reference copies",
                "directional heterogeneity among reference-mapped copies when effect rows are recovered",
            ],
            "not_supported": [
                "species-native C. reticulata ANR orthology",
                "strict cross-species exact-node recurrence",
                "duplication age, adaptation, or macroevolutionary enrichment",
            ],
        },
    }

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.out_dir / "source_protein_mapping.csv", mapping_rows, list(mapping_rows[0]))
    write_csv(args.out_dir / "anchor_to_reference_identity.csv", identity_rows, list(identity_rows[0]) if identity_rows else ["anchor_id"])
    write_csv(args.out_dir / "reference_copy_pairwise_identity.csv", pair_rows, list(pair_rows[0]) if pair_rows else ["target_id_1", "target_id_2"])
    if effects:
        write_csv(args.out_dir / "reference_copy_effects.csv", effects, list(effects[0]))
    records = [SeqRecord(Seq(str(rec.seq).rstrip("*")), id=tid.replace("gene-", ""), description=rec.id) for tid, rec in mapped.items()]
    SeqIO.write(records, args.out_dir / "anr_candidates.faa", "fasta")
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    doc = f"""# ANR reference-copy diagnostic\n\n## Current decision\n\nThe exact tea source locus `{anchor_id}` was compared against all five K08695/ANR tea-reference copies used by the *C. reticulata* mapping analysis.\n\n- Anchor resolution: `{anchor_resolution}`.\n- Best reference target: `{summary['anchor']['best_reference_target']}`.\n- Best non-gap protein identity: `{summary['anchor']['best_nongap_identity']}`.\n- Identity margin over the runner-up: `{summary['anchor']['identity_margin_over_runner_up']}`.\n- Recovered reference copies: `{summary['counts']['recovered_reference_copies']}/5`.\n- Recovered effect rows: `{summary['counts']['effect_rows_recovered']}/5`.\n- Reference-copy directional heterogeneity: `{summary['reference_copy_direction_heterogeneity']}`.\n\n## Claim boundary\n\nThe five `gene-LOC...` targets are tea-reference features used to map *C. reticulata* reads. They are not deposited species-native *C. reticulata* ANR loci. This diagnostic can resolve which tea reference copy is closest to `CSA011986` and whether mapped copies move in different directions, but strict cross-species exact-node recurrence remains zero until species-native sequences are recovered.\n"""
    (args.out_dir / "ANR_REFERENCE_COPY_DIAGNOSTIC.md").write_text(doc, encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
