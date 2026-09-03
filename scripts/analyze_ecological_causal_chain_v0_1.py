#!/usr/bin/env python3
"""Validate and summarize a branch-safe ecological causal chain for Camellia.

This audit does NOT reconstruct historical colour-transition causes.  It asks a
narrower mechanistic question that remains identifiable when individual macro
transition branches are unstable:

    flowering-window environment -> pollinator reliability
    latent floral sensory state -> pollinator choice
    pollinator service -> reproductive success

The first and third links are already frozen in the ecological-driver v2
registries.  The sensory link is tested with two independent published Camellia
behavioural studies, including Chen et al. 2020 (DOI 10.1093/jpe/rtaa023), which
was absent from the repository because Camellia is only a behavioural stimulus
inside a paper titled around Onosma.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def fnum(x: str | None) -> float | None:
    x = (x or "").strip()
    return None if x == "" else float(x)


def rr(num: str | None, den: str | None) -> float | None:
    a, b = fnum(num), fnum(den)
    if a is None or b is None or b <= 0:
        return None
    return a / b


def geometric_mean(values: list[float]) -> float:
    assert values and all(v > 0 for v in values)
    return math.exp(sum(math.log(v) for v in values) / len(values))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chain", type=Path, required=True)
    ap.add_argument("--studies", type=Path, required=True)
    ap.add_argument("--effects", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    chain = read_csv(args.chain)
    studies = read_csv(args.studies)
    effects = read_csv(args.effects)

    # Fail closed on duplicated identifiers.
    ids = [r["evidence_id"] for r in chain]
    assert len(ids) == len(set(ids)), "duplicate causal-chain evidence_id"
    study_by_id = {r["study_id"]: r for r in studies}
    effect_by_id = {r["effect_id"]: r for r in effects}
    assert len(study_by_id) == len(studies), "duplicate ecological study_id"
    assert len(effect_by_id) == len(effects), "duplicate ecological effect_id"

    # Every inherited reference must resolve against the frozen v2 registries.
    unresolved = []
    for row in chain:
        ref = row["existing_registry_ref"].strip()
        if ref.startswith("study:") and ref.split(":", 1)[1] not in study_by_id:
            unresolved.append((row["evidence_id"], ref))
        elif ref.startswith("effect:") and ref.split(":", 1)[1] not in effect_by_id:
            unresolved.append((row["evidence_id"], ref))
        elif ref not in {"new_peer_reviewed_source"} and not ref.startswith(("study:", "effect:")):
            unresolved.append((row["evidence_id"], ref))
    assert not unresolved, f"unresolved inherited references: {unresolved}"

    admitted = [r for r in chain if r["admission_status"] == "admit_primary" or r["admission_status"] == "admit_mediation"]
    by_link: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in admitted:
        by_link[row["link_class"]].append(row)

    required_links = {
        "environment_to_pollinator_reliability",
        "sensory_state_to_pollinator_choice",
        "pollinator_service_to_reproductive_success",
    }
    assert required_links == set(by_link), f"link set drift: {set(by_link)}"

    # Link 1: count independent studies/taxa rather than heterogeneous effect rows.
    env_rows = by_link["environment_to_pollinator_reliability"]
    env_studies = sorted({r["study_id"] for r in env_rows})
    env_taxa = sorted({r["taxon"] for r in env_rows})
    assert len(env_studies) == 5
    assert len(env_taxa) == 4

    # Link 2: two independent controlled/paired behavioural studies.
    sensory = by_link["sensory_state_to_pollinator_choice"]
    assert {r["study_id"] for r in sensory} == {"Mori2023", "Chen2020"}
    chen = next(r for r in sensory if r["study_id"] == "Chen2020")
    chen_uv_plus = fnum(chen["numerator"])
    chen_uv_minus = fnum(chen["denominator"])
    assert chen_uv_plus == 42 and chen_uv_minus == 15
    chen_total = int(chen_uv_plus + chen_uv_minus)
    chen_choice_fraction = chen_uv_plus / chen_total
    chen_descriptive_ratio = chen_uv_plus / chen_uv_minus
    chen_p = fnum(chen["reported_p"])
    assert chen_total == 57 and abs(chen_p - 0.013) < 1e-12

    mori = next(r for r in sensory if r["study_id"] == "Mori2023")
    mori_ratio = rr(mori["numerator"], mori["denominator"])
    assert mori_ratio is not None and mori_ratio > 20

    # Link 3: retain the frozen cross-species A/Y/W fruit-set magnitude set.
    service = by_link["pollinator_service_to_reproductive_success"]
    cross_ids = {
        "SERVICE_JAPONICA_2004",
        "SERVICE_PETELOTII_2017",
        "SERVICE_OLEIFERA_2024",
    }
    cross = [r for r in service if r["evidence_id"] in cross_ids]
    assert len(cross) == 3 and {r["visible_state"] for r in cross} == {"A", "Y", "W"}
    cross_rr = [rr(r["numerator"], r["denominator"]) for r in cross]
    assert all(v is not None for v in cross_rr)
    cross_rr_f = [float(v) for v in cross_rr if v is not None]
    gm_rr = geometric_mean(cross_rr_f)
    assert 3.52 < gm_rr < 3.54

    # Within C. oleifera service replication: bird and honeybee experiments.
    ole = [r for r in service if r["taxon"] == "Camellia oleifera"]
    assert {r["study_id"] for r in ole} == {"Zhang2024", "Liu2025"}
    ole_rr = [rr(r["numerator"], r["denominator"]) for r in ole]
    assert all(v is not None for v in ole_rr)
    ole_gm = geometric_mean([float(v) for v in ole_rr if v is not None])
    assert 2.41 < ole_gm < 2.43

    # Same-taxon bridge that does not require assigning a historical colour-change branch.
    links_by_taxon: dict[str, set[str]] = defaultdict(set)
    for row in admitted:
        # paired sensory row contains two taxa and is deliberately not split into a
        # pseudo-independent same-taxon bridge.
        if ";" not in row["taxon"]:
            links_by_taxon[row["taxon"]].add(row["link_class"])
    two_link_bridges = {
        taxon: sorted(links)
        for taxon, links in links_by_taxon.items()
        if len(links) >= 2
    }
    assert "Camellia petelotii" in two_link_bridges
    # We do NOT claim a full same-system 3-link chain.  That remains the next empirical gap.
    full_same_system = [taxon for taxon, links in links_by_taxon.items() if required_links.issubset(links)]
    assert not full_same_system

    summary = {
        "audit_version": "ecological-causal-chain-v0.1",
        "question": "Can pollinator-mediated ecological filtering be supported mechanistically without assigning causes to unstable historical colour-transition branches?",
        "environment_to_pollinator_reliability": {
            "k_independent_studies": len(env_studies),
            "k_taxa": len(env_taxa),
            "taxa": env_taxa,
            "status": "supported_as_repeated_flowering_window_mediation",
        },
        "sensory_state_to_pollinator_choice": {
            "k_independent_studies": len({r["study_id"] for r in sensory}),
            "mori_2023_same_human_red_visit_ratio": mori_ratio,
            "chen_2020_c_japonica_uv_plus_choices": int(chen_uv_plus),
            "chen_2020_c_japonica_uv_minus_choices": int(chen_uv_minus),
            "chen_2020_choice_fraction_uv_plus": chen_choice_fraction,
            "chen_2020_descriptive_uv_plus_to_uv_minus_ratio": chen_descriptive_ratio,
            "chen_2020_published_p": chen_p,
            "status": "supported_for_latent_spectral_state_not_coarse_human_hue",
            "ceiling": "behavioural choice, not lifetime fitness; Chen 2020 uses cultivated C. japonica varieties",
        },
        "pollinator_service_to_reproductive_success": {
            "cross_species_k": len(cross),
            "cross_species_visible_states": sorted({r["visible_state"] for r in cross}),
            "cross_species_geometric_mean_RR": gm_rr,
            "oleifera_independent_service_experiments": len(ole),
            "oleifera_bird_plus_bee_geometric_mean_RR": ole_gm,
            "status": "supported_quantitatively",
            "formal_inverse_variance_pooling": False,
        },
        "same_system_bridges": two_link_bridges,
        "full_three_link_same_system_chain": full_same_system,
        "hypothesis_updates": {
            "H6_pollinator_reliability_filter": "strengthened_to_mechanistic_support_not_macrohistorical_causation",
            "H8_latent_sensory_state_filtering": "strengthened_by_second_independent_Camellia_behavioural_experiment",
            "H10_flowering_window_selection": "supported_as_environment_to_service_mediation_not_direct_colour_cause",
            "H7_ecological_preadaptation_vs_genetic_permissivity": "unresolved",
        },
        "decision": {
            "best_supported_ecological_cause_layer": "context-dependent pollinator-mediated filtering of latent floral sensory/reward states",
            "upstream_modifier": "flowering-window weather/season/phenology",
            "rejected_as_general_explanation": "annual cold -> anthocyanin-like visible colour",
            "not_yet_identified": "a complete same-system sensory-state -> pollinator choice -> reproductive fitness chain tied to a robust historical flower-colour transition",
            "paper1_boundary": "This strengthens ecological mechanism/service interpretation but must not alter the frozen zero-shared-event branch-causation ceiling.",
        },
    }

    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    rows = []
    for link in sorted(by_link):
        studies_for_link = sorted({r["study_id"] for r in by_link[link]})
        rows.append({
            "link_class": link,
            "k_rows": len(by_link[link]),
            "k_independent_studies": len(studies_for_link),
            "studies": ";".join(studies_for_link),
        })
    out_csv = args.out_dir / "link_summary.csv"
    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["link_class", "k_rows", "k_independent_studies", "studies"])
        writer.writeheader()
        writer.writerows(rows)

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
