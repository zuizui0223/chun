#!/usr/bin/env python3
"""Exact finite-population random-two donor error diagnostic.

Retrospective *post-primary-outcome* explanatory calculation only.
The primary Petunieae k=2 prediction is frozen as NOT_SUPPORTED.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from run_petunieae_nested_regulatory_leaveoneout_prediction_v0_1 import (
    load_source,
    loss_gain,
    weights,
)


def decompose(x: np.ndarray, fine: list[str], names: list[str],
              distance: np.ndarray, frozen_result: dict) -> dict:
    x = np.asarray(x, dtype=float)
    state_w, near_w = weights(distance, fine, names, k=2)
    previous = loss_gain(x, state_w, near_w)
    expected_random2_loss_by_tip = []
    small_donor_penalty_by_tip = []
    for i, code in enumerate(fine):
        eligible = [j for j in range(len(fine)) if j != i and fine[j] == code]
        m = len(eligible)
        if m < 2:
            raise ValueError("frozen k=2 rule not defined for pigment class")
        donors = x[eligible]
        donor_mean = donors.mean(axis=0)
        donor_popvariance = np.square(donors - donor_mean).mean(axis=0)
        train = np.delete(x, i, axis=0)
        fold_var = train.var(axis=0, ddof=0)
        fold_var = np.where(fold_var > 1e-12, fold_var, 1.0)
        baseline_per_gene = np.square(x[i] - donor_mean) / fold_var

        # Exact random WITHOUT-replacement 2-donor mean-variance penalty.
        # E[(mean_sample_2 - mean_population)^2] =
        # ((m-2)/(2*(m-1))) * variance_ddof0(donors).
        extra = (m-2)/(2*(m-1))*donor_popvariance/fold_var
        expected_random2_loss_by_tip.append(float(np.mean(baseline_per_gene + extra)))
        small_donor_penalty_by_tip.append(float(np.mean(extra)))

    l_state = float(previous["state_only_mse"])
    l_nearest = float(previous["phylogenetic_neighbor_mse"])
    l_random = float(np.mean(expected_random2_loss_by_tip))
    penalty = float(np.mean(small_donor_penalty_by_tip))
    locality_gain = l_random-l_nearest
    net_penalty = l_nearest-l_state

    if abs(l_random-l_state-penalty) > 1e-11:
        raise ValueError("random-two penalty decomposition identity failed")
    if abs(net_penalty-(penalty-locality_gain)) > 1e-11:
        raise ValueError("net gain decomposition identity failed")
    for key, current in (("baseline_loss",l_state),("neighbor_loss",l_nearest)):
        if abs(current-float(frozen_result[key])) > 1e-10:
            raise ValueError(f"pre-existing frozen prediction result drift: {key}")
    if abs((l_state-l_nearest)/l_state - float(frozen_result["observed_relative_prediction_gain"])) > 1e-10:
        raise ValueError("pre-existing positive-gain/FAIL boundary drift")

    by_state = []
    for code in sorted(set(fine)):
        ids=np.flatnonzero(np.asarray(fine)==code)
        avg_baseline=float(np.mean(previous["per_tip_state_only_mse"][ids]))
        avg_nearest=float(np.mean(previous["per_tip_neighbor_mse"][ids]))
        avg_random=float(np.mean(np.asarray(expected_random2_loss_by_tip)[ids]))
        by_state.append({
           "fine_code":code,"retained_tips":int(len(ids)),
           "baseline_mse":avg_baseline,
           "random_two_expected_mse":avg_random,
           "phylogeny_two_mse":avg_nearest,
           "donor_penalty":avg_random-avg_baseline,
           "locality_gain":avg_random-avg_nearest,
           "observed_nearest_minus_state":avg_nearest-avg_baseline,
        })

    return {
        "version":"v0.1",
        "status":"POST_OUTCOME_EXACT_PREDICTOR_DECOMPOSITION_DESCRIPTIVE_ONLY",
        "sample_tips":len(fine),
        "genes":int(x.shape[1]),
        "donors_k":2,
        "fine_classes":len(set(fine)),
        "state_only_mse":l_state,
        "random_two_expected_mse":l_random,
        "nearest_two_mse":l_nearest,
        "small_donor_penalty":penalty,
        "locality_gain_over_random_two":locality_gain,
        "net_nearest_two_penalty":net_penalty,
        "small_donor_penalty_relative_to_state_mean":penalty/l_state,
        "locality_gain_relative_to_state_mean":locality_gain/l_state,
        "net_penalty_relative_to_state_mean":net_penalty/l_state,
        "algebraic_identity_pass":True,
        "frozen_primary_decision":"NOT_SUPPORTED",
        "no_new_p_value":True,
        "frozen_primary_outcome_unchanged":True,
        "per_state_descriptive":by_state,
        "boundary":"Exact conditional finite-population expected error, not a phylogenetic process model, independent taxon replication, or causal mechanism. No predictor re-optimization."
    }


def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--original-design",type=Path,required=True)
    p.add_argument("--prediction-design",type=Path,required=True)
    p.add_argument("--frozen-result",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    original=json.loads(a.original_design.read_text(encoding="utf-8"))
    design=json.loads(a.prediction_design.read_text(encoding="utf-8"))
    prior=json.loads(a.frozen_result.read_text(encoding="utf-8"))
    D,fine,names,X=load_source(a.source,design,original)
    result=decompose(X,fine,names,D,prior)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
