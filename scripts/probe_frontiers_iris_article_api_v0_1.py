#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import urllib.request
from pathlib import Path

UA = "chun-iris-article-api-probe/0.1"
A = "569811"
URLS = [
    f"https://www.frontiersin.org/api/v4/articles/{A}",
    f"https://www.frontiersin.org/api/v4/articles/{A}/",
    f"https://www.frontiersin.org/api/v4/articles/{A}/files",
    f"https://www.frontiersin.org/api/v4/articles/{A}/file",
    f"https://www.frontiersin.org/api/v4/articles/{A}/supplementary-materials",
    f"https://www.frontiersin.org/api/v3/articles/{A}",
]


def fetch(url: str) -> tuple[str, int, str, bytes]:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": UA, "Accept": "application/json,text/plain,*/*"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return (
            r.geturl(),
            r.status,
            (r.headers.get("Content-Type") or "").split(";", 1)[0].lower(),
            r.read(),
        )


def collect_file_like_strings(obj):
    hits = []

    def walk(x, path=""):
        if isinstance(x, dict):
            for k, v in x.items():
                walk(v, f"{path}.{k}" if path else str(k))
        elif isinstance(x, list):
            for i, v in enumerate(x):
                walk(v, f"{path}[{i}]")
        elif isinstance(x, str) and (
            ".xlsx" in x.lower()
            or ".csv" in x.lower()
            or "/file/" in x.lower()
        ):
            hits.append({"path": path, "value": x})

    walk(obj)
    return hits[:200]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    probes = []
    for url in URLS:
        try:
            final_url, status, content_type, body = fetch(url)
            rec = {
                "url": url,
                "final_url": final_url,
                "status": status,
                "content_type": content_type,
                "bytes": len(body),
                "prefix": body[:4000].decode("utf-8", "replace"),
            }
            try:
                parsed = json.loads(body)
                rec["json_type"] = type(parsed).__name__
                rec["json_keys"] = list(parsed)[:100] if isinstance(parsed, dict) else None
                rec["file_like_strings"] = collect_file_like_strings(parsed)
            except Exception:
                pass
            probes.append(rec)
        except Exception as exc:
            probes.append({"url": url, "error": repr(exc)})

    result = {
        "version": "v0.1",
        "status": "ARTICLE_METADATA_PROBE_ONLY",
        "probes": probes,
        "row_level_values_emitted": False,
        "auc_computed": False,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
