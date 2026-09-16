#!/usr/bin/env python3
from __future__ import annotations

import argparse
import collections
import hashlib
import importlib.util
import io
import json
import math
import re
import ssl
import tempfile
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import numpy as np
from Bio import Phylo
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "data/solanaceae_red_biochemical_resolution_profile_prereg_v0_1.json"
CROSSWALK = ROOT / "data/solanaceae_red_archived_treebase_crosswalk_v0_2.json"
PREFLIGHT = ROOT / "scripts/preflight_solanaceae_red_biochemical_source_v0_3.py"

SEED = 20260915
B = 9999
NAMES = ["coarse", "intermediate", "fine"]
EXPECTED_SUPPLEMENT_SHA256 = "be5b7c75d52fef4714080938d638e31645ef5909c6b7a40ca1e8f2cadacebc2a"
TREE_OBJECT = "tree_85881.phy"
TREEBASE_STATIC_COMMIT = "7adf8ff09557dc1d368d4b8f8e7848c98da7ad93"
UA = "Mozilla/5.0 CHUN-solanaceae-red-outcome/0.1"


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def fetch(url: str, timeout: int = 120) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout, context=ssl.create_default_context()) as response:
        return response.read()


def load_preflight_module():
    spec = importlib.util.spec_from_file_location("solanaceae_preflight_v03", PREFLIGHT)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load frozen Solanaceae source preflight")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def parse_numeric_proportion(value: object) -> float | None:
    text = str(value).strip()
    if not text or text.lower() in {"na", "n/a", "nan", "none", "null", ".", "-"}:
        return None
    if text.endswith("%"):
        text = text[:-1].strip()
    if not re.fullmatch(r"[+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", text):
        return None
    out = float(text)
    if not math.isfinite(out) or out < 0:
        return None
    return out


def parse_carotenoid_presence(value: object) -> bool | None:
    text = re.sub(r"\s+", " ", str(value).strip().lower())
    present = {"present", "yes", "y", "1", "+", "true"}
    absent = {"absent", "no", "n", "0", "-", "false"}
    if text in present:
        return True
    if text in absent:
        return False
    return None


def state_codes(*, pel: float, cya: float, dele: float, carotenoid: bool) -> dict[str, str]:
    p = pel > 0
    c = cya > 0
    d = dele > 0
    car = bool(carotenoid)
    if d:
        highest = "DELPHINIDIN"
    elif c:
        highest = "CYANIDIN"
    elif p:
        highest = "PELARGONIDIN"
    else:
        highest = "NONE"
    return {
        "coarse": f"A{int(p or c or d)}_C{int(car)}",
        "intermediate": f"C{int(car)}_H{highest}",
        "fine": f"C{int(car)}_P{int(p)}_C{int(c)}_D{int(d)}",
    }


def common_frame(raw_states: dict[str, dict[str, str]], minimum_fine_count: int = 5) -> tuple[list[str], list[str]]:
    fine_counts = collections.Counter(v["fine"] for v in raw_states.values())
    rare = sorted(state for state, count in fine_counts.items() if count < minimum_fine_count)
    rare_set = set(rare)
    retained = [name for name, states in raw_states.items() if states["fine"] not in rare_set]
    return retained, rare


def enc(states: list[str]) -> np.ndarray:
    mapping = {value: i for i, value in enumerate(sorted(set(states)))}
    return np.array([mapping[x] for x in states], dtype=np.int16)


def auc(states: np.ndarray, ii: np.ndarray, jj: np.ndarray, ranks: np.ndarray) -> float:
    same = states[ii] == states[jj]
    n1 = int(same.sum())
    n0 = len(same) - n1
    if n1 == 0 or n0 == 0:
        raise ValueError("AUC undefined: same-state pair response has one class")
    u = float(ranks[same].sum()) - n1 * (n1 + 1) / 2.0
    return u / (n1 * n0)


def upper(null: np.ndarray, observed: float) -> float:
    return (1.0 + float(np.count_nonzero(null >= observed))) / (len(null) + 1.0)


def classify_terminal(*, aucs: list[float] | np.ndarray, signal_p: list[float] | np.ndarray, winner_vs_runner_p: float) -> str:
    obs = np.asarray(aucs, dtype=float)
    ps = np.asarray(signal_p, dtype=float)
    sig = (obs > 0.5) & (ps <= 0.05)
    if not bool(sig.any()):
        return "PROFILE_NO_PHYLOGENETIC_SIGNAL"
    order = np.argsort(-obs, kind="stable")
    winner = int(order[0])
    runner = int(order[1])
    delta = float(obs[winner] - obs[runner])
    if bool(sig[winner]) and delta > 0 and winner_vs_runner_p <= 0.05:
        return {
            0: "PROFILE_SIGNALLED_COARSE",
            1: "PROFILE_SIGNALLED_INTERMEDIATE",
            2: "PROFILE_SIGNALLED_FINE",
        }[winner]
    return "PROFILE_SIGNALLED_TIED"


def normalize_header(text: str) -> str:
    text = text.lower().replace("′", "'").replace("–", "-").replace("—", "-")
    text = re.sub(r"[^a-z0-9%+\-']+", " ", text)
    return " ".join(text.split())


def header_rows_before_species_data(rows: list[list[str]], species_column_index: int) -> list[list[str]]:
    headers = []
    binomial = re.compile(r"^[A-Z][A-Za-z-]+\s+[a-z][A-Za-z-]+\b")
    for row in rows:
        cell = row[species_column_index].strip() if species_column_index < len(row) else ""
        if binomial.match(re.sub(r"\s+", " ", cell)):
            break
        headers.append(row)
    if not headers or len(headers) == len(rows):
        raise RuntimeError("could not delimit source header block before first species data row")
    return headers


def required_column_map(header_rows: list[list[str]], species_column_index: int) -> dict[str, int]:
    width = max((len(r) for r in header_rows), default=0)
    labels = []
    for ci in range(width):
        pieces = [normalize_header(row[ci]) for row in header_rows if ci < len(row) and row[ci].strip()]
        labels.append(" | ".join(dict.fromkeys(pieces)))

    def candidates(token: str) -> list[int]:
        return [i for i, label in enumerate(labels) if token in label]

    out = {"species": species_column_index}
    for key, token in [
        ("pelargonidin", "pelargonidin"),
        ("cyanidin", "cyanidin"),
        ("delphinidin", "delphinidin"),
        ("carotenoid", "carotenoid"),
    ]:
        hits = candidates(token)
        if len(hits) != 1:
            raise RuntimeError(f"required source column {key!r} is not unique; hits={hits}; labels={labels}")
        out[key] = hits[0]
    if len(set(out.values())) != len(out):
        raise RuntimeError(f"required source columns collide: {out}; labels={labels}")
    return out


def combined_header_labels(header_rows: list[list[str]], width: int) -> list[str]:
    labels = []
    for ci in range(width):
        pieces = [row[ci].strip() for row in header_rows if ci < len(row) and row[ci].strip()]
        labels.append(" | ".join(dict.fromkeys(pieces)))
    return labels


def docx_table_rows(docx_bytes: bytes, table_index: int) -> list[list[str]]:
    with zipfile.ZipFile(io.BytesIO(docx_bytes)) as zf:
        root = ET.fromstring(zf.read("word/document.xml"))
    preflight = load_preflight_module()
    local_name = preflight.base.local_name
    text_content = preflight.base.text_content
    tables = [x for x in root.iter() if local_name(x.tag) == "tbl"]
    if table_index >= len(tables):
        raise RuntimeError(f"selected table index {table_index} outside DOCX table count {len(tables)}")
    trs = [x for x in list(tables[table_index]) if local_name(x.tag) == "tr"]
    return [[text_content(tc) for tc in list(tr) if local_name(tc.tag) == "tc"] for tr in trs]


def stable_acquisition_summary(acquisition: dict) -> dict:
    for route_key in ["oa_package", "europe_pmc", "current_pmc_bin", "article_fallback"]:
        route = acquisition.get(route_key)
        if not isinstance(route, dict) or not route.get("selected_method"):
            continue
        return {
            "route": route_key,
            "selected_method": route.get("selected_method"),
            "selected_member": route.get("selected_member"),
            "selected_url": route.get("selected_url") or route.get("selected_package_url") or route.get("selected_final_url"),
        }
    return {"route": "unknown", "selected_method": None, "selected_member": None, "selected_url": None}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    cross = json.loads(CROSSWALK.read_text(encoding="utf-8"))
    if prereg["status"] != "FROZEN_BEFORE_SOLANACEAE_RED_TABLES1_ROW_LEVEL_OUTCOME_OPENING":
        raise ValueError("prereg status drift")
    if prereg["primary_statistic"]["permutations"] != B or prereg["primary_statistic"]["seed"] != SEED:
        raise ValueError("permutation contract drift")
    if cross["status"] != "PASS_ARCHIVED_TREEBASE_S16617_OBJECT_CROSSWALK_FROZEN":
        raise ValueError("frozen crosswalk receipt not PASS")
    if cross["tree_object"]["filename"] != TREE_OBJECT or cross["frozen_gate"]["exact_match_count"] < 20:
        raise ValueError("frozen tree/crosswalk contract drift")
    if cross["crosswalk"]["fuzzy_or_synonym_repair_used"] is not False:
        raise ValueError("fuzzy/synonym repair appeared after freeze")

    preflight = load_preflight_module()
    with tempfile.TemporaryDirectory() as td:
        docx_bytes, acquisition = preflight.v2.acquire_pmc_supplement(
            prereg["source"]["primary_pigment_pmcid"],
            prereg["source"]["supplement_file"],
            Path(td),
        )
    if sha256_bytes(docx_bytes) != EXPECTED_SUPPLEMENT_SHA256:
        raise ValueError("frozen supplement SHA256 mismatch")
    identifiers = preflight.inspect_docx_identifiers(docx_bytes, prereg["source"]["supplement_file"])
    if identifiers["unique_normalized_species"] != 27:
        raise ValueError("source species universe drift")

    rows = docx_table_rows(docx_bytes, identifiers["selected_table_index"])
    species_ci = int(identifiers["selected_species_column_index"])
    header_rows = header_rows_before_species_data(rows, species_ci)
    cols = required_column_map(header_rows, species_ci)
    header_labels = combined_header_labels(header_rows, max(len(r) for r in header_rows))
    base = preflight.base

    row_by_species: dict[str, list[str]] = {}
    duplicate_species = []
    for row in rows[len(header_rows):]:
        if species_ci >= len(row):
            continue
        norm = base.norm_species(row[species_ci])
        if not norm:
            continue
        if norm in row_by_species:
            duplicate_species.append(norm)
        row_by_species[norm] = row
    if duplicate_species:
        raise RuntimeError(f"duplicate source species rows after normalization: {sorted(set(duplicate_species))}")

    raw_states: dict[str, dict[str, str]] = {}
    ineligible = []
    missing_rows = []
    for item in cross["crosswalk"]["exact_matches"]:
        norm = item["normalized"]
        tree_tip = item["tree_tip"]
        row = row_by_species.get(norm)
        if row is None:
            missing_rows.append(norm)
            continue
        values = {key: (row[cols[key]] if cols[key] < len(row) else "") for key in ["pelargonidin", "cyanidin", "delphinidin", "carotenoid"]}
        pel = parse_numeric_proportion(values["pelargonidin"])
        cya = parse_numeric_proportion(values["cyanidin"])
        dele = parse_numeric_proportion(values["delphinidin"])
        car = parse_carotenoid_presence(values["carotenoid"])
        if pel is None or cya is None or dele is None or car is None:
            ineligible.append({
                "normalized": norm,
                "tree_tip": tree_tip,
                "unresolved_fields": [name for name, val in [("pelargonidin", pel), ("cyanidin", cya), ("delphinidin", dele), ("carotenoid", car)] if val is None],
                "carotenoid_token_if_unresolved": values["carotenoid"] if car is None else None,
            })
            continue
        raw_states[tree_tip] = state_codes(pel=pel, cya=cya, dele=dele, carotenoid=car)

    if missing_rows:
        raise RuntimeError(f"frozen exact crosswalk species missing from source table: {missing_rows}")

    retained, rare = common_frame(raw_states, minimum_fine_count=5)
    states = {name: [raw_states[tip][name] for tip in retained] for name in NAMES}
    hold_reasons = []
    if len(retained) < int(prereg["primary_frame"]["minimum_retained_tips"]):
        hold_reasons.append("COMMON_TIPS_LT_20")
    for name in NAMES:
        if len(set(states[name])) < int(prereg["primary_frame"]["minimum_states_per_resolution"]):
            hold_reasons.append(f"{name.upper()}_STATES_LT_2")

    tree_url = "https://raw.githubusercontent.com/bomeara/treebasestatic/" + f"{TREEBASE_STATIC_COMMIT}/trees/2016/{TREE_OBJECT}"
    tree_bytes = fetch(tree_url)
    if sha256_bytes(tree_bytes) != cross["tree_object"]["sha256"]:
        raise ValueError("frozen TreeBASE tree SHA256 mismatch")
    tree = Phylo.read(io.StringIO(tree_bytes.decode("utf-8")), "newick")
    terminals = {tip.name: tip for tip in tree.get_terminals() if tip.name}
    if any(tip not in terminals for tip in retained):
        raise RuntimeError("retained frozen tree tip absent from recovered S16617 tree")

    base_result = {
        "version": "v0.1",
        "status": "SOLANACEAE_RED_BIOCHEMICAL_RESOLUTION_PROFILE_RESULT",
        "programme_role": prereg["programme_role"],
        "prospective_label": prereg["prospective_label"],
        "do_not_count_as_new_prospective_replication": True,
        "source": {
            "supplement_sha256": EXPECTED_SUPPLEMENT_SHA256,
            "supplement_acquisition": stable_acquisition_summary(acquisition),
            "treebase_study_id": cross["treebase_study_id"],
            "tree_object": TREE_OBJECT,
            "tree_sha256": cross["tree_object"]["sha256"],
            "crosswalk_status": cross["status"],
            "crosswalk_exact_matches": cross["frozen_gate"]["exact_match_count"],
            "source_unmatched_before_outcome": cross["crosswalk"]["source_unmatched"],
        },
        "schema": {
            "selected_table_index": identifiers["selected_table_index"],
            "header_row_count": len(header_rows),
            "required_column_indices": cols,
            "required_column_labels": {key: header_labels[ci] for key, ci in cols.items()},
        },
        "primary_frame": {
            "crosswalk_matched_tips": cross["frozen_gate"]["exact_match_count"],
            "eligible_before_rare_filter": len(raw_states),
            "ineligible_after_outcome_opening": ineligible,
            "rare_fine_states_excluded": rare,
            "eligible_tips": len(retained),
            "coarse_state_counts": dict(sorted(collections.Counter(states["coarse"]).items())),
            "intermediate_state_counts": dict(sorted(collections.Counter(states["intermediate"]).items())),
            "fine_state_counts": dict(sorted(collections.Counter(states["fine"]).items())),
        },
        "seed": SEED,
        "permutations": B,
        "post_hoc_rescue_allowed": False,
        "paper1_science_changed": False,
    }

    if hold_reasons:
        out = {
            **base_result,
            "terminal_class": "HOLD_INSUFFICIENT_COMMON_FRAME_OR_STATE_VARIATION",
            "hold_reasons": hold_reasons,
            "resolution_profile_AUC_computed": False,
            "winner_computed": False,
        }
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({"terminal_class": out["terminal_class"], "eligible_tips": len(retained), "hold_reasons": hold_reasons}, indent=2))
        return 0

    n = len(retained)
    ii, jj = np.triu_indices(n, 1)
    dist = np.array([tree.distance(terminals[retained[int(i)]], terminals[retained[int(j)]]) for i, j in zip(ii, jj)], dtype=float)
    ranks = rankdata(-dist, method="average")
    encs = {name: enc(states[name]) for name in NAMES}
    observed = np.array([auc(encs[name], ii, jj, ranks) for name in NAMES], dtype=float)

    null = np.empty((3, B), dtype=float)
    rng = np.random.default_rng(SEED)
    base_idx = np.arange(n)
    for b in range(B):
        perm = rng.permutation(base_idx)
        for q, name in enumerate(NAMES):
            null[q, b] = auc(encs[name][perm], ii, jj, ranks)
    signal_p = np.array([upper(null[q], observed[q]) for q in range(3)], dtype=float)
    order = np.argsort(-observed, kind="stable")
    winner = int(order[0])
    runner = int(order[1])
    delta = float(observed[winner] - observed[runner])
    pwin = upper(null[winner] - null[runner], delta)
    terminal = classify_terminal(aucs=observed, signal_p=signal_p, winner_vs_runner_p=pwin)

    pairwise = {}
    for x in range(3):
        for y in range(x + 1, 3):
            d = float(observed[x] - observed[y])
            pairwise[f"{NAMES[x]}_minus_{NAMES[y]}"] = {"observed": d, "p_gt_zero": upper(null[x] - null[y], d)}
            pairwise[f"{NAMES[y]}_minus_{NAMES[x]}"] = {"observed": -d, "p_gt_zero": upper(null[y] - null[x], -d)}

    out = {
        **base_result,
        "terminal_class": terminal,
        "resolution_profile_AUC_computed": True,
        "winner_computed": True,
        "observed": dict(zip([f"AUC_{name}" for name in NAMES], [float(x) for x in observed])),
        "p_signal_one_sided": dict(zip(NAMES, [float(x) for x in signal_p])),
        "winner": NAMES[winner],
        "runner_up": NAMES[runner],
        "winner_minus_runner_up": delta,
        "p_winner_gt_runner": pwin,
        "pairwise_differences": pairwise,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "terminal_class": terminal,
        "eligible_tips": n,
        "AUC": dict(zip(NAMES, observed.tolist())),
        "p_signal": dict(zip(NAMES, signal_p.tolist())),
        "winner": NAMES[winner],
        "p_winner_gt_runner": pwin,
        "rare_fine_states_excluded": rare,
        "ineligible_count": len(ineligible),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
