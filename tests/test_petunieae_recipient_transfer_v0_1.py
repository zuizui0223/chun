from pathlib import Path
import sys
import itertools
import numpy as np
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from audit_petunieae_recipient_transfer_v0_1 import donor_weights, recipient_losses, summarize_recipients


def example():
    rng = np.random.default_rng(24)
    x = rng.normal(size=(8, 3))
    names = [f's{i}' for i in range(8)]
    states = ['a']*4 + ['b']*4
    d = np.abs(np.arange(8)[:,None] - np.arange(8)[None,:]).astype(float)
    return x, states, names, d


def test_no_self_or_cross_state_donor_and_lexical_ties():
    x, states, names, d = example()
    d[:] = 1; np.fill_diagonal(d, 0)
    w0, w1 = donor_weights(d, states, names)
    assert np.allclose(w0.sum(1), 1) and np.allclose(w1.sum(1), 1)
    assert not np.diag(w0).any() and not np.diag(w1).any()
    assert np.flatnonzero(w1[3]).tolist() == [0, 1]
    assert not w1[:4,4:].any() and not w0[:4,4:].any()


def test_random_two_formula_and_signal_minus_penalty_identity():
    x, states, names, d = example()
    w0, w1 = donor_weights(d, states, names)
    out = recipient_losses(x, w0, w1, states)
    direct = []
    for i in range(8):
        var = np.delete(x, i, axis=0).var(axis=0)
        var = np.where(var > 1e-12, var, 1)
        donors = [j for j in range(8) if j != i and states[j] == states[i]]
        losses = [(((x[a]+x[b])/2-x[i])**2/var).mean()
                  for a,b in itertools.combinations(donors,2)]
        direct.append(np.mean(losses))
    np.testing.assert_allclose(out['random_two'], direct, atol=1e-12)
    np.testing.assert_allclose(out['locality_benefit']-out['donor_count_penalty'],
                               out['baseline']-out['nearest_two'], atol=1e-12)
    assert (out['donor_count_penalty'] >= -1e-12).all()


def test_positive_pooled_gain_need_not_be_majority_or_single_recipient_stable():
    baseline = np.array([1., 1., 1., 1.])
    near = np.array([.2, 1.1, 1.1, 1.1])
    r = summarize_recipients(['a','b','c','d'], ['x']*4, baseline, near)
    assert r['pooled_relative_gain'] == pytest.approx(.125)
    assert r['n_improved_recipients'] == 1
    assert r['n_worse_recipients'] == 3
    assert r['median_paired_loss_improvement'] == pytest.approx(-.1)
    assert r['positive_after_omitting_one_recipient'] == 3
    assert r['single_recipient_omissions_reversing_positive_gain'] == ['a']
    assert r['recipient_omission_does_not_refit']


def test_recipient_ties_and_no_new_p_values():
    r = summarize_recipients(['a','b','c'], ['x']*3,
                             np.array([1.,1.,1.]), np.array([1.,.5,1.5]))
    assert r['n_tied_recipients'] == 1
    assert r['n_improved_recipients'] == r['n_worse_recipients'] == 1
    assert r['new_p_values'] == 0
    assert r['independent_recipient_trials_assumed'] is False


def test_missing_donors_invalid_losses_and_duplicate_ids_fail():
    with pytest.raises(ValueError):
        donor_weights(np.eye(2), ['a','a'], ['x','y'])
    with pytest.raises(ValueError):
        summarize_recipients(['a','a','c'], ['x']*3, np.ones(3), np.ones(3))
    with pytest.raises(ValueError):
        summarize_recipients(['a','b','c'], ['x']*3, np.ones(3), np.array([1.,np.nan,1.]))
