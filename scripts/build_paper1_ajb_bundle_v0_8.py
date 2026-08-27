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
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, required=True)
    a = ap.parse_args()
    bundle = a.out_dir
    work = bundle.parent / "paper1_v0_8_work"
    if bundle.exists():
        shutil.rmtree(bundle)
    if work.exists():
        shutil.rmtree(work)
    for p in [bundle / "manuscript", bundle / "main_figures", bundle / "appendices", bundle / "provenance", work]:
        p.mkdir(parents=True, exist_ok=True)

    # 1. Validate current scientific result/figure contract v0.2.1.
    registry_dir = work / "registry"
    run(
        "scripts/validate_paper1_result_registry.py",
        "--registry", "data/paper1_authoritative_results_v0_2_1.csv",
        "--figures", "data/paper1_main_figure_manifest_v0_2_1.csv",
        "--out-dir", str(registry_dir),
    )
    cp(registry_dir / "summary.json", bundle / "provenance/registry_gate_summary.json")

    # 2. Re-generate the science v0.2.1 manuscript from immutable v0.2 source.
    science = work / "PAPER1_AJB_MANUSCRIPT_V0_2_1.md"
    run(
        "scripts/build_paper1_science_v0_2_1.py",
        "--source", "manuscript/PAPER1_AJB_MANUSCRIPT_V0_2.md",
        "--out", str(science),
        "--summary", str(bundle / "provenance/science_v0_2_1_build_summary.json"),
    )
    run(
        "scripts/validate_paper1_reference_registry_v0_2_1.py",
        "--registry", "data/paper1_reference_registry_v0_2_1.csv",
        "--manuscript", str(science),
        "--out", str(bundle / "provenance/science_reference_registry_summary.json"),
    )
    cp(science, bundle / "provenance/PAPER1_AJB_MANUSCRIPT_V0_2_1.md")

    # 3. Apply novelty framing v0.3.1 and bind it to the 22-reference registry.
    framed = work / "PAPER1_AJB_MANUSCRIPT_V0_3_1.md"
    run(
        "scripts/build_paper1_novelty_framed_v0_3_1.py",
        "--source", str(science),
        "--out", str(framed),
        "--summary", str(bundle / "provenance/novelty_framing_v0_3_1_summary.json"),
    )
    run(
        "scripts/validate_paper1_reference_registry_v0_4.py",
        "--registry", "data/paper1_reference_registry_v0_4.csv",
        "--manuscript", str(framed),
        "--out", str(bundle / "provenance/reference_registry_v0_4_summary.json"),
    )
    cp(framed, bundle / "provenance/PAPER1_AJB_MANUSCRIPT_V0_3_1.md")

    # 4. Journal-facing Markdown v0.8.
    submission = bundle / "manuscript/PAPER1_AJB_UPLOAD_V0_8.md"
    run(
        "scripts/build_paper1_submission_v0_8.py",
        "--source", str(framed),
        "--appendix-map", "data/paper1_ajb_appendix_mapping_v0_4.csv",
        "--figure-manifest", "data/paper1_main_figure_manifest_v0_2_1.csv",
        "--out", str(submission),
        "--summary", str(bundle / "provenance/submission_v0_8_build_summary.json"),
    )
    run(
        "scripts/validate_paper1_reference_registry_v0_4.py",
        "--registry", "data/paper1_reference_registry_v0_4.csv",
        "--manuscript", str(submission),
        "--out", str(bundle / "provenance/submission_reference_registry_summary.json"),
    )

    # 5. Rebuild Main Figures. Only Fig.1 uses the v0.2.1 ascertainment update.
    fig1, fig2, fig34, fig5, fig6 = [work / x for x in ("fig1", "fig2", "fig34", "fig5", "fig6")]
    run(
        "scripts/build_paper1_fig1_framework_v0_2_1.py",
        "--framework", "data/paper1_fig1_framework_v0_2.csv",
        "--observation", "data/paper1_fig1_observation_contract_v0_2_1.csv",
        "--out-dir", str(fig1),
    )
    run("scripts/build_paper1_fig2_molecular_v0_2.py", "--signatures", "data/paper1_fig2_candidate_free_signature_v0_2.csv", "--intervals", "data/paper1_fig2_recurrence_intervals_v0_2.csv", "--overlap", "data/paper1_fig2_direct_overlap_v0_2.csv", "--out-dir", str(fig2))
    run("scripts/build_paper1_fig3_fig4_audits_v0_2.py", "--numeric-inputs", "data/paper1_figure_numeric_inputs_v0_1.csv", "--out-dir", str(fig34))
    run("scripts/build_paper1_fig5_macro_v0_2.py", "--nearest", "data/paper1_fig5_nearest_same_v0_2.csv", "--robustness", "data/paper1_fig5_robustness_status_v0_2.csv", "--out-dir", str(fig5))
    run("scripts/build_paper1_fig6_identifiability_v0_2.py", "--events", "data/paper1_fig6_event_gate_v0_2.csv", "--synthesis", "data/paper1_fig6_synthesis_v0_2.csv", "--out-dir", str(fig6))
    figure_sources = {
        1: fig1 / "paper1_fig1_framework_v0_2_1",
        2: fig2 / "paper1_fig2_molecular_v0_2",
        3: fig34 / "paper1_fig3_evidence_attrition_v0_2",
        4: fig34 / "paper1_fig4_topology_concordance_v0_2",
        5: fig5 / "paper1_fig5_macro_v0_2",
        6: fig6 / "paper1_fig6_identifiability_synthesis_v0_2",
    }
    for i, base in figure_sources.items():
        for ext in ("png", "svg"):
            cp(base.with_suffix(f".{ext}"), bundle / f"main_figures/Figure_{i}.{ext}")

    # 6. Supporting Information. S1 tracks v0.2.1; S2-S8 remain frozen scientific inputs.
    supp = work / "supp"
    run("scripts/build_paper1_supp_figures_v0_2.py", "--registry", "data/paper1_authoritative_results_v0_2_1.csv", "--out-dir", str(supp))
    cp(supp / "summary.json", bundle / "provenance/supplementary_figure_summary.json")
    appendix_sources = {
        1: "data/paper1_authoritative_results_v0_2_1.csv",
        2: "data/paper1_fig2_candidate_free_signature_v0_2.csv",
        3: "data/paper1_fig2_recurrence_intervals_v0_2.csv",
        4: "data/paper1_fig2_direct_overlap_v0_2.csv",
        5: "data/wfo55_accepted_species_wild_colour_registry_v0_1.csv",
        6: "data/ecological_driver_effect_size_registry_v0_2.csv",
    }
    for i, src in appendix_sources.items():
        cp(src, bundle / f"appendices/Appendix_S{i}.csv")
    cp(supp / "FigS1_molecular_support_v0_2.png", bundle / "appendices/Appendix_S7.png")
    cp(supp / "FigS2_ecology_boundary_v0_2.png", bundle / "appendices/Appendix_S8.png")

    # 7. DOCX from the exact final Markdown.
    run(
        "scripts/build_paper1_ajb_docx_v0_8.py",
        "--source", str(submission),
        "--out", str(bundle / "manuscript/PAPER1_AJB_UPLOAD_V0_8.docx"),
        "--summary", str(bundle / "provenance/docx_v0_8_summary.json"),
    )

    # 8. Provenance: science, novelty, formal search, and submission contracts.
    provenance = [
        "data/paper1_authoritative_results_v0_2_1.csv",
        "data/paper1_main_figure_manifest_v0_2_1.csv",
        "data/paper1_fig1_observation_contract_v0_2_1.csv",
        "data/paper1_reference_registry_v0_2_1.csv",
        "data/paper1_reference_registry_v0_4.csv",
        "data/paper1_ajb_appendix_mapping_v0_4.csv",
        "data/paper1_bibliographic_db_queries_v0_1.csv",
        "data/paper1_bibliographic_priority_screen_v0_1.csv",
        "docs/MICRO_ACCESSIBILITY_V0_2_RESULT.md",
        "docs/PAPER1_BIBLIOGRAPHIC_DB_SEARCH_2026-08-27.md",
        "docs/PAPER1_LITERATURE_SATURATION_TEST_2026-08-27.md",
        "docs/PAPER1_NOVELTY_LITERATURE_AUDIT_2026-08-27.md",
        "docs/PAPER1_NOVELTY_CORE_ATTACK_ADDENDUM_2026-08-27.md",
        "docs/EVIDENCE_AUDIT_2026-08-26.md",
    ]
    for src in provenance:
        cp(src, bundle / "provenance" / Path(src).name)
    cp("docs/PAPER1_AJB_UPLOAD_BUNDLE_V0_8_README.md", bundle / "README.md")

    # 9. Final cross-file audit + SHA256 manifest.
    run("scripts/audit_paper1_ajb_bundle_v0_8.py", "--bundle", str(bundle), "--out", str(bundle / "BUNDLE_MANIFEST.json"))
    manifest = json.loads((bundle / "BUNDLE_MANIFEST.json").read_text(encoding="utf-8"))
    print(json.dumps({k: v for k, v in manifest.items() if k != "files"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
