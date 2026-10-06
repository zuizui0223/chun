# Petunia colour-regain benchmark v0.1

## Why this system matters

Petunia supplies a high-quality mechanistic test of colour reacquisition from a recent colorless floral ancestor.

The best-supported long-tube phylogeny places white *P. axillaris* as sister to the two coloured species *P. secreta* and *P. exserta*. AN2/MYB histories support two independent regains of floral anthocyanin pigmentation from a colorless ancestor.

This system therefore tests a narrower question than the Camellia Paper 1 recurrence analysis:

> When colour is regained twice from a recent colorless state, is the same molecular programme restored?

## Event 1 — *Petunia secreta*

Purple pigmentation is regained by a simple compensatory mutation in `AN2`: an additional 2-bp deletion restores the reading frame of a previously nonfunctional R2R3-MYB regulator (`10.1016/j.cub.2018.10.019`).

At the atlas ontology level this is a `PATHWAY_SPECIFIC_REGULATOR` regain.

The study does not justify coding every other pigment module as unchanged, so unmeasured axes remain unknown.

## Event 2 — *Petunia exserta*

Red pigmentation is regained without resurrection of `AN2` (`10.1093/plcell/koab114`). Instead, multiple changes contribute:

- redeployment/upregulation of the AN2 paralog `DPL` in the petal limb (`PATHWAY_SPECIFIC_REGULATOR`);
- loss/downregulation of the competing flavonol regulator `MYB-FL` (`COPIGMENT/FLUX`);
- rebalancing of F3'H and F3'5'H expression (`BRANCH_ENZYME`);
- low acyltransferase/AAT expression, reducing pigment acylation (`PIGMENT_MODIFICATION_MODULE`).

The red phenotype is produced primarily with cyanidin/delphinidin rather than by a simple switch to pelargonidin.

Dryad `10.5061/dryad.jsxksn083` provides a large open source bundle including normalized expression counts and pathway/MYB sequence resources.

## Benchmark interpretation

The two events share a high-level feature—recruitment/restoration of a pathway-specific MYB regulatory route—but **do not replay one identical molecular programme**.

This is useful for the white-baseline atlas because it provides direct empirical support for two claims that should remain separate:

1. retained biochemical machinery can permit colour reacquisition after a colorless state;
2. reacquisition need not use the same complete molecular implementation.

However, the current event count is only two. Petunia alone is therefore not promoted as a standalone quantitative recurrence estimator requiring >=3 independent transitions.

Its atlas role is:

`WHITE_BASELINE_REGAIN_MECHANISTIC_BENCHMARK`.

## Relation to Camellia

Petunia complements rather than duplicates Camellia.

- Camellia: repeated visible transition classes remeasured in a common A/F/C/P state space; whole-package recurrence contracts under standardized observation.
- Petunia: two historically resolved colour regains from a recent colorless ancestor, each with experimentally characterized but contrasting regulatory architecture.

Together they motivate a cross-clade hypothesis that **latent pigment-network capacity can be redeployed repeatedly while the exact route of redeployment remains contingent**.

## Claim ceiling

Do not claim:

- that Petunia has >=3 independent regain events in this benchmark;
- that all pathway axes were measured equivalently in *P. secreta* and *P. exserta*;
- that the two events prove a general rule across angiosperms;
- that colour regain necessarily reverses the exact mutations responsible for ancestral colour loss.

## Next gate

1. ingest the 2021 Dryad bundle and map expression/pathway data into the atlas molecular ontology;
2. identify whether the 2018 *P. secreta* functional/source data can be reconstructed at comparable module resolution;
3. represent both events as partially observed module signatures rather than filling unknown axes;
4. use Petunia as a two-event white-regain benchmark inside the pooled cross-clade model, not as a forced standalone recurrence estimate.
