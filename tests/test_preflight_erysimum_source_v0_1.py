from __future__ import annotations

import importlib.util
import io
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts"/"preflight_erysimum_source_v0_1.py"
spec=importlib.util.spec_from_file_location("e",SCRIPT)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_archive_inventory_and_code_evidence():
    b=io.BytesIO()
    with zipfile.ZipFile(b,"w") as z:
        z.writestr("Script.R",'d <- read.csv("traits.csv")\ncorolla.color <- factor(x, labels=c("yellow","lilac","white"))\nt <- read.tree("tree.tre")\n')
        z.writestr("traits.csv","species,color\nA,yellow\n")
        z.writestr("tree.tre","(A:1,B:1);")
    inv=mod.archive_inventory(b.getvalue())
    assert {x["path"] for x in inv}=={"Script.R","traits.csv","tree.tre"}
    ev=mod.code_evidence(b.getvalue())
    assert ev and ev[0]["path"]=="Script.R"
    trees=mod.tree_candidates(b.getvalue())
    assert trees[0]["tip_count"]==2
    assert trees[0]["missing_nonroot_branch_lengths"]==0


def test_verify_md5_metadata():
    body=b"abc"
    x=mod.verify_against_metadata(body,{"size":3,"digest":"md5:900150983cd24fb0d6963f7d28e17f72"})
    assert x["size_match"] is True
    assert x["digest_match"] is True


def test_file_name_variants():
    assert mod.file_name({"path":"x.zip"})=="x.zip"
    assert mod.file_name({"filename":"y.zip"})=="y.zip"


def test_dedupe_file_objects_collapses_same_identity():
    o={
      "path":mod.PACKAGE,
      "id":123,
      "size":456,
      "digest":"md5:900150983cd24fb0d6963f7d28e17f72",
      "_links":{"stash:download":{"href":"https://datadryad.org/api/v2/files/123/download"}}
    }
    out=mod.dedupe_file_objects([dict(o),dict(o),dict(o)])
    assert len(out)==1
