#!/usr/bin/env python3
"""Test whether coarse visible flower-colour states compress stronger historical structure.

Input is the compact Fan2026 × GBIF × CHELSA species table.  The known FUZZY
GBIF duplicate `Camellia kissi` is dropped when the exact `C. kissii` row is
also present, matching the exact-taxonomy gate used elsewhere in this branch.

This is a descriptive/preliminary model comparison. Traditional sections are a
historical/taxonomic proxy, not a substitute for the primary nuclear phylogeny.
"""
from __future__ import annotations
import argparse
import pathlib
import re
import pandas as pd
import statsmodels.formula.api as smf

METRICS=("bio1_median","bio6_median","bio6_q05","bio1_iqr")


def norm_section(x: str) -> str:
    x=str(x or "").lower().strip()
    x=re.sub(r"^section\s+", "", x)
    x=re.sub(r"^sect\.\s*", "", x)
    return x.split(";")[0].strip()


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument("species_csv",type=pathlib.Path)
    ap.add_argument("--models",type=pathlib.Path,required=True)
    ap.add_argument("--breadth",type=pathlib.Path,required=True)
    a=ap.parse_args()

    df=pd.read_csv(a.species_csv)
    if {"Camellia kissi","Camellia kissii"}.issubset(set(df["taxon"])):
        df=df[df["taxon"]!="Camellia kissi"].copy()
    df["section_norm"]=df["section"].map(norm_section)

    model_rows=[]
    for scope,d in (("all_WAY",df),("AW_only",df[df.colour_state.isin(["A","W"])].copy())):
        for metric in METRICS:
            fits={
                "null":smf.ols(f"{metric} ~ 1",data=d).fit(),
                "colour":smf.ols(f"{metric} ~ C(colour_state)",data=d).fit(),
                "section":smf.ols(f"{metric} ~ C(section_norm)",data=d).fit(),
                "section+colour":smf.ols(f"{metric} ~ C(section_norm)+C(colour_state)",data=d).fit(),
            }
            best=min(x.aic for x in fits.values())
            for name,fit in fits.items():
                model_rows.append({
                    "scope":scope,
                    "metric":metric,
                    "model":name,
                    "n_species":int(fit.nobs),
                    "r2":fit.rsquared,
                    "adj_r2":fit.rsquared_adj,
                    "global_p":"" if name=="null" else fit.f_pvalue,
                    "aic":fit.aic,
                    "delta_aic":fit.aic-best,
                })

    n_sections=df.section_norm.nunique()
    breadth=[]
    for state,g in df.groupby("colour_state",sort=True):
        sections=sorted(g.section_norm.dropna().unique())
        breadth.append({
            "colour_state":state,
            "n_species":len(g),
            "n_sections":len(sections),
            "fraction_of_observed_sections":len(sections)/n_sections,
            "sections":";".join(sections),
        })

    a.models.parent.mkdir(parents=True,exist_ok=True)
    a.breadth.parent.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(model_rows).to_csv(a.models,index=False)
    pd.DataFrame(breadth).to_csv(a.breadth,index=False)


if __name__=="__main__":
    main()
