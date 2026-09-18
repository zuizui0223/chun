#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

BASES = [\n    "https://services.phaidra.univie.ac.at/api",\n    "https://phaidra.univie.ac.at/api",\n]
COLLECTION = "o:2098641"
UA = "CHUN-abiotic-source-gate/0.1"


def get_json(url: str, timeout: int = 60) -> tuple[Any | None, dict]:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            ctype = r.headers.get("Content-Type", "")
            diag = {"url": url, "http_status": getattr(r, "status", 200), "bytes": len(raw), "content_type": ctype}
            try:
                return json.loads(raw.decode("utf-8")), diag
            except Exception as e:
                diag["parse_error"] = f"{type(e).__name__}: {e}"
                diag["prefix"] = raw[:200].decode("utf-8", "replace")
                return None, diag
    except Exception as e:
        return None, {"url": url, "error": f"{type(e).__name__}: {e}"}


def _walk_values(x: Any):
    if isinstance(x, dict):
        for k, v in x.items():
            yield k, v
            yield from _walk_values(v)
    elif isinstance(x, list):
        for v in x:
            yield from _walk_values(v)


def extract_pids(payload: Any) -> list[str]:
    found: set[str] = set()
    def visit(x: Any):
        if isinstance(x, str):
            for m in re.finditer(r"\bo:\d+\b", x):
                found.add(m.group(0))
        elif isinstance(x, dict):
            for k, v in x.items():
                if k.lower() in {"pid", "id", "member", "object"} and isinstance(v, str) and re.fullmatch(r"o:\d+", v):
                    found.add(v)
                visit(v)
        elif isinstance(x, list):
            for v in x:
                visit(v)
    visit(payload)
    found.discard(COLLECTION)
    return sorted(found, key=lambda s: int(s.split(":")[1]))


def _string_from_key(payload: Any, target: str) -> str | None:
    for k, v in _walk_values(payload):
        if k == target:
            if isinstance(v, str):
                return v
            if isinstance(v, list):
                for item in v:
                    if isinstance(item, str):
                        return item
                    if isinstance(item, dict):
                        for vv in item.values():
                            if isinstance(vv, str):
                                return vv
                            if isinstance(vv, list):
                                for q in vv:
                                    if isinstance(q, str):
                                        return q
                                    if isinstance(q, dict):
                                        for z in q.values():
                                            if isinstance(z, str):
                                                return z
    return None


def _number_from_key(payload: Any, keys: tuple[str, ...]) -> int | float | None:
    for k, v in _walk_values(payload):
        if k in keys and isinstance(v, (int, float)):
            return v
        if k in keys and isinstance(v, str):
            try:
                return int(v)
            except Exception:
                try:
                    return float(v)
                except Exception:
                    pass
    return None


def summarize_info(pid: str, payload: Any) -> dict:
    filename = _string_from_key(payload, "ebucore:filename") or _string_from_key(payload, "filename")
    mimetype = _string_from_key(payload, "ebucore:hasMimeType") or _string_from_key(payload, "mimetype")
    title = _string_from_key(payload, "bf:mainTitle") or _string_from_key(payload, "dc_title") or _string_from_key(payload, "title")
    size = _number_from_key(payload, ("size", "tsize", "filesize"))
    text = " ".join(str(x) for x in (filename, title, mimetype) if x).lower()
    candidate = any(tok in text for tok in (
        "clim", "environment", "temperature", "aridity", "uv", "occurrence", "gbif",
        ".csv", ".rds", ".rdata", ".rda", ".zip", ".r"
    ))
    return {
        "pid": pid,
        "filename": filename,
        "title": title,
        "mimetype": mimetype,
        "size": size,
        "candidate_environment_or_code": candidate,
    }


def head_url(url: str, timeout: int = 60) -> dict:
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": UA, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return {
                "url": url,
                "http_status": getattr(r, "status", 200),
                "content_type": r.headers.get("Content-Type"),
                "content_length": r.headers.get("Content-Length"),
                "content_disposition": r.headers.get("Content-Disposition"),
                "location": r.headers.get("Location"),
            }
    except Exception as e:
        return {"url": url, "error": f"{type(e).__name__}: {e}"}


def collection_member_pids() -> tuple[list[str], list[dict], dict[str, Any], dict | None]:
    diagnostics: list[dict] = []
    raw_sources: dict[str, Any] = {}
    root_summary = None
    encoded = urllib.parse.quote(COLLECTION, safe="")

    # First determine what o:2098641 actually is. It may be a collection,
    # container, or a single packaged asset.
    for base in BASES:
        for pid_token in (encoded, COLLECTION):
            u = f"{base}/object/{pid_token}/info"
            payload, diag = get_json(u)
            diagnostics.append(diag)
            if payload is not None:
                raw_sources[f"root_info:{base}:{pid_token}"] = payload
                root_summary = summarize_info(COLLECTION, payload)
                pids = extract_pids(payload)
                if pids:
                    return pids, diagnostics, raw_sources, root_summary
                break
        if root_summary is not None:
            break

    # If the root info did not expose members, try the relationships and Solr APIs.
    for base in BASES:
        for pid_token in (encoded, COLLECTION):
            u1 = f"{base}/collection/{pid_token}/members"
            payload, diag = get_json(u1)
            diagnostics.append(diag)
            if payload is not None:
                raw_sources[f"collection_members:{base}:{pid_token}"] = payload
                pids = extract_pids(payload)
                if pids:
                    return pids, diagnostics, raw_sources, root_summary

        q = urllib.parse.quote(f'ismemberof:"{COLLECTION}"')
        u2 = f"{base}/search/select?q={q}&rows=500&wt=json"
        payload, diag = get_json(u2)
        diagnostics.append(diag)
        if payload is not None:
            raw_sources[f"solr_search:{base}"] = payload
            pids = extract_pids(payload)
            if pids:
                return pids, diagnostics, raw_sources, root_summary

    return [], diagnostics, raw_sources, root_summary


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    pids, diagnostics, raw_sources, root_summary = collection_member_pids()
    inventory = []
    info_diags = []
    if pids:
        for pid in pids:
            encoded = urllib.parse.quote(pid, safe="")
            payload, diag = get_json(f"{BASE}/object/{encoded}/info")
            info_diags.append({"pid": pid, **diag})
            if payload is None:
                inventory.append({"pid": pid, "info_status": "UNAVAILABLE"})
            else:
                row = summarize_info(pid, payload)
                row["info_status"] = "READY"
                inventory.append(row)

    candidate_count = sum(bool(x.get("candidate_environment_or_code")) for x in inventory)
    download_heads = []
    encoded = urllib.parse.quote(COLLECTION, safe="")
    for base in BASES:
        for pid_token in (encoded, COLLECTION):
            download_heads.append(head_url(f"{base}/object/{pid_token}/download"))
    if inventory:
        status = "PHAIDRA_ABIOTIC_SOURCE_INVENTORY_READY"
    elif root_summary and any(root_summary.get(k) for k in ("filename","mimetype","size","title")):
        status = "PHAIDRA_ABIOTIC_ROOT_OBJECT_READY"
    else:
        status = "HOLD_PHAIDRA_COLLECTION_INVENTORY_UNAVAILABLE"
    out = {
        "version": "v0.1",
        "status": status,
        "collection": COLLECTION,
        "member_count": len(pids),
        "candidate_file_count": candidate_count,
        "root_object": root_summary,
        "download_head_diagnostics": download_heads,
        "members": inventory,
        "diagnostics": diagnostics,
        "info_diagnostics": info_diags,
        "outcome_firewall": {
            "file_contents_downloaded": False,
            "environmental_rows_opened": False,
            "flower_memory_outcome_fit": False
        },
        "paper1_science_changed": False,
        "el_v0_2_science_changed": False
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "status": status,
        "member_count": len(pids),
        "candidate_file_count": candidate_count,
        "root_object": root_summary,
        "download_heads": download_heads,
        "candidate_members": [x for x in inventory if x.get("candidate_environment_or_code")]
    }, indent=2))


if __name__ == "__main__":
    main()
