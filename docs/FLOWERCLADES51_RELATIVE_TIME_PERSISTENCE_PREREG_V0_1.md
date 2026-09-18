# Relative phylogenetic-time flower-color half-depth — estimand contract v0.1

## Provenance

PR #300 contains a failing contract test committed before the relative-time persistence result of PR #299 was frozen. That test already specified the exact source hashes, 28-clade common frame, normalized patristic-depth axis, exponential model, outputs `lambda` and `ln(2)/lambda`, and prohibition on absolute-time claims.

The machine-readable object is being materialized after outcome exposure, so this is **not** presented as a prospective preregistration. The pre-outcome contract is retained as provenance for the estimand.

## Biological quantity

For each clade and phenotype resolution,

`P(same state | d) = q + (1-q) exp(-lambda d)`

where:

- `d` is pairwise patristic distance divided by twice clade crown height;
- `q` is the exact finite-sample probability that a random unordered pair shares state, determined by observed state counts;
- `lambda` is the decay rate of excess state retention above that baseline.

The biologically interpretable summary is

`half-depth = ln(2)/lambda`.

It is the fraction of clade crown depth over which modelled excess same-state retention falls by one half. It is **not** an estimate in millions of years.

## Fit

Fit lambda by maximizing Bernoulli pairwise pseudo-log-likelihood with q fixed. Optimization is on log(lambda), bounded to lambda in [1e-4, 1e4].

Species pairs are not treated as independent inferential replicates. Lambda is a within-clade descriptive estimand; cross-clade paired tests use clade as the unit.

## Resolution comparison

Reuse exactly the existing 28 completed coarse/intermediate/fine common frames.

Primary descriptive output: median half-depth at each resolution.

Omnibus comparison: Friedman paired test across the three resolutions and 28 clades. Pairwise two-sided Wilcoxon tests are reported only if the Friedman test is significant at 0.05.

Within each clade, the resolution with the largest half-depth is recorded descriptively; exact ties remain ties.

## Interpretation

A larger half-depth means that excess same-state identity persists across a greater fraction of the clade's relative evolutionary depth. A smaller value means rapid erosion toward the clade-frequency baseline.

This analysis is a biologically interpretable transformation of the same flower-color states and phylogenetic distances already used by CHUN. It cannot be counted as independent replication.

Camellia Paper 1 and frozen EL v0.2 remain unchanged.
