#!/usr/bin/env python3
"""Acquire article-level Larter et al. 2018 sources without coding traits.

No pigment row is parsed or attached to a tree here. The purpose is only to
recover machine-readable article/supplement bytes that can support a frozen
row-level trait audit later.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import urllib.parse
import urllib.request
from pathlib import Path

DOI = "10.1093/molbev/msy117"
UA = "chun-iochrominae-larter-source-audit/1.0"
NATURALIS_PDF = "https://www.naturalis.nl/system/files/inline/Larter%20et%20al%202018%20MBE%20-%20Convergent%20evolution%20at%20the%20pathway%20level%20predictable%20regulatory%20changes%20during%20flower%20color%20transitions.pdf"


def get(url: str, accept: str = "*/*"):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read(), r.geturl(), dict(r.headers)


def save(out: Path, name: str, raw: bytes, requested: str, resolved: str, headers: dict):
    target = out / name
    target.write_bytes(raw)
    return {
        "name": name,
        "requested": requested,
        "resolved": resolved,
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "content_type": headers.get("Content-Type"),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, required=True)
    a = ap.parse_args()
    a.out_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "doi": DOI,
        "scope": "ARTICLE_SOURCE_ACQUISITION_ONLY_NO_TRAIT_CODING_NO_ENDPOINT",
        "files": [],
        "errors": [],
        "pmcid": None,
        "biological_endpoint_computed": False,
    }

    q = urllib.parse.quote(f"DOI:{DOI}")
    search = f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={q}&format=json"
    try:
        raw, resolved, headers = get(search, "application/json,*/*")
        summary["files"].append(save(a.out_dir, "europepmc_search.json", raw, search, resolved, headers))
        obj = json.loads(raw)
        hits = obj.get("resultList", {}).get("result", [])
        for h in hits:
            if str(h.get("doi", "")).lower() == DOI.lower():
                summary["pmcid"] = h.get("pmcid")
                summary["europepmc_result"] = h
                break
    except Exception as e:
        summary["errors"].append({"source": "europepmc_search", "error": f"{type(e).__name__}: {e}"})

    pmcid = summary.get("pmcid")
    if pmcid:
        routes = {
            "fulltext.xml": f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML",
            "supplementary.zip": f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/supplementaryFiles",
        }
        for name, url in routes.items():
            try:
                raw, resolved, headers = get(url)
                if name.endswith(".zip") and raw[:2] != b"PK":
                    raise ValueError(f"supplement response is not ZIP: prefix={raw[:20]!r}")
                summary["files"].append(save(a.out_dir, name, raw, url, resolved, headers))
            except Exception as e:
                summary["errors"].append({"source": name, "url": url, "error": f"{type(e).__name__}: {e}"})

    try:
        raw, resolved, headers = get(NATURALIS_PDF, "application/pdf,*/*")
        if not raw.startswith(b"%PDF"):
            raise ValueError(f"Naturalis response is not PDF: prefix={raw[:20]!r}")
        summary["files"].append(save(a.out_dir, "lартer_2018_mbe.pdf".replace("арт", "art"), raw, NATURALIS_PDF, resolved, headers))
    except Exception as e:
        summary["errors"].append({"source": "naturalis_pdf", "url": NATURALIS_PDF, "error": f"{type(e).__name__}: {e}"})

    summary["machine_readable_article_source_recovered"] = any(
        f["name"] in {"fulltext.xml", "supplementary.zip"} for f in summary["files"]
    )
    summary["pdf_recovered"] = any(f["name"].endswith(".pdf") for f in summary["files"])
    summary["claim_boundary"] = "Source acquisition only. Raster/PDF appearance is not a permitted complete 28-row trait table under the frozen gate."
    (a.out_dir / "article_source_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "pmcid": summary["pmcid"],
        "machine_readable_article_source_recovered": summary["machine_readable_article_source_recovered"],
        "pdf_recovered": summary["pdf_recovered"],
        "errors": summary["errors"],
        "biological_endpoint_computed": False,
    }, indent=2))


if __name__ == "__main__":
    main()
