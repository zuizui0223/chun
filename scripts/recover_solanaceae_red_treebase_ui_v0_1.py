#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import re
from pathlib import Path
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "data/solanaceae_red_biochemical_resolution_profile_prereg_v0_1.json"
PREFLIGHT = ROOT / "scripts/preflight_solanaceae_red_biochemical_source_v0_3.py"

spec = importlib.util.spec_from_file_location("solanaceae_preflight_v03", PREFLIGHT)
if spec is None or spec.loader is None:
    raise RuntimeError("could not load preflight v0.3")
pre = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pre)
base = pre.base


def fetch_text(url: str, timeout: int = 90) -> tuple[str, dict]:
    payload, final_url, content_type = base.fetch(url, timeout=timeout)
    return payload.decode("utf-8", errors="replace"), {
        "url": url,
        "final_url": final_url,
        "content_type": content_type,
        "bytes": len(payload),
        "sha256": base.sha256_bytes(payload),
    }


def extract_tree_ids(html: str) -> list[str]:
    hits: set[str] = set()
    for pat in (
        r"TB2:(Tr\d+)",
        r"(?:tree|treeid|treeId|id)[=/?:&\"']+(Tr\d+)",
        r"(?:tree|treeid|treeId)[=/?:&\"']+(\d+)",
    ):
        for x in re.findall(pat, html, flags=re.I):
            s = str(x)
            hits.add(s if s.lower().startswith("tr") else f"Tr{s}")
    return sorted(hits, key=lambda x: int(re.sub(r"\D", "", x) or 0))


def hrefs(html: str, base_url: str) -> list[str]:
    raw = re.findall(r"href=[\"']([^\"']+)[\"']", html, flags=re.I)
    return sorted({urljoin(base_url, h.replace("&amp;", "&")) for h in raw})


def retrieve_tree(tree_id: str) -> dict:
    urls = [
        f"https://purl.org/phylo/treebase/phylows/tree/TB2:{tree_id}?format=nexml",
        f"http://purl.org/phylo/treebase/phylows/tree/TB2:{tree_id}?format=nexml",
        f"https://www.treebase.org/treebase-web/phylows/tree/TB2:{tree_id}?format=nexml",
        f"https://treebase.org/treebase-web/phylows/tree/TB2:{tree_id}?format=nexml",
    ]
    attempts = []
    for url in urls:
        try:
            payload, final_url, content_type = base.fetch(url, timeout=120)
            rec = {
                "url": url,
                "final_url": final_url,
                "content_type": content_type,
                "bytes": len(payload),
                "sha256": base.sha256_bytes(payload),
            }
            try:
                info = base.parse_nexml(payload)
                rec["parsed_nexml"] = True
                rec["tree_count"] = info["tree_count"]
                attempts.append(rec)
                if info["tree_count"]:
                    return {
                        "tree_id": tree_id,
                        "payload_available": True,
                        "payload_sha256": base.sha256_bytes(payload),
                        "selected_url": url,
                        "selected_final_url": final_url,
                        "nexml": info,
                        "attempts": attempts,
                    }
            except Exception as exc:
                rec["parsed_nexml"] = False
                rec["parse_error"] = f"{type(exc).__name__}: {exc}"
                attempts.append(rec)
        except Exception as exc:
            attempts.append({"url": url, "error": f"{type(exc).__name__}: {exc}"})
    return {"tree_id": tree_id, "payload_available": False, "nexml": None, "attempts": attempts}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--receipt", type=Path, required=True)
    a = ap.parse_args()
    a.out_dir.mkdir(parents=True, exist_ok=True)

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    assert prereg["status"] == "FROZEN_BEFORE_SOLANACEAE_RED_TABLES1_ROW_LEVEL_OUTCOME_OPENING"
    assert prereg["source"]["treebase_study_id"] == "S16617"
    assert prereg["source"]["row_level_trait_values_opened_for_this_profile_before_freeze"] is False

    # Reacquire the same supplement, but inspect identifiers only.
    filename = prereg["source"]["supplement_file"]
    docx, pmc = pre.base.acquire_pmc_supplement(
        prereg["source"]["primary_pigment_pmcid"], filename, a.out_dir
    )
    doc = pre.inspect_docx_identifiers(docx, filename)
    trait_species = set(doc["normalized_species"])
    assert len(trait_species) == 27

    summary_urls = [
        "https://www.treebase.org/treebase-web/search/study/summary.html?id=16617",
        "https://treebase.org/treebase-web/search/study/summary.html?id=16617",
    ]
    tree_urls = [
        "https://www.treebase.org/treebase-web/search/study/trees.html?id=16617",
        "https://treebase.org/treebase-web/search/study/trees.html?id=16617",
    ]

    ui_attempts = []
    discovered_ids: set[str] = set()
    source_identity_supported = False
    for kind, urls in (("summary", summary_urls), ("trees", tree_urls)):
        for url in urls:
            try:
                html, meta = fetch_text(url, timeout=120)
                lower = html.lower()
                meta.update({
                    "kind": kind,
                    "contains_s16617": "s16617" in lower or "study 16617" in lower,
                    "contains_source_doi": "10.1111/nph.13576" in lower,
                    "contains_source_title_fragment": "widespread flower color convergence" in lower,
                })
                ids = extract_tree_ids(html)
                meta["tree_ids"] = ids
                meta["tree_related_hrefs"] = [h for h in hrefs(html, meta["final_url"]) if "tree" in h.lower()][:200]
                ui_attempts.append(meta)
                discovered_ids.update(ids)
                if meta["contains_source_doi"] or meta["contains_source_title_fragment"]:
                    source_identity_supported = True
            except Exception as exc:
                ui_attempts.append({"kind": kind, "url": url, "error": f"{type(exc).__name__}: {exc}"})

    individual = [retrieve_tree(tid) for tid in sorted(discovered_ids, key=lambda x: int(re.sub(r"\D", "", x) or 0))]
    candidates = []
    for obj in individual:
        if not obj["payload_available"]:
            continue
        for tr in obj["nexml"]["trees"]:
            tree_norm = {n for n in (base.norm_species(x) for x in tr["tip_labels"]) if n}
            exact = sorted(trait_species & tree_norm)
            candidates.append({
                "source_tree_object": obj["tree_id"],
                "tree_id": tr["tree_id"],
                "tree_label": tr["tree_label"],
                "tip_count": tr["tip_count"],
                "all_edges_have_length": tr["all_edges_have_length"],
                "normalized_tip_count": len(tree_norm),
                "trait_species_exact_matches": len(exact),
                "trait_species_unmatched": sorted(trait_species - tree_norm),
            })

    eligible = [c for c in candidates if c["all_edges_have_length"] and c["trait_species_exact_matches"] >= 20]
    if not source_identity_supported and not discovered_ids:
        status = "HOLD_TREEBASE_WEB_UI_STUDY_UNAVAILABLE"
    elif not discovered_ids:
        status = "HOLD_TREEBASE_WEB_UI_HAS_NO_DISCOVERABLE_TREE_OBJECT"
    elif len(eligible) == 1:
        status = "PASS_TREEBASE_UI_RECOVERED_SINGLE_ELIGIBLE_SOURCE_TREE"
    elif len(eligible) == 0:
        status = "HOLD_NO_RECOVERED_TREE_OBJECT_MEETS_FROZEN_GATE"
    else:
        status = "HOLD_MULTIPLE_RECOVERED_TREE_OBJECTS_MEET_FROZEN_GATE"

    firewall = {k: False for k in [
        "pigment_values_emitted", "pigment_states_computed", "state_frequencies_computed",
        "patristic_distances_computed", "profile_auc_computed", "permutations_computed",
        "winner_class_computed",
    ]}
    receipt = {
        "version": "v0.1",
        "system": "SOLANACEAE_RED_27",
        "study_id": "S16617",
        "status": status,
        "source_identity_supported_by_ui": source_identity_supported,
        "ui_attempts": ui_attempts,
        "discovered_tree_object_ids": sorted(discovered_ids),
        "recovered_tree_object_count": sum(x["payload_available"] for x in individual),
        "candidate_tree_count": len(candidates),
        "eligible_tree_count": len(eligible),
        "eligible_trees": eligible,
        "individual_tree_attempts": individual,
        "species_identifier_count": len(trait_species),
        "supplement_sha256": doc["docx_sha256"],
        "outcome_firewall": firewall,
        "substitute_tree_used": False,
        "profile_outcome_opened": False,
        "paper1_science_changed": False,
        "claim_boundary": "Source-faithful recovery only: TreeBASE S16617 Web UI and tree objects. No substitute phylogeny and no pigment/profile outcome is opened.",
    }
    a.receipt.parent.mkdir(parents=True, exist_ok=True)
    a.receipt.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": status,
        "source_identity_supported_by_ui": source_identity_supported,
        "discovered_tree_object_ids": receipt["discovered_tree_object_ids"],
        "recovered_tree_object_count": receipt["recovered_tree_object_count"],
        "eligible_tree_count": len(eligible),
        "outcome_firewall": firewall,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
