#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import re
import urllib.request
from pathlib import Path

URLS = [
    "https://www.frontiersin.org/journals/plant-science/articles/10.3389/fpls.2020.569811/full",
    "https://www.frontiersin.org/articles/10.3389/fpls.2020.569811/full",
]
UA = "chun-iris-html-asset-probe/0.1"


def fetch(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.geturl(), (r.headers.get("Content-Type") or "").split(";", 1)[0].lower(), r.read()


def extract(text: str):
    normalized = html.unescape(text).replace("\\/", "/").replace("\\u0026", "&")
    patterns = [
        r"https?://[^\"'<>\s]+/articles/569811/file/[^\"'<>\s]+",
        r"/api/v[34]/articles/569811/file/[^\"'<>\s]+",
        r"https?://[^\"'<>\s]+/articles/569811/[^\"'<>\s]*(?:xlsx|csv)[^\"'<>\s]*",
        r"[^\"'<>\s]{0,120}(?:Table_1|Data_Sheet_[0-9]+)[^\"'<>\s]{0,240}",
    ]
    hits = []
    for p in patterns:
        hits.extend(re.findall(p, normalized, flags=re.I))
    # Stable de-duplication and trim obvious HTML punctuation.
    return list(dict.fromkeys(x.rstrip(",);]") for x in hits))[:500]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    probes = []
    for url in URLS:
        try:
            final, ct, body = fetch(url)
            text = body.decode("utf-8", "replace")
            probes.append({
                "url": url,
                "final_url": final,
                "content_type": ct,
                "bytes": len(body),
                "asset_like_strings": extract(text),
            })
        except Exception as exc:
            probes.append({"url": url, "error": repr(exc)})
    result = {
        "version": "v0.1",
        "status": "HTML_ASSET_LINK_PROBE_ONLY",
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
