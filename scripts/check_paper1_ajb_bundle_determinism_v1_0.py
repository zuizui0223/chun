#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def inventory(root: Path) -> dict[str, str]:
    return {
        str(p.relative_to(root)): sha256(p)
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--first", type=Path, required=True)
    ap.add_argument("--second", type=Path, required=True)
    a = ap.parse_args()

    first = inventory(a.first)
    second = inventory(a.second)
    if first.keys() != second.keys():
        raise SystemExit(
            "bundle file-list nondeterminism: "
            + json.dumps({
                "only_first": sorted(first.keys() - second.keys()),
                "only_second": sorted(second.keys() - first.keys()),
            }, indent=2)
        )

    changed = [
        {"path": path, "first": first[path], "second": second[path]}
        for path in first
        if first[path] != second[path]
    ]
    if changed:
        raise SystemExit("bundle SHA256 nondeterminism:\n" + json.dumps(changed, indent=2))

    print(json.dumps({
        "status": "PAPER1_AJB_V1_0_BYTE_REPRODUCIBLE",
        "n_files": len(first),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
