#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import shutil
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mapping", type=Path, required=True)
    ap.add_argument("--bundle-root", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    a = ap.parse_args()

    rows = read_csv(a.mapping)
    if [r["appendix_id"] for r in rows] != [f"Appendix S{i}" for i in range(1, 10)]:
        raise SystemExit("Appendix mapping must contain ordered Appendix S1-S9")
    a.out_dir.mkdir(parents=True, exist_ok=True)
    copied = []
    for r in rows:
        src = a.bundle_root / r["source_file_or_output"]
        dst = a.out_dir / r["upload_name"]
        if not src.exists():
            raise SystemExit(f"Appendix source missing: {src}")
        shutil.copy2(src, dst)
        copied.append({
            "appendix_id": r["appendix_id"],
            "internal_item": r["internal_item"],
            "source": str(src.relative_to(a.bundle_root)),
            "upload_name": dst.name,
            "title_or_legend": r["title_or_legend"],
            "bytes": dst.stat().st_size,
        })

    index = a.out_dir / "Appendix_index.csv"
    with index.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(copied[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(copied)

    summary = {
        "appendix_count": len(copied),
        "upload_names": [x["upload_name"] for x in copied],
        "mapping": copied,
    }
    a.summary.parent.mkdir(parents=True, exist_ok=True)
    a.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"appendix_count": len(copied), "upload_names": summary["upload_names"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
