#!/usr/bin/env python3
"""Acquire/inventory Iochrominae falsification sources without computing an endpoint.

This script is deliberately source-only. It may retrieve tree/trait archives and
TreeBASE text, but it must not join observed pigment assignments to topology or
compute any phylogenetic signal statistic.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

UA = "chun-iochrominae-falsification-source-audit/1.0"

DRYAD = {
    "TREE_2018": "10.5061/dryad.5jn7b",
    "TRAIT_MECHANISM_2018": "10.5061/dryad.p5dq84v",
    "TEMPO_COLOUR_2015": "10.5061/dryad.0732g",
}

TREEBASE_URLS = {
    "nexus_https": "https://purl.org/phylo/treebase/phylows/study/TB2:S1553?format=nexus",
    "nexml_https": "https://purl.org/phylo/treebase/phylows/study/TB2:S1553?format=nexml",
    "nexus_http": "http://purl.org/phylo/treebase/phylows/study/TB2:S1553?format=nexus",
}


def req(url: str, accept: str = "*/*"):
    r = urllib.request.Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept": accept,
            "Referer": "https://github.com/zuizui0223/chun",
        },
    )
    with urllib.request.urlopen(r, timeout=90) as h:
        return h.read(), h.geturl(), dict(h.headers)


def json_req(url: str):
    raw, resolved, headers = req(url, "application/json,*/*")
    return json.loads(raw), resolved, headers


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


def abs_dryad(url: str):
    if url.startswith("/"):
        return "https://datadryad.org" + url
    return url


def numeric_file_id(rec):
    for k in ("id", "fileId", "file_id"):
        if rec.get(k) is not None:
            return str(rec[k])
    for h in hrefs(rec):
        parts = [x for x in urllib.parse.urlparse(h).path.split("/") if x]
        for i, p in enumerate(parts):
            if p == "files" and i + 1 < len(parts) and parts[i + 1].isdigit():
                return parts[i + 1]
    return None


def flatten_records(obj):
    if isinstance(obj, list):
        return obj
    out = []
    if isinstance(obj, dict):
        for k in ("files", "versions", "stash:files", "stash:versions"):
            v = obj.get(k)
            if isinstance(v, list):
                out.extend(v)
        emb = obj.get("_embedded")
        if isinstance(emb, dict):
            for v in emb.values():
                if isinstance(v, list):
                    out.extend(v)
    return out


def choose_latest_version(meta, api):
    candidates = []
    for h in hrefs(meta):
        if "versions" in h.lower():
            candidates.append(abs_dryad(h))
    candidates.append(api + "/versions")
    errors = []
    for url in dict.fromkeys(candidates):
        try:
            obj, resolved, _ = json_req(url)
            vals = flatten_records(obj)
            if vals:
                def rank(x):
                    for k in ("versionNumber", "version", "id"):
                        v = x.get(k)
                        if isinstance(v, (int, float)):
                            return float(v)
                        if isinstance(v, str) and re.fullmatch(r"\d+(?:\.\d+)?", v):
                            return float(v)
                    return 0.0
                return max(vals, key=rank), resolved, errors
            if isinstance(obj, dict) and any(k in obj for k in ("versionNumber", "version")):
                return obj, resolved, errors
        except Exception as e:
            errors.append({"url": url, "error": f"{type(e).__name__}: {e}"})
    return meta, api, errors


def get_file_records(version, api):
    candidates = []
    for h in hrefs(version):
        if "files" in h.lower():
            candidates.append(abs_dryad(h))
    vid = version.get("id") or version.get("versionNumber")
    if vid is not None:
        candidates.append(f"https://datadryad.org/api/v2/versions/{vid}/files")
    candidates.append(api + "/files")
    errors = []
    for url in dict.fromkeys(candidates):
        try:
            obj, resolved, _ = json_req(url)
            vals = flatten_records(obj)
            if vals:
                return vals, resolved, errors
        except Exception as e:
            errors.append({"url": url, "error": f"{type(e).__name__}: {e}"})
    return [], None, errors


def file_name(rec, i):
    return str(rec.get("path") or rec.get("filename") or rec.get("name") or f"file_{i:03d}")


def file_routes(rec):
    routes = []
    for h in hrefs(rec):
        if "download" in h.lower() or "/files/" in h.lower():
            routes.append(abs_dryad(h))
    fid = numeric_file_id(rec)
    if fid:
        routes.extend([
            f"https://datadryad.org/stash/downloads/file_stream/{fid}",
            f"https://datadryad.org/api/v2/files/{fid}/download",
        ])
    return list(dict.fromkeys(routes))


def acquire_dryad(key: str, doi: str, out: Path):
    ddir = out / key.lower()
    ddir.mkdir(parents=True, exist_ok=True)
    api = "https://datadryad.org/api/v2/datasets/" + urllib.parse.quote("doi:" + doi, safe="")
    result = {
        "dataset_id": key,
        "doi": doi,
        "api": api,
        "metadata_ok": False,
        "file_inventory_ok": False,
        "downloaded_count": 0,
        "files": [],
        "errors": [],
    }
    try:
        meta, resolved, _ = json_req(api)
        result["metadata_ok"] = True
        result["metadata_resolved"] = resolved
        result["identifier"] = meta.get("identifier")
        (ddir / "dataset_metadata.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    except Exception as e:
        result["errors"].append({"stage": "metadata", "error": f"{type(e).__name__}: {e}"})
        return result

    version, vresolved, verr = choose_latest_version(meta, api)
    result["version_resolved"] = vresolved
    result["errors"].extend({"stage": "versions", **x} for x in verr)
    files, fresolved, ferr = get_file_records(version, api)
    result["files_resolved"] = fresolved
    result["errors"].extend({"stage": "files", **x} for x in ferr)
    result["file_inventory_ok"] = bool(files)
    (ddir / "file_inventory.json").write_text(json.dumps(files, indent=2) + "\n", encoding="utf-8")

    extracted = ddir / "downloaded"
    extracted.mkdir(exist_ok=True)
    for i, rec in enumerate(files):
        name = file_name(rec, i)
        fid = numeric_file_id(rec)
        entry = {
            "name": name,
            "file_id": fid,
            "routes": file_routes(rec),
            "downloaded": False,
            "attempts": [],
        }
        for route in entry["routes"]:
            try:
                raw, resolved, headers = req(route, "application/octet-stream,*/*")
                if not raw:
                    raise ValueError("empty response")
                safe = re.sub(r"[^A-Za-z0-9._-]+", "_", Path(name).name) or f"file_{i:03d}"
                target = extracted / f"{i:03d}_{safe}"
                target.write_bytes(raw)
                entry.update({
                    "downloaded": True,
                    "resolved": resolved,
                    "bytes": len(raw),
                    "sha256": hashlib.sha256(raw).hexdigest(),
                    "saved_as": target.name,
                    "content_type": headers.get("Content-Type"),
                })
                result["downloaded_count"] += 1
                break
            except Exception as e:
                entry["attempts"].append({"route": route, "error": f"{type(e).__name__}: {e}"})
        result["files"].append(entry)
    return result


def acquire_treebase(out: Path):
    tdir = out / "treebase_s1553"
    tdir.mkdir(parents=True, exist_ok=True)
    result = {"study": "TB2:S1553", "attempts": [], "retrieved": []}
    for key, url in TREEBASE_URLS.items():
        try:
            raw, resolved, headers = req(url, "application/x-nexus,application/xml,text/plain,*/*")
            suffix = ".xml" if "xml" in (headers.get("Content-Type") or "").lower() or key.startswith("nexml") else ".nex"
            target = tdir / f"{key}{suffix}"
            target.write_bytes(raw)
            rec = {
                "key": key,
                "requested": url,
                "resolved": resolved,
                "bytes": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
                "content_type": headers.get("Content-Type"),
                "saved_as": target.name,
            }
            result["retrieved"].append(rec)
        except Exception as e:
            result["attempts"].append({"key": key, "url": url, "error": f"{type(e).__name__}: {e}"})
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    summary = {
        "version": "v1",
        "scope": "SOURCE_ACQUISITION_ONLY_NO_TRAIT_TREE_JOIN_NO_ENDPOINT",
        "dryad": [],
        "treebase": None,
    }
    for key, doi in DRYAD.items():
        summary["dryad"].append(acquire_dryad(key, doi, args.out_dir))
    summary["treebase"] = acquire_treebase(args.out_dir)
    summary["any_2018_tree_bytes"] = any(
        d["dataset_id"] == "TREE_2018" and d["downloaded_count"] > 0 for d in summary["dryad"]
    )
    summary["any_trait_source_bytes"] = any(
        d["dataset_id"] in {"TRAIT_MECHANISM_2018", "TEMPO_COLOUR_2015"} and d["downloaded_count"] > 0
        for d in summary["dryad"]
    )
    summary["treebase_retrieved"] = bool(summary["treebase"]["retrieved"])
    summary["biological_endpoint_computed"] = False
    summary["claim_boundary"] = "Acquisition/inventory only; no pigment-to-tree join and no biological support/refutation inference."
    (args.out_dir / "source_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "tree_2018_bytes": summary["any_2018_tree_bytes"],
        "trait_source_bytes": summary["any_trait_source_bytes"],
        "treebase_retrieved": summary["treebase_retrieved"],
        "dryad_downloaded": {d["dataset_id"]: d["downloaded_count"] for d in summary["dryad"]},
        "biological_endpoint_computed": False,
    }, indent=2))


if __name__ == "__main__":
    main()
