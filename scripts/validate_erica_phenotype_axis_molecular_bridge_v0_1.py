#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from collections import Counter
from pathlib import Path

SRC=Path('data/erica_white_yellow_mechanisms_v0_1.csv')
EXPECTED=Path('data/erica_phenotype_axis_molecular_bridge_summary_v0_1.json')
with SRC.open(newline='',encoding='utf-8') as f: rows=list(csv.DictReader(f))
assert len(rows)==8
white=[r for r in rows if r['target_state']=='WHITE']; yellow=[r for r in rows if r['target_state']=='YELLOW']
assert (len(white),len(yellow))==(6,2)
assert all(r['focal_node']=='F3_PRIME_H' and r['node_level']=='BRANCH_HYDROXYLATION' for r in yellow)
assert all(r['focal_node']!='F3_PRIME_H' for r in white)
white_nodes=Counter(r['focal_node'] for r in white)
assert set(white_nodes)=={'UDP_GST','ANS','DFR','bHLH'}
assert max(white_nodes.values())==2
summary={
 'version':'v0.1','same_radiation':'CAPE_ERICA',
 'source_doi':'10.3389/fpls.2019.01565','derived_taxa':8,
 'phenotype_axes':{
   'PIGMENT_DEPLETION_WHITE':{
     'taxa':6,'focal_node_classes':sorted(white_nodes),'unique_focal_node_classes':4,
     'branch_hydroxylation_F3_prime_H':'0/6'},
   'HUE_BRANCH_YELLOW':{
     'taxa':2,'focal_node_classes':['F3_PRIME_H'],'branch_hydroxylation_F3_prime_H':'2/2',
     'implementation':['REGULATORY_MRE','CODING_LOSS']}},
 'cross_level_result':'HUE_BRANCH_CONCENTRATES_ON_F3_PRIME_H_WHILE_PIGMENT_DEPLETION_DISPERSES_ACROSS_LATE_AND_REGULATORY_NODES',
 'alignment_to_iochrominae':'RETROSPECTIVE_INDEPENDENT_ALIGNMENT_AT_PHENOTYPE_AXIS_TO_MOLECULAR_SUBSPACE_LEVEL',
 'prospective_status':'NOT_PROSPECTIVE_EXISTING_TABLE_PREVIOUSLY_INSPECTED',
 'event_independence':'PUTATIVE_COMPARISON_SETS_NOT_USED_AS_EVENT_RATE_DENOMINATOR',
 'claim_boundary':'Descriptive same-radiation axis mapping only; no pooled event rate, no exact mutation recurrence estimate, and no prospective validation claim.',
 'paper1_science_changed':False}
assert summary==json.loads(EXPECTED.read_text())
print(json.dumps(summary,indent=2))
