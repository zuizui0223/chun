#!/usr/bin/env python3
"""Acquire and audit Silene falsification source objects without computing signal.

The script may inspect row-level trait/accession schemas and source-state counts. It must
not join observed flower-colour assignments to a phylogeny or compute Sankoff/Fitch.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import urllib.parse
import zipfile
from collections import Counter
from pathlib import Path

import requests

UA = {"User-Agent": "chun-silene-falsification-source-audit/1.0 (+https://github.com/zuizui0223/chun)"}
PMCID = "PMC9485837"
DRYAD_DOI = "10.5061/dryad.wstqjq2pf"
EUROPE_PMC_SUPP = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{PMCID}/supplementaryFiles"
EUROPE_PMC_XML = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{PMCID}/fullTextXML"
OUT_DEFAULT = Path("analysis/_generated/silene_falsification_source_v1")
COLOURS = {"white": "WHITE", "pink": "PINK", "red": "RED"}


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def get(url: str, accept: str = "*/*"):
    try:
        r = requests.get(url, headers={**UA, "Accept": accept}, timeout=120, allow_redirects=True)
        return {
            "requested": url, "resolved": r.url, "status": r.status_code,
            "content_type": r.headers.get("content-type", ""), "bytes": len(r.content),
            "sha256": sha(r.content) if r.ok and r.content else None,
            "raw": r.content if r.ok else b"",
        }
    except Exception as e:
        return {"requested": url, "resolved": None, "status": None, "error": repr(e), "bytes": 0, "sha256": None, "raw": b""}


def json_get(url: str):
    rec = get(url, "application/json,*/*")
    if not rec["raw"]:
        return rec, None
    try:
        return rec, json.loads(rec["raw"])
    except Exception as e:
        rec["json_error"] = repr(e)
        return rec, None


def hrefs(obj):
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "href" and isinstance(v, str): out.append(v)
            else: out.extend(hrefs(v))
    elif isinstance(obj, list):
        for v in obj: out.extend(hrefs(v))
    return out


def normalize_dryad(url: str) -> str:
    return "https://datadryad.org" + url if url.startswith("/") else url


def flatten_records(obj):
    vals = []
    if isinstance(obj, list):
        vals.extend(x for x in obj if isinstance(x, dict))
    elif isinstance(obj, dict):
        for v in obj.values():
            if isinstance(v, list): vals.extend(x for x in v if isinstance(x, dict))
            elif isinstance(v, dict): vals.extend(flatten_records(v))
    return vals


def file_id(f):
    for k in ("id", "fileId", "file_id"):
        if f.get(k) is not None: return str(f[k])
    for h in hrefs(f):
        m = re.search(r"/files/(\d+)", h)
        if m: return m.group(1)
    return None


def dryad_inventory(out: Path):
    enc = urllib.parse.quote("doi:" + DRYAD_DOI, safe="")
    api = f"https://datadryad.org/api/v2/datasets/{enc}"
    meta_req, meta = json_get(api)
    result = {"doi": DRYAD_DOI, "metadata_request": {k:v for k,v in meta_req.items() if k != "raw"}, "files": []}
    if not isinstance(meta, dict):
        result["status"] = "METADATA_UNAVAILABLE"
        return result
    (out / "dryad_metadata.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")

    candidates = [normalize_dryad(h) for h in hrefs(meta) if "versions" in h.lower()]
    candidates += [api + "/versions"]
    files = []
    seen_urls = set()
    for vu in dict.fromkeys(candidates):
        vr, vo = json_get(vu)
        if vo is None: continue
        for h in hrefs(vo):
            if "files" in h.lower():
                fu = normalize_dryad(h)
                if fu in seen_urls: continue
                seen_urls.add(fu)
                fr, fo = json_get(fu)
                if fo is not None: files.extend(flatten_records(fo))
        for rec in flatten_records(vo):
            for h in hrefs(rec):
                if "files" in h.lower():
                    fu = normalize_dryad(h)
                    if fu in seen_urls: continue
                    seen_urls.add(fu)
                    fr, fo = json_get(fu)
                    if fo is not None: files.extend(flatten_records(fo))
    # Fallback from version id if embedded links were absent.
    if not files:
        for rec in flatten_records(meta):
            vid = rec.get("id")
            if vid:
                _, fo = json_get(f"https://datadryad.org/api/v2/versions/{vid}/files")
                if fo is not None: files.extend(flatten_records(fo))

    uniq, keys = [], set()
    for f in files:
        fid = file_id(f); name = f.get("path") or f.get("filename") or f.get("name")
        if not (fid or name): continue
        k = (str(fid), str(name))
        if k not in keys: keys.add(k); uniq.append(f)
    (out / "dryad_file_records.json").write_text(json.dumps(uniq, indent=2) + "\n", encoding="utf-8")

    ddir = out / "dryad_downloaded"; ddir.mkdir(exist_ok=True)
    for i, f in enumerate(uniq):
        fid = file_id(f)
        name = str(f.get("path") or f.get("filename") or f.get("name") or f"file_{i}")
        routes = []
        for h in hrefs(f):
            if "download" in h.lower(): routes.append(normalize_dryad(h))
        if fid:
            routes += [f"https://datadryad.org/stash/downloads/file_stream/{fid}", f"https://datadryad.org/api/v2/files/{fid}/download"]
        entry = {"id": fid, "name": name, "downloaded": False, "attempts": []}
        for route in dict.fromkeys(routes):
            rr = get(route, "application/octet-stream,*/*")
            entry["attempts"].append({k:v for k,v in rr.items() if k != "raw"})
            if rr["raw"] and "json" not in rr["content_type"].lower():
                p = ddir / Path(name).name; p.write_bytes(rr["raw"])
                entry.update({"downloaded": True, "saved_as": str(p), "bytes": len(rr["raw"]), "sha256": sha(rr["raw"])})
                break
        result["files"].append(entry)
    result["status"] = "INVENTORIED"
    return result


def extract_europe_pmc(out: Path):
    s = get(EUROPE_PMC_SUPP, "application/zip,*/*")
    x = get(EUROPE_PMC_XML, "application/xml,text/xml,*/*")
    result = {
        "supplementary_request": {k:v for k,v in s.items() if k != "raw"},
        "fulltext_xml_request": {k:v for k,v in x.items() if k != "raw"},
        "members": []
    }
    if x["raw"]:
        (out / "fulltext.xml").write_bytes(x["raw"])
    if not s["raw"] or not zipfile.is_zipfile(io.BytesIO(s["raw"])):
        result["supplementary_zip_valid"] = False
        return result
    result["supplementary_zip_valid"] = True
    (out / "supplementaryFiles.zip").write_bytes(s["raw"])
    edir = out / "pmc_supplement"; edir.mkdir(exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(s["raw"])) as zf:
        for m in zf.infolist():
            if m.is_dir(): continue
            raw = zf.read(m); p = edir / Path(m.filename).name; p.write_bytes(raw)
            result["members"].append({"name": m.filename, "saved_as": str(p), "bytes": len(raw), "sha256": sha(raw), "suffix": p.suffix.lower()})
    return result


def read_delimited(path: Path):
    raw = path.read_text(encoding="utf-8-sig", errors="replace")
    dialect = csv.excel_tab if path.suffix.lower() == ".tsv" else csv.excel
    try:
        sample = raw[:4096]; delim = csv.Sniffer().sniff(sample, delimiters=",\t;").delimiter
    except Exception:
        delim = "\t" if path.suffix.lower() == ".tsv" else ","
    return list(csv.DictReader(io.StringIO(raw), delimiter=delim))


def norm_header(s): return re.sub(r"[^a-z0-9]+", "", str(s or "").lower())


def audit_tables(out: Path):
    trait_candidates, accession_candidates = [], []
    for p in out.rglob("*"):
        if not p.is_file(): continue
        rows = None
        if p.suffix.lower() in {".csv", ".tsv"}:
            try: rows = read_delimited(p)
            except Exception: rows = None
        elif p.suffix.lower() in {".xlsx", ".xlsm"}:
            try:
                import openpyxl
                wb = openpyxl.load_workbook(p, read_only=True, data_only=True)
                for ws in wb.worksheets:
                    vals = list(ws.iter_rows(values_only=True))
                    if not vals: continue
                    headers = [str(x or "") for x in vals[0]]
                    rr = [dict(zip(headers, row)) for row in vals[1:] if any(x is not None and str(x).strip() for x in row)]
                    trait_candidates.extend(classify_rows(p, rr, sheet=ws.title)[0])
                    accession_candidates.extend(classify_rows(p, rr, sheet=ws.title)[1])
            except Exception:
                pass
            continue
        if rows is not None:
            t, a = classify_rows(p, rows)
            trait_candidates.extend(t); accession_candidates.extend(a)
    return trait_candidates, accession_candidates


def classify_rows(path: Path, rows, sheet=None):
    if not rows: return [], []
    headers = list(rows[0].keys()); nh = {norm_header(h): h for h in headers}
    species_cols = [orig for k,orig in nh.items() if any(x in k for x in ("species", "taxon", "scientificname"))]
    colour_cols = [orig for k,orig in nh.items() if "color" in k or "colour" in k]
    acc_cols = [orig for k,orig in nh.items() if "accession" in k or "genbank" in k]
    trait, acc = [], []
    if species_cols and colour_cols:
        spc, cc = species_cols[0], colour_cols[0]
        parsed = []
        unknown = []
        for r in rows:
            sp = str(r.get(spc) or "").strip(); val = str(r.get(cc) or "").strip().lower()
            if not sp or not val: continue
            token = re.split(r"[/;, ]+", val)[0]
            state = COLOURS.get(token)
            if state: parsed.append((sp,state))
            else: unknown.append({"species":sp,"raw":val})
        if parsed:
            counts = Counter(x[1] for x in parsed)
            trait.append({"path":str(path),"sheet":sheet,"species_column":spc,"colour_column":cc,"n_parsed":len(parsed),"state_counts":dict(counts),"unknown_nonempty":unknown[:20],"table_sha256":sha(path.read_bytes())})
    if species_cols and acc_cols:
        spc, ac = species_cols[0], acc_cols[0]
        n = sum(bool(str(r.get(spc) or "").strip()) and bool(str(r.get(ac) or "").strip()) for r in rows)
        if n:
            acc.append({"path":str(path),"sheet":sheet,"species_column":spc,"accession_column":ac,"n_rows_with_accession":n,"table_sha256":sha(path.read_bytes())})
    return trait, acc


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out-dir", type=Path, default=OUT_DEFAULT); a = ap.parse_args()
    a.out_dir.mkdir(parents=True, exist_ok=True)
    dryad = dryad_inventory(a.out_dir)
    pmc = extract_europe_pmc(a.out_dir)
    trait, accession = audit_tables(a.out_dir)
    summary = {
        "version":"v1", "source_only":True, "biological_endpoint_computed":False,
        "observed_assignment_scored":False, "dryad":dryad, "europe_pmc":pmc,
        "trait_candidates":trait, "accession_candidates":accession,
        "trait_source_gate_candidate": any(x["n_parsed"] >= 40 and set(x["state_counts"]).issubset({"WHITE","PINK","RED"}) for x in trait),
        "accession_source_gate_candidate": any(x["n_rows_with_accession"] >= 30 for x in accession),
        "claim_boundary":"Source retrieval/schema audit only. No trait-tree join, no topology-conditioned label test, no Sankoff/Fitch endpoint."
    }
    (a.out_dir/"source_summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("SILENE_SOURCE_AUDIT="+json.dumps({
        "dryad_files":[{"id":f.get("id"),"name":f.get("name"),"downloaded":f.get("downloaded"),"statuses":[x.get("status") for x in f.get("attempts",[])]} for f in dryad.get("files",[])],
        "pmc_members":pmc.get("members",[]), "trait_candidates":trait, "accession_candidates":accession,
        "trait_source_gate_candidate":summary["trait_source_gate_candidate"], "accession_source_gate_candidate":summary["accession_source_gate_candidate"],
        "biological_endpoint_computed":False
    },ensure_ascii=False))

if __name__ == "__main__": main()
