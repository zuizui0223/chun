from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "fetch_pmc_cloud_media_v0_1.py"
spec = importlib.util.spec_from_file_location("pmc_cloud", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_s3_media_url_maps_to_https_and_preserves_md5():
    url, md5 = mod.s3_to_https(
        "s3://pmc-oa-opendata/PMC12946509.1/PBI-24-1725-s002.xlsx"
        "?md5=7e89c77d11b9fd273f9cf491a930885d"
    )
    assert url == (
        "https://pmc-oa-opendata.s3.amazonaws.com/"
        "PMC12946509.1/PBI-24-1725-s002.xlsx"
    )
    assert md5 == "7e89c77d11b9fd273f9cf491a930885d"


def test_choose_version_prefers_published_open_access_then_latest():
    rows = [
        {"version": 1, "is_pmc_openaccess": True, "is_manuscript": True},
        {"version": 2, "is_pmc_openaccess": True, "is_manuscript": False},
        {"version": 3, "is_pmc_openaccess": True, "is_manuscript": True},
    ]
    assert mod.choose_version(rows)["version"] == 2


def test_invalid_pmcid_is_rejected_before_network():
    try:
        mod.list_versions("12946509")
    except ValueError as exc:
        assert "invalid PMCID" in str(exc)
    else:
        raise AssertionError("invalid PMCID was accepted")
