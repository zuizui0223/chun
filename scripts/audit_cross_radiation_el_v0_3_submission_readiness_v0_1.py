#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MAN=ROOT/"manuscript"/"CROSS_RADIATION_EVOLUTION_LETTERS_V0_3_TEMPORAL_MEMORY_CANDIDATE.md"
META=ROOT/"submission"/"CROSS_RADIATION_EL_SUBMISSION_METADATA_V0_2.json"
VALIDATOR=ROOT/"scripts"/"validate_cross_radiation_el_submission_metadata_v0_2.py"

GUIDELINES_URL="https://academic.oup.com/evlett/pages/author-guidelines"
GUIDELINES_CHECKED="2026-09-29"


def words(s:str)->int:
    return len(re.findall(r"\b[\w][\w'’.-]*\b",s))


def between(s:str,start:str,end:str|None)->str:
    i=s.find(start)
    if i<0: return ""
    i+=len(start)
    j=s.find(end,i) if end else -1
    return s[i:j if j>=0 else None]


def metadata_summary()->dict:
    spec=importlib.util.spec_from_file_location("meta_validator",VALIDATOR)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod.validate_metadata(json.loads(META.read_text()))


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--figure-manifest",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    a.out.parent.mkdir(parents=True,exist_ok=True)

    s=MAN.read_text()
    title=between(s,"# Title","Running title").replace("*","").strip()
    teaser=between(s,"## Teaser text","# Abstract").strip()
    abstract=between(s,"# Abstract","Keywords:").strip()
    km=re.search(r"Keywords:\s*([^\n]+)",s)
    keywords=[x.strip() for x in (km.group(1) if km else "").split(";") if x.strip()]
    refs=s.find("# References")
    end=s.find("# Data and code availability")
    main=s[:end if end>=0 else refs]
    figsec=between(s,"# Figure legends and alt text","# References")
    figure_count=len(re.findall(r"\*\*Figure \d+\.",figsec))
    alt_count=len(re.findall(r"\*\*Alt text:\*\*",figsec))

    figs=json.loads(a.figure_manifest.read_text())
    meta=metadata_summary()
    journal_checks={
      "title_words":{"value":words(title),"limit":30,"pass":words(title)<=30},
      "abstract_words":{"value":words(abstract),"limit":300,"pass":words(abstract)<=300},
      "teaser_words":{"value":words(teaser),"limit":150,"pass":words(teaser)<=150},
      "keywords":{"value":len(keywords),"limit":10,"pass":len(keywords)<=10},
      "approximate_main_text_words":{"value":words(main),"guide":5000,"pass":words(main)<=5000},
      "required_end_matter":{
        "data_and_code": "# Data and code availability" in s,
        "author_contributions":"# Author contributions" in s,
        "funding":"# Funding" in s,
        "conflict_of_interest":"# Conflict of interest" in s,
        "acknowledgements":"# Acknowledgements" in s
      },
      "figures":{"count":figure_count,"alt_text_count":alt_count,"all_have_alt_text":figure_count==alt_count},
      "submission_figure_files":{"count":len(figs["figures"]),"all_pdf":all(x["format"]=="pdf" for x in figs["figures"])},
    }
    auto_pass=(
      all(v["pass"] for k,v in journal_checks.items() if isinstance(v,dict) and "pass" in v)
      and all(journal_checks["required_end_matter"].values())
      and journal_checks["figures"]["all_have_alt_text"]
      and journal_checks["submission_figure_files"]["all_pdf"]
    )
    human_holds={
      "phase1_author_identity":meta["phase1_missing"],
      "phase2_declarations":meta["phase2_missing"],
      "phase3_archive":meta["phase3_missing"]
    }
    out={
      "version":"v0.1",
      "status":"EL_V0_3_AUTOMATED_SUBMISSION_CHECKS_PASS_HUMAN_METADATA_HOLD" if auto_pass else "EL_V0_3_AUTOMATED_SUBMISSION_CHECKS_FAIL",
      "guidelines":{"url":GUIDELINES_URL,"checked_on":GUIDELINES_CHECKED,"article_type":"Letter"},
      "manuscript":str(MAN.relative_to(ROOT)),
      "journal_checks":journal_checks,
      "metadata_validator_state":meta,
      "human_only_holds":human_holds,
      "remaining_render_note":"Initial free-format submission permits a single readable manuscript file; line numbering should be applied in the final human-metadata render. Frozen science markdown is not modified by this audit.",
      "archive_preparation_note":"A persistent identifier is still required by the repository metadata contract before final bundle; this audit does not invent a DOI.",
      "automated_checks_pass":auto_pass,
      "ready_for_final_bundle":bool(auto_pass and meta["ready_for_final_bundle"]),
      "scientific_results_changed":False,
      "frozen_v0_3_science_changed":False
    }
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
