#!/usr/bin/env python3
"""Audit Fan2026 Supplementary Table S2 anthocyanin matrix.

The article text describes 29 red-like petal species and 2–15 anthocyanins per
species. The public workbook contains 33 species-labelled rows before the note
block. We do not guess which four rows belong outside the described 29-species
panel. Instead we freeze the mismatch and report matrix-level heterogeneity with
an explicit `supplement_rows_unresolved` claim ceiling.
"""
from __future__ import annotations
import argparse,csv,json,math
from itertools import combinations
from pathlib import Path
from statistics import mean,median,stdev
from openpyxl import load_workbook


def fnum(x):
    try:return float(x or 0)
    except Exception:return 0.0

def bray_comp(a,b):
    sa=sum(a);sb=sum(b)
    if sa<=0 or sb<=0:return None
    pa=[x/sa for x in a];pb=[x/sb for x in b]
    return 0.5*sum(abs(x-y) for x,y in zip(pa,pb))

def q(xs,p):
    ys=sorted(xs);n=len(ys)
    if not n:return None
    h=(n-1)*p;i=math.floor(h);j=math.ceil(h)
    return ys[i] if i==j else ys[i]*(j-h)+ys[j]*(h-i)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--workbook',type=Path,required=True);ap.add_argument('--output-dir',type=Path,required=True);ap.add_argument('--article-expected-red-like-species',type=int,default=29);a=ap.parse_args()
    wb=load_workbook(a.workbook,read_only=True,data_only=True);ws=wb['Table.S2']
    headers=[str(x or '').strip() for x in next(ws.iter_rows(min_row=2,max_row=2,values_only=True))]
    pigment_headers=headers[1:24]
    rows=[]
    for r in ws.iter_rows(min_row=3,values_only=True):
        name=str(r[0] or '').replace('\xa0',' ').strip()
        if not name:break
        if name.lower().startswith('note'):break
        vals=[fnum(x) for x in r[1:24]]
        total=sum(vals);rich=sum(x>0 for x in vals);cy=sum(vals[i] for i,h in enumerate(pigment_headers) if h.startswith('Cy'));dp=sum(vals[i] for i,h in enumerate(pigment_headers) if h.startswith('Dp'))
        frac=cy/total if total>0 else None
        p=[x/total for x in vals if x>0] if total>0 else []
        sh=-sum(x*math.log(x) for x in p) if p else None
        rows.append({'species_label':name,'total_reported_anthocyanin':total,'detected_anthocyanin_richness':rich,'cyanidin_total':cy,'delphinidin_total':dp,'cyanidin_fraction':frac,'composition_shannon':sh,'claim_ceiling':'Fan2026 Table S2 supplement row; membership in article-described 29-red-like panel unresolved until crosswalk is explicit'})
    if not rows:raise SystemExit('no Table S2 species rows found')
    matrix=[]
    # Re-read values in same row order for pairwise composition distances.
    for r in ws.iter_rows(min_row=3,max_row=2+len(rows),values_only=True):matrix.append([fnum(x) for x in r[1:24]])
    d=[bray_comp(matrix[i],matrix[j]) for i,j in combinations(range(len(matrix)),2)];d=[x for x in d if x is not None]
    totals=[r['total_reported_anthocyanin'] for r in rows];rich=[r['detected_anthocyanin_richness'] for r in rows];cf=[r['cyanidin_fraction'] for r in rows if r['cyanidin_fraction'] is not None]
    byname={r['species_label']:k for k,r in enumerate(rows)}
    jp=next((k for n,k in byname.items() if n=='C. japonica'),None);ru=next((k for n,k in byname.items() if 'rusticana' in n),None)
    pair={}
    if jp is not None and ru is not None:
        pair={'C_japonica_vs_rusticana_composition_bray':bray_comp(matrix[jp],matrix[ru]),'rusticana_to_japonica_total_ratio':totals[ru]/totals[jp] if totals[jp]>0 else None,'C_japonica_richness':rich[jp],'C_rusticana_richness':rich[ru]}
    summary={'source':'Fan2026_PMC12946509_TableS2','article_expected_red_like_species':a.article_expected_red_like_species,'supplement_species_label_rows':len(rows),'row_count_difference':len(rows)-a.article_expected_red_like_species,'article_stated_richness_range':'2-15','supplement_row_richness_min':min(rich),'supplement_row_richness_median':median(rich),'supplement_row_richness_max':max(rich),'rows_below_article_stated_min_richness':sum(x<2 for x in rich),'total_anthocyanin_min':min(totals),'total_anthocyanin_median':median(totals),'total_anthocyanin_max':max(totals),'total_max_to_min_ratio':max(totals)/min(totals) if min(totals)>0 else None,'total_cv':stdev(totals)/mean(totals),'pairwise_normalized_composition_bray_q25':q(d,.25),'pairwise_normalized_composition_bray_median':median(d),'pairwise_normalized_composition_bray_q75':q(d,.75),'pairwise_normalized_composition_bray_max':max(d),'rows_cyanidin_fraction_gt_0_9':sum(x>.9 for x in cf),'rows_with_delphinidin':sum(r['delphinidin_total']>0 for r in rows),**pair,'decision':'do not infer a 29-species red-state macro matrix from all 33 supplement rows until the article-to-supplement row crosswalk is resolved','claim_ceiling':'quantitative supplement-matrix audit and heterogeneity diagnostic; unresolved panel membership prevents treating all rows as the article-described red-like macro sample'}
    a.output_dir.mkdir(parents=True,exist_ok=True)
    with (a.output_dir/'species_row_summary.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (a.output_dir/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
