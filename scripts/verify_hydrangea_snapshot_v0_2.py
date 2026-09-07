#!/usr/bin/env python3
"""Offline scientific replay with explicit high-rate-plateau diagnosis.

The fixed checksum protects input identity, not a preferred biological result.
New source observations require a new analysis and a new versioned snapshot.
"""
from __future__ import annotations
import argparse,csv,hashlib,json
from pathlib import Path
import numpy as np
from Bio import Phylo
from analyze_hydrangea_mk_v0_2 import run,ingroup_tree
from audit_hydrangea_inference_v0_2 import run as audit
from diagnose_hydrangea_rate_scale_v0_2 import diagnose

CANONICAL_SHA='8e92550a46b1a7bb18f2aa77d2d33b73ddb5544b441d3aaab0ef62916ddc8c49'


def replay(inputs: Path,expected: Path,out: Path):
    x=json.loads(inputs.read_text());saved=json.loads(expected.read_text())
    actual=hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
    if actual!=CANONICAL_SHA:raise ValueError('frozen source snapshot differs from executed input')
    rows=[dict(accession=a,source_taxon=x['taxa'][i],sampled_clade=c,visible_state=s) for a,i,c,s in x['rows']]
    if len(rows)!=len({r['accession'] for r in rows}):raise ValueError('duplicate accession')
    for path in ('prepared','trees','analysis','robustness'):(out/path).mkdir(parents=True,exist_ok=True)
    trait=out/'prepared/terminal_states.csv'
    with trait.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    for tag,tree in x['trees'].items():(out/'trees'/f'{tag}.treefile').write_text(tree+'\n')
    generated=run(out/'trees',trait,out/'analysis',balanced=20)
    ingroup={r['accession'] for r in rows if r['sampled_clade']=='CORNIDIA'}
    for tag in x['trees']:
        tree,mono=ingroup_tree(Phylo.read(out/'trees'/f'{tag}.treefile','newick'),ingroup)
        if not mono:raise ValueError('ingroup lost monophyly')
        Phylo.write(tree,out/'analysis'/f'{tag}_cornidia.nwk','newick',format_branch_length='%1.12f')
    profiles=audit(out,out/'robustness',profiles_only=True)['profiles']
    for old in saved['primary_fits']:
        key=(old['alignment'],old['model'],old['root_prior'])
        new=next(r for r in generated['primary_fits'] if (r['alignment'],r['model'],r['root_prior'])==key)
        for field in ('log_likelihood','AIC','rate_ratio_return_to_gain','root_probability_white','expected_white_to_red','expected_red_to_white'):
            if not np.isclose(new[field],old[field],rtol=2e-4,atol=2e-4):raise ValueError(f'numerical replay mismatch {key} {field}')
        if old['model']=='ARD':
            pr=next(r for r in profiles if (r['alignment'],r['root_prior'])==(old['alignment'],old['root_prior']))
            for field in ('profile95_lower','profile95_upper','LR_against_equal_rates'):
                if not np.isclose(pr[field],old[field],rtol=2e-4,atol=2e-4):raise ValueError(f'profile replay mismatch {key} {field}')
    fits=list(csv.DictReader((out/'analysis/model_fits.csv').open()))
    scale=diagnose(out,out/'scale_diagnostic')
    expected_scale=json.loads((expected.parent/'rate_scale_diagnostic.json').read_text())
    for tag in ('short_3161','long_3167'):
        new,old=scale[tag],expected_scale[tag]
        for field in ('draws','usable_ARD_draws','scale_unidentified_draws'):
            if new[field]!=old[field]:raise ValueError(f'rate-scale diagnostic mismatch {tag} {field}')
        if not np.allclose(new['usable_ratio_min_median_max'],old['usable_ratio_min_median_max'],rtol=2e-4,atol=2e-4):
            raise ValueError('identified balanced ratio replay mismatch')
    if not scale['all_primary_scale_identified']:raise ValueError('primary rates became scale-unidentified')
    report=dict(status='PASS_OFFLINE_NUMERICAL_REPLAY',canonical_input_sha256=actual,
        actual_model_fits=len(fits),profiles_recomputed=len(profiles),
        rate_scale_unidentified_draws={tag:scale[tag]['scale_unidentified_draws'] for tag in ('short_3161','long_3167')},
        source_reacquisition='NOT_REQUESTED_OFFLINE_REPLAY',
        sequence_bootstrap_replay='SEPARATE_AUDIT_REQUIRES_ORIGINAL_UFBOOT_ARTIFACT',paper1_science_changed=False)
    (out/'replay_audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--inputs',type=Path,required=True);p.add_argument('--expected',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();replay(a.inputs,a.expected,a.out)
