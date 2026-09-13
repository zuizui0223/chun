#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--prereg', type=Path, default=Path('data/intermediate_resolution_rule_prereg_v0_1.json'))
    ap.add_argument('--erratum', type=Path, default=Path('data/iris_source_schema_erratum_v0_1.json'))
    ap.add_argument('--ingest-receipt', type=Path, required=True)
    args = ap.parse_args()

    prereg = json.loads(args.prereg.read_text(encoding='utf-8'))
    err = json.loads(args.erratum.read_text(encoding='utf-8'))
    ing = json.loads(args.ingest_receipt.read_text(encoding='utf-8'))

    assert prereg['status'] == 'FROZEN_BEFORE_CHUN_IRIS_ROW_LEVEL_OUTCOME_INGESTION'
    assert prereg['fourth_radiation']['id'] == 'IRIS'
    assert prereg['phylogeny_reconstruction']['loci'] == ['matK','trnL','trnK','NADPH','rbcL','ITS']

    assert ing['status'] == 'POST_FREEZE_ROW_LEVEL_INGESTION_DIAGNOSTIC'
    assert ing['auc_computed'] is False
    assert ing['decision_computed'] is False
    header = ing['accessions']['semicolon_first_12_rows'][1]
    assert header == ['organism','matK','trnL','ndhF','trnK','rbcL','ITS'], header

    assert err['status'] == 'FROZEN_POST_ROW_INGEST_PRE_AUC_SOURCE_SCHEMA_ERRATUM'
    assert err['preregistered_locus_token'] == 'NADPH'
    assert err['corrected_source_locus_token'] == 'ndhF'
    assert err['source_accession_header'] == header
    assert err['effective_phylogeny_loci_after_erratum'] == ['matK','trnL','ndhF','trnK','rbcL','ITS']
    assert err['correction_type'] == 'SOURCE_SCHEMA_NAME_CORRECTION_ONLY'
    assert all(err['unchanged_contract'].values())
    exposure = err['outcome_exposure_at_erratum']
    assert exposure == {
        'row_level_traits_ingested': True,
        'auc_computed': False,
        'resolution_delta_computed': False,
        'pass_mixed_fail_decision_computed': False,
    }
    assert err['paper1_science_changed'] is False

    out = {
        'status': 'IRIS_SOURCE_SCHEMA_ERRATUM_VALID',
        'original_token': 'NADPH',
        'source_token': 'ndhF',
        'effective_loci': err['effective_phylogeny_loci_after_erratum'],
        'auc_exposed_before_erratum': False,
        'decision_exposed_before_erratum': False,
        'paper1_science_changed': False,
    }
    print(json.dumps(out, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
