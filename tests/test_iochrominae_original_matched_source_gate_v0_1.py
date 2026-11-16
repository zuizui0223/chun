import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location(
    "iochrominae_source_admission",
    ROOT/"scripts/audit_iochrominae_original_matched_source_gate_v0_1.py")
m=importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(m)


def fixture(tmp_path):
    h=tmp_path/"h.csv"
    q=tmp_path/"q.csv"
    t=tmp_path/"tree.nwk"
    names=["A","B","C","D","E","F"]
    h.write_text("species,anthocyanidin_mgg,flavonol_mgg\n"+
                 "".join(f"{n},1.2,0.5\n" for n in names))
    q.write_text("species,CHI,DFR\n"+
                 "".join(f"{n},2.5,1.2\n" for n in names))
    t.write_text("((A:1,B:1):1,(C:1,D:1):1,(E:1,F:1):1);\n")
    def row(path,cols=None):
        return {"path":str(path),"original_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
                "original_source_url":"https://example.org/original",
                "source_publication":"source published study",
                "species_column":"species","numeric_columns":cols}
    manifest={"hplc":row(h,["anthocyanidin_mgg","flavonol_mgg"]),
              "qpcr":row(q,["CHI","DFR"]),
              "dated_tree":{**row(t),"original_author_used_tree_verified":True}}
    # Synthetic reviewer fixture; this is NOT a real provider attestation.
    manifest["independent_provenance_review"]={
        "status":"VERIFIED","reviewer":"synthetic-test-only",
        "evidence_url":"https://example.org/synthetic-review",
        "sha256_by_source":{key:manifest[key]["original_sha256"]
                            for key in ("hplc","qpcr","dated_tree")}}
    return manifest


def test_same_original_source_all_three_layers_admitted(tmp_path):
    d=fixture(tmp_path)
    result=m.audit(d)
    assert result["status"]=="ADMIT_RAW_MATCHED_SOURCE_FRAME_NOT_AN_EFFECT_RESULT"
    assert result["n_complete_tips"]==6
    assert result["n_shared_tips"]==6
    assert result["no_gene_to_metabolite_prediction_computed"]


def test_unverified_alternative_phylogeny_is_never_admitted(tmp_path):
    d=fixture(tmp_path)
    d["dated_tree"]["original_author_used_tree_verified"]=False
    with pytest.raises(ValueError,match="different study tree"):
        m.audit(d)


def test_raw_hplc_byte_change_or_missing_receipt_rejected(tmp_path):
    d=fixture(tmp_path)
    Path(d["hplc"]["path"]).write_text("species,anthocyanidin_mgg\nA,1\n")
    with pytest.raises(ValueError,match="hash mismatch"):
        m.audit(d)
    d=fixture(tmp_path)
    d["qpcr"]["original_sha256"]=None
    with pytest.raises(ValueError,match="SHA256"):
        m.audit(d)


def test_duplicate_replicate_taxa_not_silently_averaged(tmp_path):
    d=fixture(tmp_path)
    q=Path(d["qpcr"]["path"])
    q.write_text(q.read_text()+"A,2.5,1.2\n")
    d["qpcr"]["original_sha256"]=hashlib.sha256(q.read_bytes()).hexdigest()
    d["independent_provenance_review"]["sha256_by_source"]["qpcr"]=d["qpcr"]["original_sha256"]
    with pytest.raises(ValueError,match="replicate rows"):
        m.audit(d)


def test_non_numeric_measurements_do_not_create_complete_tip(tmp_path):
    d=fixture(tmp_path)
    q=Path(d["qpcr"]["path"])
    q.write_text(q.read_text().replace("F,2.5,1.2","F,NA,1.2"))
    d["qpcr"]["original_sha256"]=hashlib.sha256(q.read_bytes()).hexdigest()
    d["independent_provenance_review"]["sha256_by_source"]["qpcr"]=d["qpcr"]["original_sha256"]
    result=m.audit(d)
    assert result["n_shared_tips"]==6
    assert result["n_complete_tips"]==5
    assert "F" not in result["complete_original_tip_names"]


def test_missing_branch_lengths_and_missing_source_rejected(tmp_path):
    d=fixture(tmp_path)
    tree=Path(d["dated_tree"]["path"])
    tree.write_text("((A,B),(C,D),(E,F));\n")
    d["dated_tree"]["original_sha256"]=hashlib.sha256(tree.read_bytes()).hexdigest()
    d["independent_provenance_review"]["sha256_by_source"]["dated_tree"]=d["dated_tree"]["original_sha256"]
    with pytest.raises(ValueError,match="branch lengths absent"):
        m.audit(d)
    d=fixture(tmp_path)
    d["dated_tree"]["path"]=str(tmp_path/"no.nwk")
    with pytest.raises(ValueError,match="missing"):
        m.audit(d)


def test_self_attested_original_source_is_not_admitted_without_external_review(tmp_path):
    d=fixture(tmp_path)
    del d["independent_provenance_review"]
    with pytest.raises(ValueError,match="independent original-source provenance"):
        m.audit(d)
    d=fixture(tmp_path)
    d["independent_provenance_review"]["sha256_by_source"]["hplc"]="0"*64
    with pytest.raises(ValueError,match="independent review hash"):
        m.audit(d)
    d=fixture(tmp_path)
    d["independent_provenance_review"]["evidence_url"]="unverifiable-local-note"
    with pytest.raises(ValueError,match="web-accessible"):
        m.audit(d)
