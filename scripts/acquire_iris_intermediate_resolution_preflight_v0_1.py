#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

PMC_ID = "PMC7588356"
PMC_NUMERIC = "7588356"
XML_URL = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={PMC_NUMERIC}&retmode=xml"
CLOUD_BUCKET = "pmc-oa-opendata"
CLOUD_HTTPS = f"https://{CLOUD_BUCKET}.s3.amazonaws.com"
XLINK = "{http://www.w3.org/1999/xlink}href"
USER_AGENT = "chun-iris-preregistered-analysis/0.2"


def fetch_with_meta(url: str) -> tuple[str, str, bytes]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=120) as r:
        final_url = r.geturl()
        content_type = (r.headers.get("Content-Type") or "").split(";", 1)[0].strip().lower()
        return final_url, content_type, r.read()


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def text_content(el: ET.Element) -> str:
    return " ".join("".join(el.itertext()).split())


def candidate_urls(href: str) -> list[str]:
    """Legacy article-page candidates retained only as cheap first attempts.

    PMC removed the legacy OA package service and legacy dataset distribution in
    August 2026. These URLs may therefore 404; the authoritative fallback below
    is the current PMC Article Datasets AWS structure.
    """
    urls: list[str] = []
    if href.startswith("http://") or href.startswith("https://"):
        urls.append(href)
    h = href.lstrip("/")
    urls.extend(
        [
            f"https://pmc.ncbi.nlm.nih.gov/articles/{PMC_ID}/bin/{h}",
            f"https://pmc.ncbi.nlm.nih.gov/articles/instance/{PMC_NUMERIC}/bin/{h}",
            urllib.parse.urljoin(f"https://pmc.ncbi.nlm.nih.gov/articles/{PMC_ID}/", href),
        ]
    )
    return list(dict.fromkeys(urls))


def looks_like_html(content_type: str, b: bytes) -> bool:
    prefix = b[:512].lstrip().lower()
    return (
        content_type in {"text/html", "application/xhtml+xml"}
        or prefix.startswith(b"<!doctype html")
        or prefix.startswith(b"<html")
        or b"<html" in prefix[:200]
    )


def _xml_local(el: ET.Element, name: str) -> list[ET.Element]:
    return [x for x in el.iter() if x.tag.rsplit("}", 1)[-1] == name]


def cloud_article_versions() -> tuple[list[str], dict[str, object]]:
    """List current PMC AWS article-version prefixes without opening outcomes."""
    query = urllib.parse.urlencode(
        {"list-type": "2", "prefix": f"{PMC_ID}.", "delimiter": "/"}
    )
    list_url = f"{CLOUD_HTTPS}/?{query}"
    final_url, content_type, payload = fetch_with_meta(list_url)
    root = ET.fromstring(payload)
    prefixes = [
        (p.text or "").strip()
        for cp in _xml_local(root, "CommonPrefixes")
        for p in _xml_local(cp, "Prefix")
        if (p.text or "").strip()
    ]
    rx = re.compile(rf"^{re.escape(PMC_ID)}\.(\d+)/$")
    versioned: list[tuple[int, str]] = []
    for prefix in prefixes:
        m = rx.fullmatch(prefix)
        if m:
            versioned.append((int(m.group(1)), prefix))
    versioned.sort()
    versions = [p for _, p in versioned]
    if not versions:
        raise RuntimeError(
            f"PMC Cloud Service returned no article-version prefix for {PMC_ID}: {prefixes}"
        )
    meta = {
        "cloud_bucket": CLOUD_BUCKET,
        "cloud_list_url": final_url,
        "cloud_list_content_type": content_type,
        "cloud_list_sha256": sha256_bytes(payload),
        "cloud_version_prefixes": versions,
        "cloud_selected_version_prefix": versions[-1],
    }
    return versions, meta


def s3_url_to_https(s3_url: str) -> str:
    parsed = urllib.parse.urlsplit(s3_url)
    if parsed.scheme != "s3" or parsed.netloc != CLOUD_BUCKET:
        raise RuntimeError(f"unexpected PMC media URL: {s3_url}")
    key = parsed.path.lstrip("/")
    # The metadata md5 query is a checksum annotation, not required for HTTP retrieval.
    return f"{CLOUD_HTTPS}/{urllib.parse.quote(key, safe='/._-')}"


def cloud_media_member(href: str) -> tuple[str, str, bytes, dict[str, object]]:
    """Resolve one supplement through the post-Aug-2026 PMC Cloud Service."""
    versions, list_meta = cloud_article_versions()
    selected = versions[-1].rstrip("/")

    metadata_candidates = [
        f"{CLOUD_HTTPS}/metadata/{selected}.json",
        f"{CLOUD_HTTPS}/{selected}/{selected}.json",
    ]
    metadata_attempts: list[dict[str, object]] = []
    metadata: dict[str, object] | None = None
    metadata_url = ""
    metadata_bytes = b""
    for url in metadata_candidates:
        try:
            final, ct, b = fetch_with_meta(url)
            metadata_attempts.append(
                {
                    "requested_url": url,
                    "final_url": final,
                    "content_type": ct,
                    "bytes": len(b),
                    "sha256": sha256_bytes(b),
                }
            )
            x = json.loads(b.decode("utf-8"))
            if not isinstance(x, dict):
                raise RuntimeError("metadata JSON is not an object")
            metadata = x
            metadata_url = final
            metadata_bytes = b
            break
        except Exception as e:
            metadata_attempts.append({"requested_url": url, "error": repr(e)})
    if metadata is None:
        raise RuntimeError(f"could not retrieve current PMC cloud metadata: {metadata_attempts}")

    if metadata.get("pmcid") != PMC_ID:
        raise RuntimeError(f"cloud metadata PMCID mismatch: {metadata.get('pmcid')!r}")
    media_urls = metadata.get("media_urls")
    if not isinstance(media_urls, list) or not media_urls:
        raise RuntimeError("cloud metadata contains no media_urls")
    media_urls = [str(x) for x in media_urls]

    target = Path(urllib.parse.urlsplit(href).path).name.lower()
    target_suffix = Path(target).suffix.lower()

    def media_basename(u: str) -> str:
        return Path(urllib.parse.urlsplit(u).path).name.lower()

    exact = [u for u in media_urls if media_basename(u) == target]
    candidates = exact
    resolution = "EXACT_BASENAME"
    if not candidates and target_suffix:
        candidates = [u for u in media_urls if Path(media_basename(u)).suffix.lower() == target_suffix]
        resolution = "UNIQUE_EXTENSION_FALLBACK"
    if len(candidates) != 1:
        raise RuntimeError(
            f"cloud media did not uniquely resolve {href!r}; exact={exact}; "
            f"extension_candidates={candidates}; available={[media_basename(u) for u in media_urls]}"
        )

    source_s3 = candidates[0]
    https_url = s3_url_to_https(source_s3)
    final, content_type, payload = fetch_with_meta(https_url)
    if looks_like_html(content_type, payload) or len(payload) <= 100:
        raise RuntimeError(
            f"resolved cloud supplement invalid: {final} type={content_type} bytes={len(payload)}"
        )

    md5_expected = urllib.parse.parse_qs(urllib.parse.urlsplit(source_s3).query).get("md5", [None])[0]
    md5_observed = hashlib.md5(payload).hexdigest()  # nosec B303 - source integrity check only
    if md5_expected and md5_observed.lower() != md5_expected.lower():
        raise RuntimeError(
            f"PMC cloud md5 mismatch for {source_s3}: expected={md5_expected} observed={md5_observed}"
        )

    meta: dict[str, object] = {
        **list_meta,
        "cloud_metadata_url": metadata_url,
        "cloud_metadata_sha256": sha256_bytes(metadata_bytes),
        "cloud_metadata_attempts": metadata_attempts,
        "cloud_media_count": len(media_urls),
        "cloud_media_basenames": [media_basename(u) for u in media_urls],
        "cloud_resolution": resolution,
        "cloud_source_s3_url": source_s3,
        "cloud_resolved_https_url": final,
        "cloud_md5_expected": md5_expected,
        "cloud_md5_observed": md5_observed,
    }
    return final, content_type, payload, meta


def download_href(href: str) -> tuple[str, str, bytes, list[dict[str, object]]]:
    attempts: list[dict[str, object]] = []
    for url in candidate_urls(href):
        try:
            final_url, content_type, b = fetch_with_meta(url)
            attempt = {
                "requested_url": url,
                "final_url": final_url,
                "content_type": content_type,
                "bytes": len(b),
                "magic_hex": b[:16].hex(),
                "html_rejected": looks_like_html(content_type, b),
            }
            attempts.append(attempt)
            if len(b) <= 100 or attempt["html_rejected"]:
                continue
            return final_url, content_type, b, attempts
        except Exception as e:
            attempts.append({"requested_url": url, "error": repr(e)})

    # Authoritative post-Aug-2026 distribution path.
    try:
        final_url, content_type, b, cloud_meta = cloud_media_member(href)
        attempts.append(
            {
                "pmc_cloud_service_fallback": True,
                **cloud_meta,
                "bytes": len(b),
                "magic_hex": b[:16].hex(),
            }
        )
        return final_url, content_type, b, attempts
    except Exception as e:
        attempts.append({"pmc_cloud_service_fallback": True, "error": repr(e)})

    raise RuntimeError(
        "could not download a non-HTML supplement for href %r\n%s"
        % (href, json.dumps(attempts, indent=2))
    )


def identify_supplements(root: ET.Element) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for sm in root.findall(".//supplementary-material"):
        label = text_content(sm.find("label")) if sm.find("label") is not None else ""
        caption = text_content(sm.find("caption")) if sm.find("caption") is not None else ""
        desc = f"{label} {caption}".strip()
        hrefs: list[str] = []
        for e in sm.iter():
            href = e.attrib.get(XLINK)
            if href:
                hrefs.append(href)
        out.append({"description": desc, "hrefs": hrefs})
    return out


def choose(items: list[dict[str, object]], pattern: str) -> dict[str, object]:
    rx = re.compile(pattern, re.I)
    hits = [x for x in items if rx.search(str(x["description"]))]
    if len(hits) != 1:
        raise RuntimeError(
            f"expected one supplement for {pattern!r}, found {len(hits)}: "
            f"{[x['description'] for x in hits]}"
        )
    return hits[0]


def inspect_xlsx(name: str, b: bytes, container_member: str | None = None) -> dict[str, object]:
    import pandas as pd

    xls = pd.ExcelFile(io.BytesIO(b), engine="openpyxl")
    sheets: list[dict[str, object]] = []
    for sheet in xls.sheet_names:
        df = pd.read_excel(io.BytesIO(b), sheet_name=sheet, nrows=0, engine="openpyxl")
        sheets.append({"sheet": str(sheet), "columns": [str(c) for c in df.columns]})
    out: dict[str, object] = {"logical_name": name, "format": "xlsx", "sheets": sheets}
    if container_member is not None:
        out["container_member"] = container_member
    return out


def inspect_text_table(name: str, filename: str, b: bytes, container_member: str | None = None) -> dict[str, object]:
    text = b.decode("utf-8-sig", errors="replace")
    sample = text[:8192]
    delimiter = "\t" if filename.lower().endswith((".tsv", ".txt")) or sample.count("\t") > sample.count(",") else ","
    reader = csv.reader(io.StringIO(text), delimiter=delimiter)
    header = next(reader, [])
    out: dict[str, object] = {
        "logical_name": name,
        "format": "tsv_or_text" if delimiter == "\t" else "csv_or_text",
        "delimiter": "TAB" if delimiter == "\t" else "COMMA",
        "header": header,
    }
    if container_member is not None:
        out["container_member"] = container_member
    return out


def inspect_table(name: str, filename: str, content_type: str, b: bytes) -> dict[str, object]:
    if looks_like_html(content_type, b):
        raise RuntimeError(f"HTML reached table inspector for {filename}")

    lower = filename.lower().split("#", 1)[-1]
    if zipfile.is_zipfile(io.BytesIO(b)):
        with zipfile.ZipFile(io.BytesIO(b)) as zf:
            members = [m for m in zf.namelist() if not m.endswith("/") and not m.startswith("__MACOSX/")]
            if "[Content_Types].xml" in members and any(m.startswith("xl/") for m in members):
                return inspect_xlsx(name, b)
            tabular = [m for m in members if m.lower().endswith((".xlsx", ".csv", ".tsv", ".txt"))]
            if len(tabular) != 1:
                raise RuntimeError(
                    f"generic ZIP for {filename} has {len(tabular)} candidate tabular members; members={members[:50]}"
                )
            member = tabular[0]
            payload = zf.read(member)
            if member.lower().endswith(".xlsx"):
                return inspect_xlsx(name, payload, container_member=member)
            return inspect_text_table(name, member, payload, container_member=member)

    if b.startswith(bytes.fromhex("d0cf11e0a1b11ae1")) or lower.endswith(".xls"):
        import pandas as pd

        xls = pd.ExcelFile(io.BytesIO(b), engine="xlrd")
        sheets: list[dict[str, object]] = []
        for sheet in xls.sheet_names:
            df = pd.read_excel(io.BytesIO(b), sheet_name=sheet, nrows=0, engine="xlrd")
            sheets.append({"sheet": str(sheet), "columns": [str(c) for c in df.columns]})
        return {"logical_name": name, "format": "xls", "sheets": sheets}

    if lower.endswith(".xlsx"):
        raise RuntimeError(f"filename suggests XLSX but payload is not a valid ZIP: {filename}")
    return inspect_text_table(name, filename, b)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    xml_final_url, xml_content_type, xml_bytes = fetch_with_meta(XML_URL)
    root = ET.fromstring(xml_bytes)
    supplements = identify_supplements(root)

    trait_item = choose(supplements, r"Supplementary\s+Table\s*1|Data table")
    accession_item = choose(supplements, r"Supplementary\s+Material\s*1|Accession numbers")

    outputs: list[dict[str, object]] = []
    for logical, item in [("traits", trait_item), ("accessions", accession_item)]:
        hrefs = item.get("hrefs") or []
        if not hrefs:
            raise RuntimeError(f"no href for {logical}: {item}")
        href = str(hrefs[0])
        url, content_type, b, attempts = download_href(href)
        inspection = inspect_table(logical, url, content_type, b)
        inspection.update(
            {
                "description": item["description"],
                "href": href,
                "resolved_url": url,
                "content_type": content_type,
                "bytes": len(b),
                "sha256": sha256_bytes(b),
                "magic_hex": b[:16].hex(),
                "download_attempts": attempts,
            }
        )
        outputs.append(inspection)

    receipt = {
        "version": "v0.2",
        "status": "POST_FREEZE_SOURCE_HEADER_PREFLIGHT_ONLY",
        "freeze_contract": "data/intermediate_resolution_rule_prereg_v0_1.json",
        "pmc_id": PMC_ID,
        "xml_url": XML_URL,
        "xml_final_url": xml_final_url,
        "xml_content_type": xml_content_type,
        "xml_sha256": sha256_bytes(xml_bytes),
        "supplement_count_in_xml": len(supplements),
        "files": outputs,
        "row_level_values_emitted": False,
        "auc_computed": False,
        "paper1_science_changed": False,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
