#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import urllib.request
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from Bio import Phylo
from scipy.stats import rankdata

TRAIT_URL = "https://pmc-oa-opendata.s3.amazonaws.com/PMC7588356.1/Table_1.xlsx"
TRAIT_SHA256 = "183ef5231c48e782b0ea69a7aa5605d40c892dd91d9d9b2d259ed7b65d230072"
SEED = 20260913
B = 9999
HUE = {
    "mar": "MAROON", "ora": "ORANGE", "pin": "PINK", "pur": "PURPLE",
    "red": "RED", "yel": "YELLOW", "whi": "WHITE",
}
PIGMENT = {"ant": "ANTHOCYANIN", "car": "CAROTENOID", "no": "NO_CHROMATIC_PIGMENT"}


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "chun-iris-prospective-outcome/0.1"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read()


def clean(x: object) -> str:
    if pd.isna(x):
        return ""
    return re.sub(r"\s+", " ", str(x)).strip()


def default_accession_label(source_label: str) -> str:
    m = re.match(r"^Iris\s+([^\s]+)", clean(source_label))
    if not m:
        raise ValueError(f"cannot derive Iris epithet from {source_label!r}")
    return "Iris_" + m.group(1).replace("-", "_")


def load_crosswalk(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    with path.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row["status"] != "ADMITTED":
                raise SystemExit(f"non-admitted frozen crosswalk row: {row}")
            out[clean(row["trait_source_label"])] = clean(row["accession_source_label"])
    return out


def auc_from_fixed_score_ranks(labels: np.ndarray, score_ranks: np.ndarray) -> float:
    labels = np.asarray(labels, dtype=bool)
    n1 = int(labels.sum()); n0 = int((~labels).sum())
    if n1 == 0 or n0 == 0:
        raise ValueError("AUC undefined: outcome has one class")
    # rankdata ranks increasing predictor; predictor is -patristic distance.
    u = float(score_ranks[labels].sum()) - n1 * (n1 + 1) / 2.0
    return u / (n1 * n0)


def pair_labels(states: np.ndarray, ii: np.ndarray, jj: np.ndarray) -> np.ndarray:
    return states[ii] == states[jj]


def emp_upper(null: np.ndarray, obs: float) -> float:
    return (1.0 + float(np.count_nonzero(null >= obs))) / (len(null) + 1.0)


def emp_lower(null: np.ndarray, obs: float) -> float:
    return (1.0 + float(np.count_nonzero(null <= obs))) / (len(null) + 1.0)


def sha256_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as fh:
        for block in iter(lambda: fh.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--tree', type=Path, required=True)
    ap.add_argument('--crosswalk', type=Path, default=Path('data/iris_source_taxon_crosswalk_v0_1.csv'))
    ap.add_argument('--prereg', type=Path, default=Path('data/intermediate_resolution_rule_prereg_v0_1.json'))
    ap.add_argument('--tree-semantics', type=Path, default=Path('data/iris_tree_record_semantics_v0_1.json'))
    ap.add_argument('--out', type=Path, required=True)
    a=ap.parse_args()

    prereg=json.loads(a.prereg.read_text())
    if prereg['status'] != 'FROZEN_BEFORE_CHUN_IRIS_ROW_LEVEL_OUTCOME_INGESTION':
        raise SystemExit('unexpected prereg status')
    if prereg['primary_statistic']['permutations'] != B or prereg['primary_statistic']['seed'] != SEED:
        raise SystemExit('frozen permutation contract drifted')
    sem=json.loads(a.tree_semantics.read_text())
    if sem['status'] != 'FROZEN_PRE_TREE_PRE_AUC_RECORD_SEMANTICS':
        raise SystemExit('tree semantics not frozen')
    if sem['outcome_exposure_at_freeze']['auc_computed'] is not False:
        raise SystemExit('tree semantics indicate prior outcome exposure')

    raw=fetch(TRAIT_URL)
    if hashlib.sha256(raw).hexdigest() != TRAIT_SHA256:
        raise SystemExit('trait source SHA drift')
    df=pd.read_excel(io.BytesIO(raw), sheet_name='Source of data', engine='openpyxl')
    df.columns=[clean(c) for c in df.columns]
    required={'Species','Colour','Pigment'}
    if not required.issubset(df.columns):
        raise SystemExit(f'trait schema drift: {df.columns.tolist()}')

    cross=load_crosswalk(a.crosswalk)
    rows=[]
    unknown_colour=set(); unknown_pigment=set()
    for _,r in df.iterrows():
        src=clean(r['Species']); c=clean(r['Colour']).lower(); p=clean(r['Pigment']).lower()
        tax=cross.get(src, default_accession_label(src))
        if tax == 'Iris_darwasica':
            continue
        fine=HUE.get(c)
        inter=PIGMENT.get(p)
        if fine is None and c and '&' not in c: unknown_colour.add(c)
        if inter is None and p and '&' not in p: unknown_pigment.add(p)
        coarse=None if inter is None else ('NO_CHROMATIC_PIGMENT' if inter=='NO_CHROMATIC_PIGMENT' else 'CHROMATIC_PIGMENT_PRESENT')
        rows.append({'taxon':tax,'source_label':src,'raw_colour':c,'raw_pigment':p,
                     'coarse':coarse,'intermediate':inter,'fine':fine})
    if unknown_colour or unknown_pigment:
        raise SystemExit(f'unknown single-state codes colour={sorted(unknown_colour)} pigment={sorted(unknown_pigment)}')
    trait_by_tax={r['taxon']:r for r in rows}
    if len(trait_by_tax) != len(rows):
        dup=[k for k,v in Counter(r['taxon'] for r in rows).items() if v>1]
        raise SystemExit(f'duplicate mapped trait taxa: {dup}')

    tree=Phylo.read(str(a.tree),'newick')
    tips=[t.name for t in tree.get_terminals()]
    if len(tips) != len(set(tips)):
        raise SystemExit('duplicate tree tip labels')
    missing_from_tree=sorted(set(trait_by_tax)-set(tips))
    if missing_from_tree:
        raise SystemExit(f'frozen crosswalk does not reach tree tips: {missing_from_tree}')

    # Common primary frame: tree tip + one unambiguous hue + one unambiguous major-pigment state.
    eligible=[t for t in tips if t in trait_by_tax and trait_by_tax[t]['fine'] is not None and trait_by_tax[t]['intermediate'] is not None]
    fine_counts0=Counter(trait_by_tax[t]['fine'] for t in eligible)
    rare=sorted(k for k,v in fine_counts0.items() if v < 5)
    eligible=[t for t in eligible if trait_by_tax[t]['fine'] not in set(rare)]
    if len(eligible) < 20:
        raise SystemExit(f'implausibly small primary frame: {len(eligible)}')

    coarse=np.array([trait_by_tax[t]['coarse'] for t in eligible], dtype=object)
    inter=np.array([trait_by_tax[t]['intermediate'] for t in eligible], dtype=object)
    fine=np.array([trait_by_tax[t]['fine'] for t in eligible], dtype=object)
    n=len(eligible)
    ii,jj=np.triu_indices(n,1)
    dist=np.empty(len(ii),dtype=float)
    for k,(i,j) in enumerate(zip(ii,jj)):
        dist[k]=tree.distance(eligible[int(i)], eligible[int(j)])
    score=-dist
    score_ranks=rankdata(score, method='average')

    def calc(states: np.ndarray) -> float:
        return auc_from_fixed_score_ranks(pair_labels(states,ii,jj), score_ranks)

    obs_c=calc(coarse); obs_i=calc(inter); obs_f=calc(fine)
    obs_dic=obs_i-obs_c; obs_dif=obs_i-obs_f

    rng=np.random.default_rng(SEED)
    null_c=np.empty(B); null_i=np.empty(B); null_f=np.empty(B)
    order=np.arange(n)
    for b in range(B):
        perm=rng.permutation(order)
        # Frozen joint permutation: one identical taxon permutation for the complete triplet.
        null_c[b]=calc(coarse[perm]); null_i[b]=calc(inter[perm]); null_f[b]=calc(fine[perm])
    null_dic=null_i-null_c; null_dif=null_i-null_f

    p_i=emp_upper(null_i,obs_i)
    p_dic=emp_upper(null_dic,obs_dic); p_dif=emp_upper(null_dif,obs_dif)
    p_dic_lower=emp_lower(null_dic,obs_dic); p_dif_lower=emp_lower(null_dif,obs_dif)

    sig_i=(obs_i>0.5 and p_i<=0.05)
    pass_rule=(sig_i and obs_dic>0 and p_dic<=0.05 and obs_dif>0 and p_dif<=0.05)
    significantly_worse=(obs_dic<0 and p_dic_lower<=0.05) or (obs_dif<0 and p_dif_lower<=0.05)
    if pass_rule:
        decision='PASS'
    elif obs_i<=0.5 or significantly_worse:
        decision='FAIL'
    else:
        decision='MIXED'

    out={
      'version':'v0.1',
      'status':'IRIS_PROSPECTIVE_INTERMEDIATE_RESOLUTION_PRIMARY_RESULT',
      'decision':decision,
      'freeze_contract':str(a.prereg),
      'freeze_contract_sha256':sha256_file(a.prereg),
      'tree_semantics_contract':str(a.tree_semantics),
      'tree_semantics_sha256':sha256_file(a.tree_semantics),
      'crosswalk_sha256':sha256_file(a.crosswalk),
      'trait_source_sha256':TRAIT_SHA256,
      'tree_sha256':sha256_file(a.tree),
      'seed':SEED,'permutations':B,
      'primary_frame':{
        'tree_tips':len(tips),
        'trait_rows_after_source_exclusion':len(rows),
        'unambiguous_before_rare_filter':sum(1 for t in tips if t in trait_by_tax and trait_by_tax[t]['fine'] is not None and trait_by_tax[t]['intermediate'] is not None),
        'rare_fine_states_excluded':rare,
        'eligible_tips':n,
        'fine_state_counts':dict(sorted(Counter(fine).items())),
        'intermediate_state_counts':dict(sorted(Counter(inter).items())),
        'coarse_state_counts':dict(sorted(Counter(coarse).items())),
      },
      'observed':{
        'AUC_coarse':obs_c,'AUC_intermediate':obs_i,'AUC_fine':obs_f,
        'delta_intermediate_minus_coarse':obs_dic,
        'delta_intermediate_minus_fine':obs_dif,
      },
      'empirical_p_one_sided':{
        'intermediate_signal':p_i,
        'intermediate_gt_coarse':p_dic,
        'intermediate_gt_fine':p_dif,
        'coarse_gt_intermediate_for_fail_check':p_dic_lower,
        'fine_gt_intermediate_for_fail_check':p_dif_lower,
      },
      'null_summary':{
        'AUC_coarse_mean':float(null_c.mean()),'AUC_intermediate_mean':float(null_i.mean()),'AUC_fine_mean':float(null_f.mean()),
        'delta_intermediate_minus_coarse_mean':float(null_dic.mean()),
        'delta_intermediate_minus_fine_mean':float(null_dif.mean()),
      },
      'decision_contract_verbatim':prereg['decision_rule'],
      'post_hoc_upgrade_allowed':False,
      'paper1_science_changed':False,
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print('=== IRIS PROSPECTIVE PRIMARY RESULT ===')
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
