#!/usr/bin/env python3
"""Audit whether taxon overlap between candidate-free molecular systems and ecology is event-matched.

This intentionally distinguishes three increasingly strict quantities:
1. taxon-name overlap;
2. contrast/unit overlap;
3. same-study/sample event overlap.

The goal is to prevent same-species evidence from being silently upgraded into a
micro-to-ecology causal bridge.
"""
from __future__ import annotations
import argparse,csv,json
from collections import Counter
from pathlib import Path


def read_csv(p:Path):
    with p.open(newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))


def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('--contract',type=Path,required=True);ap.add_argument('--candidate-free',type=Path,required=True);ap.add_argument('--pollination',type=Path,required=True);ap.add_argument('--out-dir',type=Path,required=True);a=ap.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
    contract=read_csv(a.contract);cf=read_csv(a.candidate_free);poll=read_csv(a.pollination)
    assert len(contract)==5
    clusters=sorted({r['dependence_cluster'] for r in cf});assert len(clusters)==5
    contract_clusters=sorted(r['dependence_cluster'] for r in contract);assert clusters==contract_clusters
    poll_taxa={r['taxon'] for r in poll}

    # Independent reconstruction of the candidate-free taxon roster from the frozen labels.
    expected_taxa={
        'CJAPONICA':'Camellia japonica',
        'CRETICULATA':'Camellia reticulata',
        'CSIN_WHITE_PINK':'Camellia sinensis',
        'CNITIDISSIMA':'Camellia nitidissima',
        'CPERPETUA':'Camellia perpetua',
    }
    for r in contract: assert r['taxon']==expected_taxa[r['dependence_cluster']]

    taxon_overlap=[r for r in contract if r['taxon'] in poll_taxa]
    asserted_overlap=[r for r in contract if r['taxon_match']=='yes']
    assert {r['dependence_cluster'] for r in taxon_overlap}=={r['dependence_cluster'] for r in asserted_overlap}
    assert len(taxon_overlap)==3
    contrast_overlap=[r for r in contract if r['contrast_match']=='yes']
    same_sample=[r for r in contract if r['same_study_or_sample']=='yes']
    event_matched=[r for r in contract if r['event_match_status']=='identified']
    assert not contrast_overlap and not same_sample and not event_matched

    statuses=Counter(r['event_match_status'] for r in contract)
    rows=[]
    for r in contract:
        rows.append({
            'dependence_cluster':r['dependence_cluster'],
            'taxon':r['taxon'],
            'taxon_overlap':r['taxon'] in poll_taxa,
            'contrast_match':r['contrast_match'],
            'same_study_or_sample':r['same_study_or_sample'],
            'event_match_status':r['event_match_status'],
            'reason':r['reason'],
        })
    with (a.out_dir/'overlap_audit.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

    summary={
        'analysis':'micro_ecology_overlap_v0.1',
        'candidate_free_systems':len(contract),
        'pollination_taxa':len(poll_taxa),
        'taxon_name_overlap_systems':len(taxon_overlap),
        'taxon_name_overlap_fraction_of_candidate_free':len(taxon_overlap)/len(contract),
        'contrast_matched_systems':len(contrast_overlap),
        'same_study_or_sample_systems':len(same_sample),
        'event_matched_systems':len(event_matched),
        'event_status_counts':dict(statuses),
        'overlap_clusters':[r['dependence_cluster'] for r in taxon_overlap],
        'decision':'taxon-level overlap is 3/5, but exact molecular-ecological contrast/event overlap is 0/5; current public evidence cannot test whether candidate-free A/F/C/P implementation predicts ecological function within the same evolutionary or experimental event',
        'highest_leverage_targets':[
            'Camellia japonica: measure molecular/pigment/UV state and pollinator effectiveness/fitness in the same wild contrast',
            'Camellia perpetua: connect seasonal field ecology to matched petal molecular/spectral measurements rather than importing an independent S1-S5 developmental series',
            'Camellia sinensis: avoid upgrading cultivar/developmental colour contrasts to seed-garden pollination causation without matched material',
        ],
        'claim_ceiling':'identifiability/overlap audit only; 3/5 taxon overlap must not be represented as three causal micro-to-ecology replications',
    }
    (a.out_dir/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');print(json.dumps(summary,indent=2,ensure_ascii=False));return 0

if __name__=='__main__':raise SystemExit(main())
