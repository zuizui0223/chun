#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ALLOWED_STATUS = {"authoritative", "sensitivity", "superseded"}
ALLOWED_ROLE = {"main", "supplement", "context", "exclude"}
ALLOWED_FIG_STATUS = {"main", "supplement"}
LOCAL_REF_PREFIXES = ("docs/", "data/", "scripts/", "manuscript/", "supplement/", ".github/")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def split_ids(value: str) -> list[str]:
    return [x.strip() for x in (value or "").split(";") if x.strip()]


def infer_registry_version(path: Path) -> str:
    stem = path.stem
    if "_v" not in stem:
        return "unknown"
    token = stem.rsplit("_v", 1)[1].replace("_", ".")
    return f"v{token}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", type=Path, required=True)
    ap.add_argument("--figures", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()

    registry = read_csv(args.registry)
    figures = read_csv(args.figures)
    if not registry or not figures:
        raise SystemExit("registry and figure manifest must both be non-empty")

    required_registry = {
        "result_id", "layer", "status", "manuscript_role", "claim",
        "value_summary", "source_refs", "supersedes", "claim_boundary",
    }
    required_fig = {
        "figure_id", "panel_id", "panel_title", "result_ids",
        "plot_design", "manuscript_status",
    }
    if not required_registry.issubset(registry[0]):
        raise SystemExit(f"registry columns missing: {sorted(required_registry - set(registry[0]))}")
    if not required_fig.issubset(figures[0]):
        raise SystemExit(f"figure columns missing: {sorted(required_fig - set(figures[0]))}")

    ids = [r["result_id"].strip() for r in registry]
    if any(not x for x in ids):
        raise SystemExit("empty result_id")
    dupes = [x for x, n in Counter(ids).items() if n > 1]
    if dupes:
        raise SystemExit(f"duplicate result_id values: {dupes}")
    by_id = {r["result_id"]: r for r in registry}

    errors: list[str] = []
    local_source_refs_checked = 0
    for row in registry:
        rid = row["result_id"]
        if row["status"] not in ALLOWED_STATUS:
            errors.append(f"{rid}: invalid status {row['status']}")
        if row["manuscript_role"] not in ALLOWED_ROLE:
            errors.append(f"{rid}: invalid manuscript_role {row['manuscript_role']}")
        if not row["claim"].strip() or not row["value_summary"].strip() or not row["source_refs"].strip():
            errors.append(f"{rid}: claim/value/source_refs must be non-empty")
        if row["status"] == "superseded" and row["manuscript_role"] != "exclude":
            errors.append(f"{rid}: superseded result must have manuscript_role=exclude")
        if row["manuscript_role"] == "exclude" and row["status"] != "superseded":
            errors.append(f"{rid}: exclude role reserved for superseded results")

        # In v0.2, `supersedes` can mean "supersedes as the primary framing or
        # estimator" without invalidating a still-authoritative supporting result.
        # Scientific exclusion is represented only by status=superseded plus
        # manuscript_role=exclude.
        for prior in split_ids(row["supersedes"]):
            if prior not in by_id:
                errors.append(f"{rid}: supersedes unknown result {prior}")
            elif prior == rid:
                errors.append(f"{rid}: result cannot supersede itself")

        for source_ref in split_ids(row["source_refs"]):
            if source_ref in by_id:
                continue
            if source_ref.startswith(LOCAL_REF_PREFIXES):
                local_source_refs_checked += 1
                if not Path(source_ref).exists():
                    errors.append(f"{rid}: local source_ref does not exist: {source_ref}")

    dependencies: list[dict[str, str]] = []
    referenced = defaultdict(list)
    main_referenced: set[str] = set()
    for row in figures:
        if row["manuscript_status"] not in ALLOWED_FIG_STATUS:
            errors.append(f"{row['figure_id']}{row['panel_id']}: invalid manuscript_status")
        refs = split_ids(row["result_ids"])
        if not refs:
            errors.append(f"{row['figure_id']}{row['panel_id']}: no result_ids")
        for rid in refs:
            if rid not in by_id:
                errors.append(f"{row['figure_id']}{row['panel_id']}: unknown result {rid}")
                continue
            result = by_id[rid]
            if row["manuscript_status"] == "main" and result["status"] == "superseded":
                errors.append(f"{row['figure_id']}{row['panel_id']}: main figure uses superseded {rid}")
            if row["manuscript_status"] == "main" and result["manuscript_role"] == "exclude":
                errors.append(f"{row['figure_id']}{row['panel_id']}: main figure uses excluded {rid}")
            referenced[rid].append(f"{row['figure_id']}{row['panel_id']}")
            if row["manuscript_status"] == "main":
                main_referenced.add(rid)
            dependencies.append({
                "figure_id": row["figure_id"],
                "panel_id": row["panel_id"],
                "result_id": rid,
                "result_status": result["status"],
                "result_role": result["manuscript_role"],
                "layer": result["layer"],
            })

    main_ids = {r["result_id"] for r in registry if r["manuscript_role"] == "main"}
    unreferenced_main = sorted(main_ids - main_referenced)
    if unreferenced_main:
        errors.append(f"main-role results absent from main-figure manifest: {unreferenced_main}")

    main_fig_numbers = sorted({
        r["figure_id"] for r in figures if r["manuscript_status"] == "main"
    })
    expected_main_figures = [f"Fig{i}" for i in range(1, 7)]
    if main_fig_numbers != expected_main_figures:
        errors.append(
            f"expected exactly main Fig1..Fig6, observed {main_fig_numbers}"
        )

    if errors:
        raise SystemExit("\n".join(errors))

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(
        args.out_dir / "figure_dependency_matrix.csv",
        dependencies,
        ["figure_id", "panel_id", "result_id", "result_status", "result_role", "layer"],
    )
    write_csv(
        args.out_dir / "paper1_main_results.csv",
        [r for r in registry if r["manuscript_role"] == "main"],
        list(registry[0]),
    )
    write_csv(
        args.out_dir / "paper1_superseded_results.csv",
        [r for r in registry if r["status"] == "superseded"],
        list(registry[0]),
    )

    summary = {
        "registry_version": infer_registry_version(args.registry),
        "registry_file": str(args.registry),
        "figure_manifest_file": str(args.figures),
        "n_results": len(registry),
        "status_counts": dict(Counter(r["status"] for r in registry)),
        "manuscript_role_counts": dict(Counter(r["manuscript_role"] for r in registry)),
        "layer_counts": dict(Counter(r["layer"] for r in registry)),
        "n_main_figures": len(main_fig_numbers),
        "n_main_panels": sum(r["manuscript_status"] == "main" for r in figures),
        "n_dependency_edges": len(dependencies),
        "n_main_results_referenced": len(main_ids),
        "n_local_source_refs_checked": local_source_refs_checked,
        "main_figures_use_superseded_results": False,
        "authoritative_contract": (
            "Paper 1 main text and figures may use authoritative or explicitly labelled sensitivity "
            "results only. Superseded results are provenance/history and must not re-enter main figures."
        ),
    }
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
