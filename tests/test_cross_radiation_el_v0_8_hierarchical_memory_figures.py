from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts"/"build_cross_radiation_el_v0_8_hierarchical_memory_figures.py"

spec=importlib.util.spec_from_file_location("figs",SCRIPT)
if spec is None or spec.loader is None:
    raise RuntimeError("figure builder cannot be loaded")
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_figure_specs_include_prospective_schistanthe_in_figure5():
    specs=mod.figure_specs()
    assert [x["figure"] for x in specs]==[1,2,3,4,5]
    assert [x["filename"] for x in specs]==[
        "fig1_memory_architecture.png",
        "fig2_hidden_memory_clades.png",
        "fig3_hidden_vs_global_tilt.png",
        "fig4_petunieae_hidden_memory.png",
        "fig5_evidence_tiers.png",
    ]
    f5=specs[-1]
    assert "results/schistanthe_hidden_memory_v0_1/result_v0_1.json" in f5["sources"]
    assert "data/hierarchical_evolutionary_memory_synthesis_v0_2.json" in f5["sources"]


def test_standardized_clade_join_is_unchanged():
    d=mod.load_hidden_architecture_join()
    assert len(d)==21
    assert (d["centered_auc_effect"]>0).sum()==18
    assert (d["scale_tilt"]<0).sum()==6
    assert ((d["scale_tilt"]<0)&(d["centered_auc_effect"]>0)).sum()==5


def test_build_all_produces_five_pngs_and_v08_manifest(tmp_path):
    manifest=mod.build_all(tmp_path)
    assert manifest["status"]=="EL_V0_8_HIERARCHICAL_MEMORY_FIGURES_BUILT"
    assert manifest["candidate"]=="Evolution Letters v0.8 hierarchical memory with Schistanthe"
    assert manifest["current_submission_unchanged"]=="Evolution Letters v0.3"
    assert len(manifest["figures"])==5
    for row in manifest["figures"]:
        p=tmp_path/row["filename"]
        assert p.is_file()
        assert p.read_bytes()[:8]==b"\x89PNG\r\n\x1a\n"
        assert p.stat().st_size>1000
    assert (tmp_path/"figure_build_manifest_v0_1.json").is_file()
