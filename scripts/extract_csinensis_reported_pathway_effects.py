#!/usr/bin/env python3
"""Extract stage-matched white-vs-pink pathway effects from Zhou et al. 2020 supplements.

Table S8 supplies stage-specific flavonoid gene annotations and expression values.
Table S6 and S9 contain broader all-sample expression profiles for selected WGCNA
hub/module genes. We keep data-source provenance explicit and never treat stages
or genes as independent studies.

Primary effect: mean(log2(FPKM+1)) in pink BTP minus white ZJW within the same
stage and gene. Hedges g is also reported as a descriptive replicate-standardized
within-study effect (n=3 vs n=3), but downstream cross-study meta-analysis must
respect the single CSIN_WHITE_PINK independence cluster.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import defaultdict
from pathlib import Path
from statistics import mean, stdev

from openpyxl import load_workbook

STAGES = range(1, 6)
GENE_PATTERNS = [
    ("DFR", re.compile(r"\bDFR\b|DIHYDROFLAVONOL[- ]?4[- ]?REDUCTASE", re.I)),
    ("ANS", re.compile(r"\bANS\b|ANTHOCYANIDIN SYNTHASE", re.I)),
    ("UFGT", re.compile(r"\bUFGT\b|UDP.*GLUCOSYLTRANSFERASE", re.I)),
    ("FLS", re.compile(r"\bFLS\d*\b|FLAVONOL SYNTHASE", re.I)),
    ("ANR", re.compile(r"\bANR\b|ANTHOCYANIDIN REDUCTASE", re.I)),
    ("LAR", re.compile(r"\bF?LAR\b|LEUCOANTHOCYANIDIN REDUCTASE", re.I)),
    ("CHS", re.compile(r"\bCHS\d*\b|CHALCONE SYNTHASE", re.I)),
    ("F3H", re.compile(r"\bF3H\b|FLAVANONE 3[- ]HYDROXYLASE", re.I)),
    ("F3H_PRIME", re.compile(r"F3['’]H", re.I)),
    ("F3H_5PRIME", re.compile(r"F3['’]5['’]H", re.I)),
]


def norm_gene_name(text: object) -> str | None:
    s = str(text or "").strip()
    if not s or s == "--":
        return None
    for name, pat in GENE_PATTERNS:
        if pat.search(s):
            return name
    return None


def fnum(x):
    try:
        if x is None or str(x).strip() == "":
            return None
        v = float(x)
        return v if math.isfinite(v) and v >= 0 else None
    except Exception:
        return None


def hedges_g(pink: list[float], white: list[float]) -> float | None:
    if len(pink) < 2 or len(white) < 2:
        return None
    sp_num = (len(pink)-1)*stdev(pink)**2 + (len(white)-1)*stdev(white)**2
    df = len(pink) + len(white) - 2
    if df <= 0:
        return None
    sp = math.sqrt(sp_num / df)
    if sp == 0:
        return None
    d = (mean(pink)-mean(white))/sp
    j = 1 - 3/(4*(len(pink)+len(white))-9)
    return j*d


def load_s8(path: Path):
    wb = load_workbook(path, read_only=True, data_only=True)
    annotations: dict[str, str] = {}
    records = []
    for stage in STAGES:
        ws = next((x for x in wb.worksheets if f"stage{stage}" in x.title.lower()), None)
        if ws is None:
            continue
        for row in ws.iter_rows(values_only=True):
            gid = str(row[0] or "").strip()
            if not gid or gid.startswith("#") or gid.lower().startswith("supplement"):
                continue
            raw_name = row[1] if len(row) > 1 else None
            gclass = norm_gene_name(raw_name)
            if gclass:
                annotations[gid] = gclass
            # S8 uses ID/name then three ZJW FPKM/count pairs and three BTP pairs.
            if len(row) < 14:
                continue
            white = [fnum(row[i]) for i in (2,4,6)]
            pink = [fnum(row[i]) for i in (8,10,12)]
            white = [x for x in white if x is not None]
            pink = [x for x in pink if x is not None]
            if gclass and white and pink:
                records.append((gid,gclass,stage,"S8_stage_selected",white,pink))
    return annotations, records


def find_header(ws, predicate, max_rows=8):
    for idx, row in enumerate(ws.iter_rows(min_row=1, max_row=max_rows, values_only=True), start=1):
        vals=[str(x or "").strip() for x in row]
        if predicate(vals):
            return idx, vals
    return None, None


def load_s6(path: Path):
    wb=load_workbook(path,read_only=True,data_only=True); ws=wb.active
    hrow, headers=find_header(ws,lambda v: any(x.endswith("_FPKM") for x in v) and ("#ID" in v or "ID" in v))
    if hrow is None:return {},[]
    idx={h:i for i,h in enumerate(headers)}
    idcol=idx.get("#ID",idx.get("ID",0)); namecol=idx.get("gene_name",1)
    records=[]; annotations={}
    for row in ws.iter_rows(min_row=hrow+1,values_only=True):
        gid=str(row[idcol] or "").strip()
        if not gid:continue
        gclass=norm_gene_name(row[namecol] if namecol<len(row) else None)
        if not gclass:continue
        annotations[gid]=gclass
        for stage in STAGES:
            white=[];pink=[]
            for rep in (1,2,3):
                for prefix,dest in (("ZJW",white),("BTP",pink)):
                    key=f"{prefix}{stage}{rep}_FPKM"
                    if key in idx and idx[key]<len(row):
                        v=fnum(row[idx[key]])
                        if v is not None:dest.append(v)
            if white and pink:records.append((gid,gclass,stage,"S6_hub_full_profile",white,pink))
    return annotations,records


def load_s9(path: Path, annotations: dict[str,str]):
    wb=load_workbook(path,read_only=True,data_only=True);ws=wb.active
    hrow,headers=find_header(ws,lambda v: "modColor" in v and any(re.fullmatch(r"ZJW[1-5][1-3]",x) for x in v))
    if hrow is None:return []
    idx={h:i for i,h in enumerate(headers)}
    # In the source workbook the first header cell is blank; gene ID is column 1.
    records=[]
    for row in ws.iter_rows(min_row=hrow+1,values_only=True):
        gid=str(row[0] or "").strip()
        if gid not in annotations:continue
        gclass=annotations[gid]
        for stage in STAGES:
            white=[];pink=[]
            for rep in (1,2,3):
                for prefix,dest in (("ZJW",white),("BTP",pink)):
                    key=f"{prefix}{stage}{rep}"
                    if key in idx and idx[key]<len(row):
                        v=fnum(row[idx[key]])
                        if v is not None:dest.append(v)
            if white and pink:records.append((gid,gclass,stage,"S9_module_full_profile",white,pink))
    return records


def summarize_gene_records(records):
    # Prefer full-profile sources over stage-selected S8 for a given gene/stage.
    priority={"S6_hub_full_profile":0,"S9_module_full_profile":1,"S8_stage_selected":2}
    chosen={}
    for rec in records:
        key=(rec[0],rec[2])
        if key not in chosen or priority[rec[3]]<priority[chosen[key][3]]:
            chosen[key]=rec
    out=[]
    for (gid,stage),(gid,gclass,stage,source,white,pink) in sorted(chosen.items(),key=lambda x:(x[0][1],x[0][0])):
        lw=[math.log2(x+1) for x in white];lp=[math.log2(x+1) for x in pink]
        out.append({
            "independence_cluster":"CSIN_WHITE_PINK","gene_id":gid,"gene_class":gclass,"stage":stage,"source_table":source,
            "n_white":len(white),"n_pink":len(pink),"mean_white_fpkm":mean(white),"mean_pink_fpkm":mean(pink),
            "mean_log2_white":mean(lw),"mean_log2_pink":mean(lp),"pink_minus_white_log2fpkm":mean(lp)-mean(lw),
            "hedges_g_log2fpkm":hedges_g(lp,lw),
            "claim_ceiling":"within-study reported FPKM effect; stages/genes are repeated measures, not independent studies"
        })
    return out


def module_name(gclass):
    if gclass in {"DFR","ANS","UFGT"}:return "anthocyanin_downstream"
    if gclass=="FLS":return "flavonol_branch"
    if gclass in {"ANR","LAR"}:return "proanthocyanidin_branch"
    if gclass in {"CHS","F3H","F3H_PRIME","F3H_5PRIME"}:return "shared_or_upstream_flavonoid"
    return None


def summarize_modules(gene_rows):
    out=[]
    by=defaultdict(list)
    for r in gene_rows:
        mod=module_name(r["gene_class"])
        if mod:by[(r["stage"],mod)].append(r)
    for (stage,mod),rs in sorted(by.items()):
        vals=[r["pink_minus_white_log2fpkm"] for r in rs]
        out.append({"independence_cluster":"CSIN_WHITE_PINK","stage":stage,"module":mod,"n_genes":len(rs),"mean_gene_log2_effect":mean(vals),"median_gene_log2_effect":sorted(vals)[len(vals)//2],"gene_ids":";".join(r["gene_id"] for r in rs),"claim_ceiling":"descriptive module summary from reported selected/hub/module genes; not an unbiased whole-pathway estimate"})
    # Predefined contrasts where both modules exist.
    lookup={(r["stage"],r["module"]):r for r in out}
    contrast=[]
    for stage in STAGES:
        a=lookup.get((stage,"anthocyanin_downstream"));f=lookup.get((stage,"flavonol_branch"));p=lookup.get((stage,"proanthocyanidin_branch"))
        if a and f:
            contrast.append({"independence_cluster":"CSIN_WHITE_PINK","stage":stage,"contrast":"anthocyanin_minus_flavonol","difference_of_module_log2_effects":a["mean_gene_log2_effect"]-f["mean_gene_log2_effect"],"claim_ceiling":"positive means the pink-vs-white expression shift is more anthocyanin-side than flavonol-side in this reported gene subset"})
        if a and p:
            contrast.append({"independence_cluster":"CSIN_WHITE_PINK","stage":stage,"contrast":"anthocyanin_minus_proanthocyanidin","difference_of_module_log2_effects":a["mean_gene_log2_effect"]-p["mean_gene_log2_effect"],"claim_ceiling":"keeps PA branch separate because LAR/ANR need not track FLS"})
    return out,contrast


def write_csv(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    fields=list(rows[0]) if rows else ["empty"]
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)


def main():
    ap=argparse.ArgumentParser();ap.add_argument("--s6",type=Path,required=True);ap.add_argument("--s8",type=Path,required=True);ap.add_argument("--s9",type=Path,required=True);ap.add_argument("--out-dir",type=Path,required=True);a=ap.parse_args()
    ann8,r8=load_s8(a.s8);ann6,r6=load_s6(a.s6);ann={**ann8,**ann6};r9=load_s9(a.s9,ann)
    gene=summarize_gene_records(r8+r6+r9);mods,contrasts=summarize_modules(gene)
    write_csv(a.out_dir/"gene_stage_effects.csv",gene);write_csv(a.out_dir/"module_stage_effects.csv",mods);write_csv(a.out_dir/"module_contrasts.csv",contrasts)
    summary={"independence_cluster":"CSIN_WHITE_PINK","s8_annotated_gene_ids":len(ann8),"s6_annotated_gene_ids":len(ann6),"gene_stage_effect_rows":len(gene),"module_stage_rows":len(mods),"module_contrast_rows":len(contrasts),"sources":{"S6":str(a.s6),"S8":str(a.s8),"S9":str(a.s9)},"claim_ceiling":"reported processed-expression pilot; one biological independence cluster; no cross-study pooled effect yet"}
    (a.out_dir/"summary.json").write_text(json.dumps(summary,indent=2)+"\n");print(json.dumps(summary,indent=2))

if __name__=="__main__":main()
