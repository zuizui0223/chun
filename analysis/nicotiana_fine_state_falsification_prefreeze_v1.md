# Nicotiana fine-state falsification — prospective pre-freeze v1

Freeze status: **FROZEN BEFORE INSPECTION OF THE SUPPLEMENTARY TRAIT ROWS AND BEFORE COMPUTATION OF THE MATCHED CONDITIONAL FINE-STATE ENDPOINT**.

## Question

Does residual phylogenetic organization at fine flower-colour resolution persist after conditioning on an a priori biological coarse layer in a fifth independent radiation?

Test unit: **Nicotiana**, using the source-defined non-hybrid diploid subset.

Primary source: McCarthy E. W. et al. (2015), *The effect of polyploidy and hybridization on the evolution of floral colour in Nicotiana (Solanaceae)*, Annals of Botany 115:1117–1131, DOI `10.1093/aob/mcv048`.

The source is attractive for falsification rather than confirmatory selection: it describes floral colour as only weakly constrained by phylogeny. That published Mantel result is background only and is **not** the endpoint tested here.

## Frozen biological unit and eligibility rule

Use one species-level evolutionary unit per source taxon. Follow the source paper's own tree-like-history restriction:

1. include only **non-hybrid diploid** taxa eligible for the source's phylogenetic signal / ancestral-state analyses;
2. exclude source-designated polyploids and homoploid hybrids before the endpoint is computed;
3. do not exclude any species based on colour, chlorophyll status, contribution to the parsimony score, or the eventual result;
4. multiple source accessions or colour morphs of the same species are not independent evolutionary replicates. Their observed states are combined into species-level allowed-state sets.

If the source supplement cannot unambiguously recover the source-defined non-hybrid/diploid classification, classify `HOLD_ELIGIBILITY_SCHEMA` rather than creating a post-hoc classification.

## Frozen fine alphabet

Use the eight spectral-reflectance colour categories defined by the source cluster analysis:

`MAGENTA, RED, PINK, UV_WHITE, WHITE, YELLOW, GREEN, DARK_GREEN`.

Use only explicit source category labels/codes. If the supplement uses codes, map them to these labels only when the source supplies an unambiguous codebook. Any unrecognized non-empty spectral category causes `HOLD_SCHEMA`; do not merge or invent categories after inspection.

For species represented by multiple eligible accessions or morphs, retain the union of all source-observed spectral categories as the species' allowed fine-state vector.

## Frozen primary coarse layer

Use the source authors' **presence/absence of chlorophyll in petal tissue** as the primary biological coarse layer:

- `CHLOROPHYLL_PRESENT`
- `CHLOROPHYLL_ABSENT`

For species with multiple eligible source records, retain the complete allowed chlorophyll-status set. Do not infer chlorophyll from apparent green colour when a source chlorophyll observation exists, and do not use the fine-state result to resolve conflicting records.

During the primary conditional permutation, exchange whole species-level fine-state vectors only among tips with the **identical allowed chlorophyll-status set**. This preserves the coarse biochemical layer, source polymorphism/accession ambiguity, the global fine-state frequency structure, and uncertainty counts.

## Frozen topology rule

Primary topology priority:

1. a machine-readable source 95% majority-rule plastid tree or source posterior-tree object, if recoverable directly from the article supplement/archive without reconstructing analytical choices;
2. otherwise an OpenTree induced subtree on the frozen eligible taxa, using exact one-to-one TNRS matching and topology only.

Do not choose a topology based on the flower-colour endpoint. If both source and OpenTree topologies become available, the non-primary topology is a predeclared sensitivity, not a second biological replication.

Taxon normalization before TNRS is restricted to deterministic formatting: genus capitalization, explicit hybrid-marker formatting already made irrelevant by the non-hybrid eligibility rule, author-string removal, and explicit source infraspecific rank retention. Approximate TNRS matching is prohibited.

## Frozen admission gate

Proceed to biological classification only if all are true:

1. at least **80%** of source-defined eligible non-hybrid diploid species with both spectral-category and chlorophyll information are represented one-to-one in the admitted topology;
2. the admitted intersection contains at least **20 species**;
3. every admitted tip has at least one source-coded fine spectral state and at least one source-coded chlorophyll status;
4. definite `CHLOROPHYLL_PRESENT` and definite `CHLOROPHYLL_ABSENT` each contain at least **5 admitted species**;
5. at least one definite chlorophyll class contains at least **3 distinct fine spectral states** and at least **10 admitted species**;
6. no taxon is excluded because of its contribution to the signal statistic.

Failure of these gates is `HOLD_OBSERVATION_REGIME`, not a counterexample.

## Frozen statistic and primary null

Statistic: unordered Sankoff/Fitch minimum number of changes for the eight-state species-level allowed spectral-state vectors on the admitted topology.

Primary null: **9,999 conditional permutations**. Each permutation exchanges entire species-level fine-state vectors only within identical frozen chlorophyll-status sets. The observed assignment is permutation zero.

Seed: `20260908`.

Primary outputs:

- `observed_minimum_changes`;
- `null_mean` and null quantiles;
- `observed_over_null_mean`;
- `p_lower = (1 + count(null <= observed)) / 10000`.

## Frozen primary decision

- `SUPPORTIVE_ALIGNMENT`: `p_lower <= 0.01` and `observed_over_null_mean < 1`.
- `PRIMARY_FAIL`: either condition is not met.

A primary failure is not by itself a cross-radiation refutation.

## Frozen sensitivities

### 1. Single-fine-state species only

Remove species whose eligible source records span more than one spectral category; repeat the same chlorophyll-conditioned test. This asks whether a result depends on treating source colour polymorphism/multiple accessions as an allowed-state vector.

### 2. Definite-chlorophyll species only

Remove species whose eligible source records span both chlorophyll states; repeat the primary conditional test on species with one definite coarse biochemical state.

### 3. Source spectral WHITE-like / non-WHITE-like coarse sensitivity

Define a second coarse representation directly from the source spectral alphabet:

- `WHITE_LIKE`: `WHITE`, `UV_WHITE`
- `NONWHITE_LIKE`: the other six spectral categories.

For multistate species, retain the complete implied allowed coarse set and shuffle whole fine-state vectors only within identical allowed WHITE-like status sets. This sensitivity connects the fifth test to the binary conditioning used in earlier radiations without replacing the primary chlorophyll layer.

### 4. Topology sensitivity

If both a machine-readable source tree and OpenTree fallback are recovered independently of the endpoint, repeat the frozen primary test on the alternate topology. Otherwise record `NOT_AVAILABLE`; absence is not biological failure.

## Frozen final classification

- primary support with no material contradictory admitted sensitivity => `SUPPORTIVE_ALIGNMENT`;
- primary fail and all admitted trait sensitivities fail => `REFUTATION` of the surviving recurrence generalization by this matched fifth radiation;
- material disagreement among primary/admitted sensitivities => `MIXED`;
- inadequate coverage/schema/topology => `HOLD` or `HOLD_OBSERVATION_REGIME`;
- adverse primary result with required robustness not adjudicable => `ADVERSE_BUT_NOT_REFUTATION`.

The existing cross-radiation state before this endpoint is **3 clean supportive radiations + 1 prospectively tested MIXED radiation (Iris)**. Nicotiana can change that state only through this frozen matched test.

## Prohibited post-hoc moves

After source-table inspection or endpoint computation begins, do not:

- redefine the eight spectral categories;
- infer chlorophyll state from colour to repair missing source values;
- include hybrids/polyploids because they improve coverage or significance;
- split one species into multiple independent evolutionary replicates;
- change the `p <= 0.01` support threshold;
- relax exact TNRS matching;
- choose a different coarse layer because it gives a smaller p-value;
- choose among trees based on the flower-colour result;
- count sensitivities or posterior trees as independent radiations.

This file is the decision record for the fifth-radiation falsification test.
