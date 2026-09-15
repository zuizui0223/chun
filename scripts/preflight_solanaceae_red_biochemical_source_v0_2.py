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


def supplement_from_europe_pmc(pmcid: str, filename: str, out_dir: Path):
    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/supplementaryFiles"
    attempts = []
    try:
        payload, final_url, content_type = base.fetch(url, timeout=120)
        rec = {
            "method": "europe_pmc_supplementaryFiles",
            "url": url,
            "final_url": final_url,
            "content_type": content_type,
            "bytes": len(payload),
            "sha256": base.sha256_bytes(payload),
            "is_zip": payload.startswith(b"PK"),
        }
        if not payload.startswith(b"PK"):
            attempts.append(rec)
            return None, {"attempts": attempts, "selected_method": None}
        with zipfile.ZipFile(io.BytesIO(payload)) as zf:
            matches = [name for name in zf.namelist() if Path(name).name == filename]
            rec["matching_members"] = matches
            attempts.append(rec)
            if len(matches) != 1:
                return None, {"attempts": attempts, "selected_method": None}
            docx = zf.read(matches[0])
        ok = is_docx(docx)
        attempts.append({
            "method": "europe_pmc_member",
            "member": matches[0],
            "bytes": len(docx),
            "sha256": base.sha256_bytes(docx),
            "is_docx": ok,
        })
        if ok:
            (out_dir / filename).write_bytes(docx)
            return docx, {
                "attempts": attempts,
                "selected_method": "europe_pmc_supplementaryFiles",
                "selected_url": url,
                "selected_member": matches[0],
            }
    except Exception as exc:
        attempts.append({
            "method": "europe_pmc_supplementaryFiles",
            "url": url,
            "error": f"{type(exc).__name__}: {exc}",
        })
    return None, {"attempts": attempts, "selected_method": None}


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
            "europe_pmc": None,
            "current_pmc_bin": None,
            "article_fallback": None,
        }

    payload, europe = supplement_from_europe_pmc(pmcid, filename, out_dir)
    if payload is not None:
        return payload, {
            "oa_package": oa,
            "europe_pmc": europe,
            "current_pmc_bin": None,
            "article_fallback": None,
        }

    payload, current = supplement_from_current_pmc_bin(pmcid, filename, out_dir)
    if payload is not None:
        return payload, {
            "oa_package": oa,
            "europe_pmc": europe,
            "current_pmc_bin": current,
            "article_fallback": None,
        }

    payload, article = base.supplement_from_article_links(pmcid, filename, out_dir)
    if payload is not None:
        return payload, {
            "oa_package": oa,
            "europe_pmc": europe,
            "current_pmc_bin": current,
            "article_fallback": article,
        }

    raise RuntimeError(
        "could not recover exact PMC supplement; OA + EuropePMC + current-bin + article attempts="
        + json.dumps({
            "oa": oa,
            "europe_pmc": europe,
            "current_pmc_bin": current,
            "article": article,
        })
    )


base.acquire_pmc_supplement = acquire_pmc_supplement

if __name__ == "__main__":
    raise SystemExit(base.main())
