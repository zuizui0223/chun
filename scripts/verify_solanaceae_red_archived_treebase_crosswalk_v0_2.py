#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import io
import json
import re
import ssl
import tempfile
import urllib.request
from collections import Counter
from pathlib import Path

from Bio import Phylo

ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "data/solanaceae_red_biochemical_resolution_profile_prereg_v0_1.json"
PREFLIGHT = ROOT / "scripts/preflight_solanaceae_red_biochemical_source_v0_3.py"

TREEBASE_STATIC_COMMIT = "7adf8ff09557dc1d368d4b8f8e7848c98da7ad93"
TREEBASE_STATIC_TREE_BLOB = "7d145c11d61b795d6939934368092fe12723529e"
TREEBASE_STATIC_FILE_ADD_COMMIT = "c83783faaa86566015d90c52bf06d67f62bfb2c8"
TREEBASE_STUDIES_COMMIT = "e08d03e4d6a945bd2fa3d927d93bd45a89a6bc77"
TREE_OBJECT = "tree_85881.phy"
TREE_LABEL = "MLT"
EXPECTED_TREE_TERMINALS = 1344
EXPECTED_SUPPLEMENT_SHA256 = "be5b7c75d52fef4714080938d638e31645ef5909c6b7a40ca1e8f2cadacebc2a"
UA = "Mozilla/5.0 CHUN-archived-treebase-crosswalk/0.2"


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def fetch(url: str, timeout: int = 120) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout, context=ssl.create_default_context()) as response:
        return response.read()


def normalize_source_species(name: str) -> str | None:
    text = re.sub(r"\s+", " ", name.strip().replace("×", "x"))
    m = re.match(r"^([A-Z][A-Za-z-]+)\s+([a-z][A-Za-z-]+)\b", text)
    return f"{m.group(1).lower()}_{m.group(2).lower()}" if m else None


def normalize_tree_tip(name: str) -> str | None:
    text = name.strip()
    if not text:
        return None
    parts = [p for p in text.split("_") if p]
    if len(parts) >= 2:
        return f"{parts[0].lower()}_{parts[1].lower()}"
    return normalize_source_species(text)


def normalize_full_tree_tip(name: str) -> str:
    return re.sub(r"[\s_]+", "_", name.strip()).lower()


def exact_crosswalk(source_names: list[str], tree_tips: list[str]) -> dict:
    source_pairs = [(name, normalize_source_species(name)) for name in source_names]
    tree_pairs = [(name, normalize_tree_tip(name)) for name in tree_tips]
    tree_by_norm: dict[str, list[str]] = {}
    for raw, norm in tree_pairs:
        if norm:
            tree_by_norm.setdefault(norm, []).append(raw)

    matches = []
    unmatched = []
    for raw, norm in source_pairs:
        if norm and len(tree_by_norm.get(norm, [])) == 1:
            matches.append({"source": raw, "normalized": norm, "tree_tip": tree_by_norm[norm][0]})
        else:
            unmatched.append(raw)
    return {
        "exact_match_count": len(matches),
        "exact_matches": matches,
        "source_unmatched": sorted(unmatched),
        "fuzzy_or_synonym_repair_used": False,
    }


def classify_gate(
    source_identity_supported: bool,
    archived_tree_object_count: int,
    terminal_count: int,
    duplicate_normalized_tips: int,
    nonroot_branches_missing_length: int,
    exact_match_count: int,
) -> str:
    if not source_identity_supported:
        return "HOLD_ARCHIVED_TREEBASE_SOURCE_IDENTITY_NOT_CORROBORATED"
    if archived_tree_object_count != 1:
        return "HOLD_ARCHIVED_TREEBASE_TREE_OBJECT_COUNT_NOT_ONE"
    if terminal_count <= 0 or duplicate_normalized_tips != 0 or nonroot_branches_missing_length != 0:
        return "HOLD_ARCHIVED_TREEBASE_TREE_INTEGRITY_GATE"
    if exact_match_count < 20:
        return "HOLD_ARCHIVED_TREEBASE_EXACT_CROSSWALK_BELOW_20"
    return "PASS_ARCHIVED_TREEBASE_S16617_OBJECT_CROSSWALK_FROZEN"


def stable_acquisition_summary(acquisition: dict) -> dict:
    for route in ("oa_package", "europe_pmc", "current_pmc_bin", "article_fallback"):
        info = acquisition.get(route)
        if not isinstance(info, dict) or not info.get("selected_method"):
            continue
        attempts = info.get("attempts", [])
        member_record = next(
            (
                record
                for record in reversed(attempts)
                if isinstance(record, dict)
                and record.get("sha256") == EXPECTED_SUPPLEMENT_SHA256
                and record.get("is_docx") is True
            ),
            None,
        )
        if member_record is None:
            raise RuntimeError("selected supplement route lacks the exact frozen DOCX member record")
        return {
            "route": route,
            "selected_method": info.get("selected_method"),
            "selected_url": info.get("selected_url") or info.get("selected_package_url"),
            "selected_member": info.get("selected_member") or member_record.get("member"),
            "member_bytes": member_record.get("bytes"),
            "member_sha256": member_record.get("sha256"),
        }
    raise RuntimeError("no stable selected supplement acquisition route")


def load_preflight_module():
    spec = importlib.util.spec_from_file_location("solanaceae_preflight_v03", PREFLIGHT)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load frozen Solanaceae source preflight")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    assert prereg["status"] == "FROZEN_BEFORE_SOLANACEAE_RED_TABLES1_ROW_LEVEL_OUTCOME_OPENING"
    assert prereg["source"]["treebase_study_id"] == "S16617"
    assert prereg["source"]["tree_parent_article_doi"] == "10.1111/nph.13576"
    assert prereg["source"]["row_level_trait_values_opened_for_this_profile_before_freeze"] is False

    static_study_url = (
        "https://raw.githubusercontent.com/bomeara/treebasestatic/"
        f"{TREEBASE_STATIC_COMMIT}/studies/study_16617.html"
    )
    static_tree_url = (
        "https://raw.githubusercontent.com/bomeara/treebasestatic/"
        f"{TREEBASE_STATIC_COMMIT}/trees/2016/{TREE_OBJECT}"
    )
    independent_study_url = (
        "https://raw.githubusercontent.com/rdmpage/treebase-studies/"
        f"{TREEBASE_STUDIES_COMMIT}/studies/S16617.xml"
    )

    study_html = fetch(static_study_url)
    tree_bytes = fetch(static_tree_url)
    independent_xml = fetch(independent_study_url)
    study_text = study_html.decode("utf-8", errors="replace")
    independent_text = independent_xml.decode("utf-8", errors="replace")

    tree_links = re.findall(r"\.\./trees/2016/(tree_\d+\.phy)", study_text)
    unique_tree_links = sorted(set(tree_links))
    static_identity = (
        "10.1111/nph.13576" in study_text
        and TREE_OBJECT in unique_tree_links
        and TREE_LABEL in study_text
        and "Species Tree" in study_text
        and str(EXPECTED_TREE_TERMINALS) in study_text
    )
    independent_identity = (
        "S16617" in independent_text
        and "10.1111/nph.13576" in independent_text
        and "Solanaceae" in independent_text
    )
    source_identity_supported = static_identity and independent_identity and unique_tree_links == [TREE_OBJECT]

    tree = Phylo.read(io.StringIO(tree_bytes.decode("utf-8")), "newick")
    terminals = [tip.name for tip in tree.get_terminals() if tip.name]
    full_norm_counts = Counter(normalize_full_tree_tip(x) for x in terminals)
    duplicate_normalized_tips = sum(n - 1 for n in full_norm_counts.values() if n > 1)
    all_clades = list(tree.find_clades(order="preorder"))
    nonroot = all_clades[1:]
    nonroot_missing = sum(clade.branch_length is None for clade in nonroot)

    preflight = load_preflight_module()
    with tempfile.TemporaryDirectory() as td:
        out_dir = Path(td)
        supplement_name = prereg["source"]["supplement_file"]
        docx, acquisition = preflight.v2.acquire_pmc_supplement(
            prereg["source"]["primary_pigment_pmcid"], supplement_name, out_dir
        )
        doc = preflight.inspect_docx_identifiers(docx, supplement_name)
    assert doc["docx_sha256"] == EXPECTED_SUPPLEMENT_SHA256
    assert doc["unique_normalized_species"] == 27
    stable_acquisition = stable_acquisition_summary(acquisition)

    source_names = [x.replace("_", " ").title() for x in doc["normalized_species"]]
    source_names = [" ".join([p.split()[0].capitalize(), p.split()[1].lower()]) for p in source_names]
    crosswalk = exact_crosswalk(source_names, terminals)

    status = classify_gate(
        source_identity_supported=source_identity_supported,
        archived_tree_object_count=len(unique_tree_links),
        terminal_count=len(terminals),
        duplicate_normalized_tips=duplicate_normalized_tips,
        nonroot_branches_missing_length=nonroot_missing,
        exact_match_count=crosswalk["exact_match_count"],
    )

    firewall = {key: False for key in [
        "pigment_values_emitted",
        "pigment_states_computed",
        "state_frequencies_computed",
        "patristic_distances_computed",
        "profile_auc_computed",
        "permutations_computed",
        "winner_class_computed",
    ]}
    receipt = {
        "version": "v0.2",
        "system": "SOLANACEAE_RED_27",
        "status": status,
        "treebase_study_id": "S16617",
        "tree_parent_article_doi": "10.1111/nph.13576",
        "source_recovery_class": "ARCHIVED_TREEBASE_SERIALIZATION_RECOVERY_NOT_SUBSTITUTE_TREE",
        "source_identity": {
            "supported": source_identity_supported,
            "treebasestatic_repository_commit": TREEBASE_STATIC_COMMIT,
            "treebasestatic_tree_blob": TREEBASE_STATIC_TREE_BLOB,
            "treebasestatic_file_add_commit": TREEBASE_STATIC_FILE_ADD_COMMIT,
            "independent_treebase_studies_commit": TREEBASE_STUDIES_COMMIT,
            "static_study_path": "studies/study_16617.html",
            "static_study_sha256": sha256_bytes(study_html),
            "independent_study_path": "studies/S16617.xml",
            "independent_study_sha256": sha256_bytes(independent_xml),
            "study_tree_links": unique_tree_links,
            "tree_label": TREE_LABEL,
            "substitute_tree_used": False,
        },
        "tree_object": {
            "filename": TREE_OBJECT,
            "sha256": sha256_bytes(tree_bytes),
            "terminal_count": len(terminals),
            "expected_terminal_count_from_archived_study": EXPECTED_TREE_TERMINALS,
            "duplicate_normalized_tips": duplicate_normalized_tips,
            "nonroot_branch_count": len(nonroot),
            "nonroot_branches_missing_length": nonroot_missing,
        },
        "trait_identifier_source": {
            "supplement": prereg["source"]["supplement_file"],
            "supplement_sha256": doc["docx_sha256"],
            "unique_species_identifiers": doc["unique_normalized_species"],
            "acquisition": stable_acquisition,
            "outcome_columns_emitted": False,
            "outcome_data_rows_emitted": False,
        },
        "crosswalk": crosswalk,
        "frozen_gate": {
            "minimum_exact_matches": 20,
            "exact_match_count": crosswalk["exact_match_count"],
            "automatic_synonym_or_fuzzy_repair_allowed": False,
        },
        "outcome_firewall": firewall,
        "profile_outcome_opened": False,
        "paper1_science_changed": False,
        "next_gate": (
            "After this source/tree crosswalk receipt is frozen on main, a separate outcome execution may open "
            "Table S1 pigment values and apply the already-preregistered common-frame/AUC/permutation estimator."
            if status.startswith("PASS_")
            else "Do not open Table S1 pigment outcomes."
        ),
    }

    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": status,
        "tree_terminal_count": len(terminals),
        "exact_match_count": crosswalk["exact_match_count"],
        "source_unmatched": crosswalk["source_unmatched"],
        "nonroot_branches_missing_length": nonroot_missing,
        "duplicate_normalized_tips": duplicate_normalized_tips,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
