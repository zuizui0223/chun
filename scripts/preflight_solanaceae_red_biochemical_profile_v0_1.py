#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import unicodedata
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

PMC_ID = 'PMC4804202'
PMC_NUMERIC = '4804202'
PMC_BUCKET = 'pmc-oa-opendata'
PMC_HTTPS = f'https://{PMC_BUCKET}.s3.amazonaws.com'
SUPPLEMENT_BASENAME = 'supp_plw013_plw013supp_table1.docx'
TREEBASE_STUDY = 'S16617'
USER_AGENT = 'chun-solanaceae-red-biochemical-preflight/0.1'
W_NS = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def fetch(url: str, timeout: int = 120) -> tuple[str, str, bytes]:
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT, 'Accept': '*/*'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.geturl(), (r.headers.get('Content-Type') or '').split(';', 1)[0].strip().lower(), r.read()


def local(tag: str) -> str:
    return tag.rsplit('}', 1)[-1]


def cloud_versions() -> tuple[list[str], dict[str, object]]:
    q = urllib.parse.urlencode({'list-type': '2', 'prefix': f'{PMC_ID}.', 'delimiter': '/'})
    url = f'{PMC_HTTPS}/?{q}'
    final, ct, b = fetch(url)
    root = ET.fromstring(b)
    prefixes = []
    for el in root.iter():
        if local(el.tag) == 'Prefix' and el.text and re.fullmatch(rf'{re.escape(PMC_ID)}\.\d+/', el.text.strip()):
            prefixes.append(el.text.strip())
    prefixes = sorted(set(prefixes), key=lambda x: int(x.split('.')[1].rstrip('/')))
    if not prefixes:
        raise RuntimeError(f'no PMC cloud article version for {PMC_ID}')
    return prefixes, {
        'cloud_list_url': final,
        'cloud_list_content_type': ct,
        'cloud_list_sha256': sha256_bytes(b),
        'cloud_versions': prefixes,
        'selected_version': prefixes[-1],
    }


def s3_to_https(s3_url: str) -> str:
    u = urllib.parse.urlsplit(s3_url)
    if u.scheme != 's3' or u.netloc != PMC_BUCKET:
        raise RuntimeError(f'unexpected PMC S3 URL: {s3_url}')
    key = u.path.lstrip('/')
    return f'{PMC_HTTPS}/{urllib.parse.quote(key, safe="/._-")}'


def fetch_pmc_supplement() -> tuple[bytes, dict[str, object]]:
    versions, list_meta = cloud_versions()
    selected = versions[-1].rstrip('/')
    candidates = [f'{PMC_HTTPS}/metadata/{selected}.json', f'{PMC_HTTPS}/{selected}/{selected}.json']
    meta = None
    meta_b = b''
    meta_url = ''
    attempts = []
    for url in candidates:
        try:
            final, ct, b = fetch(url)
            attempts.append({'url': final, 'content_type': ct, 'bytes': len(b), 'sha256': sha256_bytes(b)})
            x = json.loads(b.decode('utf-8'))
            if isinstance(x, dict) and x.get('pmcid') == PMC_ID:
                meta, meta_b, meta_url = x, b, final
                break
        except Exception as e:
            attempts.append({'url': url, 'error': repr(e)})
    if meta is None:
        raise RuntimeError(f'PMC metadata unavailable: {attempts}')
    media = [str(x) for x in meta.get('media_urls', [])]
    hits = [u for u in media if Path(urllib.parse.urlsplit(u).path).name == SUPPLEMENT_BASENAME]
    if len(hits) != 1:
        raise RuntimeError(f'exact supplement not unique: hits={hits}; available={[Path(urllib.parse.urlsplit(u).path).name for u in media]}')
    s3_url = hits[0]
    final, ct, payload = fetch(s3_to_https(s3_url))
    if not payload.startswith(b'PK'):
        raise RuntimeError(f'supplement is not OOXML/ZIP: {final} {ct} {len(payload)} bytes')
    md5_expected = urllib.parse.parse_qs(urllib.parse.urlsplit(s3_url).query).get('md5', [None])[0]
    md5_observed = hashlib.md5(payload).hexdigest()  # nosec B303, integrity only
    if md5_expected and md5_expected.lower() != md5_observed.lower():
        raise RuntimeError(f'PMC supplement MD5 mismatch expected={md5_expected} observed={md5_observed}')
    return payload, {
        **list_meta,
        'metadata_url': meta_url,
        'metadata_sha256': sha256_bytes(meta_b),
        'metadata_attempts': attempts,
        'media_count': len(media),
        'source_s3_url': s3_url,
        'resolved_url': final,
        'content_type': ct,
        'bytes': len(payload),
        'sha256': sha256_bytes(payload),
        'md5_expected': md5_expected,
        'md5_observed': md5_observed,
    }


def cell_text(tc: ET.Element) -> str:
    return ' '.join(''.join(t.text or '' for t in tc.iter() if local(t.tag) == 't').split())


def parse_docx_schema_and_species(payload: bytes) -> dict[str, object]:
    with zipfile.ZipFile(io.BytesIO(payload)) as z:
        names = set(z.namelist())
        if 'word/document.xml' not in names:
            raise RuntimeError('DOCX lacks word/document.xml')
        root = ET.fromstring(z.read('word/document.xml'))
    tables = [x for x in root.iter() if local(x.tag) == 'tbl']
    inventory = []
    selected = None
    for ti, tbl in enumerate(tables):
        rows = [x for x in tbl if local(x.tag) == 'tr']
        row_widths = []
        header_preview = []
        header_match = None
        for ri, row in enumerate(rows):
            cells = [x for x in row if local(x.tag) == 'tc']
            row_widths.append(len(cells))
            if ri < 2:
                texts = [cell_text(c) for c in cells]
                header_preview.append(texts)
                for ci, txt in enumerate(texts):
                    low = txt.lower().strip()
                    if low in {'species', 'species name', 'taxon', 'taxon name', 'study species'} or 'species' == low.rstrip(':'):
                        header_match = (ri, ci, texts)
        inventory.append({
            'table_index': ti,
            'row_count': len(rows),
            'max_column_count': max(row_widths, default=0),
            'first_two_rows_only': header_preview,
            'species_header_found_in_first_two_rows': header_match is not None,
        })
        if header_match is not None:
            if selected is not None:
                raise RuntimeError('species header found in multiple DOCX tables; ambiguous source table')
            selected = (ti, rows, header_match)
    if selected is None:
        raise RuntimeError('no exact species/taxon header in first two rows of any DOCX table')
    ti, rows, (header_ri, species_ci, header_cells) = selected
    species = []
    for row in rows[header_ri + 1:]:
        cells = [x for x in row if local(x.tag) == 'tc']
        if species_ci >= len(cells):
            continue
        txt = cell_text(cells[species_ci]).strip()
        if txt:
            species.append(txt)
    return {
        'docx_table_count': len(tables),
        'table_inventory': inventory,
        'selected_table_index': ti,
        'header_row_index_zero_based': header_ri,
        'species_column_index_zero_based': species_ci,
        'header_cells': header_cells,
        'species_row_count': len(species),
        'species_labels': species,
        'non_species_outcome_cells_read_below_header': False,
    }


def norm_binomial(x: str) -> str | None:
    s = unicodedata.normalize('NFKD', x).replace('×', ' ').replace('_', ' ')
    s = re.sub(r'[^A-Za-z\- ]+', ' ', s)
    toks = [t.lower() for t in s.split() if t]
    # Drop leading numeric/sample tokens if any; find first plausible two-token Latin label.
    for i in range(len(toks) - 1):
        if re.fullmatch(r'[a-z][a-z\-]+', toks[i]) and re.fullmatch(r'[a-z][a-z\-]+', toks[i + 1]):
            if toks[i] not in {'cf', 'aff', 'sp', 'spp'} and toks[i + 1] not in {'cf', 'aff', 'sp', 'spp'}:
                return toks[i] + ' ' + toks[i + 1]
    return None


def treebase_fetch() -> tuple[bytes, dict[str, object]]:
    urls = [
        f'https://purl.org/phylo/treebase/phylows/study/TB2:{TREEBASE_STUDY}?format=nexml',
        f'https://treebase.org/treebase-web/phylows/study/TB2:{TREEBASE_STUDY}?format=nexml',
        f'https://www.treebase.org/treebase-web/phylows/study/TB2:{TREEBASE_STUDY}?format=nexml',
    ]
    attempts = []
    for url in urls:
        try:
            final, ct, b = fetch(url)
            attempts.append({'requested_url': url, 'final_url': final, 'content_type': ct, 'bytes': len(b), 'sha256': sha256_bytes(b)})
            prefix = b[:500].lstrip().lower()
            if len(b) > 500 and b'html' not in prefix:
                ET.fromstring(b)
                return b, {'attempts': attempts, 'selected_url': final, 'bytes': len(b), 'sha256': sha256_bytes(b)}
        except Exception as e:
            attempts.append({'requested_url': url, 'error': repr(e)})
    raise RuntimeError(f'TreeBASE NeXML unavailable: {attempts}')


def parse_treebase_nexml(payload: bytes) -> dict[str, object]:
    root = ET.fromstring(payload)
    otu_labels = {}
    for el in root.iter():
        if local(el.tag) == 'otu' and el.attrib.get('id'):
            otu_labels[el.attrib['id']] = el.attrib.get('label', '')
    trees = []
    for tree in (x for x in root.iter() if local(x.tag) == 'tree'):
        tid = tree.attrib.get('id', '')
        label = tree.attrib.get('label', '')
        metas = []
        node_otu = {}
        for el in tree.iter():
            if local(el.tag) == 'meta':
                prop = el.attrib.get('property') or el.attrib.get('rel') or ''
                content = el.attrib.get('content') or el.attrib.get('href') or (el.text or '')
                if prop or content:
                    metas.append({'property': prop, 'content': content})
            elif local(el.tag) == 'node' and el.attrib.get('otu'):
                node_otu[el.attrib.get('id', '')] = el.attrib['otu']
        edges = [x for x in tree.iter() if local(x.tag) == 'edge']
        lengths = [e.attrib.get('length') for e in edges]
        terminal_labels = [otu_labels.get(otu, '') for otu in node_otu.values() if otu_labels.get(otu, '')]
        trees.append({
            'tree_id': tid,
            'label': label,
            'metadata': metas,
            'edge_count': len(edges),
            'edges_with_length': sum(v not in (None, '') for v in lengths),
            'all_edges_have_lengths': bool(edges) and all(v not in (None, '') for v in lengths),
            'otu_label_count': len(terminal_labels),
            'otu_labels': terminal_labels,
        })
    if not trees:
        raise RuntimeError('TreeBASE NeXML contains no tree objects')
    return {'otu_count': len(otu_labels), 'tree_count': len(trees), 'trees': trees}


def select_tree_without_outcomes(inv: dict[str, object]) -> tuple[dict[str, object] | None, str]:
    trees = inv['trees']
    if len(trees) == 1:
        return trees[0], 'UNIQUE_TREE_OBJECT'
    # Metadata-only selection: accept exactly one tree whose label/meta explicitly denotes final/dated/chronogram/ultrametric/MCC.
    rx = re.compile(r'\b(final|dated|chronogram|ultrametric|maximum clade credibility|mcc)\b', re.I)
    tagged = []
    for t in trees:
        text = ' '.join([t.get('label', '')] + [str(m.get('content', '')) for m in t.get('metadata', [])])
        if rx.search(text):
            tagged.append(t)
    if len(tagged) == 1:
        return tagged[0], 'UNIQUE_METADATA_TAGGED_FINAL_DATED_TREE'
    return None, f'AMBIGUOUS_TREE_OBJECTS_total_{len(trees)}_metadata_tagged_{len(tagged)}'


def crosswalk(species: list[str], tree: dict[str, object] | None) -> dict[str, object]:
    trait_norm = [(x, norm_binomial(x)) for x in species]
    malformed_trait = [x for x, n in trait_norm if n is None]
    trait_map = {n: raw for raw, n in trait_norm if n}
    dup_trait = sorted({n for _, n in trait_norm if n and sum(1 for _, m in trait_norm if m == n) > 1})
    if tree is None:
        return {
            'trait_species_count': len(species),
            'trait_normalized_unique': len(trait_map),
            'trait_malformed': malformed_trait,
            'trait_duplicate_normalized': dup_trait,
            'tree_selected': False,
            'exact_normalized_matches': 0,
            'trait_only': sorted(trait_map),
            'tree_only': [],
        }
    labels = list(tree.get('otu_labels', []))
    tree_norm = [(x, norm_binomial(x)) for x in labels]
    tree_map: dict[str, list[str]] = {}
    for raw, n in tree_norm:
        if n:
            tree_map.setdefault(n, []).append(raw)
    exact = sorted(set(trait_map) & set(tree_map))
    return {
        'trait_species_count': len(species),
        'trait_normalized_unique': len(trait_map),
        'trait_malformed': malformed_trait,
        'trait_duplicate_normalized': dup_trait,
        'tree_selected': True,
        'tree_tip_labels': len(labels),
        'tree_normalized_unique': len(tree_map),
        'tree_duplicate_normalized': sorted(k for k, v in tree_map.items() if len(v) > 1),
        'exact_normalized_matches': len(exact),
        'matched_normalized_species': exact,
        'trait_only': sorted(set(trait_map) - set(tree_map)),
        'tree_only_count': len(set(tree_map) - set(trait_map)),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    prereg = json.loads((Path(__file__).resolve().parents[1] / 'data/solanaceae_red_biochemical_resolution_profile_prereg_v0_1.json').read_text())
    if prereg['status'] != 'FROZEN_BEFORE_SOLANACEAE_RED_TABLES1_ROW_LEVEL_OUTCOME_OPENING':
        raise SystemExit('preregistration not frozen')

    receipt: dict[str, object] = {
        'version': 'v0.1',
        'system': 'SOLANACEAE_RED_27',
        'prereg_status': prereg['status'],
        'outcome_firewall': {
            'row_level_pigment_outcomes_read': False,
            'pigment_states_computed': False,
            'state_frequencies_computed': False,
            'patristic_profile_distances_computed': False,
            'profile_auc_computed': False,
            'winner_computed': False,
        },
        'paper1_science_changed': False,
    }
    try:
        supp, smeta = fetch_pmc_supplement()
        schema = parse_docx_schema_and_species(supp)
        receipt['supplement'] = smeta
        receipt['docx_schema'] = schema
    except Exception as e:
        receipt['status'] = 'HOLD_SOURCE_ACCESS_OR_SCHEMA_OUTCOMES_UNOPENED'
        receipt['error'] = repr(e)
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(json.dumps(receipt, indent=2) + '\n')
        print(json.dumps(receipt, indent=2))
        return 0

    try:
        nb, tmeta = treebase_fetch()
        tinv = parse_treebase_nexml(nb)
        selected, selection = select_tree_without_outcomes(tinv)
        receipt['treebase_source'] = tmeta
        receipt['tree_inventory'] = tinv
        receipt['tree_selection_rule_result'] = selection
        receipt['selected_tree_id'] = selected.get('tree_id') if selected else None
        receipt['crosswalk'] = crosswalk(schema['species_labels'], selected)
    except Exception as e:
        receipt['status'] = 'HOLD_TREEBASE_ACCESS_OR_SCHEMA_OUTCOMES_UNOPENED'
        receipt['error'] = repr(e)
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(json.dumps(receipt, indent=2) + '\n')
        print(json.dumps(receipt, indent=2))
        return 0

    cw = receipt['crosswalk']
    if selected is None:
        status = 'HOLD_TREE_OBJECT_AMBIGUOUS_OR_UNAVAILABLE_OUTCOMES_UNOPENED'
    elif not selected.get('all_edges_have_lengths'):
        status = 'HOLD_SELECTED_TREE_MISSING_BRANCH_LENGTHS_OUTCOMES_UNOPENED'
    elif cw['trait_malformed'] or cw['trait_duplicate_normalized'] or cw.get('tree_duplicate_normalized'):
        status = 'HOLD_IDENTIFIER_AMBIGUITY_OUTCOMES_UNOPENED'
    elif cw['exact_normalized_matches'] < 20:
        status = 'HOLD_EXACT_CROSSWALK_LT20_OUTCOMES_UNOPENED'
    else:
        status = 'PASS_SOURCE_SCHEMA_TREE_CROSSWALK_OUTCOMES_UNOPENED'
    receipt['status'] = status
    receipt['outcome_firewall']['row_level_pigment_outcomes_read'] = False
    receipt['next_gate'] = (
        'FREEZE_THIS_PREFLIGHT_RECEIPT_BEFORE_OPENING_PIGMENT_COLUMNS_AND_COMPUTING_PROFILE'
        if status.startswith('PASS_') else
        'RESOLVE_ONLY_THE_RECORDED_SOURCE_TREE_OR_IDENTIFIER_HOLD_WITHOUT_OPENING_PIGMENT_OUTCOMES'
    )
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
