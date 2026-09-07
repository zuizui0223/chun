#!/usr/bin/env python3
"""Offline scientific replay; source retrieval is a separate explicit job.

A fixed input checksum protects this replay, not a desired biological outcome.
Changed source data require a new snapshot and a new analysis, not acceptance
because its result happens to agree with this saved result.
"""
from __future__ import annotations
import argparse,csv,hashlib,json
from collections import Counter
from pathlib import Path
import numpy as np
from Bio import Phylo
from analyze_hydrangea_mk_v0_2 import run, ingroup_tree
from audit_hydrangea_inference_v0_2 import run as audit

CANONICAL_SHA='8e92550a46b1a7bb18f2aa77d2d33b73ddb5544b441d3aaab0ef62916ddc8c49'


def replay(inputs: Path, expected: Path, out: Path):
    x=json.loads(inputs.read_text()); saved=json.loads(expected.read_text())
    actual=hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
    if actual!=CANONICAL_SHA:raise ValueError('frozen source snapshot differs from executed input')
    rows=[]
    for accession,idx,clade,state in x['rows']:
        rows.append(dict(accession=accession,source_taxon=x['taxa'][idx],sampled_clade=clade,visible_state=state))
    if len(rows)!=len({r['accession'] for r in rows}):raise ValueError('duplicate accession')
    for path in ('prepared','trees','analysis','robustness'):(out/path).mkdir(parents=True,exist_ok=True)
    trait=out/'prepared/terminal_states.csv'
    with trait.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    for tag,tree in x['trees'].items():(out/'trees'/f'{tag}.treefile').write_text(tree+'\n')
    generated=run(out/'trees',trait,out/'analysis',balanced=20)
    # Convenience pruned trees are written at full precision. Full trees remain
    # unchanged and are the authoritative likelihood inputs.
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
    for tag,reference in saved['taxon_balanced_sensitivity'].items():
        r=[r for r in fits if r['alignment']==tag and r['sampling']=='ONE_ACCESSION_PER_SOURCE_TAXON' and r['model']=='ARD']
        inside=[a for a in r if a['optimization_bound_hit']=='False']
        if len(r)!=reference['draws'] or len(inside)!=reference['interior_ARD_draws']:raise ValueError('balanced sampling replay mismatch')
        q=np.quantile([float(a['rate_ratio_return_to_gain']) for a in inside],[0,.5,1])
        if not np.allclose(q,reference['interior_ratio_min_median_max'],rtol=2e-4,atol=2e-4):raise ValueError('balanced ratio replay mismatch')
    report=dict(status='PASS_OFFLINE_NUMERICAL_REPLAY',canonical_input_sha256=actual,
        actual_model_fits=len(fits),profiles_recomputed=len(profiles),
        source_reacquisition='NOT_REQUESTED_OFFLINE_REPLAY',
        sequence_bootstrap_replay='SEPARATE_AUDIT_REQUIRES_ORIGINAL_UFBOOT_ARTIFACT',
        paper1_science_changed=False)
    (out/'replay_audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--inputs',type=Path,required=True);p.add_argument('--expected',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();replay(a.inputs,a.expected,a.out)
