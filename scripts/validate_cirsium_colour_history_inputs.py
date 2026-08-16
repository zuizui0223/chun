#!/usr/bin/env python3
"""Validate the published Cirsium colour-history scaffold.

This is deliberately a *pre-analysis* gate. It verifies that the topology,
visible-colour states, polymorphism flags, and divergence-time constraints are
internally consistent, then writes a readiness record. It must NOT fabricate a
Newick tree or equal branch lengths when the published machine-readable tree is
still unavailable.
"""

from __future__ import annotations

import argparse
import csv
import json
import pathlib


def rows(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--topology",
        type=pathlib.Path,
        default=pathlib.Path("data/cirsium_published_topology_constraints_v0_1.csv"),
    )
    parser.add_argument(
        "--states",
        type=pathlib.Path,
        default=pathlib.Path("data/cirsium_visible_colour_states_v0_1.csv"),
    )
    parser.add_argument(
        "--times",
        type=pathlib.Path,
        default=pathlib.Path("data/cirsium_divergence_time_constraints_v0_1.csv"),
    )
    parser.add_argument(
        "--out",
        type=pathlib.Path,
        default=pathlib.Path("build/cirsium_colour_history/readiness.json"),
    )
    args = parser.parse_args()

    topology = rows(args.topology)
    states = rows(args.states)
    times = rows(args.times)
    failures: list[str] = []

    top_ids = {r.get("constraint_id", "") for r in topology}
    required_top = {f"CIRTOP{i:03d}" for i in range(1, 10)}
    if top_ids != required_top:
        failures.append(
            f"topology constraint IDs changed: observed={sorted(top_ids)}, expected={sorted(required_top)}"
        )

    state_by_taxon = {r["taxon"]: r for r in states}
    expected_states = {
        "Cirsium brevicaule": "white",
        "Cirsium irumtiense": "bluish_purple",
        "Cirsium japonicum var. albescens": "white",
        "Cirsium japonicum var. takaoense": "polymorphic",
        "Cirsium japonicum var. australe": "bluish_purple",
        "Cirsium japonicum var. fukienense": "bluish_purple_to_pale_purple",
        "Cirsium japonicum var. japonicum": "unknown",
    }
    if set(state_by_taxon) != set(expected_states):
        failures.append(
            f"colour-state taxon set changed: observed={sorted(state_by_taxon)}, "
            f"expected={sorted(expected_states)}"
        )
    for taxon, expected in expected_states.items():
        if taxon not in state_by_taxon:
            continue
        observed = state_by_taxon[taxon].get("visible_colour_state", "")
        if observed != expected:
            failures.append(f"{taxon}: visible state {observed!r} != frozen {expected!r}")
        if state_by_taxon[taxon].get("pigment_chemistry_state", "") != "unknown":
            failures.append(
                f"{taxon}: visible-colour table must not silently assign pigment chemistry"
            )
        if state_by_taxon[taxon].get("anthocyanin_state", "") != "unknown":
            failures.append(
                f"{taxon}: visible-colour table must not silently assign anthocyanin state"
            )

    tak = state_by_taxon.get("Cirsium japonicum var. takaoense", {})
    if tak.get("polymorphism") != "yes":
        failures.append("var. takaoense must remain explicitly polymorphic")
    tak_states = {x for x in tak.get("within_taxon_states", "").split(";") if x}
    if tak_states != {"white", "bluish_purple"}:
        failures.append(f"var. takaoense morph states changed: {sorted(tak_states)}")
    if tak.get("transition_counting_status") != "do_not_collapse_to_one_state":
        failures.append("var. takaoense must not be collapsed to a one-state tip")

    time_ids = {r.get("time_id", "") for r in times}
    expected_time_ids = {f"CIRTIME{i:03d}" for i in range(1, 6)}
    if time_ids != expected_time_ids:
        failures.append(
            f"divergence-time IDs changed: observed={sorted(time_ids)}, expected={sorted(expected_time_ids)}"
        )
    if any(r.get("usable_as_exact_branch_length", "").lower() != "no" for r in times):
        failures.append(
            "published node-age constraints must not be promoted to exact branch lengths"
        )

    branch_lengths_ready = all(
        r.get("branch_length_status") not in {"", "unavailable_in_current_machine_readable_input"}
        for r in topology
        if r.get("topology_status", "").startswith("published_ASTRAL")
    )
    # The published tip labels use W/BP, but the current repository has not yet
    # frozen an authoritative sample/voucher mapping for every sequenced
    # takaoense individual.
    sample_morph_mapping_ready = False
    exact_tree_file_present = any(
        pathlib.Path(p).exists()
        for p in (
            "data/cirsium_published_tree.nwk",
            "data/cirsium_reproduced_nuclear_tree.nwk",
        )
    )

    readiness = {
        "schema_version": "0.1",
        "published_topology_constraints_pass": not failures,
        "visible_colour_states_pass": not failures,
        "divergence_time_constraints_pass": not failures,
        "exact_machine_readable_tree_present": exact_tree_file_present,
        "published_branch_lengths_ready": branch_lengths_ready,
        "takaoense_sample_morph_mapping_ready": sample_morph_mapping_ready,
        "ancestral_state_likelihood_admitted": bool(
            not failures
            and exact_tree_file_present
            and branch_lengths_ready
            and sample_morph_mapping_ready
        ),
        "claim_ceiling": (
            "published topology + visible-colour competing hypotheses only"
            if not exact_tree_file_present or not branch_lengths_ready or not sample_morph_mapping_ready
            else "branch-length-aware visible-colour ancestral-state analysis"
        ),
        "blocking_gates": [],
    }
    if not exact_tree_file_present:
        readiness["blocking_gates"].append("recover_or_reproduce_machine_readable_nuclear_tree")
    if not branch_lengths_ready:
        readiness["blocking_gates"].append("recover_branch_lengths_or_define_preregistered_sensitivity_ensemble")
    if not sample_morph_mapping_ready:
        readiness["blocking_gates"].append("freeze_takaoense_W_BP_sequence_sample_mapping")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(readiness, indent=2) + "\n", encoding="utf-8")

    if failures:
        print("Cirsium colour-history input gate FAILED:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(json.dumps(readiness, indent=2))
    print(
        "Input scaffold is internally consistent, but ancestral-state likelihood "
        "remains blocked until the real tree/branch lengths and W/BP sample mapping are frozen."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
