import importlib.util
import io
import json
import zipfile
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location(
    "recover_iochrominae_original_sources",
    ROOT/"scripts/recover_iochrominae_official_source_20261116.py")
m=importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(m)


def test_official_original_source_hosts_only():
    assert m.supported_url("https://oup.silverchair-cdn.com/oup/backfile/msy117_supp.pdf")
    assert m.supported_url("https://api.datadryad.org/api/v2/datasets/example")
    assert not m.supported_url("https://evil.example/msy117_supp.pdf")
    assert not m.supported_url("http://academic.oup.com/mbe/article")
    assert not m.supported_url("file:///etc/passwd")
    with pytest.raises(ValueError,match="allowlist"):
        m.download("file:///etc/passwd")


def test_signed_link_extracts_only_provider_owned_link_and_does_not_print_signature():
    article=(b'<a href="https://oup.silverchair-cdn.com/oup/backfile/msy117_supp.pdf?'
             b'Expires=123&amp;Signature=topsecret">supplement</a>')
    url=m.signed_publisher_url(article)
    assert url=="https://oup.silverchair-cdn.com/oup/backfile/msy117_supp.pdf?Expires=123&Signature=topsecret"
    assert "Signature=" not in m.sanitized(url)
    assert m.signed_publisher_url(
        b'<a href="https://evil.example/msy117_supp.pdf">malicious</a>') is None


def test_zip_contents_report_metadata_only():
    b=io.BytesIO()
    with zipfile.ZipFile(b,"w") as zf:
        zf.writestr("tree.nex","#NEXUS\n")
        zf.writestr("data/species_hplc.csv","species,measurement\nA,1\n")
    out=m.inspect(b.getvalue(),"official_archive")
    assert out["format"]=="ZIP"
    assert len(out["zip_file_list"])==2
    assert all("uncompressed_bytes" in f for f in out["zip_file_list"])
    assert "payload" not in out
    assert out["sha256"]


def test_json_archive_metadata_is_only_receipt():
    data=b'{"id":123,"title":"archived tree","_links":{"stash:files":{"href":"/api"}}}'
    result=m.inspect(data,"official_dryad_metadata")
    assert result["format"]=="JSON"
    assert result["json_links_or_identifier"]["id"]=="123"
    assert "payload" not in result


def test_alternative_shape_tree_never_overrides_original_gene_metabolite_join():
    doc=ROOT/"results/iochrominae_alternative_tree_archive_route_20261115.json"
    r=json.loads(doc.read_text())
    assert r["newly_identified_source"]["exact_2018_Larter_tree_substitution_authorized"] is False
    assert r["newly_identified_source"]["original_2015_tree_equivalence"]=="UNVERIFIED"
    assert r["no_cross_radiation_replication"]
