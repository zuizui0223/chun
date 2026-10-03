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


def pip_lines(path: Path) -> list[dict[str, object]]:
    rows = []
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
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


def inventory() -> dict:
    files = sorted([*WORKFLOWS.glob("*.yml"), *WORKFLOWS.glob("*.yaml")])
    entries = []
    families = Counter()
    unpinned = 0
    with_pip = 0
    for path in files:
        rows = pip_lines(path)
        if not rows:
            continue
        with_pip += 1
        fam = family(path)
        families[fam] += 1
        unpinned += sum(not bool(row["pinned"]) for row in rows)
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
            for row in pip_lines(path):
                if not row["pinned"]:
                    violations.append({
                        "workflow": str(path.relative_to(ROOT)),
                        **row,
                    })
        if violations:
            raise SystemExit(
                "changed workflows contain unpinned direct pip installs; "
                "move them to a version-pinned requirements file or pin every direct package:\n"
                + json.dumps(violations, indent=2)
            )
        print("CHANGED_WORKFLOW_DEPENDENCY_PINNING_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
