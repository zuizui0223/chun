#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, median


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def fnum(x: str) -> float | None:
    x = (x or "").strip()
    return None if x == "" else float(x)


def inum(x: str) -> int | None:
    x = (x or "").strip()
    return None if x == "" else int(float(x))


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        w = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        w.writeheader(); w.writerows(rows)


def log_rr_from_counts(a: int, n1: int, c: int, n0: int) -> tuple[float, float]:
    if not (0 < a <= n1 and 0 < c <= n0):
        raise ValueError("log risk ratio requires non-zero events and valid denominators")
    rr = (a / n1) / (c / n0)
    var = (1 / a - 1 / n1) + (1 / c - 1 / n0)
    return math.log(rr), math.sqrt(var)


def fixed_random_meta(effects: list[tuple[float, float]]) -> dict:
    """Future-proof inverse-variance synthesis; caller must ensure defensible SE and k>=3."""
    k = len(effects)
    wi = [1 / (se * se) for _, se in effects]
    mu_fixed = sum(w * y for w, (y, _) in zip(wi, effects)) / sum(wi)
    q = sum(w * (y - mu_fixed) ** 2 for w, (y, _) in zip(wi, effects))
    c = sum(wi) - sum(w * w for w in wi) / sum(wi)
    tau2 = max(0.0, (q - (k - 1)) / c) if c > 0 else 0.0
    wr = [1 / (se * se + tau2) for _, se in effects]
    mu = sum(w * y for w, (y, _) in zip(wr, effects)) / sum(wr)
    se_mu = math.sqrt(1 / sum(wr))
    return {
        "k": k,
        "mu_lnRR": mu,
        "pooled_RR": math.exp(mu),
        "SE_mu": se_mu,
        "CI95_low_RR": math.exp(mu - 1.96 * se_mu),
        "CI95_high_RR": math.exp(mu + 1.96 * se_mu),
        "Q": q,
        "tau2_DL": tau2,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    a = ap.parse_args()
    rows = read_csv(a.registry)
    a.out_dir.mkdir(parents=True, exist_ok=True)

    ids = [r["effect_id"] for r in rows]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate effect_id in ecological effect registry")

    audited = []
    calc_errors = []
    for r in rows:
        metric = r["effect_metric"]
        num = fnum(r["numerator_value"]); den = fnum(r["denominator_value"])
        stored = fnum(r["effect_value"])
        calc = None
        if metric == "lnRR" and num is not None and den is not None:
            if num <= 0 or den <= 0:
                raise SystemExit(f"{r['effect_id']}: non-positive lnRR input")
            calc = math.log(num / den)
            if stored is not None and abs(calc - stored) > 0.01:
                calc_errors.append((r["effect_id"], stored, calc))
        events_num, n_num = inum(r.get("events_num", "")), inum(r.get("n_num", ""))
        events_den, n_den = inum(r.get("events_den", "")), inum(r.get("n_den", ""))
        reconstructed_se = None
        if all(x is not None for x in (events_num, n_num, events_den, n_den)):
            binary_lnrr, reconstructed_se = log_rr_from_counts(events_num, n_num, events_den, n_den)
            if calc is not None and abs(binary_lnrr - calc) > 0.01:
                raise SystemExit(f"{r['effect_id']}: raw-count lnRR conflicts with proportion lnRR")
        direct_se = fnum(r.get("se_value", ""))
        variance_status = r["variance_status"]
        defensible_se = reconstructed_se if reconstructed_se is not None else None
        # Provisional Wald-derived SEs are intentionally NOT treated as defensible for pooling.
        formal_pool_eligible = defensible_se is not None
        audited.append({
            **r,
            "recomputed_effect": "" if calc is None else f"{calc:.6f}",
            "reconstructed_se": "" if reconstructed_se is None else f"{reconstructed_se:.6f}",
            "direct_se_registry": "" if direct_se is None else f"{direct_se:.6f}",
            "formal_pool_eligible": str(formal_pool_eligible).lower(),
            "audit_note": "raw-count variance reconstructed" if reconstructed_se is not None else variance_status,
        })
    if calc_errors:
        raise SystemExit(f"stored effect values disagree with recomputation: {calc_errors}")

    # Primary quantitative synthesis: bird access -> fruit set.
    bird = [r for r in audited if r["axis"] == "pollinator_service" and r["outcome"] == "fruit_set"]
    bird_units = [r["independence_unit"] for r in bird]
    if len(bird) != len(set(bird_units)):
        raise SystemExit("bird-service primary set contains duplicate independence units")
    bird_ln = [float(r["recomputed_effect"]) for r in bird]
    bird_rr = [math.exp(x) for x in bird_ln]
    bird_states = sorted({r["visible_state"] for r in bird})
    leave_one_out = []
    for omit in range(len(bird)):
        kept = [x for i, x in enumerate(bird_ln) if i != omit]
        leave_one_out.append({
            "omitted_effect": bird[omit]["effect_id"],
            "remaining_k": len(kept),
            "mean_lnRR": mean(kept),
            "geometric_mean_RR": math.exp(mean(kept)),
        })
    bird_formal = [(float(r["recomputed_effect"]), float(r["reconstructed_se"])) for r in bird if r["formal_pool_eligible"] == "true"]
    bird_summary = {
        "k_independent_species": len(bird),
        "visible_states_represented": bird_states,
        "positive_direction_count": sum(x > 0 for x in bird_ln),
        "equal_weight_mean_lnRR": mean(bird_ln),
        "equal_weight_geometric_mean_RR": math.exp(mean(bird_ln)),
        "median_RR": median(bird_rr),
        "min_RR": min(bird_rr),
        "max_RR": max(bird_rr),
        "leave_one_out_RR_min": min(x["geometric_mean_RR"] for x in leave_one_out),
        "leave_one_out_RR_max": max(x["geometric_mean_RR"] for x in leave_one_out),
        "n_with_defensible_sampling_variance": len(bird_formal),
        "inverse_variance_meta_performed": len(bird_formal) >= 3,
        "interpretation_ceiling": "exploratory magnitude synthesis; no hue moderator test because A/Y/W each have only one independent bird-exclusion species",
    }
    if len(bird_formal) >= 3:
        bird_summary["inverse_variance_meta"] = fixed_random_meta(bird_formal)

    # Pollen limitation: reconstruct any exact binary RR effects but do not pool unless >=3.
    pl = [r for r in audited if r["axis"] == "pollen_limitation" and r["outcome"] == "fruit_set"]
    pl_formal = [(float(r["recomputed_effect"]), float(r["reconstructed_se"])) for r in pl if r["formal_pool_eligible"] == "true"]
    pl_effects = []
    for r in pl:
        rr = math.exp(float(r["recomputed_effect"])) if r["recomputed_effect"] else None
        se = fnum(r["reconstructed_se"])
        out = {"effect_id": r["effect_id"], "taxon": r["taxon"], "RR": rr, "SE_lnRR": se}
        if rr is not None and se is not None:
            y = math.log(rr)
            out.update({"CI95_low_RR": math.exp(y - 1.96 * se), "CI95_high_RR": math.exp(y + 1.96 * se)})
        pl_effects.append(out)

    # Descriptive inventory by ecological axis.
    axis_counts = Counter(r["axis"] for r in rows)
    variance_counts = Counter(r["variance_status"] for r in rows)
    summary = {
        "registry_effects": len(rows),
        "axis_counts": dict(sorted(axis_counts.items())),
        "variance_status_counts": dict(sorted(variance_counts.items())),
        "bird_service_fruit_set": bird_summary,
        "pollen_limitation_fruit_set": {
            "k_quantitative": len(pl),
            "n_with_defensible_sampling_variance": len(pl_formal),
            "inverse_variance_meta_performed": len(pl_formal) >= 3,
            "effects": pl_effects,
        },
        "decision": {
            "formal_meta_now": "not yet for Camellia bird-service or pollen-limitation because <3 independent effects have defensible sampling variance",
            "quantitative_result_now": "bird-access fruit-set effects can be summarized on a common lnRR scale across three independent Camellia species; raw-data recovery is the next gate for formal pooling",
            "paper1_status": "ecological-driver layer reopened; submission bundle remains provisional",
        },
    }

    fields = list(audited[0].keys())
    write_csv(a.out_dir / "effect_audit.csv", audited, fields)
    write_csv(a.out_dir / "bird_service_leave_one_out.csv", leave_one_out,
              ["omitted_effect", "remaining_k", "mean_lnRR", "geometric_mean_RR"])
    (a.out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
