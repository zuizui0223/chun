#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"


def main() -> int:
    files = sorted([*WORKFLOWS.glob("*.yml"), *WORKFLOWS.glob("*.yaml")])
    if not files:
        raise SystemExit("no workflow files found")
    failures: list[str] = []
    for path in files:
        try:
            with path.open(encoding="utf-8") as handle:
                doc = yaml.safe_load(handle)
            if not isinstance(doc, dict):
                failures.append(f"{path.relative_to(ROOT)}: top level is not a mapping")
                continue
            if "jobs" not in doc:
                failures.append(f"{path.relative_to(ROOT)}: missing jobs mapping")
        except Exception as exc:
            failures.append(f"{path.relative_to(ROOT)}: {exc}")
    if failures:
        raise SystemExit("workflow YAML integrity failures:\n" + "\n".join(failures))
    print(f"WORKFLOW_YAML_INTEGRITY_PASS files={len(files)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
