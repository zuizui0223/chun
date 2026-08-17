#!/usr/bin/env python3
"""Separate family-level micro recurrence from strict ortholog/paralog recurrence.

The input is a provenance crosswalk built without macro-transition information.
A feature can be recurrent at the family/module-name level while having no
sequence-resolved ortholog repeated across independent biological clusters.
That distinction is the pre-macro claim gate for H_MICRO_MACRO_REUSE.
"""
from __future__ import annotations
import argparse,csv
from collections import defaultdict
from pathlib import Path

ANCHOR_STATUSES={
    'exact_named_sequence_anchor',
    'named_paralogs_resolved_within_species',
}

def yes(x:str)->bool:
    return x.strip().lower()=='yes'

def rank_class(family_n:int, anchored_n:int, exact_recurrent_n:int)->str:
    if exact_recurrent_n>=2:
        return 'A_strict_crossspecies_node_recurrent'
    if family_n>=2:
        return 'B_family_recurrent_orthology_unresolved'
    if family_n==1 and anchored_n>=1:
        return 'C_strict_node_single_cluster_only'
    return 'D_single_cluster_family_only'

def macro_level(family_n:int, exact_recurrent_n:int)->str:
    if exact_recurrent_n>=2:
        return 'ready_strict_node_level'
    if family_n>=2:
        return 'ready_family_or_module_level_only'
    return 'not_recurrent_for_enrichment'

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('crosswalk',type=Path)
    ap.add_argument('--resolution-output',type=Path,required=True)
    ap.add_argument('--score-output',type=Path,required=True)
    a=ap.parse_args()
    with a.crosswalk.open(newline='',encoding='utf-8') as fh:
        rows=list(csv.DictReader(fh))

    by_feature=defaultdict(list)
    for r in rows:
        if yes(r['family_recurrence_counted']):
            by_feature[(r['feature'],r['module'])].append(r)

    resolution=[];score=[]
    for (feature,module),rs in sorted(by_feature.items()):
        family_clusters=sorted({r['independence_cluster'] for r in rs})
        anchored_clusters=sorted({r['independence_cluster'] for r in rs if r['orthology_status'] in ANCHOR_STATUSES})
        unresolved_clusters=sorted({r['independence_cluster'] for r in rs if r['orthology_status'] not in ANCHOR_STATUSES})

        # Strict recurrence requires the same non-empty strict node label in >=2
        # independent biological clusters. Within-cluster paralogs never count as
        # independent reuse.
        labels=defaultdict(set)
        for r in rs:
            lab=r['strict_node_label'].strip()
            if lab and r['orthology_status']=='exact_named_sequence_anchor':
                labels[lab].add(r['independence_cluster'])
        recurrent_labels=sorted(lab for lab,clusters in labels.items() if len(clusters)>=2)
        exact_clusters=sorted(set().union(*(labels[x] for x in recurrent_labels))) if recurrent_labels else []

        statuses=sorted({r['orthology_status'] for r in rs})
        source_ids=sorted({r['source_ids'] for r in rs if r['source_ids']})
        resolution.append({
            'feature':feature,'module':module,
            'family_recurrence_clusters':len(family_clusters),
            'named_or_sequence_anchored_clusters':len(anchored_clusters),
            'strict_crossspecies_exact_recurrence_clusters':len(exact_clusters),
            'unresolved_or_family_only_clusters':len(unresolved_clusters),
            'recurrent_strict_node_labels':';'.join(recurrent_labels),
            'independence_clusters':';'.join(family_clusters),
            'orthology_statuses':';'.join(statuses),
            'source_id_sets':' | '.join(source_ids),
            'resolution_conclusion':('strict cross-species node recurrence demonstrated' if exact_clusters else ('family recurrence demonstrated; exact ortholog/paralog recurrence not yet demonstrated' if len(family_clusters)>=2 else 'single-cluster evidence only')),
            'claim_boundary':'gene-symbol/family recurrence is an upper bound on exact ortholog reuse; sequence-resolved cross-species mapping is required before node-level macro enrichment'
        })
        score.append({
            'feature':feature,'module':module,
            'family_recurrence_clusters':len(family_clusters),
            'anchored_clusters':len(anchored_clusters),
            'strict_crossspecies_recurrence_clusters':len(exact_clusters),
            'harmonized_rank_class':rank_class(len(family_clusters),len(anchored_clusters),len(exact_clusters)),
            'macro_test_level':macro_level(len(family_clusters),len(exact_clusters)),
            'primary_family_predictor':len(family_clusters),
            'strict_node_predictor':len(exact_clusters),
            'claim_boundary':'use family/module predictor for first held-out macro test; strict-node predictor stays zero/not-ready unless the same sequence-resolved ortholog recurs in >=2 independent micro clusters'
        })

    for path,data in [(a.resolution_output,resolution),(a.score_output,score)]:
        path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('w',newline='',encoding='utf-8') as fh:
            w=csv.DictWriter(fh,fieldnames=list(data[0]));w.writeheader();w.writerows(data)

if __name__=='__main__':main()
