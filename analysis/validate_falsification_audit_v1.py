from pathlib import Path
import csv
import json

ROOT = Path(__file__).resolve().parents[1]
ledger = ROOT / 'analysis' / 'falsification_candidates_v1.tsv'
rule = ROOT / 'analysis' / 'falsification_decision_rule_v1.md'
audit = ROOT / 'analysis' / 'falsification_audit_v1.md'
iris_result = ROOT / 'analysis' / 'iris_fine_state_falsification_result_v1.json'
nicotiana_result = ROOT / 'analysis' / 'nicotiana_fine_state_falsification_result_v1.json'

for p in (ledger, rule, audit, iris_result, nicotiana_result):
    assert p.exists(), p

rows = list(csv.DictReader(ledger.open(encoding='utf-8'), delimiter='\t'))
assert rows, 'candidate ledger is empty'
required = {'test_unit', 'inference_level', 'claim', 'current_status', 'candidate_counterexample', 'reason'}
assert required.issubset(rows[0]), rows[0].keys()
valid_status = {
    'HOLD', 'REFUTATION', 'ADVERSE_BUT_NOT_REFUTATION',
    'SUPPORTIVE_ALIGNMENT', 'MIXED', 'SUPERSEDED_REFUTED', 'PREFROZEN_TEST'
}
for r in rows:
    assert r['test_unit'].strip()
    assert r['inference_level'].strip()
    assert r['claim'].strip()
    assert r['current_status'].strip() in valid_status, r
    assert r['candidate_counterexample'] in {'yes', 'no', 'pending'}, r
    assert r['reason'].strip()

for r in rows:
    if r['current_status'] == 'HOLD':
        assert r['candidate_counterexample'] == 'no', r
    if r['current_status'] == 'REFUTATION':
        assert r['candidate_counterexample'] == 'yes', r
    if r['current_status'] == 'PREFROZEN_TEST':
        assert r['candidate_counterexample'] == 'pending', r

iris = [r for r in rows if r['test_unit'] == 'Iris']
assert len(iris) == 1, iris
assert iris[0]['current_status'] == 'MIXED', iris[0]
assert iris[0]['candidate_counterexample'] == 'no', iris[0]

nic = [r for r in rows if r['test_unit'] == 'Nicotiana_nonhybrid_diploids']
assert len(nic) == 1, nic
assert nic[0]['current_status'] == 'HOLD', nic[0]
assert nic[0]['candidate_counterexample'] == 'no', nic[0]

iris_json = json.loads(iris_result.read_text(encoding='utf-8'))
assert iris_json['classification'] == 'MIXED'

nic_json = json.loads(nicotiana_result.read_text(encoding='utf-8'))
assert nic_json['classification'] == 'HOLD_OBSERVATION_REGIME'
assert nic_json['endpoint_computed'] is False
assert nic_json['tree_admission']['n_tree_overlap'] == 17
assert nic_json['tree_admission']['frozen_coverage_gate_80pct'] is True
assert nic_json['tree_admission']['frozen_minimum_n_20_gate'] is False

text = rule.read_text(encoding='utf-8')
for key in [
    'Already rejected stronger claim', 'Surviving claim under prospective falsification',
    'Matched phenotype level', 'Matched statistic', 'Failure of the surviving prediction',
    'Mechanistic non-replication'
]:
    assert key in text, key

audit_text = audit.read_text(encoding='utf-8')
for key in [
    'Already falsified / superseded',
    'Surviving positive object before prospective stress tests',
    'Prospective fourth-radiation test: Iris',
    'Prospective fifth-radiation attempt: Nicotiana',
    'Current cross-radiation state',
    'Next falsification target'
]:
    assert key in audit_text, key

print(f'validated {len(rows)} falsification-audit rows: Iris MIXED, Nicotiana HOLD_OBSERVATION_REGIME, matched decision rule')
