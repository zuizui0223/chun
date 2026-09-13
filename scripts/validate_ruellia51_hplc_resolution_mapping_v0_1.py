#!/usr/bin/env python3
import csv
from pathlib import Path
p=Path('data/ruellia51_hplc_resolution_mapping_v0_1.csv')
with p.open(newline='') as f:
    rows=list(csv.DictReader(f))
assert [r['level'] for r in rows]==['coarse','intermediate','fine']
assert rows[0]['state_definition']=='ANY_PRESENT vs NONE'
assert rows[1]['state_definition']=='three-bit PEL/CYA/DEL branch-presence pattern'
assert rows[2]['state_definition']=='six-bit compound-presence pattern in listed order'
print('RUELLIA51_HPLC_RESOLUTION_MAPPING_PASS')
