#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def run(*args: str) -> None:
    cmd = [sys.executable, *args]
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True, env={**os.environ, "MPLBACKEND": "Agg"})


def cp(src: str | Path, dst: str | Path) -> None:
    src, dst = Path(src), Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--out-dir", type=Path, required=True); a = ap.parse_args()
    bundle = a.out_dir
    work = bundle.parent / "paper1_v0_7_work"
    if bundle.exists(): shutil.rmtree(bundle)
    if work.exists(): shutil.rmtree(work)
    for p in [bundle / "manuscript", bundle / "main_figures", bundle / "appendices", bundle / "provenance", work]:
        p.mkdir(parents=True, exist_ok=True)

    # 1. Freeze scientific contract (unchanged Paper 1 v0.2).
    registry_dir = work / "registry"
    run("scripts/validate_paper1_result_registry.py",
        "--registry", "data/paper1_authoritative_results_v0_2.csv",
        "--figures", "data/paper1_main_figure_manifest_v0_2.csv",
        "--out-dir", str(registry_dir))
    cp(registry_dir / "summary.json", bundle / "provenance/registry_gate_summary.json")

    # 2. Generate the novelty-audited framing and bind it to the 21-reference registry.
    framed = work / "PAPER1_AJB_MANUSCRIPT_V0_3.md"
    run("scripts/build_paper1_novelty_framed_v0_3.py",
        "--source", "manuscript/PAPER1_AJB_MANUSCRIPT_V0_2.md",
        "--out", str(framed),
        "--summary", str(bundle / "provenance/novelty_framing_summary.json"))
    run("scripts/validate_paper1_reference_registry_v0_3.py",
        "--registry", "data/paper1_reference_registry_v0_3.csv",
        "--manuscript", str(framed),
        "--out", str(bundle / "provenance/reference_registry_summary.json"))
    cp(framed, bundle / "provenance/PAPER1_AJB_MANUSCRIPT_V0_3.md")

    # 3. Convert framing v0.3 to the journal-facing v0.7 manuscript.
    submission = bundle / "manuscript/PAPER1_AJB_UPLOAD_V0_7.md"
    run("scripts/build_paper1_submission_v0_7.py",
        "--source", str(framed),
        "--appendix-map", "data/paper1_ajb_appendix_mapping_v0_3.csv",
        "--figure-manifest", "data/paper1_main_figure_manifest_v0_2.csv",
        "--out", str(submission),
        "--summary", str(bundle / "provenance/submission_v0_7_build_summary.json"))
    run("scripts/validate_paper1_reference_registry_v0_3.py",
        "--registry", "data/paper1_reference_registry_v0_3.csv",
        "--manuscript", str(submission),
        "--out", str(bundle / "provenance/submission_reference_registry_summary.json"))

    # 4. Rebuild frozen Main Figures 1-6.
    fig1, fig2, fig34, fig5, fig6 = [work / x for x in ("fig1", "fig2", "fig34", "fig5", "fig6")]
    run("scripts/build_paper1_fig1_framework_v0_2.py", "--framework", "data/paper1_fig1_framework_v0_2.csv", "--observation", "data/paper1_fig1_observation_contract_v0_2.csv", "--out-dir", str(fig1))
    run("scripts/build_paper1_fig2_molecular_v0_2.py", "--signatures", "data/paper1_fig2_candidate_free_signature_v0_2.csv", "--intervals", "data/paper1_fig2_recurrence_intervals_v0_2.csv", "--overlap", "data/paper1_fig2_direct_overlap_v0_2.csv", "--out-dir", str(fig2))
    run("scripts/build_paper1_fig3_fig4_audits_v0_2.py", "--numeric-inputs", "data/paper1_figure_numeric_inputs_v0_1.csv", "--out-dir", str(fig34))
    run("scripts/build_paper1_fig5_macro_v0_2.py", "--nearest", "data/paper1_fig5_nearest_same_v0_2.csv", "--robustness", "data/paper1_fig5_robustness_status_v0_2.csv", "--out-dir", str(fig5))
    run("scripts/build_paper1_fig6_identifiability_v0_2.py", "--events", "data/paper1_fig6_event_gate_v0_2.csv", "--synthesis", "data/paper1_fig6_synthesis_v0_2.csv", "--out-dir", str(fig6))
    figure_sources = {
        1: fig1 / "paper1_fig1_framework_v0_2",
        2: fig2 / "paper1_fig2_molecular_v0_2",
        3: fig34 / "paper1_fig3_evidence_attrition_v0_2",
        4: fig34 / "paper1_fig4_topology_concordance_v0_2",
        5: fig5 / "paper1_fig5_macro_v0_2",
        6: fig6 / "paper1_fig6_identifiability_synthesis_v0_2",
    }
    for i, base in figure_sources.items():
        for ext in ("png", "svg"):
            cp(base.with_suffix(f".{ext}"), bundle / f"main_figures/Figure_{i}.{ext}")

    # 5. Supporting Information stays on the frozen v0.2 scientific sources.
    supp = work / "supp"
    run("scripts/build_paper1_supp_figures_v0_2.py", "--registry", "data/paper1_authoritative_results_v0_2.csv", "--out-dir", str(supp))
    cp(supp / "summary.json", bundle / "provenance/supplementary_figure_summary.json")
    appendix_sources = {
        1: "data/paper1_authoritative_results_v0_2.csv",
        2: "data/paper1_fig2_candidate_free_signature_v0_2.csv",
        3: "data/paper1_fig2_recurrence_intervals_v0_2.csv",
        4: "data/paper1_fig2_direct_overlap_v0_2.csv",
        5: "data/wfo55_accepted_species_wild_colour_registry_v0_1.csv",
        6: "data/ecological_driver_effect_size_registry_v0_2.csv",
    }
    for i, src in appendix_sources.items(): cp(src, bundle / f"appendices/Appendix_S{i}.csv")
    cp(supp / "FigS1_molecular_support_v0_2.png", bundle / "appendices/Appendix_S7.png")
    cp(supp / "FigS2_ecology_boundary_v0_2.png", bundle / "appendices/Appendix_S8.png")

    # 6. Journal-facing DOCX from the exact final Markdown.
    run("scripts/build_paper1_ajb_docx_v0_7.py",
        "--source", str(submission),
        "--out", str(bundle / "manuscript/PAPER1_AJB_UPLOAD_V0_7.docx"),
        "--summary", str(bundle / "provenance/docx_v0_7_summary.json"))

    # 7. Frozen provenance and audit boundary.
    for src in [
        "data/paper1_authoritative_results_v0_2.csv",
        "data/paper1_main_figure_manifest_v0_2.csv",
        "data/paper1_reference_registry_v0_3.csv",
        "data/paper1_ajb_appendix_mapping_v0_3.csv",
        "docs/EVIDENCE_AUDIT_2026-08-26.md",
        "docs/PAPER1_NOVELTY_LITERATURE_AUDIT_2026-08-27.md",
        "docs/PAPER1_NOVELTY_CORE_ATTACK_ADDENDUM_2026-08-27.md",
    ]:
        cp(src, bundle / "provenance" / Path(src).name)
    cp("docs/PAPER1_AJB_UPLOAD_BUNDLE_V0_7_README.md", bundle / "README.md")

    # 8. Final cross-file audit + SHA256 manifest.
    run("scripts/audit_paper1_ajb_bundle_v0_7.py", "--bundle", str(bundle), "--out", str(bundle / "BUNDLE_MANIFEST.json"))
    manifest = json.loads((bundle / "BUNDLE_MANIFEST.json").read_text(encoding="utf-8"))
    print(json.dumps({k: v for k, v in manifest.items() if k != "files"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
