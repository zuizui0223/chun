#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    a = ap.parse_args()

    src = Path("scripts/build_paper1_novelty_framing_v0_3_3.py").read_text(encoding="utf-8")
    patches = {
        '"same biological systems are held constant and the observation rule is standardized",':
            '"biological systems are held constant and the observation rule is standardized",',
        '"two agreements",': '"agreement remained only two",',
    }
    for old, new in patches.items():
        if src.count(old) != 1:
            raise SystemExit(f"v0.3.3 QC patch contract drift: {old}")
        src = src.replace(old, new, 1)

    with tempfile.TemporaryDirectory(prefix="paper1_v033_qc_") as td:
        patched = Path(td) / "build_paper1_novelty_framing_v0_3_3_patched.py"
        patched.write_text(src, encoding="utf-8")
        subprocess.run([
            sys.executable,
            str(patched),
            "--source", str(a.source),
            "--out", str(a.out),
            "--summary", str(a.summary),
        ], check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
