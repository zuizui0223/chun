from __future__ import annotations
import importlib.util, hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts"/"recheck_iochrominae_dryad_access_v0_3.py"
spec=importlib.util.spec_from_file_location("r",SCRIPT)
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

def test_collect_candidate_urls_recurses_links_and_deduplicates():
    x={"_links":{"self":{"href":"https://x/a"},"stash:download":{"href":"https://x/d"}},"nested":[{"href":"https://x/d"}]}
    assert mod.collect_candidate_urls(x)==["https://x/a","https://x/d"]

def test_exact_match_requires_size_and_digest():
    body=b"abc"
    meta={"size":3,"digestType":"md5","digest":hashlib.md5(body).hexdigest()}
    assert mod.exact_match(meta,body) is True
    assert mod.exact_match(meta,b"abcd") is False
