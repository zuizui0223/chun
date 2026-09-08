from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parents[1]
ledger = ROOT / 'analysis' / 'falsification_candidates_v1.tsv'
rule = ROOT / 'analysis' / 'falsification_decision_rule_v1.md'

assert ledger.exists(), ledger
assert rule.exists(), rule

rows = list(csv.DictReader(ledger.open(encoding='utf-8'), delimiter='\t'))
assert rows, 'candidate ledger is empty'
valid_status = {'HOLD', 'aligned', 'complementary', 'REFUTATION', 'ADVERSE_BUT_NOT_REFUTATION', 'SUPPORTIVE_ALIGNMENT'}
for r in rows:
    assert r['radiation'].strip()
    assert r['phenotype_axis'].strip()
    assert r['current_status'].strip() in valid_status, r
    assert r['candidate_counterexample'] in {'yes', 'no'}, r

# A HOLD cannot be silently counted as a counterexample.
for r in rows:
    if r['current_status'] == 'HOLD':
        assert r['candidate_counterexample'] == 'no', r

text = rule.read_text(encoding='utf-8')
for key in ['Matched phenotype level', 'Matched observation regime', 'Directional incompatibility', 'Mechanistic non-replication']:
    assert key in text, key

print(f'validated {len(rows)} falsification-audit candidate rows')
