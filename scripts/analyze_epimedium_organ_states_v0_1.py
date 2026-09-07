#!/usr/bin/env python3
"""Actual source-table audit, not a reconstruction of evolutionary events.

Zhang et al. (2023), DOI 10.3389/fpls.2023.1234148, CC BY.
Only genus expansion/whitespace normalization is applied to source taxon names.
Colour codes are analysed as nominal categories within each source variable;
no code-to-hue equivalence or anthocyanin state is imputed.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import re
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

DOI = '10.3389/fpls.2023.1234148'
PIN = '057a0aaa603cfa4d9683a2eac75e747cb14bd1294e541feb82483fe6bc160e45'
PANEL = ('acuminatum', 'leptorrhizum', 'epsteinii', 'zhushanense',
         'franchetii', 'sagittatum', 'lishihchenii', 'wushanense')
POLYMORPHISM_SOURCE = '10.3897/phytokeys.118.30268'


def taxon_name(text: str) -> str:
    text = re.sub(r'\s+', ' ', text.strip())
    match = re.match(r'^(?:E\.|Epimedium)\s+([A-Za-z][A-Za-z0-9-]*)', text)
    if not match:
        raise ValueError(f'unrecognized source taxon: {text!r}')
    return 'Epimedium ' + match[1]


def read_table(path: Path) -> list[dict]:
    with path.open(newline='', encoding='utf-8') as fh:
        rows = list(csv.reader(fh))
    if len(rows) < 4 or rows[2][0] != '2':
        raise ValueError(f'unexpected positional export layout: {path}')
    header = [v.strip() for v in rows[2][1:]]
    used = [x for x in header if x]
    if len(used) != len(set(used)):
        raise ValueError('duplicate nonempty source header')
    return [{'source_row': int(row[0]), **{k: v for k, v in zip(header, row[1:]) if k}}
            for row in rows[3:]]


def verify_positional_export(source: Path, sheet_number: int) -> None:
    """Independently reconcile every exported cell against the pinned XLSX XML."""
    ns = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    with zipfile.ZipFile(source/'Table_1.xlsx') as z:
        root = ET.fromstring(z.read('xl/sharedStrings.xml'))
        strings = [''.join(t.text or '' for t in x.findall('.//s:t',ns)) for x in root.findall('s:si',ns)]
        xml = ET.fromstring(z.read(f'xl/worksheets/sheet{sheet_number}.xml'))
    observed = {}
    for row in xml.findall('s:sheetData/s:row',ns):
        cells = {}
        for c in row.findall('s:c',ns):
            value = c.find('s:v',ns)
            val = '' if value is None else (value.text or '')
            kind = c.attrib.get('t','n')
            if kind == 's':
                val = strings[int(val)] if val else ''
            elif kind == 'inlineStr':
                val = ''.join(t.text or '' for t in c.findall('.//s:t',ns))
            column = re.match(r'[A-Z]+',c.attrib['r'])[0]
            idx = 0
            for letter in column:
                idx = 26*idx+ord(letter)-64
            cells[idx] = val
        if any(cells.values()):
            observed[int(row.attrib['r'])] = cells
    with (source/f'Table_1_sheet{sheet_number}.csv').open(newline='',encoding='utf-8') as fh:
        rows = list(csv.reader(fh))[1:]
    if {int(r[0]) for r in rows} != set(observed):
        raise ValueError('CSV/XML source row mismatch')
    for r in rows:
        cells = observed[int(r[0])]
        if any(v != cells.get(i,'') for i,v in enumerate(r[1:],1)):
            raise ValueError(f'CSV/XML cell mismatch at sheet {sheet_number}, row {r[0]}')


def entropy(counts: Counter) -> float:
    total = sum(counts.values())
    if total <= 0:
        raise ValueError('empty entropy input')
    return -sum(v / total * math.log2(v / total) for v in counts.values() if v)


def nominal_summary(pairs: list[tuple[str, str]]) -> dict:
    a, b, ab = Counter(x for x, _ in pairs), Counter(y for _, y in pairs), Counter(pairs)
    ha, hb, hab = entropy(a), entropy(b), entropy(ab)
    return {'n_source_taxa': len(pairs), 'sepal_categories': len(a), 'spur_categories': len(b),
            'joint_categories': len(ab), 'entropy_sepal_bits': ha, 'entropy_spur_bits': hb,
            'entropy_joint_bits': hab, 'mutual_information_bits': ha + hb - hab,
            'spur_given_sepal_bits': hab - ha, 'sepal_given_spur_bits': hab - hb,
            'spur_states_per_sepal_state': {x: len({y for xx, y in pairs if x == xx}) for x in sorted(a)},
            'sepal_states_per_spur_state': {y: len({x for x, yy in pairs if y == yy}) for y in sorted(b)},
            'sepal_sufficient_for_spur': all(len({y for xx, y in pairs if x == xx}) == 1 for x in a),
            'spur_sufficient_for_sepal': all(len({x for x, yy in pairs if y == yy}) == 1 for y in b)}


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f'cannot silently emit empty table {path}')
    with path.open('w', newline='', encoding='utf-8') as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def run(source: Path, out: Path) -> dict:
    digest = hashlib.sha256((source / 'Table_1.xlsx').read_bytes()).hexdigest()
    if digest != PIN:
        raise ValueError('source workbook SHA256 changed; review before admission')
    manifest = json.loads((source / 'source_manifest.json').read_text(encoding='utf-8'))
    if manifest['source_doi'] != DOI or manifest['workbooks'][0]['sha256'] != PIN:
        raise ValueError('source identity manifest mismatch')
    for sheet in manifest['workbooks'][0]['sheets']:
        if sheet['name'].strip() in {'Table S1', 'Table S2', 'Table S4', 'Table S9'} and sheet['formula_cells']:
            raise ValueError('formula cache cannot be accepted as a new trait observation')
    for sheet_no in (1, 2, 4, 9):
        verify_positional_export(source, sheet_no)
    s1, s4, s9 = [read_table(source / f'Table_1_sheet{i}.csv') for i in (1, 4, 9)]
    if len(s4) != 699 or len(s1) != 57:
        raise ValueError('source row-count drift')
    with (source / 'Table_1_sheet2.csv').open(newline='', encoding='utf-8') as fh:
        s2 = list(csv.reader(fh))
    if not any('Color Sepal' in r and 'SepalC' in r for r in s2):
        raise ValueError('missing sepal variable definition')
    if not any('Color Spur' in r and 'SpurC' in r for r in s2):
        raise ValueError('missing spur variable definition')
    by_taxon, by_stratum = defaultdict(list), defaultdict(list)
    long_rows = []
    for r in s4:
        name = taxon_name(r['Species'])
        if not all(r[k].strip() for k in ('Species', 'Locality', 'Voucher', 'Herbarium', 'SepalC', 'SpurC')):
            raise ValueError(f'missing source field at row {r["source_row"]}')
        if r['SepalC'] not in {'0', '1', '2', '3'} or r['SpurC'] not in {'0', '1', '2', '3', '4'}:
            raise ValueError('unexpected nominal colour code')
        by_taxon[name].append(r)
        by_stratum[(name, r['Locality'], r['Voucher'])].append(r)
        for variable, organ, column in [('SepalC', 'INNER_SEPAL', 'G'), ('SpurC', 'PETAL_SPUR', 'H')]:
            long_rows.append({'measurement_id': f'Z2023_S4_R{r["source_row"]}',
                'taxon_source': r['Species'], 'taxon_normalized': name,
                'taxonomic_status': 'SOURCE_NAME_NOT_ACCEPTED_TAXON_AUDIT',
                'locality_source': r['Locality'], 'voucher_source': r['Voucher'],
                'herbarium_source': r['Herbarium'], 'display_organ': organ,
                'source_variable': variable, 'source_state_code': r[variable],
                'visible_hue': 'UNRESOLVED_CODEBOOK', 'source_doi': DOI,
                'source_sheet': 'Table S4', 'source_cell': f'{column}{r["source_row"]}',
                'source_xlsx_sha256': PIN})
    species = []
    for name, rows in sorted(by_taxon.items()):
        ac, bc = sorted({r['SepalC'] for r in rows}), sorted({r['SpurC'] for r in rows})
        pc = sorted({(r['SepalC'], r['SpurC']) for r in rows})
        species.append({'taxon_normalized': name, 'source_rows': len(rows),
            'source_strata': len({(r['Locality'], r['Voucher']) for r in rows}),
            'sepal_codes': ';'.join(ac), 'spur_codes': ';'.join(bc),
            'joint_codes': ';'.join(f'{x}:{y}' for x, y in pc),
            'within_source_taxon_code_variation': len(pc) > 1,
            'population_monomorphism': 'NOT_IDENTIFIABLE_FROM_THIS_TABLE',
            'source_row_start': min(r['source_row'] for r in rows),
            'source_row_end': max(r['source_row'] for r in rows)})
    if len(species) != 42:
        raise ValueError('unexpected taxon group count')
    # A taxon with multiple recorded combinations is not majority-collapsed.
    if any(r['within_source_taxon_code_variation'] for r in species):
        raise ValueError('multistate taxa require an explicit weighted-state analysis')
    named = [r for r in species if r['taxon_normalized'] != 'Epimedium sp1']
    named_pairs = [(r['sepal_codes'], r['spur_codes']) for r in named]
    all_pairs = [(r['sepal_codes'], r['spur_codes']) for r in species]
    contingency = [{'sepal_source_code': x, 'spur_source_code': y,
                    'named_taxa': Counter(named_pairs)[(x,y)], 'all_source_taxa': Counter(all_pairs)[(x,y)],
                    'measurement_rows': sum(r['SepalC'] == x and r['SpurC'] == y for r in s4)}
                   for x, y in sorted(set(all_pairs))]
    id_lookup = {r['ID']: r for r in s1}
    if len(id_lookup) != len(s1):
        raise ValueError('duplicate GBS identifier')
    crosswalk = []
    for r in s9:
        raw_label = r['Species']
        name = taxon_name(raw_label)
        is_out = '(outgroup)' in raw_label
        raw_id = '' if is_out else raw_label.split()[-1]
        # One explicit source-supported transcription reconciliation, not fuzzy matching.
        rid = 'JS26' if (name, raw_id) == ('Epimedium shennongjiaense', 'S26') else raw_id
        if is_out:
            status, agree, s1row = 'AUTHOR_SUBSTITUTED_OUTGROUP_NOT_SAME_GENOMIC_TIP', 'NOT_APPLICABLE', ''
        elif rid in id_lookup and taxon_name(id_lookup[rid]['Species']) == name:
            status = 'EXACT_ID_AND_TAXON' if rid == raw_id else 'EXPLICIT_S26_TO_JS26_WITH_MATCHED_TAXON'
            s1row = id_lookup[rid]['source_row']
            agree = bool(name in by_taxon and {(x['SepalC'], x['SpurC']) for x in by_taxon[name]} == {(r['SepalC'], r['SpurC'])})
        else:
            status, agree, s1row = 'UNRESOLVED', False, ''
        crosswalk.append({'s9_source_row': r['source_row'], 's9_label': raw_label,
            'taxon_normalized': name, 'reported_id': raw_id, 'reconciled_id': rid,
            's1_source_row': s1row, 'join_status': status,
            'sepal_code': r['SepalC'], 'spur_code': r['SpurC'], 's4_code_agreement': agree})
    molecular = []
    s1taxa = {taxon_name(r['Species']) for r in s1}
    s9taxa = {r['taxon_normalized'] for r in crosswalk if 'OUTGROUP' not in r['join_status']}
    for epithet in PANEL:
        name = 'Epimedium ' + epithet
        molecular.append({'taxon_normalized': name, 'in_gbs_sampling_s1': name in s1taxa,
            'in_reproductive_s4': name in by_taxon, 'in_summary_s9': name in s9taxa,
            'exact_molecular_individual_match': 'NOT_ESTABLISHED',
            'historical_transition_direction': 'NOT_ESTABLISHED',
            'independent_event_count': 'NOT_ESTIMATED',
            'external_colour_variation_warning': name in {'Epimedium acuminatum','Epimedium leptorrhizum'},
            'variation_source_doi': POLYMORPHISM_SOURCE if name in {'Epimedium acuminatum','Epimedium leptorrhizum'} else ''})
    complete = [r for r in crosswalk if 'OUTGROUP' not in r['join_status']]
    summary = {'source_doi': DOI, 'source_workbook_sha256': PIN,
        'actual_ingestion': True, 'independent_xlsx_csv_cell_check': 'PASS_S1_S2_S4_S9',
        'source_measurement_rows': len(s4), 'source_taxon_groups': len(species),
        'named_source_taxa': len(named), 'unidentified_groups': 1, 'source_strata': len(by_stratum),
        'organ_long_rows': len(long_rows),
        'within_taxon_variable_codes': sum(r['within_source_taxon_code_variation'] for r in species),
        'within_stratum_variable_codes': sum(len({(r['SepalC'],r['SpurC']) for r in rr}) > 1 for rr in by_stratum.values()),
        'primary_equal_taxon_weight': nominal_summary(named_pairs),
        'sensitivity_include_unidentified': nominal_summary(all_pairs),
        's9_total_data_rows': len(s9), 's9_ingroup_data_rows': len(complete), 's9_outgroup_rows': len(s9)-len(complete),
        'article_methods_reported_ingroup_plus_outgroup': '35+1',
        's9_observed_ingroup_plus_outgroup': f'{len(complete)}+{len(s9)-len(complete)}',
        'article_vs_s9_count_discrepancy': len(s9) != 36,
        's9_exact_id_matches': sum(r['join_status'] == 'EXACT_ID_AND_TAXON' for r in crosswalk),
        's9_explicit_id_corrections': sum(r['join_status'].startswith('EXPLICIT') for r in crosswalk),
        's9_unresolved_ingroup_joins': sum(r['join_status'] == 'UNRESOLVED' for r in complete),
        's9_s4_state_agreements': sum(r['s4_code_agreement'] is True for r in complete),
        'molecular_taxa_total': len(molecular),
        'molecular_taxa_in_s1': sum(r['in_gbs_sampling_s1'] for r in molecular),
        'molecular_taxa_in_s4': sum(r['in_reproductive_s4'] for r in molecular),
        'molecular_taxa_in_s9': sum(r['in_summary_s9'] for r in molecular),
        'hue_label_gate': 'UNRESOLVED_CODEBOOK_NO_HUE_IMPUTATION',
        'population_polymorphism_inference': 'NOT_IDENTIFIABLE_FROM_TAXON_CONSTANT_COLOUR_CODES',
        'historical_event_analysis': 'NOT_RUN', 'phylogenetic_correction': 'NOT_RUN',
        'p_values': 'NOT_COMPUTED_NO_INDEPENDENT_EVOLUTIONARY_REPLICATION_ASSUMED',
        'pooled_atlas_model': 'NOT_RUN', 'paper1_science_changed': False}
    out.mkdir(parents=True, exist_ok=True)
    for filename, rows in [('individual_organ_codes.csv',long_rows), ('source_taxon_summary.csv',species),
        ('organ_joint_codes.csv',contingency), ('s9_s1_s4_crosswalk.csv',crosswalk), ('molecular_panel_overlap.csv',molecular)]:
        write_csv(out/filename, rows)
    (out/'summary.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    return summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--source-dir', type=Path, required=True)
    ap.add_argument('--out-dir', type=Path, required=True)
    a=ap.parse_args()
    print(json.dumps(run(a.source_dir,a.out_dir),indent=2,ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
