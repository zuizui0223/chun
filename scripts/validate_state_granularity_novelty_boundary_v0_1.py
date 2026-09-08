#!/usr/bin/env python3
"""Validate the state-granularity novelty boundary and forbid unsupported priority claims."""
from __future__ import annotations
import csv,re
from pathlib import Path

MATRIX=Path('data/state_granularity_novelty_boundary_v0_1.csv')
DOC=Path('docs/STATE_GRANULARITY_NOVELTY_BOUNDARY_V0_1.md')
REQUIRED_IDS={
 'GENERAL_CHARACTER_CONSTRUCTION','MOLECULAR_LUMPABILITY','NICOTIANA_CATEGORY_ALIASING',
 'ANTIRRHINEAE_POLYMORPHISM','IRIS_POLYMORPHIC_MODEL','SOLANACEAE_PATHWAY_ALIASING',
 'CAMELLIA_THREE_STATE_ASR','CURRENT_MULTI_RADIATION_TEST'}
REQUIRED_DOIS={
 '10.1093/sysbio/syz005','10.1093/sysbio/syab074','10.1093/aob/mcv048',
 '10.1093/aob/mcw043','10.3389/fpls.2020.569811','10.1111/nph.13576','10.1111/pbi.70442'}

rows=list(csv.DictReader(MATRIX.open()))
ids={r['evidence_id'] for r in rows}
assert ids==REQUIRED_IDS,(ids,REQUIRED_IDS)
assert len(rows)==len(ids)
for r in rows:
    assert r['priority_claim_allowed'] in {'NO','NO_FIRST_PRIORITY_CLAIM'}
    assert r['prior_art_establishes'] and r['remaining_distinct_contribution']
text=DOC.read_text()
for doi in REQUIRED_DOIS: assert doi in text,doi
assert 'NOVELTY_BOUNDARY_SET_NO_PRIORITY_CLAIM' in text
assert 'state-granularity' in text.lower() or 'state granularity' in text.lower()
# Forbid affirmative priority formulas while allowing explicit negative examples such as
# “Do not claim: the first ...” and “first ... remains unverified”.
for line in text.splitlines():
    low=line.lower().strip()
    if 'first' not in low: continue
    allowed=any(x in low for x in ('do **not** currently claim','do not currently claim','unverified','not evidence of priority','not the general observation'))
    if not allowed and re.search(r'\b(first|first-ever|first demonstration)\b',low):
        raise AssertionError('unsupported priority wording: '+line)
print({'rows':len(rows),'priority_claims':'FORBIDDEN','status':'PASS'})
