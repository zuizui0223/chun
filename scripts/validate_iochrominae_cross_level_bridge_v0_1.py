#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from pathlib import Path

P=Path('data/iochrominae_cross_level_bridge_v0_1.csv')
EXPECTED=Path('data/iochrominae_cross_level_bridge_summary_v0_1.json')
rows=list(csv.DictReader(P.open()))
by={r['evidence_id']:r for r in rows}
expected={'INTENSITY_MODULE','HUE_BRANCH','UPSTREAM_CONSERVATION','REGAIN_MODULE'}
assert set(by)==expected
assert all(r['source_doi']=='10.1093/molbev/msy117' for r in rows)
assert by['INTENSITY_MODULE']['molecular_targets']=="F3'5'H|DFR|ANS"
assert by['HUE_BRANCH']['molecular_targets']=="F3'H|F3'5'H"
assert by['UPSTREAM_CONSERVATION']['molecular_targets']=='CHS|CHI|F3H'
assert by['REGAIN_MODULE']['evidence_status']=='SOURCE_SUPPORTED_LIMITED'
summary={
 'version':'v0.1','same_radiation':'IOCHROMINAE','source_species_scope':28,
 'phenotype_to_molecular_mappings':3,
 'intensity_maps_to':'LATE_PATHWAY_COEXPRESSION_MODULE',
 'hue_maps_to':'BRANCHING_ENZYME_SUBSPACE',
 'early_pathway_status':'COMPARATIVELY_CONSERVED_ACROSS_PIGMENT_STATES',
 'regain_status':'ONE_EXTANT_REGAIN_TIP_LIMITED',
 'cross_level_result':'PHENOTYPE_DIMENSIONS_MAP_TO_DIFFERENT_MOLECULAR_SUBSPACES_WITHIN_ONE_RADIATION',
 'does_not_establish':['universal_gene_mapping','single_causal_mutation','same_mapping_across_clades','ecological_causality'],
 'paper1_science_changed':False
}
frozen=json.loads(EXPECTED.read_text())
assert summary==frozen,(summary,frozen)
print(json.dumps(summary,indent=2))
