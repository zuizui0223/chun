#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from pathlib import Path

ORG=Path('data/atlas_epimedium_ingested_v0_1/analysis/source_taxon_summary.csv')
OVER=Path('data/atlas_epimedium_ingested_v0_1/analysis/molecular_panel_overlap.csv')
MOL=Path('data/epimedium_eight_species_molecular_panel_v0_1.csv')
EXPECTED=Path('data/epimedium_cross_level_endpoint_bridge_summary_v0_1.json')

def read(p):
    with p.open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))
org={r['taxon_normalized']:r for r in read(ORG)}
over={r['taxon_normalized']:r for r in read(OVER)}
mol={r['taxon_accepted']:r for r in read(MOL)}
joined=[]
for taxon,r in mol.items():
    o=over[taxon]
    if o['in_reproductive_s4']!='True':continue
    s=org[taxon]
    joined.append({
      'taxon':taxon,'A_status':r['A_status'],'joint_code':s['joint_codes'],
      'sepal_codes':s['sepal_codes'],'spur_codes':s['spur_codes'],
      'ANS_state':r['ANS_state'],'DFR_state':r['DFR_state'],
      'CHS_state':r['CHS_state'],'FLS_state':r['FLS_state'],
      'external_colour_variation_warning':o['external_colour_variation_warning']=='True'})
assert len(joined)==6
aminus=[r for r in joined if r['A_status']=='A_MINUS'];aplus=[r for r in joined if r['A_status']=='A_PLUS']
assert len(aminus)==len(aplus)==3
assert {r['joint_code'] for r in aminus}=={'1:1'}
assert all(r['ANS_state']=='LOW' for r in aminus)
assert sum(r['DFR_state']=='LOW' for r in aminus)==2
assert {r['CHS_state'] for r in aminus}=={'NO_A_MINUS_SPECIFIC_CHANGE','CHS1_LOW','CHS2_LOW'}
assert {r['joint_code'] for r in aplus}=={'2:2','3:3'}
assert not ({r['joint_code'] for r in aplus}&{r['joint_code'] for r in aminus})
summary={
 'version':'v0.1','same_radiation':'EPIMEDIUM_SECT_DIPHYLLON',
 'molecular_panel_taxa':8,'macro_molecular_overlap_taxa':6,
 'overlap_A_plus':3,'overlap_A_minus':3,
 'A_minus_shared_source_joint_code':'1:1',
 'A_minus_ANS_low':'3/3','A_minus_DFR_low':'2/3',
 'A_minus_CHS_implementations':['NO_A_MINUS_SPECIFIC_CHANGE','CHS1_LOW','CHS2_LOW'],
 'A_plus_source_joint_codes':['2:2','3:3'],
 'source_code_to_hue':'UNRESOLVED_CODEBOOK_NO_HUE_IMPUTATION',
 'historical_event_independence':'FAIL_HOLD_NOT_ESTIMATED',
 'cross_level_result':'SAME_SOURCE_ENDPOINT_CODE_WITH_RECURRENT_CORE_AND_HETEROGENEOUS_MOLECULAR_IMPLEMENTATION',
 'claim_boundary':'Endpoint/taxon bridge only; not an estimate of independent transition recurrence, exact molecular-individual matching, or visible hue identity.',
 'paper1_science_changed':False}
assert summary==json.loads(EXPECTED.read_text())
print(json.dumps(summary,indent=2))
