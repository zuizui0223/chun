# Silene fine-state falsification — endpoint pre-freeze v1

Freeze status: **FROZEN BEFORE COMPUTATION OR INTERPRETATION OF THE SILENE CONDITIONAL FINE-STATE ENDPOINT**.

Canonical decision record: Issue #224.

## Role

Test unit: **North/Central American Silene sampled by Berardi et al. (2022)**.

Candidate selection is retrospective because the publication has already been inspected for source structure. The endpoint itself is prospectively frozen here. Do not describe a successful result as a blind prospective discovery.

Question:

> Does fine visible flower-colour state retain phylogenetic organization after conditioning on a priori pigment presence?

No transition direction, ancestral state, pollinator cause, molecular mechanism or rate is tested by this endpoint.

## Frozen trait source and representation

Primary phenotype source: Berardi et al. (2022), Frontiers in Plant Science, DOI `10.3389/fpls.2022.945806`; Dryad DOI `10.5061/dryad.wstqjq2pf`.

Use the source species-level colour coding without rebinning:

- `WHITE`
- `PINK`
- `RED`

Frozen coarse map:

- `UNPIGMENTED`: WHITE
- `PIGMENTED`: PINK, RED

Retain the source authors' coding decisions exactly, including polymorphic/pale/orange-pink cases. Do not infer colour from photographs after endpoint inspection.

## Frozen source hierarchy

Trait hierarchy:

1. publisher/Dryad row-level CSV or spreadsheet from `10.5061/dryad.wstqjq2pf`;
2. publisher/Europe-PMC supplementary machine-readable table if it is demonstrably the same species-level coding;
3. otherwise `HOLD_TRAIT_SOURCE`.

Primary topology hierarchy:

1. machine-readable published topology for the reported ITS phylogenetic analysis if recovered;
2. if no source Newick/Nexus tree is supplied, a **trait-blind reconstruction** from the exact published ITS accession set recovered from source supplementary material is allowed, but the reconstruction recipe and accession set must be checksum-pinned before any colour assignment is joined;
3. OpenTree is not a primary rescue for this test because the publication supplies a dedicated ITS phylogenetic analysis and the Epimedium audit showed that an unresolved induced topology can make the null non-identifiable.

The reconstruction fallback, if needed, is frozen as:

- use only the source accession list, without filtering by colour;
- fetch the published ITS sequences by accession;
- MAFFT alignment with a deterministic command recorded in the workflow;
- infer a maximum-likelihood topology with a frozen GTR+G4 nucleotide model using a current reproducible ML implementation available in CI;
- topology only for Sankoff; branch lengths are ignored;
- no tip may be dropped because of its eventual fine-state assignment.

If sequence retrieval/reconstruction cannot be completed source-faithfully, stop as `HOLD_TREE_SOURCE` rather than substituting an unrelated tree after seeing the endpoint.

## Frozen analysis universe and taxon matching

The source reports 47 species in the trait dataset and a published ITS phylogenetic analysis on 37 species. The primary phylogenetic universe is the source ITS-analysis taxon set.

Taxon matching:

1. preserve source species names as immutable identifiers;
2. normalize whitespace and underscore/space only;
3. apply synonym/name corrections only if the source or a pre-endpoint taxonomic crosswalk explicitly documents them;
4. require one-to-one trait row ↔ tree tip mapping;
5. record every exclusion and reason before any observed score is computed.

## Frozen admission gates

Open the biological endpoint only if all are true:

1. checksum-pinnable row-level species colour table is recovered;
2. checksum-pinnable published topology or frozen trait-blind ITS reconstruction is recovered;
3. at least 80% of the published 37-species phylogenetic universe and absolute `n >= 30` are represented one-to-one in the tree–trait intersection;
4. all admitted tips have one source-coded fine state;
5. both PINK and RED remain represented inside `PIGMENTED`, with at least 10 PIGMENTED tips total;
6. admitted topology is not a complete star and has at least two binary internal splits;
7. the frozen conditional null is non-degenerate before the observed assignment is interpreted.

Gates 1–5 failure => a specific observation/source HOLD. Gates 6–7 failure => `HOLD_IDENTIFIABILITY`. HOLD is not biological evidence.

## Frozen identifiability audit

Before interpreting the observed taxon-to-colour assignment:

- use the admitted topology plus only the frozen counts of WHITE/PINK/RED and coarse memberships;
- generate at least 512 deterministic-seed label arrangements exchanging only PINK and RED among PIGMENTED tips; WHITE stays fixed as the sole UNPIGMENTED fine state;
- seed `20260908`;
- compute unordered Fitch/Sankoff score for those arrangements.

Require at least two distinct scores and `null_max > null_min`.

Record tree diagnostics: tip count, internal-node count, binary internal-node count, maximum internal degree and complete-star flag.

If the statistic is invariant under the frozen null, stop at `HOLD_IDENTIFIABILITY` without reading the observed result.

## Frozen statistic and null

Statistic: unordered Fitch/Sankoff minimum changes among `WHITE/PINK/RED` on the admitted topology.

Null: 9,999 conditional permutations exchanging complete fine labels only within frozen coarse class. Thus PINK/RED labels randomize only among PIGMENTED tips; WHITE positions remain fixed.

Seed: `20260908`.

Outputs:

- observed minimum changes;
- null min/max/mean and quantiles;
- observed/null mean ratio;
- `p_lower = (1 + count(null <= observed)) / 10000`.

## Frozen decision

Primary support requires both:

- `p_lower <= 0.01`;
- observed/null mean `< 1`.

Otherwise primary = `PRIMARY_FAIL`.

A primary fail is not automatically `REFUTATION`. Any predeclared admissible topology sensitivity must also be adverse; material disagreement gives `MIXED`. If no independent topology sensitivity is source-faithfully available after an adverse primary, final status is `ADVERSE_BUT_NOT_REFUTATION`, not automatic refutation.

If primary supports but required topology robustness cannot be adjudicated, use `SUPPORTIVE_BUT_TOPOLOGY_UNRESOLVED` rather than a clean additional replication.

## Prohibited post-endpoint moves

After the first observed score is computed, do not:

- merge PINK and RED;
- move source-coded taxa among WHITE/PINK/RED;
- alter the coarse map;
- lower n/coverage or identifiability thresholds;
- replace accessions or drop taxa because of the result;
- choose a different topology because it is favorable;
- change the p threshold;
- treat alternative trees as independent radiations.

This pre-freeze precedes any Silene conditional fine-state result used for cross-radiation interpretation.
