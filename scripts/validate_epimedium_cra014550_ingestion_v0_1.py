#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json
from pathlib import Path

EXPECTED_FLOWER = {
    ('Epimedium pseudowushanense','PETAL','MAGENTA'),
    ('Epimedium acuminatum','PETAL','MAGENTA'),
    ('Epimedium jinchengshanense','PETAL','YELLOW'),
    ('Epimedium baojingense','PETAL','GREEN'),
    ('Epimedium hunanense','SEPAL','RED'),
    ('Epimedium baojingense','SEPAL','GREEN'),
    ('Epimedium acuminatum','SEPAL','WHITE'),
}
EXPECTED_LEAF = {
    ('Epimedium pubescens','LEAF','GREEN'),
    ('Epimedium pubescens','LEAF','MAGENTA'),
}
SAMPLE_COLUMNS = [
    'run_accession','sample_accession','library_id','species','organ','visible_state',
    'biological_replicate','individuals_pooled','source_group_id','raw_file_1','raw_file_2',
    'checksum_type','checksum_1','checksum_2','metadata_source','status','notes',
]


def read(path: Path):
    with path.open(newline='', encoding='utf-8') as fh:
        return list(csv.DictReader(fh))


def read_with_header(path: Path):
    with path.open(newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        return reader.fieldnames, list(reader)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--groups', type=Path, required=True)
    ap.add_argument('--sources', type=Path, required=True)
    ap.add_argument('--sample-manifest', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()

    groups = read(a.groups)
    sources = read(a.sources)
    sample_header, sample_rows = read_with_header(a.sample_manifest)
    if not groups or not sources:
        raise SystemExit('empty CRA014550 contract input')
    if sample_header != SAMPLE_COLUMNS:
        raise SystemExit(f'sample-manifest header drift: {sample_header}')
    if sample_rows:
        raise SystemExit('pre-ingestion sample manifest must remain empty until real repository metadata are verified')

    flower = [r for r in groups if r['primary_flower_analysis'].lower() == 'yes']
    leaf = [r for r in groups if r['primary_flower_analysis'].lower() == 'no']
    flower_keys = {(r['species'], r['organ'], r['visible_state']) for r in flower}
    leaf_keys = {(r['species'], r['organ'], r['visible_state']) for r in leaf}
    if flower_keys != EXPECTED_FLOWER:
        raise SystemExit(f'flower group drift: {sorted(flower_keys ^ EXPECTED_FLOWER)}')
    if leaf_keys != EXPECTED_LEAF:
        raise SystemExit(f'leaf context drift: {sorted(leaf_keys ^ EXPECTED_LEAF)}')

    for r in groups:
        if int(r['expected_biological_replicates']) != 3:
            raise SystemExit(f"{r['group_id']}: expected biological replicates must remain 3")
        if int(r['individuals_per_replicate']) != 3:
            raise SystemExit(f"{r['group_id']}: each biological replicate must remain a pool of 3 individuals")
        if not r['voucher'].strip():
            raise SystemExit(f"{r['group_id']}: missing voucher")

    flower_libs = sum(int(r['expected_biological_replicates']) for r in flower)
    leaf_libs = sum(int(r['expected_biological_replicates']) for r in leaf)
    if flower_libs != 21 or leaf_libs != 6:
        raise SystemExit(f'expected library-count contract drift: flower={flower_libs}, leaf={leaf_libs}')

    src = {r['resource_id']: r for r in sources}
    if src.get('CRA014550', {}).get('accession') != 'CRA014550':
        raise SystemExit('CRA014550 accession drift')
    if src.get('CRA014550', {}).get('status') != 'REMOTE_VERIFIED_NOT_INGESTED':
        raise SystemExit('raw accession must remain not ingested until real metadata/binaries are present')
    if src.get('EPUB_GENOME', {}).get('accession') != 'GWHBECS00000000':
        raise SystemExit('E. pubescens reference accession drift')
    if src.get('FLOWER_EXPECTATION', {}).get('status') != 'FROZEN_PRE_INGESTION':
        raise SystemExit('flower expectation must be frozen pre-ingestion')

    summary = {
        'version': 'v0.1',
        'flower_state_groups': len(flower),
        'expected_flower_biological_libraries': flower_libs,
        'secondary_leaf_state_groups': len(leaf),
        'expected_secondary_leaf_libraries': leaf_libs,
        'sample_manifest_rows': len(sample_rows),
        'sample_manifest_status': 'EMPTY_BY_DESIGN_PRE_INGESTION',
        'raw_accession': 'CRA014550',
        'reference_genome': 'GWHBECS00000000',
        'raw_ingestion_status': 'BLOCKED_PENDING_REPOSITORY_METADATA_AND_BINARIES',
        'historical_transition_inference': 'FORBIDDEN_FROM_CROSS_SECTIONAL_GROUPS',
        'paper1_science_changed': False,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
