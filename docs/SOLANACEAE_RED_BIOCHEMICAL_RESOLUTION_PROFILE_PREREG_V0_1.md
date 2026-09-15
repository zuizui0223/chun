# Solanaceae red-flower biochemical resolution profile — preregistration v0.1

## Decision

Admit the 27-species Ng & Smith red-flowered Solanaceae dataset as a **candidate** second non-visible exact-profile unit, but freeze the representation and estimator before opening its row-level pigment values for this CHUN profile.

This candidate was identified after the existing frontier was frozen: Iochrominae remains source-access blocked, Ruellia is blocked on the authoritative timed tree, Rhododendron is source-access blocked, Gesnerioideae is non-nested, and Antirrhineae collapses intermediate to fine. The Solanaceae source is different: its species-level pigment table is deposited with an open PMC article and its parent phylogeny is archived under TreeBASE S16617.

## Source facts used before the freeze

Ng & Smith (2016; DOI `10.1093/aobpla/plw013`, PMCID `PMC4804202`) report 27 red-flowered Solanaceae species. Supporting Table S1 is described by the source as containing the relative proportions of pelargonidin-, cyanidin- and delphinidin-based anthocyanidins, carotenoid presence, spectral hue and provenance for the study species.

The red-flower article explicitly uses the phylogenetic analysis from Ng & Smith (2016; DOI `10.1111/nph.13576`). That parent study archives its Solanaceae tree under TreeBASE study `S16617`.

These are source/schema facts. No Table S1 species-level pigment values are used to choose the hierarchy below.

## Frozen nested biochemical hierarchy

The source itself distinguishes two pigment classes (anthocyanins and carotenoids) and three anthocyanidin hydroxylation branches (pelargonidin, cyanidin and delphinidin). The hierarchy therefore uses only those source-defined variables.

### Coarse

`(ANY_ANTHOCYANIDIN_PRESENT, CAROTENOID_PRESENT)`

This retains the broad pigment-pathway configuration rather than human-visible red hue, which is intentionally nearly constant across the source sample.

### Intermediate

`(CAROTENOID_PRESENT, HIGHEST_HYDROXYLATION_BRANCH_PRESENT)`

The anthocyanidin branch order is frozen as:

`DELPHINIDIN > CYANIDIN > PELARGONIDIN > NONE`

This is a pathway-order summary, not an abundance winner. It is determined only from branch presence.

### Fine

`(CAROTENOID_PRESENT, PELARGONIDIN_PRESENT, CYANIDIN_PRESENT, DELPHINIDIN_PRESENT)`

Fine therefore maps deterministically to intermediate and coarse. No color-name thresholds, clustering, PCA or post-outcome binning are allowed.

Presence is defined as a reported relative proportion strictly greater than zero. Exact zero means absent. Missing/non-numeric anthocyanidin values or unresolved carotenoid status make the taxon ineligible before state-frequency filtering.

## Frozen common-frame rule

As in the existing Petunieae biochemical profile:

1. build fine states first;
2. exclude every fine state represented by fewer than five taxa;
3. use exactly the same retained taxa at coarse, intermediate and fine resolution;
4. require at least 20 retained taxa;
5. require at least two states at every resolution;
6. otherwise terminate without profile AUC.

## Frozen tree rule

Use only a branch-length tree object from TreeBASE `S16617` that source metadata unambiguously identifies as the final published Ng & Smith 2016 Solanaceae phylogeny consumed by the red-flower analysis. The source trait table may be used for identifiers after this preregistration, but not to choose among tree alternatives.

If TreeBASE metadata leaves more than one eligible tree object and source metadata alone cannot select one, terminate `HOLD_TREE_OBJECT_AMBIGUOUS_OR_UNAVAILABLE`. A substitute OpenTree, synthetic, newly inferred or outcome-selected tree is forbidden in v0.1.

## Frozen estimator

For the common retained frame:

- pair response: same state versus different state;
- predictor score: negative patristic distance;
- metric: rank ROC AUC;
- joint label permutations: `9999`;
- seed: `20260915`;
- signal: `AUC > 0.5` and one-sided permutation `p <= 0.05`;
- unique winner: the highest-AUC resolution is signal-positive and beats the runner-up with joint-permutation `p <= 0.05`.

The terminal-class vocabulary is identical in meaning to the existing exact-profile programme: coarse / intermediate / fine unique signal, tied signal, no signal, or fail-closed HOLD.

## Interpretation boundary

This will be retrospective standardized training even if it completes. The publication and broad aggregate pigment findings predate CHUN, so it cannot count as a new prospective replication.

A completed result would answer only whether this independent **non-visible pigment representation** exhibits a resolution profile under the same estimator family. It cannot by itself establish a general `biochemical -> fine` rule. Its information value is that it would create a second independent biochemical/non-visible exact-profile unit and make representation-level moderation testable under honest leave-one-out validation.

## Outcome firewall at this commit

At freeze time:

- Table S1 row-level pigment values have not been ingested into CHUN for this profile;
- no Solanaceae-red profile state counts exist;
- no patristic distances have been computed for this candidate;
- no profile AUC or permutation p-value exists;
- no winner class exists.

The next step is source/schema preflight only: recover exact supplementary bytes, inspect structural headers, inventory TreeBASE `S16617`, and establish an identifier/tree crosswalk without computing pigment states or AUCs.

Camellia Paper 1 remains unchanged.
