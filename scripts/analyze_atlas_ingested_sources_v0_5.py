#!/usr/bin/env python3
"""Data-level Epimedium audit: organ states, replication units, and voucher joins.

Works on source-row CSVs exported by the read-only OOXML inventory. Colour codes
stay categorical and uninterpreted; ordered numbers are never pigment amounts.
This audit does not reconstruct ancestors, date transitions, infer selection,
or link the separate 2011 molecular accessions to the 2023 morphology samples.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

DOI = '10.3389/fpls.2023.1234148'
SOURCE_SHA256 = '057a0aaa603cfa4d9683a2eac75e747cb14bd1294e541feb82483fe6bc160e45'
FIELDS = ['source_doi', 'source_file_sha256', 'source_sheet', 'source_row',
          'source_taxon', 'display_organ', 'source_colour_code', 'semantic_colour',
          'semantic_mapping_status', 'source_voucher', 'source_locality',
          'gbs_sample_id', 'voucher_join_status']

def ws(value): return ' '.join(value.split())

def read_table(folder, number):
    path = folder / f'Table_1.xlsx__Table_S{number}.csv'
    with path.open(newline='', encoding='utf-8') as f: raw = list(csv.reader(f))
    if len(raw) < 3: raise ValueError('Missing title/header/data: ' + str(path))
    header = ['source_row'] + [x.strip() for x in raw[1][1:]]
    if len(set(header)) != len(header): raise ValueError('Duplicate header')
    rows = []
    for row in raw[2:]:
        if len(row) > len(header) and any(x.strip() for x in row[len(header):]):
            raise ValueError('Unexpected nonempty overflow columns')
        rows.append(dict(zip(header, (row + [''] * len(header))[:len(header)])))
    return rows

def write_csv(path, fields, rows):
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)

def paired_counts(groups):
    counts = Counter()
    for values in groups.values():
        states = {(v['SepalC'], v['SpurC']) for v in values}
        if len(states) == 1: counts[next(iter(states))] += 1
    return [{'sepal_code': a, 'spur_code': b, 'count': n} for (a,b),n in sorted(counts.items())]

def analyze(folder, out):
    workbook = folder / 'Table_1.xlsx'
    if hashlib.sha256(workbook.read_bytes()).hexdigest() != SOURCE_SHA256:
        raise ValueError('Source workbook drift; review new bytes before analysis')
    s1, s4, s9 = [read_table(folder, n) for n in (1, 4, 9)]
    if len(s4) != 699: raise ValueError('Source row-count drift')
    if len({r['source_row'] for r in s4}) != len(s4): raise ValueError('Duplicate source row ID')
    for row in s4:
        for name in ('Species','Locality','Voucher','SepalC','SpurC'):
            if not row.get(name, '').strip(): raise ValueError('Missing ' + name)
        if row['SepalC'] not in {'0','1','2','3'} or row['SpurC'] not in {'0','1','2','3','4'}:
            raise ValueError('Colour code outside source dictionary')
    by_voucher = defaultdict(list)
    for row in s1: by_voucher[ws(row['Voucher'])].append(row)
    taxon_groups, voucher_groups = defaultdict(list), defaultdict(list)
    normalized, unmatched, join_ids = [], {}, {}
    for row in s4:
        taxon_groups[row['Species']].append(row)
        voucher_groups[(row['Species'], row['Locality'], ws(row['Voucher']))].append(row)
        hits = by_voucher[ws(row['Voucher'])]
        status = 'EXACT_WHITESPACE_NORMALIZED' if len(hits) == 1 else ('UNMATCHED' if not hits else 'AMBIGUOUS')
        gbs_id = hits[0]['ID'] if len(hits) == 1 else ''
        if gbs_id:
            # Voucher equality must not override an incompatible source species.
            epithet = re.match(r'E\.\s+(\S+)', hits[0]['Species'])
            if not epithet or ws(row['Species']) != 'E. ' + epithet[1]:
                raise ValueError('Voucher/species disagreement')
            join_ids.setdefault(gbs_id, []).append(row)
        else: unmatched[ws(row['Voucher'])] = row['Species']
        for organ, field in [('INNER_SEPAL','SepalC'), ('PETAL_SPUR','SpurC')]:
            normalized.append(dict(zip(FIELDS, [DOI, SOURCE_SHA256, 'Table S4', row['source_row'],
              row['Species'], organ, row[field], 'UNKNOWN', 'NUMERIC_CODE_ONLY_PENDING_LEGEND',
              row['Voucher'], row['Locality'], gbs_id, status])))
    summaries = []
    for taxon, rows in sorted(taxon_groups.items()):
        a, b = sorted({r['SepalC'] for r in rows}), sorted({r['SpurC'] for r in rows})
        summaries.append({'source_taxon': taxon, 'morphometric_rows': len(rows),
            'voucher_blocks': len({(r['Locality'], ws(r['Voucher'])) for r in rows}),
            'sepal_codes': ';'.join(a), 'spur_codes': ';'.join(b),
            'observed_colour_pairs': ';'.join(a+':'+b for a,b in sorted({(r['SepalC'],r['SpurC']) for r in rows})),
            'within_taxon_code_variation_observed': len(a)>1 or len(b)>1,
            'species_polymorphism_status': 'NOT_ASCERTAINABLE_FROM_CONSTANT_SOURCE_CODING'})
    s9_join = []
    for row in s9:
        m = re.search(r'\bJS\d+\b', row['Species']); identifier = m[0] if m else ''
        observed = {(r['SepalC'], r['SpurC']) for r in join_ids.get(identifier, [])}
        state = (row['SepalC'], row['SpurC'])
        s9_join.append({'source_row': row['source_row'], 'source_tip_label': row['Species'],
            'gbs_sample_id': identifier, 's9_sepal_code': state[0], 's9_spur_code': state[1],
            's4_colour_match': ('MATCH' if state in observed else 'CONFLICT') if observed else 'UNLINKED'})
    out.mkdir(parents=True, exist_ok=True)
    write_csv(out/'epimedium_organ_rows_v0_5.csv',FIELDS,normalized)
    write_csv(out/'epimedium_source_taxon_summary_v0_5.csv',list(summaries[0]),summaries)
    write_csv(out/'epimedium_s9_voucher_crosscheck_v0_5.csv',list(s9_join[0]),s9_join)
    contingency = []
    for unit, groups in [('morphometric_row',{str(i):[r] for i,r in enumerate(s4)}),
                         ('voucher_block',voucher_groups),('source_taxon',taxon_groups)]:
        contingency.extend(dict(unit=unit,**r) for r in paired_counts(groups))
    write_csv(out/'epimedium_organ_code_contingencies_v0_5.csv', ['unit','sepal_code','spur_code','count'], contingency)
    result = {'source_doi': DOI, 'source_sha256': SOURCE_SHA256,
        'morphometric_rows':len(s4), 'source_taxa':len(taxon_groups),
        'named_source_taxa':len([t for t in taxon_groups if not re.match(r'E\.\s+sp\d', t)]),
        'source_unknown_taxa':len([t for t in taxon_groups if re.match(r'E\.\s+sp\d', t)]),
        'voucher_blocks':len(voucher_groups), 'organ_rows':len(normalized),
        'discordant_organ_morphometric_rows':sum(r['SepalC']!=r['SpurC'] for r in s4),
        'discordant_organ_voucher_blocks':sum(any(r['SepalC']!=r['SpurC'] for r in g) for g in voucher_groups.values()),
        'discordant_organ_source_taxa':sum(any(r['SepalC']!=r['SpurC'] for r in g) for g in taxon_groups.values()),
        'within_taxon_code_variable_groups':sum(len({(r['SepalC'],r['SpurC']) for r in g})>1 for g in taxon_groups.values()),
        'within_voucher_code_variable_groups':sum(len({(r['SepalC'],r['SpurC']) for r in g})>1 for g in voucher_groups.values()),
        's1_gbs_accessions':len(s1), 'matched_voucher_blocks':len(join_ids),
        'matched_morphometric_rows':sum(len(v) for v in join_ids.values()),
        'unmatched_vouchers':unmatched, 's9_rows':len(s9),
        's9_exact_linked_colour_agreements':sum(r['s4_colour_match']=='MATCH' for r in s9_join),
        's9_linked_colour_conflicts':sum(r['s4_colour_match']=='CONFLICT' for r in s9_join),
        's9_unlinked_labels':[r['source_tip_label'] for r in s9_join if r['s4_colour_match']=='UNLINKED'],
        'source_taxon_pair_counts':paired_counts(taxon_groups),
        'within_population_polymorphism_inferred':False,
        'molecular_2011_accession_crosswalk_established':False,
        'historical_event_analysis':'NOT_RUN', 'paper1_science_changed':False}
    (out/'epimedium_empirical_audit_v0_5.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return result

def fetch_figure(folder):
    from ingest_atlas_public_sources_v0_5 import get, record_bytes
    from resolve_atlas_source_payloads_v0_5 import https_s3
    metadata = json.loads((folder/'pmc_article_metadata.json').read_text())
    files=[]
    for value in metadata['media_urls']:
        if not value.split('?')[0].endswith('-g004.jpg'): continue
        url, expected = https_s3(value); data, resolved = get(url)
        if not expected or hashlib.md5(data).hexdigest()!=expected: raise ValueError('Figure checksum failure')
        files.append(record_bytes(data,resolved,'source_figure4.jpg',folder))
    (folder/'figure_provenance.json').write_text(json.dumps(files,indent=2)+'\n')

def main():
    p=argparse.ArgumentParser();p.add_argument('--source-dir',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--fetch-source-figure',action='store_true');a=p.parse_args()
    if a.fetch_source_figure: fetch_figure(a.source_dir)
    result=analyze(a.source_dir,a.out)
    print('EMPIRICAL_RESULT',json.dumps(result,ensure_ascii=False),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
