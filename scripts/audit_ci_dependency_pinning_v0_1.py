#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
PIP_RE = re.compile(r"(?:python\s+-m\s+pip|(?<!-)\bpip)\s+install\b(?P<args>.*)")


def family(path: Path) -> str:
    stem = path.stem
    for prefix in (
        "paper1", "cross-radiation", "flowerclades51", "merianieae",
        "gesnerioideae", "ruellia", "iris", "petunieae", "solanaceae",
        "rhododendron", "iochrominae", "candidate-free", "hidden-memory",
        "schistanthe", "source-first", "epimedium", "flower-fruit",
    ):
        if stem.startswith(prefix):
            return prefix
    return "other:" + stem.split("-", 1)[0]


def pip_lines_from_text(text: str) -> list[dict[str, object]]:
    rows = []
    for lineno, raw in enumerate(text.splitlines(), start=1):
        m = PIP_RE.search(raw)
        if not m:
            continue
        args = m.group("args").strip()
        requirement_file = bool(re.search(r"(?:^|\s)(?:-r|--requirement)(?:\s|=)", args))
        direct_tokens = [
            tok for tok in re.split(r"\s+", args)
            if tok and not tok.startswith("-") and not tok.endswith("\\")
        ]
        directly_pinned = bool(direct_tokens) and all(
            "==" in tok or tok.startswith(("git+", "https://", "http://"))
            for tok in direct_tokens
        )
        rows.append({
            "line": lineno,
            "command": raw.strip(),
            "pinned": requirement_file or directly_pinned,
            "via_requirement_file": requirement_file,
        })
    return rows


def pip_lines(path: Path) -> list[dict[str, object]]:
    return pip_lines_from_text(path.read_text(encoding="utf-8"))


def new_unpinned_rows(
    current_rows: list[dict[str, object]],
    base_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    """Return only unpinned install commands newly introduced vs the base.

    Existing dependency debt is inventoried but does not block unrelated workflow
    maintenance. Increasing the count of an existing unpinned command still fails.
    """
    base_counts = Counter(
        str(row["command"])
        for row in base_rows
        if not bool(row["pinned"])
    )
    seen = Counter()
    added = []
    for row in current_rows:
        if bool(row["pinned"]):
            continue
        command = str(row["command"])
        seen[command] += 1
        if seen[command] > base_counts[command]:
            added.append(row)
    return added


def base_workflow_rows(base_ref: str, relative_path: str) -> list[dict[str, object]]:
    proc = subprocess.run(
        ["git", "show", f"{base_ref}:{relative_path}"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return []
    return pip_lines_from_text(proc.stdout)


def inventory() -> dict:
    files = sorted([*WORKFLOWS.glob("*.yml"), *WORKFLOWS.glob("*.yaml")])
    entries = []
    families = Counter()
    unpinned_by_family = Counter()
    unpinned_workflows_by_family: dict[str, set[str]] = {}
    unpinned = 0
    with_pip = 0
    for path in files:
        rows = pip_lines(path)
        if not rows:
            continue
        with_pip += 1
        fam = family(path)
        families[fam] += 1
        unpinned_rows = [row for row in rows if not bool(row["pinned"])]
        unpinned += len(unpinned_rows)
        if unpinned_rows:
            unpinned_by_family[fam] += len(unpinned_rows)
            unpinned_workflows_by_family.setdefault(fam, set()).add(str(path.relative_to(ROOT)))
        entries.append({
            "workflow": str(path.relative_to(ROOT)),
            "family": fam,
            "pip_installs": rows,
        })
    return {
        "workflow_files": len(files),
        "workflows_with_pip_install": with_pip,
        "unpinned_pip_install_lines": unpinned,
        "families": dict(sorted(families.items())),
        "unpinned_by_family": dict(sorted(unpinned_by_family.items(), key=lambda kv: (-kv[1], kv[0]))),
        "unpinned_workflows_by_family": {
            fam: sorted(paths)
            for fam, paths in sorted(
                unpinned_workflows_by_family.items(),
                key=lambda kv: (-len(kv[1]), kv[0]),
            )
        },
        "entries": entries,
    }


def changed_workflows(base_ref: str) -> list[Path]:
    proc = subprocess.run(
        ["git", "diff", "--name-only", f"{base_ref}...HEAD", "--", ".github/workflows"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    out = []
    for rel in proc.stdout.splitlines():
        path = ROOT / rel
        if path.exists() and path.suffix in {".yml", ".yaml"}:
            out.append(path)
    return sorted(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-ref")
    ap.add_argument("--report-out", type=Path)
    args = ap.parse_args()

    report = inventory()
    summary = {k: v for k, v in report.items() if k != "entries"}
    print(json.dumps(summary, indent=2, sort_keys=True))

    if args.report_out:
        args.report_out.parent.mkdir(parents=True, exist_ok=True)
        args.report_out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if args.base_ref:
        violations = []
        for path in changed_workflows(args.base_ref):
            relative = str(path.relative_to(ROOT))
            current_rows = pip_lines(path)
            base_rows = base_workflow_rows(args.base_ref, relative)
            for row in new_unpinned_rows(current_rows, base_rows):
                violations.append({
                    "workflow": relative,
                    **row,
                })
        if violations:
            raise SystemExit(
                "changed workflows introduce new unpinned direct pip installs; "
                "move new installs to a version-pinned requirements file or pin every direct package:\n"
                + json.dumps(violations, indent=2)
            )
        print("CHANGED_WORKFLOW_DEPENDENCY_PINNING_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
