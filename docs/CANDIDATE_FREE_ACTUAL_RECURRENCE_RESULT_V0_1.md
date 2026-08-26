# Candidate-free actual recurrence v0.1 — authoritative result

## Status

**Both canonical molecular observation-process tests are COMPLETE.**

Frozen successful raw-result runs:

- *Camellia japonica* Joy Kendrick (`CJAPONICA`): `32803242153`;
- *C. reticulata* Manao full-bloom white/red petal regions (`CRETICULATA`): `32823901705`;
- *C. sinensis* white-pink stage series (`CSIN_WHITE_PINK`): `32817229591`;
- *C. nitidissima* ordered yellow-development trajectory (`CNITIDISSIMA`): `32803242174`;
- *C. perpetua* ordered yellow-development trajectory (`CPERPETUA`): `32834693855`;
- unified five-system / 20-row actual-results recurrence: **`32929846096`**.

The unified workflow combines only canonical `candidate_free_measurements.csv` outputs from frozen successful raw-data runs. It never borrows literature directions to fill candidate-free cells and never filters axes by significance or expected biological direction.

## Primary result at a glance

| transition class | independent candidate-free clusters | literature exact-signature recurrence | candidate-free exact-signature recurrence | literature pairwise concordance | candidate-free pairwise concordance | width reduction |
|---|---:|---:|---:|---:|---:|---:|
| anthocyanin gain | 3 | 0.333–1.0 | **0.333 exactly** | 0.25–1.0 | **0.333–0.5** | **0.5833** |
| yellow development | 2 | 0.5–1.0 | **0.5 exactly** | 0.25–1.0 | **0.75 exactly** | **0.75** |

Selected literature leaves complete multivariate recurrence admissible in both canonical classes. The frozen pathway-wide candidate-free regime removes complete whole A/F/C/P recurrence from the admissible set in both classes.

This is **not** evidence that mechanistic recurrence is absent. The standardized data instead support **transition-class-dependent modular recurrence**.

---

## Anthocyanin-gain test

Common independent clusters:

- `CJAPONICA`;
- `CRETICULATA`;
- `CSIN_WHITE_PINK`.

All three were canonically oriented toward more red/pink before expression inspection.

### Literature regime

Seven cluster × axis cells remain unresolved, giving 2,187 exact completions.

- exact-signature recurrence: **1/3–1.0**;
- pairwise A/F/C/P concordance: **0.25–1.0**;
- pairwise identified-set width: **0.75**.

### Candidate-free regime

Only one cluster × axis cell remains unresolved (`CSIN_WHITE_PINK`, P), leaving three exact completions.

- exact-signature recurrence: **1/3 exactly**;
- pairwise A/F/C/P concordance: **1/3–1/2**;
- pairwise identified-set width: **1/6 = 0.1667**;
- width reduction: **7/12 = 0.5833**.

Thus no admissible candidate-free completion can make all three independent anthocyanin-gain clusters share one complete A/F/C/P signature.

### Direct literature-versus-candidate-free overlap

Across cells independently resolved in both regimes:

- comparable cells: **5**;
- agreement: **2/5 = 0.40**;
- conflicts: **3/5**.

| dependence cluster | axis | literature | candidate-free | interpretation |
|---|---|---|---|---|
| `CJAPONICA` | A | up | down | candidate-free effect is essentially near-flat (`g=-0.0168`), so interpret as non-reproduction rather than a strong biological reversal |
| `CRETICULATA` | A | up | up | agreement; pathway-wide effect is weak (`g=+0.1175`) |
| `CRETICULATA` | P | down | up | conflict |
| `CSIN_WHITE_PINK` | A | up | down | conflict; strong and stage-consistent decrease |
| `CSIN_WHITE_PINK` | F | down | down | agreement |

The anthocyanin result therefore shows substantial observation-regime dependence, but not a universal candidate-free reversal.

## Raw anthocyanin systems

### C. japonica Joy Kendrick

Pink→red, same cultivar, 3 × 3, first 1,000,000 paired reads/run:

- A: Hedges' g = **-0.0168**, technically down but effectively near-flat;
- F: **+0.4287**, up;
- C: **-0.9379**, down;
- P: **+1.9002**, up.

Mapping min/mean/max ≈ 76.18/77.57/79.10%.

### C. reticulata Manao sectors

Frozen same-cultivar, same full-bloom-stage white-region→red-region 3 × 3 comparison. Run identities were resolved by `GSE236364 GSM -> GEO SRX -> SRR`, not BioProject membership or accession ordering; mapping-audit run `32822609384`.

- A: **+0.1175**, up;
- F: **+0.3233**, up;
- C: **-3.4590**, down;
- P: **+0.3990**, up.

Mapping min/mean/max = 77.22/78.42/79.41%.

### C. sinensis white→pink

All five prespecified stages and all 30 runs were retained. Under the frozen `>=4/5` estimable + `>=0.8` same-sign rule:

- A: mean Hedges' g = **-2.8595**, 5/5 same sign, down;
- F: **-0.3679**, 4/5, down;
- C: **+0.8820**, 4/5, up;
- P: **-0.7558**, 3/5, unresolved.

Mapping min/mean/max = 77.55/81.16/84.29%.

---

## Yellow-development test

Common independent clusters:

- `CNITIDISSIMA`;
- `CPERPETUA`.

The cross-cluster estimator is matched between systems: OLS slope across all five prespecified S1–S5 stage means, oriented toward later/more-yellow development. Exact 5! stage-order P values are uncertainty metadata only.

### Literature regime

Three cluster × axis cells remain unresolved, giving 27 exact completions.

- exact-signature recurrence: **0.5–1.0**;
- pairwise A/F/C/P concordance: **0.25–1.0**;
- pairwise identified-set width: **0.75**.

### Candidate-free regime

All eight cluster × axis cells resolve.

- exact-signature recurrence: **0.5 exactly**;
- pairwise A/F/C/P concordance: **0.75 exactly**;
- pairwise identified-set width: **0.0**;
- width reduction: **0.75**.

The two candidate-free signatures are:

- `CNITIDISSIMA`: **A down / F up / C up / P down**;
- `CPERPETUA`: **A down / F down / C up / P down**.

They agree on **3/4 axes** and differ only at F. This follows the pre-outcome branch specified in `docs/YELLOW_TWO_CLUSTER_RECURRENCE_GATE_V0_1.md`: **axis-specific reuse without exact whole-signature recurrence**.

### Direct literature-versus-candidate-free overlap

Across independently resolved cells:

- comparable cells: **5**;
- agreement: **4/5 = 0.80**;
- conflict: **1/5** (`CPERPETUA`, F: literature up vs candidate-free down).

The high direct agreement is an important control: the candidate-free pipeline does not mechanically overturn literature directions. Yet filling the previously unmeasured axes is enough to remove full whole-package recurrence from the admissible set.

## Raw yellow systems

### C. nitidissima

Fifteen runs, S1–S5 × 3; mapping mean ≈71.68%.

- A: slope **-0.2406**, down, exact P=0.0833;
- F: **+0.1240**, up, P=0.6667;
- C: **+0.1567**, up, P=0.1667;
- P: **-0.4503**, down, P=0.0333.

### C. perpetua

Fifteen verified runs, S1–S5 × 3; mapping min/mean/max = **79.2054/81.4782/84.0166%**.

- A: slope **-0.5817**, down, exact P=0.0167;
- F: **-0.1691**, down, P=0.3167;
- C: **+0.1792**, up, P=0.0667;
- P: **-0.6156**, down, P=0.0167.

The preregistered S1→S3 yellow-onset contrast remains a within-system biological result; it is not substituted for the matched five-stage trajectory in the cross-cluster recurrence test.

See `docs/YELLOW_TWO_CLUSTER_RECURRENCE_RESULT_V0_1.md` for the dedicated yellow result and the unchanged pre-outcome decision boundary.

---

## Primary inference

The old biological shorthand — repeated visible colour transitions imply recurrence of one complete pigment-state package — is **not supported** by the standardized candidate-free measurements.

The defensible result is:

> **Repeated floral-colour change does not map to one invariant whole A/F/C/P package. Standardizing the same public systems collapses literature-permitted complete multivariate recurrence in both red/pink gain and yellow development, while revealing transition-class-dependent modular reuse.**

For anthocyanin gain, whole-signature recurrence is low and axis agreement is heterogeneous. For yellow development, exact whole-signature recurrence still fails, but A/C/P directions are reused across both independent systems, producing 0.75 pairwise concordance.

Therefore the result is not “recurrence absent.” It is a separation between:

- **whole-package recurrence**, which is not supported;
- **modular recurrence**, which remains and differs by transition class;
- **observation regime**, which materially changes what recurrence is identifiable from the same biological systems.

This does not show that anthocyanins are irrelevant, that candidate-gene studies are generally wrong, or that mutation-level reuse has been disproved. A/F/C/P are predefined pathway-wide transcript-state modules; specific paralogs, upstream regulators, spatial expression, metabolite levels, enzyme activity and post-transcriptional processes remain distinct quantities.

## Consequence for the paper

The molecular mainline is now complete:

`demonstrated feasibility -> observation regime -> identified modular/whole-package recurrence -> macroevolutionary realization`

rather than:

`visible transition -> recurrent pathway package -> macro transition`.

The independent nuclear result remains: visible-colour phylogenetic clustering is reproducible while robust individual historical transition branches are not. Together the results support a broader identification argument: **patterns may be identifiable even when the individual events, causes, or complete mechanistic packages that generated them are not.**

## Remaining gates

The molecular recurrence gate is no longer a remaining task. Remaining scientific boundaries are:

1. do not impute taxon-level A/F/C/P states on the 53-tip nuclear tree from visible hue; direct mechanistic tip coverage remains inadequate;
2. do not assign ecological causes to individual colour-transition branches; ecology remains strongest at reproductive-service/persistence level;
3. move next to manuscript/figure synthesis and final CI/repository cleanup rather than continuing open-ended molecular dataset search.
