#!/usr/bin/env python3
"""Out-of-sample test of coarse A/W visible colour as a climate predictor.

This is a direct CHUN reanalysis of the 50-species Fan2026 x GBIF x CHELSA
species matrix. It applies the frozen provenance correction for the two
Tuberculatae cold-tail rows, drops the known fuzzy duplicate C. kissi when
C. kissii is present, and then tests A/W visible colour by two prediction gates:

1. leave-one-species-out (LOSO);
2. leave-one-traditional-section-out (LOSectionO).

For each held-out row, the null predicts the training-set mean and the colour
model predicts the training-set mean for the held-out A/W class. No historical
branch or literature effect size enters this test.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter
from pathlib import Path

METRICS = ("bio1_median", "bio6_median", "bio6_q05", "bio1_iqr")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)


def norm_section(x: str) -> str:
    x = str(x or "").lower().strip()
    x = re.sub(r"^section\s+", "", x)
    x = re.sub(r"^sect\.\s*", "", x)
    return x.split(";")[0].strip()


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def apply_provenance_clean(species: list[dict[str, str]], sensitivity: list[dict[str, str]]) -> list[dict[str, object]]:
    rows = [dict(r) for r in species]
    taxa = {r["taxon"] for r in rows}
    if {"Camellia kissi", "Camellia kissii"}.issubset(taxa):
        rows = [r for r in rows if r["taxon"] != "Camellia kissi"]

    clean = {
        r["taxon"]: r
        for r in sensitivity
        if r["scenario"] == "minimal_remove_two_shared_extreme_coordinates"
    }
    assert set(clean) == {"Camellia rhytidocarpa", "Camellia tuberculata"}
    by_taxon = {r["taxon"]: r for r in rows}
    for taxon, c in clean.items():
        target = by_taxon[taxon]
        target["n_points"] = c["n_points"]
        for metric in METRICS:
            target[metric] = c[metric]
    return rows


def predict_rows(train: list[dict[str, object]], test: list[dict[str, object]], metric: str) -> list[dict[str, object]]:
    null_pred = mean([float(r[metric]) for r in train])
    by_colour: dict[str, float] = {}
    for state in ("A", "W"):
        vals = [float(r[metric]) for r in train if r["colour_state"] == state]
        assert vals, f"missing training state {state}"
        by_colour[state] = mean(vals)

    out = []
    for r in test:
        y = float(r[metric])
        colour_pred = by_colour[str(r["colour_state"])]
        out.append({
            "taxon": r["taxon"],
            "colour_state": r["colour_state"],
            "section_norm": r["section_norm"],
            "metric": metric,
            "observed": y,
            "null_prediction": null_pred,
            "colour_prediction": colour_pred,
            "null_abs_error": abs(y-null_pred),
            "colour_abs_error": abs(y-colour_pred),
            "null_sq_error": (y-null_pred)**2,
            "colour_sq_error": (y-colour_pred)**2,
        })
    return out


def summarize(mode: str, metric: str, rows: list[dict[str, object]]) -> dict[str, object]:
    n = len(rows)
    null_mae = mean([float(r["null_abs_error"]) for r in rows])
    colour_mae = mean([float(r["colour_abs_error"]) for r in rows])
    null_rmse = math.sqrt(mean([float(r["null_sq_error"]) for r in rows]))
    colour_rmse = math.sqrt(mean([float(r["colour_sq_error"]) for r in rows]))
    wins = sum(float(r["colour_abs_error"]) < float(r["null_abs_error"]) for r in rows)
    return {
        "mode": mode,
        "metric": metric,
        "n_predictions": n,
        "null_mae": null_mae,
        "colour_mae": colour_mae,
        "colour_minus_null_mae": colour_mae-null_mae,
        "null_rmse": null_rmse,
        "colour_rmse": colour_rmse,
        "colour_minus_null_rmse": colour_rmse-null_rmse,
        "colour_to_null_rmse_ratio": colour_rmse/null_rmse,
        "colour_abs_error_wins": wins,
        "colour_improves_rmse": colour_rmse < null_rmse,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--species", type=Path, required=True)
    ap.add_argument("--provenance", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args(); args.out_dir.mkdir(parents=True, exist_ok=True)

    rows = apply_provenance_clean(read_csv(args.species), read_csv(args.provenance))
    for r in rows:
        r["section_norm"] = norm_section(str(r["section"]))
    aw = [r for r in rows if r["colour_state"] in {"A", "W"}]
    counts = Counter(str(r["colour_state"]) for r in aw)
    assert len(rows) == 50 and len(aw) == 48 and counts == Counter({"W":34,"A":14})

    predictions: list[dict[str, object]] = []
    summaries: list[dict[str, object]] = []

    # Leave one species out.
    for metric in METRICS:
        pred = []
        for i, held in enumerate(aw):
            train = [r for j,r in enumerate(aw) if j != i]
            pred.extend(predict_rows(train, [held], metric))
        for r in pred: r["mode"] = "leave_one_species_out"
        predictions.extend(pred)
        summaries.append(summarize("leave_one_species_out", metric, pred))

    # Leave one traditional section out: tests generalization across historical backgrounds.
    sections = sorted({str(r["section_norm"]) for r in aw})
    for metric in METRICS:
        pred = []
        for section in sections:
            test = [r for r in aw if r["section_norm"] == section]
            train = [r for r in aw if r["section_norm"] != section]
            assert test and train
            pred.extend(predict_rows(train, test, metric))
        for r in pred: r["mode"] = "leave_one_section_out"
        predictions.extend(pred)
        summaries.append(summarize("leave_one_section_out", metric, pred))

    loso = [r for r in summaries if r["mode"] == "leave_one_species_out"]
    losec = [r for r in summaries if r["mode"] == "leave_one_section_out"]
    loso_wins = sum(bool(r["colour_improves_rmse"]) for r in loso)
    losec_wins = sum(bool(r["colour_improves_rmse"]) for r in losec)
    assert loso_wins == 0, f"frozen LOSO result drift: colour improves {loso_wins}/4 metrics"
    assert losec_wins == 0, f"frozen LOSectionO result drift: colour improves {losec_wins}/4 metrics"

    def geometric_ratio(rs):
        return math.exp(mean([math.log(float(r["colour_to_null_rmse_ratio"])) for r in rs]))

    summary = {
        "analysis": "visible_colour_out_of_sample_v0.1",
        "n_species_clean": len(rows),
        "n_AW": len(aw),
        "A": counts["A"],
        "W": counts["W"],
        "n_sections_AW": len(sections),
        "leave_one_species_out": {
            "colour_RMSE_wins": loso_wins,
            "n_metrics": len(METRICS),
            "geometric_mean_colour_to_null_RMSE_ratio": geometric_ratio(loso),
        },
        "leave_one_section_out": {
            "colour_RMSE_wins": losec_wins,
            "n_metrics": len(METRICS),
            "geometric_mean_colour_to_null_RMSE_ratio": geometric_ratio(losec),
        },
        "decision": "coarse visible A/W colour fails to improve held-out annual-climate prediction over an intercept-only null under both species and section holdout",
        "claim_ceiling": "prediction test of current species matrix; does not test flowering-window climate mediation or replace phylogenetic branch analysis",
    }

    write_csv(args.out_dir/"cv_predictions.csv", predictions)
    write_csv(args.out_dir/"cv_metric_summary.csv", summaries)
    (args.out_dir/"summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
