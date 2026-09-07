# Hydrangea sect. Cornidia transition-direction robustness v0.1

## Question

Does the published return-to-white excess disappear if the four reported transition means are challenged using their marginal 95% HPD limits?

Primary source: Granados Mendoza et al. 2021, DOI `10.3389/fpls.2021.661522`.

This audit uses the already frozen published stochastic-map QC table in `data/hydrangea_cornidia_published_transition_summary_v0_1.csv`. It is not an atlas re-estimate.

## Internal numerical consistency

The four published mean transition counts are:

- RED -> WHITE = 18.011 [12, 23]
- PURPLE -> WHITE = 4.680 [1, 7]
- WHITE -> RED = 4.939 [1, 8]
- WHITE -> PURPLE = 1.773 [0, 4]

Their mean sum is 29.403, matching the paper's rounded statement of 29.4 flower-colour changes on average for the represented transition types.

## Nominal directional contrast

Aggregating transitions toward versus away from white gives:

- coloured -> white = 22.691
- white -> coloured = 6.712
- return/gain ratio = 3.3806615017878427
- return-to-white share = 0.7717239737441758

Thus the published-map mean is strongly return-to-white biased.

## Marginal-HPD box sensitivity

A deliberately adverse rectangular calculation combines marginal HPD endpoints in the direction least favorable to return-to-white:

- minimum coloured -> white = 12 + 1 = 13
- maximum white -> coloured = 8 + 4 = 12
- minimum box return/gain ratio = 13/12 = 1.0833333333333333
- minimum box return share = 13/(13+12) = 0.52

The aggregate direction therefore still points toward white at this extreme corner.

### Pair-specific result

The aggregate robustness is not equivalent to universal pairwise asymmetry:

- RED <-> WHITE survives the same adverse endpoint comparison: 12 > 8.
- PURPLE <-> WHITE does not: 1 < 4.

So the strongest interpretation is **state-dependent aggregate return asymmetry**, not a rule that every colored state individually returns to white faster than it is gained.

## Statistical boundary

The four quoted HPD intervals are marginal intervals. Their joint posterior covariance is unavailable in the publication-level summary. Combining marginal lower/upper endpoints is therefore a conservative rectangular sensitivity exercise, **not** a joint 95% credible interval and **not** an estimate of the posterior probability that the aggregate ratio exceeds one.

A formal posterior statement requires the original stochastic-map draws or a common atlas re-estimation from terminal states and phylogeny.

## Cross-clade implication

This audit strengthens one negative result and narrows the retained candidate rule:

- a universal `white ancestor -> directional accumulation of colour` rule remains incompatible with Hydrangea;
- the asymmetry itself is state dependent, so a useful cross-clade law must concern constraints on accessible transition architecture rather than a single universal direction coefficient.

Paper 1 remains unchanged.
