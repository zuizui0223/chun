# Candidate-free actual recurrence v0.1 — authoritative result

## Status

**Primary three-cluster anthocyanin-gain observation-process test: COMPLETE.**

Frozen successful raw-result runs:

- *Camellia japonica* Joy Kendrick: `32803242153`;
- *C. reticulata* Manao full-bloom white/red petal regions: `32823901705`;
- *C. sinensis* white-pink stage series: `32817229591`;
- *C. nitidissima* ordered yellow-development trajectory: `32803242174`;
- integrated four-system actual-results recurrence: `32826059965`.

The integrated workflow combines only canonical `candidate_free_measurements.csv` outputs from frozen successful raw-data runs. It does not borrow literature directions to fill candidate-free missing cells and does not filter axes by significance or expected biological direction.

## Primary anthocyanin-gain test

The common independent dependence-cluster set is fixed to:

- `CJAPONICA`;
- `CRETICULATA`;
- `CSIN_WHITE_PINK`.

All three are canonically oriented toward more red/pink before expression inspection.

### Literature observation regime on the same three clusters

Seven cluster × axis cells remain unresolved. Exact enumeration over `{up, down, same}` gives 2,187 admissible completions.

- exact-signature recurrence: **1/3–1.0**;
- pairwise A/F/C/P concordance: **0.25–1.0**;
- pairwise-concordance identified-set width: **0.75**.

The selected literature representation therefore still permits complete multivariate recurrence.

### Candidate-free observation regime

Only one cluster × axis cell remains unresolved (`CSIN_WHITE_PINK`, P), leaving three exact completions.

- exact-signature recurrence: **1/3 exactly**;
- pairwise A/F/C/P concordance: **1/3–1/2**;
- pairwise-concordance identified-set width: **1/6 = 0.1667**.

The standardized candidate-free regime reduces identified-set width by **7/12 = 0.5833** (`0.75 -> 0.1667`). More importantly, it removes complete multivariate recurrence from the admissible set: no completion can make all three independent anthocyanin-gain clusters share one complete A/F/C/P signature.

## Direct literature-versus-candidate-free overlap

Across cells resolved independently in both regimes:

- comparable cells: **5**;
- agreement: **2/5 = 0.40**;
- conflicts: **3/5**.

| dependence cluster | axis | literature | candidate-free | interpretation |
|---|---|---|---|---|
| `CJAPONICA` | A | up | down | candidate-free effect is essentially near-flat (`g=-0.0168`), so treat as non-reproduction rather than a strong biological reversal |
| `CRETICULATA` | A | up | up | agreement; candidate-free pathway-wide effect is weak (`g=+0.1175`) |
| `CRETICULATA` | P | down | up | conflict |
| `CSIN_WHITE_PINK` | A | up | down | conflict; strong and stage-consistent candidate-free decrease |
| `CSIN_WHITE_PINK` | F | down | down | agreement |

The observation-process effect is therefore **system- and axis-dependent**, not a mechanical reversal produced by the pipeline.

## C. reticulata third-cluster result

The third independent anthocyanin-gain system was frozen before expression inspection as a within-genotype, same-stage 3 × 3 comparison in cultivar Manao:

- source: full-bloom white petal region (`SRR24413192`, `SRR24413191`, `SRR24413190`);
- target: full-bloom red petal region (`SRR24413189`, `SRR24413188`, `SRR24413187`).

Run identities were resolved by the auditable chain `GSE236364 GSM -> GEO SRX relation -> SRR`, not by BioProject membership or accession ordering. The mapping-audit run is `32822609384`.

Candidate-free results (red region minus white region):

- A: Hedges' g = **+0.1175**, up;
- F: **+0.3233**, up;
- C: **-3.4590**, down;
- P: **+0.3990**, up.

All four axes were estimable with 3 source and 3 target replicates. Salmon mapping was 77.22–79.41%, mean 78.42%.

The literature anchor `MICRO_CR_SECTOR_01` resolves A=up and P=down. Candidate-free remeasurement therefore reproduces A only weakly and conflicts on P, while independently resolving F and C.

## C. japonica result

Joy Kendrick pink -> red, 3 × 3, first 1,000,000 paired reads/run:

- A: Hedges' g = **-0.0168**, technically down but effectively near-flat;
- F: **+0.4287**, up;
- C: **-0.9379**, down;
- P: **+1.9002**, up.

Mapping min/mean/max was approximately 76.18/77.57/79.10%.

This does not establish a meaningful opposite anthocyanin response; it shows that the literature A-up representation is not reproduced as a pathway-wide transcript-module increase in this within-genotype sector contrast.

## C. sinensis result

The white -> pink stage series retained all five prespecified stages and all 30 runs. Under the frozen rule (`>=4/5` estimable stages and `>=0.8` same-sign consistency):

- A: mean Hedges' g = **-2.8595**, 5/5 same sign, down;
- F: **-0.3679**, 4/5 same sign, down;
- C: **+0.8820**, 4/5 same sign, up;
- P: **-0.7558**, 3/5 same sign, unresolved.

Mapping was 77.55–84.29%, mean 81.16%.

## Yellow-development control

`CNITIDISSIMA` is still the only candidate-free yellow-development cluster, so class-level recurrence contraction is not yet testable.

However, all four literature-resolved cells agree with the candidate-free ordered trajectory:

- A down;
- F up;
- C up;
- P down.

This 4/4 control, together with the weak A-up result in `CRETICULATA`, rejects the explanation that the standardized pipeline simply forces published directions to reverse.

## Primary inference

The old simple hypothesis — that repeated visible red/pink gains reveal one recurrent whole-module anthocyanin-up package — is **not supported by the standardized three-cluster remeasurement**.

The defensible result is:

> **Published mechanistic recurrence is materially observation-regime dependent. On the same three independent anthocyanin-gain systems, selected literature leaves complete multivariate recurrence admissible, whereas one frozen pathway-wide candidate-free regime identifies exact-signature recurrence at only 1/3 and contracts pairwise-concordance uncertainty from 0.75 to 0.1667. The disagreements are system- and axis-specific rather than a uniform pipeline-induced reversal.**

This does not show that anthocyanins are irrelevant, that candidate-gene studies are generally wrong, or that mutation-level reuse has been disproved. The A axis is a predefined pathway-wide transcript score; specific paralogs, upstream regulators, spatial expression, substrate flux, enzyme activity, post-transcriptional effects, and metabolites may behave differently.

## Consequence for the paper

The molecular mainline is now:

`demonstrated feasibility -> observation regime -> identified mechanistic recurrence -> macroevolutionary realization`

rather than:

`visible transition -> recurrent anthocyanin mechanism -> macro transition`.

The independent macro nuclear result remains: visible-colour phylogenetic clustering is reproducible while robust individual historical transition branches are not. Together, these results support an identification argument: **an apparent recurrent pattern can be measurable while its event-level mechanism is not identified, and the observation process itself must be measured rather than silently equated with biology.**

## Remaining gates

1. Add a second independent `yellow_development` candidate-free cluster before claiming class-level yellow recurrence; `CPERPETUA` is the highest-information target once its run-to-stage map is frozen.
2. Do not map A/F/C/P states onto the 53-tip nuclear tree from visible hue; direct mechanistic tip coverage remains inadequate.
3. Do not assign ecological causes to individual colour-transition branches; ecology remains strongest at reproductive-service/persistence level.
