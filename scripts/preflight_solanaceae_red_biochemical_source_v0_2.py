#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import io
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V1 = ROOT / "scripts/preflight_solanaceae_red_biochemical_source_v0_1.py"

spec = importlib.util.spec_from_file_location("solanaceae_preflight_v01", V1)
if spec is None or spec.loader is None:
    raise RuntimeError("could not load v0.1 preflight module")
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)


def is_docx(payload: bytes) -> bool:
    if not payload.startswith(b"PK"):
        return False
    try:
        with zipfile.ZipFile(io.BytesIO(payload)) as zf:
            return "word/document.xml" in zf.namelist()
    except zipfile.BadZipFile:
        return False


def supplement_from_current_pmc_bin(pmcid: str, filename: str, out_dir: Path):
    urls = [
        f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/bin/{filename}",
        f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/bin/{filename}?download=1",
    ]
    attempts = []
    for url in urls:
        try:
            payload, final_url, content_type = base.fetch(url)
            ok = is_docx(payload)
            attempts.append({
                "method": "current_pmc_bin",
                "url": url,
                "final_url": final_url,
                "content_type": content_type,
                "bytes": len(payload),
                "sha256": base.sha256_bytes(payload),
                "is_docx": ok,
            })
            if ok:
                (out_dir / filename).write_bytes(payload)
                return payload, {
                    "attempts": attempts,
                    "selected_method": "current_pmc_bin",
                    "selected_url": url,
                    "selected_final_url": final_url,
                }
        except Exception as exc:
            attempts.append({
                "method": "current_pmc_bin",
                "url": url,
                "error": f"{type(exc).__name__}: {exc}",
            })
    return None, {"attempts": attempts, "selected_method": None}


def acquire_pmc_supplement(pmcid: str, filename: str, out_dir: Path):
    payload, oa = base.supplement_from_oa_package(pmcid, filename, out_dir)
    if payload is not None:
        return payload, {
            "oa_package": oa,
            "current_pmc_bin": None,
            "article_fallback": None,
        }

    payload, current = supplement_from_current_pmc_bin(pmcid, filename, out_dir)
    if payload is not None:
        return payload, {
            "oa_package": oa,
            "current_pmc_bin": current,
            "article_fallback": None,
        }

    payload, article = base.supplement_from_article_links(pmcid, filename, out_dir)
    if payload is not None:
        return payload, {
            "oa_package": oa,
            "current_pmc_bin": current,
            "article_fallback": article,
        }

    raise RuntimeError(
        "could not recover exact PMC supplement; OA + current-bin + article attempts="
        + json.dumps({"oa": oa, "current_pmc_bin": current, "article": article})
    )


base.acquire_pmc_supplement = acquire_pmc_supplement

if __name__ == "__main__":
    raise SystemExit(base.main())
