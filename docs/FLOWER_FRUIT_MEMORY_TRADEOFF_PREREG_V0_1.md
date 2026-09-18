# Flower–fruit evolutionary-memory trade-off preregistration — v0.1

## Biological question

The source study found a negative cross-clade association between the number of flower- and fruit-color transitions, suggesting specialization on one reproductive signalling phase. The CHUN time-axis extension now asks a complementary question:

> Do clades that retain stronger flower-color memory through relative evolutionary time tend to retain weaker fruit-color memory, and vice versa?

This is deliberately framed as a **reproductive-phase memory trade-off**, not as a character-coding test.

## Retrospective boundary

Flower-color persistence has already been computed. The source dataset is known to contain fruit colors and the published study already reports a flower–fruit lability trade-off. No fruit persistence curve or cross-organ memory statistic has been computed by CHUN before this freeze.

The result is therefore retrospective and cannot be counted as an independent prospective discovery.

## Common cross-organ frame

Within each clade:

1. fine flower and fruit states represented by fewer than five source tips are identified separately;
2. any species belonging to a rare state in either organ is removed;
3. the remaining species form one identical flower/fruit tip frame;
4. require at least 20 common tips, at least two flower states, and at least two fruit states;
5. require source-tree root-to-tip CV <= 1e-8.

Relative divergence depth is pairwise patristic distance divided by twice source-tree crown height.

## Memory metric

For flower and fruit separately, but on identical species pairs:

- split pairs into ten equal-count relative-divergence bins;
- calculate same-state probability per bin;
- center on the exact without-replacement frequency baseline;
- scale to excess retention;
- integrate the curve by the signed trapezoid area.

Positive area means state sharing is concentrated above the clade-frequency expectation across relative divergence. The secondary metric is the fitted linear decay slope.

## Frozen hypothesis

If reproductive phases trade off in evolutionary lability, their memory strengths should also trade off.

Primary test:

- Spearman rho between flower and fruit signed excess-retention areas;
- expected direction: negative;
- 99,999 label permutations, seed 20260918;
- PASS only if rho < 0 and one-sided permutation P <= 0.05.

Secondary diagnostics cannot rescue a failed primary test.

## Interpretation boundary

A PASS would support a cross-organ trade-off in **evolutionary memory**, consistent with reproductive-phase specialization. It would not by itself identify energetic allocation, pollinator turnover, disperser turnover, climate, or pigment constraints as the causal mechanism.

A FAIL would mean the published transition-count trade-off does not automatically translate into a trade-off in relative-time memory shape.

Camellia Paper 1 and frozen EL v0.2 remain unchanged.
