#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--contract', type=Path, default=Path('data/iris_tree_record_semantics_v0_1.json'))
    args = ap.parse_args()
    x=json.loads(args.contract.read_text(encoding='utf-8'))
    assert x['status']=='FROZEN_PRE_TREE_PRE_AUC_RECORD_SEMANTICS'
    assert x['matphylobi_source_commit']=='a54443c475aecc8567d6981346ee53c0a126e0ca'
    m=x['matphylobi_semantics']
    assert m['sequence_assignment']=='record.seq full GenBank record'
    assert m['general_marker_blast_coordinates_used_for_sequence_slicing'] is False
    p=x['iris_primary_tree_contract']
    assert p['effective_loci']==['matK','trnL','ndhF','trnK','rbcL','ITS']
    assert p['sequence_unit']=='FULL_GENBANK_RECORD'
    assert p['cross_locus_duplicate_accessions']=='RETAIN_AS_ASSIGNED_IN_EACH_SOURCE_MARKER_COLUMN'
    assert p['Iris_darwasica']=='EXCLUDE_SOURCE_SPECIFIC_RULE'
    assert p['Iris_cedretii']=='TREE_ONLY_NO_TRAIT_ROW'
    assert p['trait_values_used_for_tree'] is False
    e=x['outcome_exposure_at_freeze']
    assert e['auc_computed'] is False
    assert e['resolution_delta_computed'] is False
    assert e['pass_mixed_fail_decision_computed'] is False
    assert x['paper1_science_changed'] is False
    print(json.dumps({'status':'IRIS_TREE_RECORD_SEMANTICS_VALID','auc_exposed':False,'paper1_science_changed':False},indent=2))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
