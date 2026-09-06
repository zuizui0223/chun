#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

PINNED_COMMIT = "0b33d5e992c39e191393bc0b86671c5c6a378e1e"
REQUIRED_MANIFEST = {
    "source_family", "role", "external_repo", "external_commit", "path",
    "blob_sha", "size_bytes", "taxon_unit", "scope", "event_use", "status", "notes",
}
EXPECTED_NETWORK_SHAS = {
    0: "7b9513df3229bdc70aaf37175baa8a30d5e28e50",
    1: "f4b982767cd8e9254d40144270ad7d0d4065a32e",
    2: "32b33ab5d65a66232b2208b7b6457d8a77384a95",
    3: "32b33ab5d65a66232b2208b7b6457d8a77384a95",
    4: "d000fc45f44231cf7847af1ec4a1a750f5365a8f",
    5: "d375ae2b734bf2ca073ccea68f0b0b3c5bb2fb3c",
}
EXPECTED_SOURCE_VALUES = {
    0: 1181.4389831867354,
    1: 724.4661130815608,
    2: 715.7344385409552,
    3: 646.2237158006756,
    4: 608.0150491452403,
    5: 576.157487931449,
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--likelihood-series", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    with a.manifest.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            raise SystemExit("manifest missing header")
        missing = REQUIRED_MANIFEST.difference(reader.fieldnames)
        if missing:
            raise SystemExit(f"manifest missing columns: {sorted(missing)}")
        rows = list(reader)

    if len(rows) != 11:
        raise SystemExit(f"expected 11 topology/network manifest rows, found {len(rows)}")
    if any(r["external_commit"] != PINNED_COMMIT for r in rows):
        raise SystemExit("external source commit drift")
    if any(r["external_repo"] != "pedrohpezzi/Petunia-Calibrachoa-Fabiana_TreeDiscordance" for r in rows):
        raise SystemExit("external repository drift")

    by_role = {r["role"]: r for r in rows}
    required_roles = {
        "COALESCENT_SPECIES_TREE", "COALESCENT_SITE_PATTERN_TREE",
        "SUPERMATRIX_INDIVIDUAL_TREE", "SPECIES_MAP", "NETWORK_LIKELIHOOD_SERIES",
        *(f"NETWORK_H{i}" for i in range(6)),
    }
    if set(by_role) != required_roles:
        raise SystemExit(f"role set drift: {sorted(set(by_role) ^ required_roles)}")

    astral = by_role["COALESCENT_SPECIES_TREE"]
    svdq = by_role["COALESCENT_SITE_PATTERN_TREE"]
    iq = by_role["SUPERMATRIX_INDIVIDUAL_TREE"]
    smap = by_role["SPECIES_MAP"]

    if astral["blob_sha"] != "04b4333e7a2e505e87dd321df1f4be88562ea4c4" or astral["taxon_unit"] != "SPECIES":
        raise SystemExit("ASTRAL species-tree contract drift")
    if svdq["blob_sha"] != "b0d30333b066db555ee456fbff140d1577bbb807" or svdq["taxon_unit"] != "SPECIES":
        raise SystemExit("SVDQuartets species-tree contract drift")
    if iq["blob_sha"] != "dbbe0ff0f352c6fc163f6c1a3117612bf0982984":
        raise SystemExit("IQ-TREE blob drift")
    if iq["taxon_unit"] != "INDIVIDUAL" or iq["status"] != "HOLD" or iq["event_use"] != "DIAGNOSTIC_ONLY_UNTIL_COLLAPSE":
        raise SystemExit("individual IQ-TREE must remain blocked for direct species-event mapping")
    if smap["blob_sha"] != "d924399feb2758e45f1641dd8f1f083b3725901e" or smap["scope"] != "19_SPECIES_NETWORK_SUBSET":
        raise SystemExit("SNaQ 19-species subset contract drift")

    for h, sha in EXPECTED_NETWORK_SHAS.items():
        r = by_role[f"NETWORK_H{h}"]
        if r["blob_sha"] != sha:
            raise SystemExit(f"SNaQ h={h} network SHA drift")
        if r["event_use"] != "NETWORK_FAMILY_SENSITIVITY" or r["status"] != "READY":
            raise SystemExit(f"SNaQ h={h} must remain in full sensitivity family")
    if by_role["NETWORK_H2"]["blob_sha"] != by_role["NETWORK_H3"]["blob_sha"]:
        raise SystemExit("pinned source diagnostic drift: net2 and net3 should be identical blobs")

    with a.likelihood_series.open(newline="", encoding="utf-8") as fh:
        lr = list(csv.DictReader(fh))
    if len(lr) != 6:
        raise SystemExit("SNaQ likelihood series must retain h=0..5")
    seen_h = set()
    for r in lr:
        h = int(r["hmax"])
        seen_h.add(h)
        if r["atlas_selection_status"] != "RETAIN_ALL":
            raise SystemExit(f"h={h}: trait-independent retain-all rule drift")
        if r["source_blob_sha"] != "3f9ced00bc8fcb11094e3db977d505a97eabcfa4":
            raise SystemExit(f"h={h}: likelihood source blob drift")
        if abs(float(r["source_value"]) - EXPECTED_SOURCE_VALUES[h]) > 1e-9:
            raise SystemExit(f"h={h}: source likelihood value drift")
    if seen_h != set(range(6)):
        raise SystemExit("SNaQ h series incomplete")

    summary = {
        "gate_version": "v0.2",
        "external_repo_commit": PINNED_COMMIT,
        "species_tree_sensitivities_ready": 2,
        "individual_supermatrix_tree_direct_event_use": "BLOCKED_PENDING_DETERMINISTIC_COLLAPSE",
        "snaq_network_subset_species": 19,
        "snaq_h_values_retained": list(range(6)),
        "snaq_net2_net3_identical_blob": True,
        "full_60_taxon_tree_ingested": False,
        "terminal_pigment_table_ingested": False,
        "event_remapping_gate": "READY_FOR_TERMINAL_STATE_INGESTION",
        "historical_recurrence_gate": "BLOCKED_PENDING_EVENT_REMAP",
        "paper1_science_changed": False,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
