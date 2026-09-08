#!/usr/bin/env python3
"""Metadata-only audit of the Phaidra collection used by the related 51-clade study.

No biological data file is opened and no flower-colour signal is computed. The
purpose is only to determine whether the public Phaidra deposit provides a
recoverable mirror/source layer for the prospectively frozen Dryad panel.
"""
from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import quote

import requests

PID = "o:2098641"
BASE = "https://services.phaidra.univie.ac.at/api"
UA = "chun-phaidra-51-source-audit/1.0"
OUT = Path("analysis/_generated/phaidra_51_mirror_v1")


def get_json(url: str):
    r = requests.get(url, headers={"User-Agent": UA, "Accept": "application/json"}, timeout=120)
    r.raise_for_status()
    return r.json()


def search(field: str):
    q = f'{field}:"{PID}"'
    url = f"{BASE}/search/select?q={quote(q, safe='')}&wt=json&rows=1000"
    return get_json(url)


def compact_doc(d: dict):
    keys = [
        "pid", "id", "title", "dc_title", "filename", "resourcetype",
        "model", "mime", "mimetype", "format", "size", "bytes",
        "created", "modified", "owner", "ispartof", "ismemberof",
    ]
    out = {k: d.get(k) for k in keys if k in d}
    # Preserve all scalar fields with names useful for source discovery, without
    # downloading or parsing object content.
    for k, v in d.items():
        kl = k.casefold()
        if any(x in kl for x in ("title", "file", "mime", "format", "size", "model", "type")):
            if isinstance(v, (str, int, float, bool)) or v is None:
                out.setdefault(k, v)
            elif isinstance(v, list) and len(v) <= 20 and all(isinstance(x, (str, int, float, bool)) for x in v):
                out.setdefault(k, v)
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    info_url = f"{BASE}/object/{PID}/info"
    info = get_json(info_url)

    searches = {}
    docs = {}
    for field in ("ismemberof", "ispartof"):
        try:
            x = search(field)
            searches[field] = x
            response = x.get("response", {}) if isinstance(x, dict) else {}
            for d in response.get("docs", []) or []:
                pid = d.get("pid") or d.get("id") or json.dumps(d, sort_keys=True)[:120]
                docs[str(pid)] = compact_doc(d)
        except Exception as e:
            searches[field] = {"error": repr(e)}

    # The info endpoint may itself expose related/member index records.
    related = []
    if isinstance(info, dict):
        for key, value in info.items():
            if isinstance(value, list) and value and all(isinstance(x, dict) for x in value):
                if any(any(z in str(k).casefold() for z in ("title", "pid", "model", "filename")) for x in value for k in x):
                    for d in value:
                        pid = d.get("pid") or d.get("id") or f"{key}:{len(related)}"
                        docs.setdefault(str(pid), compact_doc(d))
                        related.append({"container_key": key, "pid": pid})

    inventory = {
        "target_pid": PID,
        "info_url": info_url,
        "member_doc_count": len(docs),
        "member_docs": [docs[k] for k in sorted(docs)],
        "related_index": related,
        "content_opened": False,
        "signal_computed": False,
        "note": "Metadata/search records only; no member download and no trait/tree content inspection.",
    }
    (OUT / "inventory.json").write_text(json.dumps(inventory, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    # Save raw API structures for schema/provenance audit.
    (OUT / "info.json").write_text(json.dumps(info, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (OUT / "searches.json").write_text(json.dumps(searches, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print("PHAIDRA51_MIRROR_AUDIT=" + json.dumps({
        "target_pid": PID,
        "member_doc_count": len(docs),
        "member_docs": inventory["member_docs"],
        "content_opened": False,
        "signal_computed": False,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
