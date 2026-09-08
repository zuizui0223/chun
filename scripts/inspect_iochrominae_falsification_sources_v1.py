#!/usr/bin/env python3
"""Signal-blind source audit for prospective Iochrominae fine-state falsification.

This script only inventories source bytes and asks whether a machine-readable terminal
trait table and a resolved machine-readable topology are recoverable. It never computes
an observed Sankoff/Fitch score, never reads colours from a plotted figure, and never
infers terminal pigment classes from hue or from prose.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import subprocess
import urllib.parse
import zipfile
from pathlib import Path

import requests

OUT = Path("analysis/_generated/iochrominae_falsification_source_v1")
UA = {"User-Agent": "chun-iochrominae-falsification-source-audit/1.0 (+https://github.com/zuizui0223/chun)"}
DRYAD = {
    "TREE_2018": "10.5061/dryad.5jn7b",
    "DEV_2019": "10.5061/dryad.p5dq84v",
}
ARTICLE = "https://academic.oup.com/mbe/article/35/9/2159/5034462"
SPECIES_TOKENS = (
    "iochroma", "acnistus", "dunalia", "saracha", "vassobia", "eriolarynx"
)
PIGMENT_TOKENS = ("delphinidin", "cyanidin", "pelargonidin", "anthocyanidin")


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def get(url: str, accept: str = "*/*"):
    try:
        r = requests.get(url, headers={**UA, "Accept": accept}, timeout=90, allow_redirects=True)
        return {
            "requested": url,
            "resolved": r.url,
            "status": r.status_code,
            "content_type": r.headers.get("content-type", ""),
            "bytes": len(r.content),
            "sha256": sha(r.content) if r.ok and r.content else None,
            "raw": r.content if r.ok else b"",
        }
    except Exception as e:
        return {"requested": url, "resolved": None, "status": None, "error": repr(e), "bytes": 0, "sha256": None, "raw": b""}


def json_get(url: str):
    x = get(url, "application/json,*/*")
    if not x["raw"]:
        return x, None
    try:
        return x, json.loads(x["raw"])
    except Exception as e:
        x["json_error"] = repr(e)
        return x, None


def hrefs(obj):
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "href" and isinstance(v, str):
                out.append(v)
            else:
                out.extend(hrefs(v))
    elif isinstance(obj, list):
        for v in obj:
            out.extend(hrefs(v))
    return out


def normalize_dryad(url: str) -> str:
    if url.startswith("/"):
        return "https://datadryad.org" + url
    return url


def flatten_records(obj):
    vals = []
    if isinstance(obj, list):
        vals.extend(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            if isinstance(v, list):
                vals.extend(x for x in v if isinstance(x, dict))
            elif isinstance(v, dict):
                vals.extend(flatten_records(v))
    return vals


def discover_dryad(doi: str, ddir: Path):
    enc = urllib.parse.quote("doi:" + doi, safe="")
    api = f"https://datadryad.org/api/v2/datasets/{enc}"
    meta_req, meta = json_get(api)
    result = {"doi": doi, "metadata_request": {k: v for k, v in meta_req.items() if k != "raw"}, "files": []}
    if not isinstance(meta, dict):
        result["status"] = "METADATA_UNAVAILABLE"
        return result
    (ddir / "dataset_metadata.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")

    candidate_file_urls = [normalize_dryad(h) for h in hrefs(meta) if "files" in h.lower()]
    version_urls = [normalize_dryad(h) for h in hrefs(meta) if "versions" in h.lower()]
    for vu in version_urls[:3]:
        vr, vo = json_get(vu)
        if vo is not None:
            for h in hrefs(vo):
                if "files" in h.lower():
                    candidate_file_urls.append(normalize_dryad(h))
            # Some API versions embed version records rather than file hrefs.
            for rec in flatten_records(vo):
                for h in hrefs(rec):
                    if "files" in h.lower():
                        candidate_file_urls.append(normalize_dryad(h))
    candidate_file_urls += [api + "/versions"]

    file_records = []
    file_collection_requests = []
    seen = set()
    for fu in candidate_file_urls:
        if fu in seen:
            continue
        seen.add(fu)
        fr, fo = json_get(fu)
        file_collection_requests.append({k: v for k, v in fr.items() if k != "raw"})
        if fo is None:
            continue
        records = flatten_records(fo)
        records = [r for r in records if any(k in r for k in ("id", "fileId", "path", "filename", "name"))]
        if records:
            file_records.extend(records)
    # De-duplicate by id/name tuple.
    uniq = []
    keys = set()
    for f in file_records:
        fid = f.get("id") or f.get("fileId") or f.get("file_id")
        name = f.get("path") or f.get("filename") or f.get("name")
        k = (str(fid), str(name))
        if k not in keys:
            keys.add(k)
            uniq.append(f)
    result["file_collection_requests"] = file_collection_requests
    (ddir / "file_records.json").write_text(json.dumps(uniq, indent=2) + "\n", encoding="utf-8")

    extracted = ddir / "extracted"
    extracted.mkdir(parents=True, exist_ok=True)
    for i, f in enumerate(uniq):
        fid = str(f.get("id") or f.get("fileId") or f.get("file_id") or "")
        name = str(f.get("path") or f.get("filename") or f.get("name") or f"file_{i}")
        routes = []
        for h in hrefs(f):
            if "download" in h.lower() or "/files/" in h.lower():
                routes.append(normalize_dryad(h))
        if fid.isdigit():
            routes += [
                f"https://datadryad.org/stash/downloads/file_stream/{fid}",
                f"https://datadryad.org/api/v2/files/{fid}/download",
            ]
        attempts = []
        raw = b""
        chosen = None
        for route in dict.fromkeys(routes):
            rr = get(route, "application/octet-stream,*/*")
            attempts.append({k: v for k, v in rr.items() if k != "raw"})
            if rr["raw"]:
                raw = rr["raw"]
                chosen = rr
                break
        rec = {"id": fid or None, "name": name, "attempts": attempts, "downloaded": bool(raw)}
        if raw:
            safe = Path(name).name
            p = ddir / safe
            p.write_bytes(raw)
            rec.update({"bytes": len(raw), "sha256": sha(raw), "saved_as": safe, "resolved": chosen["resolved"]})
            if zipfile.is_zipfile(io.BytesIO(raw)):
                zdir = extracted / (safe + "_zip")
                zdir.mkdir(exist_ok=True)
                with zipfile.ZipFile(io.BytesIO(raw)) as zf:
                    for m in zf.infolist():
                        if m.is_dir():
                            continue
                        q = zdir / Path(m.filename).name
                        q.write_bytes(zf.read(m))
        result["files"].append(rec)
    result["status"] = "DISCOVERED"
    return result


def scan_text_candidate(path: Path):
    try:
        raw = path.read_bytes()
        if len(raw) > 10_000_000:
            return None
        text = raw.decode("utf-8", errors="ignore")
    except Exception:
        return None
    low = text.lower()
    sp = sum(tok in low for tok in SPECIES_TOKENS)
    pg = sum(tok in low for tok in PIGMENT_TOKENS)
    if sp and pg:
        # This is only a source-schema candidate. It is NOT admitted as a terminal-state map.
        return {"path": str(path), "bytes": len(raw), "sha256": sha(raw), "species_token_hits": sp, "pigment_token_hits": pg}
    return None


def scan_xlsx_candidate(path: Path):
    try:
        import openpyxl
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    except Exception:
        return []
    out = []
    for ws in wb.worksheets:
        rows = []
        for ri, row in enumerate(ws.iter_rows(values_only=True)):
            vals = ["" if v is None else str(v).strip() for v in row]
            if any(vals):
                rows.append(vals)
            if ri > 5000:
                break
        blob = "\n".join("\t".join(r) for r in rows).lower()
        sp = sum(tok in blob for tok in SPECIES_TOKENS)
        pg = sum(tok in blob for tok in PIGMENT_TOKENS)
        if sp and pg:
            out.append({"path": str(path), "sheet": ws.title, "nonempty_rows": len(rows), "species_token_hits": sp, "pigment_token_hits": pg})
    return out


def audit_oup(out: Path):
    r = get(ARTICLE, "text/html,*/*")
    rec = {"article": {k: v for k, v in r.items() if k != "raw"}, "supplement_links": [], "downloads": []}
    if not r["raw"]:
        return rec
    html = r["raw"].decode("utf-8", errors="ignore")
    links = re.findall(r'href=["\']([^"\']+)["\']', html, flags=re.I)
    links = [urllib.parse.urljoin(ARTICLE, x) for x in links]
    links = [x for x in links if any(k in x.lower() for k in ("supp", "msy117_s", "silverchair-cdn"))]
    rec["supplement_links"] = list(dict.fromkeys(links))[:50]
    sdir = out / "oup"
    sdir.mkdir(exist_ok=True)
    for i, url in enumerate(rec["supplement_links"]):
        rr = get(url)
        d = {k: v for k, v in rr.items() if k != "raw"}
        if rr["raw"]:
            suffix = Path(urllib.parse.urlparse(rr["resolved"]).path).suffix or ".bin"
            p = sdir / f"supp_{i:02d}{suffix[:8]}"
            p.write_bytes(rr["raw"])
            d["saved_as"] = str(p)
        rec["downloads"].append(d)
    return rec


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    dryad_results = {}
    for key, doi in DRYAD.items():
        ddir = OUT / key.lower()
        ddir.mkdir(exist_ok=True)
        dryad_results[key] = discover_dryad(doi, ddir)
    oup = audit_oup(OUT)

    # Inventory every recovered source object. No figure raster/OCR is permitted here.
    text_candidates = []
    xlsx_candidates = []
    tree_candidates = []
    for p in OUT.rglob("*"):
        if not p.is_file():
            continue
        suf = p.suffix.lower()
        if suf in {".xlsx", ".xlsm"}:
            xlsx_candidates.extend(scan_xlsx_candidate(p))
        elif suf in {".csv", ".tsv", ".txt", ".r", ".rdata", ".rds", ".nex", ".nexus", ".tre", ".tree", ".treefile", ".nwk", ".newick"}:
            c = scan_text_candidate(p)
            if c:
                text_candidates.append(c)
        if suf in {".nex", ".nexus", ".tre", ".tree", ".treefile", ".nwk", ".newick"}:
            try:
                txt = p.read_text(encoding="utf-8", errors="ignore")
                tree_candidates.append({"path": str(p), "bytes": p.stat().st_size, "sha256": sha(p.read_bytes()), "has_newick_parens": "(" in txt and ")" in txt})
            except Exception:
                pass

    # A candidate file containing both taxon and pigment words is NOT enough for admission.
    # Human/source audit must establish that it explicitly maps terminal taxon -> one of the
    # four primary classes. Until then trait_source_admission remains false by construction.
    summary = {
        "version": "v1",
        "source_only": True,
        "endpoint_computed": False,
        "figure_terminal_colours_read": False,
        "dryad": dryad_results,
        "oup": oup,
        "schema_candidates": {"text": text_candidates, "xlsx": xlsx_candidates},
        "tree_candidates": tree_candidates,
        "trait_source_admission": False,
        "trait_source_admission_reason": "No recovered object is auto-promoted merely from token co-occurrence; explicit terminal taxon-to-primary-anthocyanidin mapping must be audited before admission.",
        "next_status_if_no_explicit_mapping": "HOLD_TRAIT_SOURCE",
        "claim_boundary": "Source retrieval/inventory only. No terminal pigment class is inferred from hue, prose, or plotted figure colours and no phylogenetic signal statistic is computed."
    }
    (OUT / "source_audit.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    compact = {
        "dryad": {k: {"doi": v.get("doi"), "status": v.get("status"), "files": [{"id": f.get("id"), "name": f.get("name"), "downloaded": f.get("downloaded"), "attempts": [{"status": a.get("status"), "requested": a.get("requested")} for a in f.get("attempts", [])]} for f in v.get("files", [])]} for k, v in dryad_results.items()},
        "oup_supplement_links": len(oup.get("supplement_links", [])),
        "oup_downloads_ok": sum(bool(x.get("sha256")) for x in oup.get("downloads", [])),
        "text_schema_candidates": text_candidates,
        "xlsx_schema_candidates": xlsx_candidates,
        "tree_candidates": tree_candidates,
        "trait_source_admission": False,
        "endpoint_computed": False,
    }
    print("IOCHROMINAE_SOURCE_AUDIT=" + json.dumps(compact, ensure_ascii=False))


if __name__ == "__main__":
    main()
