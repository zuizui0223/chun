#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

BASES = [
    "https://services.phaidra.univie.ac.at/api",
    "https://phaidra.univie.ac.at/api",
]
ROOT_CANDIDATES = [
    {"pid": "o:2098641", "provenance": "article_data_availability_statement"},
    {"pid": "o:2322953", "provenance": "current_university_publication_record"},
]
UA = "CHUN-abiotic-source-gate/0.2"


def get_json(url: str, timeout: int = 45) -> tuple[Any | None, dict]:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            ctype = r.headers.get("Content-Type", "")
            diag = {
                "url": url,
                "http_status": getattr(r, "status", 200),
                "bytes": len(raw),
                "content_type": ctype,
            }
            if not raw:
                diag["parse_error"] = "empty response body"
                return None, diag
            try:
                return json.loads(raw.decode("utf-8")), diag
            except Exception as e:
                diag["parse_error"] = f"{type(e).__name__}: {e}"
                diag["prefix"] = raw[:200].decode("utf-8", "replace")
                return None, diag
    except Exception as e:
        return None, {"url": url, "error": f"{type(e).__name__}: {e}"}


def head_url(url: str, timeout: int = 45) -> dict:
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


def _walk_values(x: Any):
    if isinstance(x, dict):
        for k, v in x.items():
            yield k, v
            yield from _walk_values(v)
    elif isinstance(x, list):
        for v in x:
            yield from _walk_values(v)


def extract_pids(payload: Any, exclude: tuple[str, ...] = ()) -> list[str]:
    found: set[str] = set()

    def visit(x: Any):
        if isinstance(x, str):
            for m in re.finditer(r"\bo:\d+\b", x):
                found.add(m.group(0))
        elif isinstance(x, dict):
            for k, v in x.items():
                if (
                    k.lower() in {"pid", "id", "member", "object"}
                    and isinstance(v, str)
                    and re.fullmatch(r"o:\d+", v)
                ):
                    found.add(v)
                visit(v)
        elif isinstance(x, list):
            for v in x:
                visit(v)

    visit(payload)
    found.difference_update(exclude)
    return sorted(found, key=lambda s: int(s.split(":")[1]))


def _string_from_key(payload: Any, target: str) -> str | None:
    for k, v in _walk_values(payload):
        if k != target:
            continue
        if isinstance(v, str):
            return v
        if isinstance(v, list):
            stack = list(v)
            while stack:
                item = stack.pop(0)
                if isinstance(item, str):
                    return item
                if isinstance(item, dict):
                    stack.extend(item.values())
                elif isinstance(item, list):
                    stack.extend(item)
    return None


def _number_from_key(payload: Any, keys: tuple[str, ...]) -> int | float | None:
    for k, v in _walk_values(payload):
        if k not in keys:
            continue
        if isinstance(v, (int, float)):
            return v
        if isinstance(v, str):
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
    title = (
        _string_from_key(payload, "bf:mainTitle")
        or _string_from_key(payload, "dc_title")
        or _string_from_key(payload, "title")
    )
    size = _number_from_key(payload, ("size", "tsize", "filesize"))
    text = " ".join(str(x) for x in (filename, title, mimetype) if x).lower()
    candidate = any(
        tok in text
        for tok in (
            "clim",
            "environment",
            "temperature",
            "aridity",
            "uv",
            "occurrence",
            "gbif",
            "flower",
            "fruit",
            "color",
            ".csv",
            ".rds",
            ".rdata",
            ".rda",
            ".zip",
            ".r",
        )
    )
    return {
        "pid": pid,
        "filename": filename,
        "title": title,
        "mimetype": mimetype,
        "size": size,
        "candidate_environment_or_code": candidate,
    }


def first_object_info(pid: str) -> tuple[dict | None, list[dict]]:
    diagnostics: list[dict] = []
    encoded = urllib.parse.quote(pid, safe="")
    for base in BASES:
        for token in (encoded, pid):
            payload, diag = get_json(f"{base}/object/{token}/info")
            diagnostics.append(diag)
            if payload is not None:
                return summarize_info(pid, payload), diagnostics
    return None, diagnostics


def member_inventory(root_pid: str) -> tuple[list[str], list[dict]]:
    diagnostics: list[dict] = []
    encoded = urllib.parse.quote(root_pid, safe="")
    for base in BASES:
        # Relationship endpoint.
        for token in (encoded, root_pid):
            payload, diag = get_json(f"{base}/collection/{token}/members")
            diagnostics.append(diag)
            if payload is not None:
                pids = extract_pids(payload, exclude=(root_pid,))
                if pids:
                    return pids, diagnostics

        # PHAIDRA docs recommend collection membership as an fq filter.
        q = urllib.parse.quote("*:*")
        fq = urllib.parse.quote(f'ismemberof:"{root_pid}"')
        payload, diag = get_json(f"{base}/search/select?q={q}&fq={fq}&rows=500&wt=json")
        diagnostics.append(diag)
        if payload is not None:
            pids = extract_pids(payload, exclude=(root_pid,))
            if pids:
                return pids, diagnostics
    return [], diagnostics


def download_heads(pid: str) -> list[dict]:
    encoded = urllib.parse.quote(pid, safe="")
    out = []
    for base in BASES:
        for token in (encoded, pid):
            out.append(head_url(f"{base}/object/{token}/download"))
    return out


def inventory_root(candidate: dict) -> dict:
    pid = candidate["pid"]
    root, info_diag = first_object_info(pid)
    members, member_diag = member_inventory(pid)
    member_rows = []
    for member_pid in members:
        row, diags = first_object_info(member_pid)
        if row is None:
            row = {"pid": member_pid, "info_status": "UNAVAILABLE"}
        else:
            row["info_status"] = "READY"
        row["diagnostics"] = diags
        member_rows.append(row)
    return {
        "pid": pid,
        "provenance": candidate["provenance"],
        "root_object": root,
        "member_count": len(members),
        "members": member_rows,
        "root_info_diagnostics": info_diag,
        "member_inventory_diagnostics": member_diag,
        "download_head_diagnostics": download_heads(pid),
    }


def choose_source(roots: list[dict]) -> dict | None:
    # Metadata evidence only: choose a root only when its own metadata or at least
    # one member is visibly relevant to the target article/data/code.
    qualifying = []
    for root in roots:
        root_relevant = bool((root.get("root_object") or {}).get("candidate_environment_or_code"))
        relevant_members = [
            m for m in root.get("members", []) if m.get("candidate_environment_or_code")
        ]
        if root_relevant or relevant_members:
            qualifying.append(
                {
                    "pid": root["pid"],
                    "provenance": root["provenance"],
                    "root_relevant": root_relevant,
                    "relevant_member_count": len(relevant_members),
                    "relevant_members": [
                        {k: m.get(k) for k in ("pid", "filename", "title", "mimetype", "size")}
                        for m in relevant_members
                    ],
                }
            )
    if len(qualifying) == 1:
        return qualifying[0]
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    roots = [inventory_root(c) for c in ROOT_CANDIDATES]
    chosen = choose_source(roots)
    if chosen is not None:
        status = "PHAIDRA_ABIOTIC_SOURCE_IDENTITY_READY"
    elif any(r.get("root_object") or r.get("members") for r in roots):
        status = "HOLD_PHAIDRA_SOURCE_IDENTITY_AMBIGUOUS"
    else:
        status = "HOLD_PHAIDRA_SOURCE_METADATA_UNAVAILABLE"

    out = {
        "version": "v0.2",
        "status": status,
        "root_candidates": roots,
        "chosen_source": chosen,
        "source_identity_rule": "metadata-only; exactly one candidate must visibly identify article-relevant data/code",
        "outcome_firewall": {
            "member_file_contents_downloaded": False,
            "environmental_rows_opened": False,
            "flower_memory_outcome_fit": False,
        },
        "paper1_science_changed": False,
        "el_v0_2_science_changed": False,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "status": status,
                "chosen_source": chosen,
                "roots": [
                    {
                        "pid": r["pid"],
                        "root_object": r["root_object"],
                        "member_count": r["member_count"],
                        "relevant_members": [
                            {k: m.get(k) for k in ("pid", "filename", "title", "mimetype", "size")}
                            for m in r["members"]
                            if m.get("candidate_environment_or_code")
                        ],
                        "download_heads": r["download_head_diagnostics"],
                    }
                    for r in roots
                ],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
