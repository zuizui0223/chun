#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from pathlib import Path
rows=list(csv.DictReader(Path('data/aquilegia_cross_level_admission_v0_1.csv').open()))
by={r['axis']:r for r in rows}
assert set(by)=={'PIGMENT_DEPLETION_A_MINUS','HUE_BRANCH_BLUE_RED'}
assert by['PIGMENT_DEPLETION_A_MINUS']['evidence_status']=='DIRECT_CROSS_SPECIES_EXPRESSION'
assert by['PIGMENT_DEPLETION_A_MINUS']['admission_role']=='PASS_AXIS'
assert by['HUE_BRANCH_BLUE_RED']['evidence_status']=='LIMITED_PAIRWISE_AND_PATHWAY_PREDICTION'
assert by['HUE_BRANCH_BLUE_RED']['admission_role']=='HOLD_AXIS'
result={
 'version':'v0.1','same_radiation':'NORTH_AMERICAN_AQUILEGIA','required_axes':2,
 'direct_cross_species_axes':1,
 'pigment_depletion_axis':'PASS_DIRECT_CROSS_SPECIES_EXPRESSION_LATE_PATHWAY',
 'hue_branch_axis':'HOLD_LIMITED_PAIRWISE_AND_PATHWAY_PREDICTION',
 'admission_result':'FAIL_HOLD_NOT_MATCHED_RADIATION_WIDE_DIRECT_TWO_AXIS_BRIDGE',
 'prospective_replication_admitted':False,
 'claim_boundary':'Aquilegia strongly supports late-pathway convergence for anthocyanin loss, but the blue-red hue axis is not measured under a matched radiation-wide cross-species molecular observation regime. Do not count this as a third phenotype-axis-to-molecular-subspace bridge.',
 'paper1_science_changed':False}
assert result==json.loads(Path('data/aquilegia_cross_level_admission_summary_v0_1.json').read_text())
print(json.dumps(result,indent=2))
