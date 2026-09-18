#!/usr/bin/env python3
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import io
import json
import math
import re
import shutil
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
from Bio import Phylo
from scipy.stats import wilcoxon

CSV_SHA = "a253308785e4cbd0e361b3ca04cdfdae29c523eefa843375cebf8030ee0874af"
TREES_SHA = "ae5c82945e5bf9c29bcabc52d6029acd8d4f5be1fe9141fad95918eacb4f674d"
DOI_ENC = "doi%3A10.5061%2Fdryad.r4xgxd2sc"
FILE_IDS = {"final_dataset.csv": 4411881, "trees.zip": 4411880}
MAP = {
    "black": ("DARK", "NONWHITE"),
    "purple": ("COOL", "NONWHITE"),
    "green": ("COOL", "NONWHITE"),
    "orange": ("WARM", "NONWHITE"),
    "pink": ("WARM", "NONWHITE"),
    "red": ("WARM", "NONWHITE"),
    "white": ("WHITE", "WHITE"),
    "yellow": ("WARM", "NONWHITE"),
}
RESOLUTIONS = ("coarse", "intermediate", "fine")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def norm_tip(x: str) -> str:
    return re.sub(r"\s+", " ", str(x).strip().replace("_", " ")).lower()


def pair_same_baseline(states: np.ndarray) -> float:
    """Probability that a uniformly sampled unordered pair shares state."""
    n = len(states)
    if n < 2:
        return float("nan")
    counts = collections.Counter(states.tolist())
    same_pairs = sum(v * (v - 1) // 2 for v in counts.values())
    total_pairs = n * (n - 1) // 2
    return same_pairs / total_pairs


def persistence_curve(
    distances: np.ndarray,
    ii: np.ndarray,
    jj: np.ndarray,
    states: np.ndarray,
    n_bins: int = 10,
) -> dict:
    """Equal-pair-count binned same-state retention over relative patristic distance.

    Excess retention is standardized against the exact without-replacement
    same-state probability implied by the observed state frequencies.
    """
    distances = np.asarray(distances, dtype=float)
    states = np.asarray(states, dtype=object)
    same = states[ii] == states[jj]
    baseline = pair_same_baseline(states)
    if not np.isfinite(distances).all() or len(distances) == 0:
        raise ValueError("distances must be non-empty and finite")
    # The caller supplies the axis. For the production analysis this is
    # relative divergence depth = patristic distance / (2 * crown height).
    rel = distances
    order = np.argsort(rel, kind="stable")
    groups = np.array_split(order, min(n_bins, len(order)))
    bins = []
    denom = 1.0 - baseline
    for b, idx in enumerate(groups):
        if len(idx) == 0:
            continue
        p_same = float(np.mean(same[idx]))
        excess = (p_same - baseline) / denom if denom > 0 else float("nan")
        bins.append(
            {
                "bin": b + 1,
                "n_pairs": int(len(idx)),
                "mean_distance": float(np.mean(rel[idx])),
                "min_distance": float(np.min(rel[idx])),
                "max_distance": float(np.max(rel[idx])),
                "p_same": p_same,
                "excess_retention": excess,
            }
        )
    x = np.array([b["mean_distance"] for b in bins], dtype=float)
    y = np.array([b["excess_retention"] for b in bins], dtype=float)
    ok = np.isfinite(y)
    if ok.sum() >= 2:
        slope = float(np.polyfit(x[ok], y[ok], 1)[0])
        area = float(np.trapezoid(y[ok], x[ok]))
    else:
        slope = float("nan")
        area = float("nan")
    near_far = (
        float(bins[0]["excess_retention"] - bins[-1]["excess_retention"])
        if bins and np.isfinite(bins[0]["excess_retention"]) and np.isfinite(bins[-1]["excess_retention"])
        else float("nan")
    )
    return {
        "baseline_same_probability": baseline,
        "bins": bins,
        "linear_decay_slope": slope,
        "signed_excess_area": area,
        "near_far_contrast": near_far,
    }


def root_to_tip_cv(tree) -> float:
    vals = np.array([tree.distance(tree.root, tip) for tip in tree.get_terminals()], dtype=float)
    m = float(np.mean(vals))
    return float(np.std(vals, ddof=0) / m) if m > 0 else float("nan")


def relative_divergence_time(tree, pairwise_patristic: np.ndarray, ultrametric_cv_max: float = 1e-8) -> np.ndarray:
    """Express pairwise divergence as a fraction of the source-tree crown depth.

    On an ultrametric tree, patristic distance between two tips is twice their
    divergence age from the present. Dividing by 2 * crown height therefore
    yields relative divergence depth in [0, 1]. This is not an absolute-time
    calibration and must not be reported in Ma.
    """
    cv = root_to_tip_cv(tree)
    if not np.isfinite(cv) or cv > ultrametric_cv_max:
        raise ValueError(f"source tree is not sufficiently ultrametric: root-to-tip CV={cv}")
    heights = np.array([tree.distance(tree.root, tip) for tip in tree.get_terminals()], dtype=float)
    crown_height = float(np.mean(heights))
    if crown_height <= 0:
        raise ValueError("non-positive crown height")
    rel = np.asarray(pairwise_patristic, dtype=float) / (2.0 * crown_height)
    if np.nanmax(rel) > 1.0 + 1e-8 or np.nanmin(rel) < -1e-12:
        raise ValueError("relative divergence depth outside [0,1]")
    return rel


def fine_only_eligibility(colors, minimum_tips: int = 20, minimum_fine_states: int = 2) -> tuple[bool, list[str]]:
    """Eligibility for the flower-colour persistence analysis only.

    Unlike the three-resolution comparison, this frame does not require
    coarse or intermediate variation.
    """
    reasons = []
    if len(colors) < minimum_tips:
        reasons.append("COMMON_TIPS_LT_20")
    if len(set(colors)) < minimum_fine_states:
        reasons.append("FINE_STATES_LT_2")
    return (not reasons), reasons


def one_sample_direction_summary(values, favorable: str) -> dict:
    x = np.asarray(values, dtype=float)
    x = x[np.isfinite(x)]
    if favorable == "negative":
        alt = "less"
        n_favorable = int(np.sum(x < 0))
    elif favorable == "positive":
        alt = "greater"
        n_favorable = int(np.sum(x > 0))
    else:
        raise ValueError(favorable)
    w = wilcoxon(x, alternative=alt, zero_method="wilcox")
    return {
        "n": int(len(x)),
        "median": float(np.median(x)),
        "favorable_count": n_favorable,
        "wilcoxon_p_one_sided": float(w.pvalue),
    }


def _download(url: str, dest: Path) -> dict:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 CHUN-distance-persistence/0.1",
            "Accept": "*/*",
            "Referer": "https://datadryad.org/dataset/doi:10.5061/dryad.r4xgxd2sc",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as r, dest.open("wb") as f:
            shutil.copyfileobj(r, f)
        return {"url": url, "ok": True, "bytes": dest.stat().st_size}
    except Exception as e:
        if dest.exists():
            dest.unlink()
        return {"url": url, "ok": False, "error": f"{type(e).__name__}: {e}"}


def recover_exact_sources(work: Path) -> tuple[Path | None, Path | None, list[dict]]:
    work.mkdir(parents=True, exist_ok=True)
    diagnostics: list[dict] = []
    expected = {"final_dataset.csv": CSV_SHA, "trees.zip": TREES_SHA}

    # Current documented API route. It may require authentication; record rather
    # than conceal that boundary.
    for name, fid in FILE_IDS.items():
        dest = work / name
        for url in (
            f"https://datadryad.org/api/v2/files/{fid}/download",
            f"https://datadryad.org/stash/downloads/file_stream/{fid}",
        ):
            d = _download(url, dest)
            if d["ok"]:
                d["sha256"] = sha256_file(dest)
                d["digest_match"] = d["sha256"] == expected[name]
            diagnostics.append({"file": name, **d})
            if d.get("digest_match"):
                break
            if dest.exists():
                dest.unlink()

    csv_path = work / "final_dataset.csv"
    tree_path = work / "trees.zip"
    if csv_path.exists() and tree_path.exists():
        return csv_path, tree_path, diagnostics

    # Also probe the complete-dataset archive route.
    bundle = work / "dataset.zip"
    d = _download(f"https://datadryad.org/api/v2/datasets/{DOI_ENC}/download", bundle)
    diagnostics.append({"file": "dataset.zip", **d})
    if d["ok"]:
        try:
            with zipfile.ZipFile(bundle) as z:
                names = {Path(n).name: n for n in z.namelist()}
                for name in expected:
                    if name in names:
                        (work / name).write_bytes(z.read(names[name]))
            for name, digest in expected.items():
                p = work / name
                diagnostics.append(
                    {
                        "file": name,
                        "url": "dataset.zip member",
                        "ok": p.exists(),
                        "bytes": p.stat().st_size if p.exists() else None,
                        "sha256": sha256_file(p) if p.exists() else None,
                        "digest_match": p.exists() and sha256_file(p) == digest,
                    }
                )
        except Exception as e:
            diagnostics.append({"file": "dataset.zip", "ok": False, "error": f"extract: {type(e).__name__}: {e}"})
    if bundle.exists():
        bundle.unlink()

    if csv_path.exists() and sha256_file(csv_path) != CSV_SHA:
        csv_path.unlink()
    if tree_path.exists() and sha256_file(tree_path) != TREES_SHA:
        tree_path.unlink()
    return (csv_path if csv_path.exists() else None, tree_path if tree_path.exists() else None, diagnostics)


def build_states(fine_states: np.ndarray) -> dict[str, np.ndarray]:
    return {
        "fine": fine_states,
        "intermediate": np.array([MAP[x][0] for x in fine_states], dtype=object),
        "coarse": np.array([MAP[x][1] for x in fine_states], dtype=object),
    }


def analyse(csv_path: Path, trees_path: Path, outdir: Path, n_bins: int = 10) -> dict:
    rows_by_clade: dict[str, list[tuple[str, str]]] = collections.defaultdict(list)
    with csv_path.open(newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            rows_by_clade[r["clade"].strip()].append((r["species"].strip(), r["flower_color"].strip()))

    z = zipfile.ZipFile(trees_path)
    members = {
        Path(m).stem.lower(): m
        for m in z.namelist()
        if not m.endswith("/") and not m.startswith("__MACOSX/") and not m.endswith(".DS_Store")
    }

    details = {}
    curve_rows = []
    for clade in sorted(rows_by_clade):
        vals = rows_by_clade[clade]
        counts = collections.Counter(color for _, color in vals)
        unknown = set(counts) - set(MAP)
        if unknown:
            raise ValueError(f"{clade}: unknown source color tokens {sorted(unknown)}")
        rare = {k for k, v in counts.items() if v < 5}
        retained = [(sp, color) for sp, color in vals if color not in rare]
        fine_raw = [color for _, color in retained]
        interm_raw = [MAP[x][0] for x in fine_raw]
        coarse_raw = [MAP[x][1] for x in fine_raw]
        reasons = []
        if len(retained) < 20:
            reasons.append("COMMON_TIPS_LT_20")
        if len(set(fine_raw)) < 2:
            reasons.append("FINE_STATES_LT_2")
        if len(set(interm_raw)) < 2:
            reasons.append("INTERMEDIATE_STATES_LT_2")
        if len(set(coarse_raw)) < 2:
            reasons.append("COARSE_STATES_LT_2")
        if reasons:
            details[clade] = {"status": "HOLD_COMMON_FRAME", "reasons": reasons, "eligible_tips": len(retained)}
            continue

        tree = Phylo.read(io.StringIO(z.read(members[clade.lower()]).decode("utf-8-sig")), "newick")
        by_tip = {norm_tip(sp): color for sp, color in retained}
        tips = [t for t in tree.get_terminals() if norm_tip(t.name) in by_tip]
        fine_states = np.array([by_tip[norm_tip(t.name)] for t in tips], dtype=object)
        states = build_states(fine_states)
        n = len(tips)
        ii, jj = np.triu_indices(n, 1)
        dist = np.array([tree.distance(tips[int(a)], tips[int(b)]) for a, b in zip(ii, jj)], dtype=float)
        rel_time = relative_divergence_time(tree, dist)

        per_resolution = {}
        for res in RESOLUTIONS:
            curve = persistence_curve(rel_time, ii, jj, states[res], n_bins=n_bins)
            per_resolution[res] = curve
            for b in curve["bins"]:
                curve_rows.append(
                    [
                        clade,
                        res,
                        n,
                        b["bin"],
                        b["n_pairs"],
                        b["mean_distance"],
                        b["p_same"],
                        curve["baseline_same_probability"],
                        b["excess_retention"],
                    ]
                )
        area = {r: per_resolution[r]["signed_excess_area"] for r in RESOLUTIONS}
        winner = max(area, key=lambda r: (-math.inf if not np.isfinite(area[r]) else area[r]))
        details[clade] = {
            "status": "PERSISTENCE_CURVE_COMPLETE",
            "eligible_tips": n,
            "root_to_tip_cv_full_tree": root_to_tip_cv(tree),
            "relative_time_max": float(rel_time.max()),
            "relative_time_median": float(np.median(rel_time)),
            "persistence_area_winner": winner,
            "resolutions": per_resolution,
        }

    z.close()
    complete = {k: v for k, v in details.items() if v["status"] == "PERSISTENCE_CURVE_COMPLETE"}
    winner_counts = collections.Counter(v["persistence_area_winner"] for v in complete.values())
    cvs = np.array([v["root_to_tip_cv_full_tree"] for v in complete.values()], dtype=float)
    medians = {}
    for r in RESOLUTIONS:
        medians[r] = {
            "signed_excess_area": float(np.nanmedian([v["resolutions"][r]["signed_excess_area"] for v in complete.values()])),
            "near_far_contrast": float(np.nanmedian([v["resolutions"][r]["near_far_contrast"] for v in complete.values()])),
            "linear_decay_slope": float(np.nanmedian([v["resolutions"][r]["linear_decay_slope"] for v in complete.values()])),
        }

    headline = {
        "status": "FLOWERCLADES51_DISTANCE_PERSISTENCE_SPIKE_COMPLETE",
        "completed_clades": len(complete),
        "hold_clades": len(details) - len(complete),
        "persistence_area_winner_counts": dict(sorted(winner_counts.items())),
        "median_root_to_tip_cv": float(np.nanmedian(cvs)) if len(cvs) else None,
        "max_root_to_tip_cv": float(np.nanmax(cvs)) if len(cvs) else None,
        "strictly_ultrametric_cv_le_1e_8": int(np.sum(cvs <= 1e-8)) if len(cvs) else 0,
        "axis_label": "relative phylogenetic divergence depth = patristic/(2*crown height); not absolute Ma",
        "median_curve_summaries": medians,
        "claim_boundary": "retrospective descriptive persistence analysis; no causal ecological or absolute-time claim",
    }
    out = {
        "version": "v0.1",
        "source_sha256": {"final_dataset.csv": CSV_SHA, "trees.zip": TREES_SHA},
        "headline": headline,
        "results": details,
    }
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "summary.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    with (outdir / "curves.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "clade",
                "resolution",
                "eligible_tips",
                "distance_bin",
                "n_pairs",
                "mean_relative_divergence_depth",
                "p_same",
                "baseline_same_probability",
                "excess_retention",
            ]
        )
        w.writerows(curve_rows)
    return out


def analyse_fine_only(csv_path: Path, trees_path: Path, outdir: Path, n_bins: int = 10) -> dict:
    rows_by_clade: dict[str, list[tuple[str, str]]] = collections.defaultdict(list)
    with csv_path.open(newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            rows_by_clade[row["clade"].strip()].append((row["species"].strip(), row["flower_color"].strip()))

    z = zipfile.ZipFile(trees_path)
    members = {
        Path(m).stem.lower(): m for m in z.namelist()
        if not m.endswith("/") and not m.startswith("__MACOSX/") and not m.endswith(".DS_Store")
    }
    details = {}
    curves = []
    for clade in sorted(rows_by_clade):
        vals = rows_by_clade[clade]
        counts = collections.Counter(color for _, color in vals)
        rare = {state for state, n in counts.items() if n < 5}
        retained = [(sp, color) for sp, color in vals if color not in rare]
        colors = [color for _, color in retained]
        ok, reasons = fine_only_eligibility(colors)
        if not ok:
            details[clade] = {"status": "HOLD_FINE_ONLY_FRAME", "reasons": reasons, "eligible_tips": len(retained)}
            continue
        tree = Phylo.read(io.StringIO(z.read(members[clade.lower()]).decode("utf-8-sig")), "newick")
        by_tip = {norm_tip(sp): color for sp, color in retained}
        tips = [t for t in tree.get_terminals() if norm_tip(t.name) in by_tip]
        states = np.array([by_tip[norm_tip(t.name)] for t in tips], dtype=object)
        ii, jj = np.triu_indices(len(tips), 1)
        dist = np.array([tree.distance(tips[int(a)], tips[int(b)]) for a, b in zip(ii, jj)], dtype=float)
        rel_time = relative_divergence_time(tree, dist)
        curve = persistence_curve(rel_time, ii, jj, states, n_bins=n_bins)
        details[clade] = {
            "status": "FINE_VISIBLE_COLOR_PERSISTENCE_COMPLETE",
            "eligible_tips": len(tips),
            "fine_states": len(set(states.tolist())),
            "root_to_tip_cv": root_to_tip_cv(tree),
            "linear_decay_slope": curve["linear_decay_slope"],
            "signed_excess_area": curve["signed_excess_area"],
            "near_far_contrast": curve["near_far_contrast"],
            "baseline_same_probability": curve["baseline_same_probability"],
        }
        for b in curve["bins"]:
            curves.append({"clade": clade, **b})
    z.close()

    complete = {k: v for k, v in details.items() if v["status"] == "FINE_VISIBLE_COLOR_PERSISTENCE_COMPLETE"}
    slopes = [v["linear_decay_slope"] for v in complete.values()]
    areas = [v["signed_excess_area"] for v in complete.values()]
    near_far = [v["near_far_contrast"] for v in complete.values()]
    cvs = [v["root_to_tip_cv"] for v in complete.values()]
    headline = {
        "status": "FLOWERCLADES51_FINE_VISIBLE_COLOR_RELATIVE_TIME_PERSISTENCE",
        "eligible_clades": len(complete),
        "hold_clades": len(details) - len(complete),
        "root_to_tip_cv_median": float(np.median(cvs)),
        "root_to_tip_cv_max": float(np.max(cvs)),
        "slope": one_sample_direction_summary(slopes, "negative"),
        "area": one_sample_direction_summary(areas, "positive"),
        "near_far": one_sample_direction_summary(near_far, "positive"),
        "axis_label": "relative phylogenetic divergence depth; not absolute Ma",
        "claim_boundary": "retrospective interspecific state persistence, not within-population polymorphism and not independent of the existing pairwise AUC",
    }
    out = {"version": "v0.1", "headline": headline, "results": details}
    (outdir / "fine_only_summary.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    with (outdir / "fine_only_curves.csv").open("w", newline="") as f:
        if curves:
            w = csv.DictWriter(f, fieldnames=list(curves[0]))
            w.writeheader()
            w.writerows(curves)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", type=Path)
    ap.add_argument("--trees", type=Path)
    ap.add_argument("--download", action="store_true")
    ap.add_argument("--outdir", type=Path, required=True)
    ap.add_argument("--bins", type=int, default=10)
    args = ap.parse_args()

    diagnostics = []
    csv_path, trees_path = args.csv, args.trees
    if args.download:
        csv_path, trees_path, diagnostics = recover_exact_sources(args.outdir / "source")
    if csv_path is None or trees_path is None:
        args.outdir.mkdir(parents=True, exist_ok=True)
        out = {
            "version": "v0.1",
            "headline": {
                "status": "HOLD_EXACT_SOURCE_BYTES_UNAVAILABLE",
                "claim_boundary": "No persistence result computed without exact frozen source bytes.",
            },
            "download_diagnostics": diagnostics,
        }
        (args.outdir / "summary.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
        print(json.dumps(out["headline"], indent=2))
        return
    if sha256_file(csv_path) != CSV_SHA or sha256_file(trees_path) != TREES_SHA:
        raise SystemExit("source hash mismatch")
    out = analyse(csv_path, trees_path, args.outdir, n_bins=args.bins)
    fine = analyse_fine_only(csv_path, trees_path, args.outdir, n_bins=args.bins)
    out["fine_only_headline"] = fine["headline"]
    out["download_diagnostics"] = diagnostics
    (args.outdir / "summary.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"common_frame": out["headline"], "fine_only": fine["headline"]}, indent=2))


if __name__ == "__main__":
    main()
