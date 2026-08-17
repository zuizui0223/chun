#!/usr/bin/env python3
"""Freeze an ANR reference-copy diagnostic into claim-safe v0.3 ledgers."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--diagnostic-dir", type=Path, required=True)
    parser.add_argument("--orthology-v02", type=Path, required=True)
    parser.add_argument("--score-v02", type=Path, required=True)
    parser.add_argument("--crosswalk-v02", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    summary = json.loads((args.diagnostic_dir / "summary.json").read_text(encoding="utf-8"))
    mapping, _ = read_csv(args.diagnostic_dir / "source_protein_mapping.csv")
    identities, _ = read_csv(args.diagnostic_dir / "anchor_to_reference_identity.csv")
    effects_path = args.diagnostic_dir / "reference_copy_effects.csv"
    effects, _ = read_csv(effects_path) if effects_path.exists() else ([], [])

    requested = int(summary["counts"]["requested_reference_copies"])
    recovered = int(summary["counts"]["recovered_reference_copies"])
    effect_n = int(summary["counts"]["effect_rows_recovered"])
    anchor = summary["anchor"]
    anchor_recovered = bool(anchor.get("protein_accession"))
    complete_sequence_screen = anchor_recovered and recovered == requested == 5
    anchored_clusters = 2 if complete_sequence_screen else (1 if anchor_recovered else 0)
    unresolved_clusters = 0 if complete_sequence_screen else 1
    resolution = anchor.get("resolution") or "unresolved"
    best_target = anchor.get("best_reference_target")
    best_identity = anchor.get("best_nongap_identity")
    margin = anchor.get("identity_margin_over_runner_up")
    heterogeneity = bool(summary.get("reference_copy_direction_heterogeneity"))

    effect_map = {r["target_id"]: r for r in effects}
    direction_text = ";".join(
        f"{r['reference_target_id']}={effect_map.get(r['reference_target_id'], {}).get('direction', 'unresolved')}"
        for r in identities
    )
    reference_accessions = ";".join(
        f"{r['target_id']}->{r['protein_accession']}"
        for r in mapping if r["role"] == "reference_copy" and r.get("protein_accession")
    )
    anchor_mapping = next((r for r in mapping if r["role"] == "anchor"), {})

    conservative = {
        "analysis_version": "v0.1",
        "family": "ANR",
        "family_recurrence_clusters": 2,
        "reference_lineage_anchored_clusters": anchored_clusters,
        "species_native_strict_node_clusters": 0,
        "strict_crossspecies_exact_recurrence_clusters": 0,
        "sequence_screen_complete": complete_sequence_screen,
        "effect_screen_complete": effect_n == 5,
        "source_anchor_resolution": resolution,
        "source_anchor_protein_accession": anchor.get("protein_accession"),
        "best_reference_target": best_target,
        "best_reference_identity": best_identity,
        "identity_margin_over_runner_up": margin,
        "reference_copy_direction_heterogeneity": heterogeneity,
        "observed_reference_copy_directions": summary.get("observed_reference_copy_directions", []),
        "decision": (
            "ANR family recurrence is sequence-resolved at the tea source and tea-reference-copy levels. "
            "The exact tea source lineage can be compared with all five mapped reference copies, but the "
            "C. reticulata cluster remains reference-lineage rather than species-native evidence."
            if complete_sequence_screen else
            "ANR family recurrence remains supported, but the reference-copy sequence screen is incomplete."
        ),
        "claim_boundary": {
            "supported": [
                "full-length relationship of the exact tea ANR source anchor to recovered tea reference copies",
                "reference-copy direction heterogeneity when all frozen effects are recovered",
                "family/module-level recurrence across two biological source clusters",
            ],
            "not_supported": [
                "species-native C. reticulata ANR orthology",
                "strict cross-species exact-node recurrence",
                "duplication age, adaptation, or macro-transition enrichment",
            ],
        },
    }

    orth, orth_fields = read_csv(args.orthology_v02)
    for row in orth:
        if row.get("feature") != "ANR":
            continue
        row.update({
            "family_recurrence_clusters": "2",
            "named_or_sequence_anchored_clusters": str(anchored_clusters),
            "strict_crossspecies_exact_recurrence_clusters": "0",
            "unresolved_or_family_only_clusters": str(unresolved_clusters),
            "recurrent_strict_node_labels": "",
            "orthology_statuses": "source_anchor_sequence_resolved;tea_reference_copy_set_resolved" if complete_sequence_screen else "source_anchor_sequence_resolved;reference_copy_screen_incomplete",
            "resolution_conclusion": (
                f"family recurrence demonstrated; the exact tea ANR source anchor maps as {resolution} with best target {best_target} "
                f"(identity={best_identity}, margin={margin}); C. reticulata evidence remains tea-reference-mapped"
            ),
            "claim_boundary": "use ANR family/module predictor first; reference-copy sequence resolution does not create a species-native cross-species exact node",
        })

    score, score_fields = read_csv(args.score_v02)
    for row in score:
        if row.get("feature") != "ANR":
            continue
        row.update({
            "anchored_clusters": str(anchored_clusters),
            "strict_crossspecies_recurrence_clusters": "0",
            "harmonized_rank_class": "B_family_recurrent_reference_copy_resolved" if complete_sequence_screen else "B_family_recurrent_orthology_unresolved",
            "macro_test_level": "ready_family_or_module_level_only",
            "primary_family_predictor": "2",
            "strict_node_predictor": "0",
            "claim_boundary": "source and mapped reference copies are sequence-resolved, but species-native C. reticulata exact-node recurrence remains zero",
        })

    cross, cross_fields = read_csv(args.crosswalk_v02)
    for row in cross:
        if row.get("feature") != "ANR":
            continue
        if row.get("independence_cluster") == "CSIN_WHITE_PINK":
            row.update({
                "sequence_accessions_or_named_anchor": f"{anchor_mapping.get('protein_accession', '')};CSA011986->TEA022960.1/CSS0005927.1",
                "source_resolution": "exact_TPIA2_source_anchor_plus_public_Longjing43_protein",
                "orthology_status": "source_anchor_sequence_resolved",
                "notes": f"exact tea ANR source anchor recovered as {anchor_mapping.get('protein_accession', '')}",
                "claim_boundary": "source ANR lineage is resolved within tea; cross-cluster species-native identity is not established",
            })
        elif row.get("independence_cluster") == "CRETICULATA":
            row.update({
                "sequence_accessions_or_named_anchor": reference_accessions,
                "source_resolution": "five_tea_reference_copies_sequence_resolved",
                "orthology_status": "reference_mapped_copy_set_resolved",
                "notes": f"best source-anchor target={best_target}; identity={best_identity}; margin={margin}; directions={direction_text}",
                "claim_boundary": "copy relationships and mapped expression directions are resolved in the tea reference; no species-native C. reticulata locus is claimed",
            })

    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "anr_conservative_summary_v0_1.json").write_text(json.dumps(conservative, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv(args.out_dir / "orthology_resolution_by_feature_v0_3.csv", orth, orth_fields)
    write_csv(args.out_dir / "micro_accessibility_node_score_harmonized_v0_3.csv", score, score_fields)
    write_csv(args.out_dir / "pigment_node_source_id_crosswalk_v0_3.csv", cross, cross_fields)

    result = f"""# ANR conservative resolution result\n\n## Decision\n\nANR recurrence is retained at the **family/module level** across two independent source clusters. The tea source anchor `{anchor.get('protein_accession')}` was compared with all five tea-reference copies used in the *C. reticulata* mapping analysis.\n\n- Source-anchor resolution: `{resolution}`.\n- Best mapped reference target: `{best_target}`.\n- Best non-gap protein identity: `{best_identity}`.\n- Margin over the runner-up: `{margin}`.\n- Reference-copy sequences recovered: `{recovered}/5`.\n- Frozen reference-copy effects recovered: `{effect_n}/5`.\n- Opposite reference-copy directions present: `{heterogeneity}`.\n\n## Authoritative ledger state\n\n- ANR family recurrence clusters: `2`.\n- Reference-lineage-anchored clusters: `{anchored_clusters}`.\n- Species-native strict-node clusters: `0`.\n- Strict cross-species exact recurrence: `0`.\n- Family/module predictor: `2`.\n- Strict-node predictor: `0`.\n\n## Interpretation\n\nThis analysis distinguishes reuse of the ANR biochemical family from reuse of one exact evolutionary node. The five `gene-LOC...` features are tea-reference targets used to map *C. reticulata* reads. Their sequence relationships and mapped expression directions can reveal copy/paralog-specific deployment, but they are not deposited species-native *C. reticulata* loci.\n\n## Claim boundary\n\nSupported: full-length source-anchor/reference-copy relationships, mapped reference-copy direction heterogeneity when recovered, and two-cluster ANR family recurrence.\n\nNot supported: species-native *C. reticulata* ANR orthology, strict exact-node recurrence, duplication age, adaptive selection, or macro-transition enrichment.\n"""
    (args.out_dir / "ANR_CONSERVATIVE_RESOLUTION_RESULT.md").write_text(result, encoding="utf-8")
    print(json.dumps(conservative, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
