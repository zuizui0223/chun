#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import urllib.request
from collections import defaultdict
from difflib import SequenceMatcher

import pandas as pd

TRAIT_URL='https://pmc-oa-opendata.s3.amazonaws.com/PMC7588356.1/Table_1.xlsx'
ACC_URL='https://pmc-oa-opendata.s3.amazonaws.com/PMC7588356.1/Data_Sheet_1.csv'
TRAIT_SHA='183ef5231c48e782b0ea69a7aa5605d40c892dd91d9d9b2d259ed7b65d230072'
ACC_SHA='942d684256eb4527d02b274d9da374c8cc5585a190ef20a9058c231460a4ad71'


def get(url):
    req=urllib.request.Request(url,headers={'User-Agent':'chun-iris-taxon-label-inspection/0.1'})
    with urllib.request.urlopen(req,timeout=120) as r:return r.read()

def clean(x):
    if pd.isna(x):return ''
    return re.sub(r'\s+',' ',str(x)).strip()

def simple(s):
    s=clean(s).lower().replace('×','x').replace('_',' ')
    s=re.sub(r'\b(subsp|subs|var|ssp|cf)\.?\b',' ',s)
    s=re.sub(r'\b(l|mill|auct)\.?\b',' ',s)
    s=re.sub(r'[^a-z0-9]+',' ',s)
    return ' '.join(s.split())

def binom(s):
    s=simple(s)
    toks=s.split()
    if not toks:return ''
    # hybrid source form Irisxgermanica -> iris germanica
    if toks[0].startswith('irisx') and len(toks[0])>5:
        return 'iris '+toks[0][5:]
    if toks[0]=='iris' and len(toks)>1:
        if toks[1]=='x' and len(toks)>2:return 'iris '+toks[2]
        return 'iris '+toks[1]
    return ' '.join(toks[:2])

trait_b=get(TRAIT_URL); acc_b=get(ACC_URL)
assert hashlib.sha256(trait_b).hexdigest()==TRAIT_SHA
assert hashlib.sha256(acc_b).hexdigest()==ACC_SHA
traits=pd.read_excel(io.BytesIO(trait_b),sheet_name='Source of data',engine='openpyxl')
trait_raw=[clean(x) for x in traits['Species'] if clean(x)]
rows=list(csv.reader(io.StringIO(acc_b.decode('utf-8-sig')),delimiter=';'))
assert rows[1]==['organism','matK','trnL','ndhF','trnK','rbcL','ITS']
acc_raw=[clean(r[0]) for r in rows[2:] if r and clean(r[0])]

tg=defaultdict(list); ag=defaultdict(list)
for x in trait_raw:tg[binom(x)].append(x)
for x in acc_raw:ag[binom(x)].append(x)

trait_keys=set(tg); acc_keys=set(ag)
trait_only=sorted(trait_keys-acc_keys)
acc_only=sorted(acc_keys-trait_keys)

def candidates(key, pool):
    return sorted(((round(SequenceMatcher(None,key,p).ratio(),4),p) for p in pool),reverse=True)[:4]

out={
 'status':'IRIS_SOURCE_TAXON_LABEL_INSPECTION_ONLY',
 'trait_rows':len(trait_raw),'accession_rows':len(acc_raw),
 'trait_binomial_keys':len(trait_keys),'accession_binomial_keys':len(acc_keys),
 'trait_duplicate_binomial_groups':{k:v for k,v in tg.items() if len(v)>1},
 'trait_only':[{ 'key':k,'raw':tg[k],'candidate_accession_keys':candidates(k,acc_only)} for k in trait_only],
 'accession_only':[{ 'key':k,'raw':ag[k]} for k in acc_only],
 'auc_computed':False,'decision_computed':False,'trait_values_inspected':False,'paper1_science_changed':False,
}
print(json.dumps(out,indent=2,ensure_ascii=False))
