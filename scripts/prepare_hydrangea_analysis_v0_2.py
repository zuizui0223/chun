#!/usr/bin/env python3
"""Rebuild Fig.5 terminal observations and S1/FASTA joins, without OCR.

Accession order is a visual transcription; colours are independently sampled
from the checksum-pinned original figure's terminal circles, not internal pies.
No ancestral state, transition count or preferred rate direction is an input.
"""
from __future__ import annotations
import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import re
import fitz
import numpy as np
from scipy.ndimage import label
from Bio import SeqIO
from ingest_epimedium_source_v0_1 import inspect_xlsx

DOI = '10.3389/fpls.2021.661522'
ORDER = '''415 386 419 426 427 400 302 457 303 385 451 450 392 452 418 433 438 424 399 414 336 335 341 346 296 297 285 284 286 318 305 317 314 290 310 313 334 347 353 391 340 356 338 354 455 351 407 393 428 413 357 416 454 439 434 382 431 425 404 402 389 390 333 350 429 436 435 421 420 423 401 453 396 398 397 387 384 375 378 377 379 376 381 380 374 168 212 408 143 081 075 194 040 440 025 039 098'''.split()
HASHES = {
    'article.pdf': '98f38a6d4514ecf587d9fc561ed0b34847ecb292015c274cb25ed5950525cd1f',
    'files/Data_Sheet_1/Supplementary Material S1.xlsx': '161bcaedf6140130fad3d33535bbac87d3efc61c18977ccc91b0d3793b60f8e5',
    'files/Data_Sheet_1/Supplementary Material S2_original.FASTA': '6de349001df2214a9e37bf2ece72231601ace27b8663d64d7fc06c8032634804',
    'files/Data_Sheet_1/Supplementary Material S2_phylogenetic inference.FASTA': '0f810741a1a2a5706fc083d0e2eeb04903b407e8de2d08285355a5e92fd8c0c0',
}
FIGURE_SHA = 'd27ec6621e55dd432148cb7c7ef13355c096cd487d36ca5c954d983c29e2d357'


def colour(rgb):
    r, g, b = rgb
    if min(rgb) > 220:
        return 'WHITE'
    if r > 170 and g < 80 and b < 80:
        return 'RED'
    if r > 80 and b > 120 and g < 110:
        return 'PURPLE'
    raise ValueError(f'undecodable terminal colour: {rgb}')


def run(source: Path, out: Path):
    for name, expected in HASHES.items():
        if hashlib.sha256((source / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f'source checksum mismatch: {name}')
    ids = ['HY' + x for x in ORDER]
    if len(ids) != 97 or len(set(ids)) != 97:
        raise ValueError('invalid visual label transcription')
    doc = fitz.open(source / 'article.pdf')
    images = [doc.extract_image(x[0]) for x in doc[8].get_images()]
    image = next(x for x in images if hashlib.sha256(x['image']).hexdigest() == FIGURE_SHA)
    pix = fitz.Pixmap(image['image'])
    if pix.n != 3 or (pix.width, pix.height) != (1772, 2397):
        raise ValueError('unexpected original figure geometry')
    rgb = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
    labels, n = label((rgb[:, 1322:1349].min(axis=2) < 150).any(axis=1))
    if n != len(ids):
        raise ValueError(f'expected 97 terminal-circle bands, got {n}')
    centers = [float(np.flatnonzero(labels == i).mean()) for i in range(1, n + 1)]
    states, medians = [], []
    for y in centers:
        yi = round(y)
        median = np.median(rgb[yi-2:yi+3, 1332:1337], axis=(0, 1))
        state = colour(median)
        # The inference must not depend on one pixel or JPEG edge.
        for dy in (-2, 0, 2):
            for dx in (-2, 0, 2):
                other = np.median(rgb[yi+dy-1:yi+dy+2, 1334+dx-1:1334+dx+2], axis=(0, 1))
                if colour(other) != state:
                    raise ValueError('terminal transect sensitivity failed')
        states.append(state)
        medians.append(median.tolist())
    s1 = inspect_xlsx((source / 'files/Data_Sheet_1/Supplementary Material S1.xlsx').read_bytes())[0]
    samples, section, group = {}, None, None
    for row in s1['records']:
        c = row['cells']
        text, accession = c.get(0, '').strip(), c.get(1, '').strip()
        if text == 'Hydrangea section Cornidia':
            group, section = 'CORNIDIA', text
        elif text == 'Outgroup':
            group, section = 'OUTGROUP', None
        elif text.startswith('Hydrangea section ') or text == 'Unclassified':
            section = text
        if re.fullmatch(r'HY\d{3}', accession):
            if accession in samples or group is None or section is None:
                raise ValueError('ambiguous specimen table join')
            samples[accession] = dict(source_s1_row=row['source_row'], source_taxon=text,
                                     sampled_clade=group, source_section=section,
                                     voucher=c.get(2, '').strip(), field_origin=c.get(4, '').strip())
    maps = {}
    for tag, filename in [('short_3161', 'Supplementary Material S2_original.FASTA'),
                          ('long_3167', 'Supplementary Material S2_phylogenetic inference.FASTA')]:
        seqs = list(SeqIO.parse(source / 'files/Data_Sheet_1' / filename, 'fasta'))
        table = {x.id.split('_')[0]: x for x in seqs}
        if len(table) != len(seqs) or set(table) != set(ids) or set(samples) != set(ids):
            raise ValueError('figure/S1/alignment accession mismatch')
        maps[tag] = table
    short, long = maps['short_3161'], maps['long_3167']
    if any(len(short[x]) != 3161 or len(long[x]) != 3167 for x in ids):
        raise ValueError('alignment length drift')
    if any(str(short[x].seq) != str(long[x].seq[:2923] + long[x].seq[2929:]) for x in ids):
        raise ValueError('six-column alignment reconciliation failed')
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for i, (accession, state, y, median) in enumerate(zip(ids, states, centers, medians), 1):
        rows.append(dict(figure_row=i, accession=accession, **samples[accession], visible_state=state,
                         figure_center_x=1334, figure_center_y=y, median_r=median[0],
                         median_g=median[1], median_b=median[2], alignment_tip=long[accession].id,
                         display_organ='SOURCE_TYPED_DISPLAY_PERIANTH', source_doi=DOI))
    with (out / 'terminal_states.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (out / 'figure5_tip_order.txt').write_text('\n'.join(ids) + '\n')
    for tag, table in maps.items():
        with (out / (tag + '.fasta')).open('w') as f:
            for accession in sorted(table):
                f.write('>' + accession + '\n' + str(table[accession].seq) + '\n')
    taxa = {}
    for row in rows:
        if row['sampled_clade'] == 'CORNIDIA':
            taxa.setdefault(row['source_taxon'], set()).add(row['visible_state'])
    summary = dict(source_doi=DOI, hashes=HASHES, figure_embedded_jpeg_sha256=FIGURE_SHA,
                   recovered_accessions=len(rows), colour_observation='PUBLISHED_TERMINAL_DOT_NOT_INTERNAL_PIE',
                   accession_transcription='VISUALLY_REVIEWED_NO_OCR',
                   state_counts={g: dict(Counter(r['visible_state'] for r in rows if r['sampled_clade'] == g))
                                 for g in ('CORNIDIA', 'OUTGROUP')},
                   cornidia_source_taxon_units=len(taxa),
                   mixed_source_taxa={t: sorted(s) for t, s in taxa.items() if len(s) > 1},
                   methods_count_discrepancy='Methods 89+8; archived S1/alignment/figure resolve to 88+9',
                   alignment_discrepancy='File labelled original is shorter; removing columns 2924-2929 from inference-labelled file yields it exactly',
                   accepted_taxonomy_reconciliation='NOT_COMPLETED',
                   independent_historical_event_counts='NOT_INFERRED_AT_PREPARATION',
                   paper1_science_changed=False)
    (out / 'preparation_summary.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return summary


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    run(a.source, a.out)
