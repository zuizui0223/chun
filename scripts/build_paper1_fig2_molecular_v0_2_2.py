#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--signatures", type=Path, required=True)
    ap.add_argument("--intervals", type=Path, required=True)
    ap.add_argument("--overlap", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()

    intervals = rows(args.intervals)
    overlap = {r["transition_class"]: r for r in rows(args.overlap)}
    anth_lit_pair = next(r for r in intervals if r["transition_class"] == "anthocyanin_gain" and r["regime"] == "literature" and r["metric"] == "pairwise_axis_concordance")
    if (anth_lit_pair["minimum"], anth_lit_pair["maximum"], anth_lit_pair["n_unresolved_cluster_axes"], anth_lit_pair["source_run"]) != ("0.3333333333", "1.0", "6", "33045356947"):
        raise SystemExit(f"v0.2.2 anthocyanin interval drift: {anth_lit_pair}")
    ao = overlap["anthocyanin_gain"]
    if (ao["n_comparable_resolved_cells"], ao["n_agree"], ao["conflicts"]) != ("6", "2", "CJAPONICA:A;CJAPONICA:F;CRETICULATA:P;CSIN_WHITE_PINK:A"):
        raise SystemExit(f"v0.2.2 overlap drift: {ao}")

    base_builder = Path(__file__).with_name("build_paper1_fig2_molecular_v0_2.py")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        subprocess.run([
            sys.executable, str(base_builder),
            "--signatures", str(args.signatures),
            "--intervals", str(args.intervals),
            "--overlap", str(args.overlap),
            "--out-dir", str(td),
        ], check=True)
        svg = args.out_dir / "paper1_fig2_molecular_v0_2_2.svg"
        png = args.out_dir / "paper1_fig2_molecular_v0_2_2.png"
        shutil.copy2(td / "paper1_fig2_molecular_v0_2.svg", svg)
        shutil.copy2(td / "paper1_fig2_molecular_v0_2.png", png)

    summary = {
        "status": "paper1_fig2_molecular_v0_2_2_built",
        "signature_rows": 20,
        "interval_rows": 8,
        "overlap_rows": 2,
        "anthocyanin_literature_run": "33045356947",
        "candidate_free_run": "32929846096",
        "yellow_literature_run": "32929846096",
        "anthocyanin_direct_agreement": "2/6",
        "candidate_free_changed": False,
        "yellow_changed": False,
        "outputs": [str(svg), str(png)],
        "claim_boundary": "presentation only; Luo 2016 updates literature-side CJAPONICA F and no candidate-free direction",
    }
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
