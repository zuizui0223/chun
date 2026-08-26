# chun

**Camellia flower-colour evolution from molecular accessibility to macroevolutionary persistence.**

The project asks whether pigment-network changes that recur at developmental or within-lineage scales predict flower-colour transitions across *Camellia*. Visible colour and biochemical state remain separate: anthocyanin, flavonol, proanthocyanidin and carotenoid evidence are never inferred from hue alone.

## Current answer

The direct prediction is **not yet demonstrated**.

- A micro-only predictor now exists: independent evidence-cluster recurrence is highest for anthocyanin-downstream, flavonol and regulatory modules, with FLS and ANS the most recurrent explicit nodes in the current ledger.
- Sequence-aware resolution supports flexible molecular implementation: FLS includes a same-lineage recurrence mode, whereas DFR shows module reuse through different paralogs.
- At macro scale, accepted wild flower colour shows topology-robust **local phylogenetic conservatism**, not unrestricted lability.
- The decisive enrichment test cannot yet be run: strict and dominant wild-colour encodings share **zero robust accepted-species transition branches**.

The supported result is therefore a cross-scale mismatch—molecular implementation can be flexible while macroevolutionary colour remains locally constrained. Current public data do **not** show that high micro-accessibility predicts which macro transition occurs.

## Claim boundary

This repository supports pattern-level comparison, not branch-specific causation. It does not establish:

- transition probabilities or mutation rates from the micro recurrence score;
- exact gene/module reuse on a reconstructed macro transition branch;
- a universal white ancestor, cold-adaptation route or pollinator-driven transition;
- causal ecological filtering of a particular accepted-species colour event.

The macro test reopens only when new data identify transition events that are robust to accepted taxonomy, wild-colour uncertainty and nuclear topology.

## Scope

`chun` is now *Camellia*-only. East Asian *Cirsium* phylogenomics, colour history and molecular mechanism belong to [EAzami](https://github.com/zuizui0223/EAzami). The initial cross-family scaffold remains recoverable in Git history but is not an active analysis input here. See [repository scope and handoff](docs/REPOSITORY_SCOPE.md).

## Authoritative evidence products

- [Paper 1 authoritative result registry](docs/PAPER1_AUTHORITATIVE_RESULT_REGISTRY.md)
- [Current micro-to-macro evidence audit](docs/EVIDENCE_AUDIT_2026-08-26.md)
- [Micro-accessibility score v0.1](docs/MICRO_ACCESSIBILITY_SCORE_V0_1_RESULT.md)
- [Pigment-state schema](docs/PIGMENT_STATE_SCHEMA.md)
- [Camellia evidence matrix v0.1](data/evidence_matrix_v0_1.csv)
- [Camellia hypothesis ledger v0.1](data/hypothesis_test_ledger_v0_1.csv)
- [Source/provenance registry v0.1](data/source_registry_v0_1.csv)

## Public raw-data anchor

`SRP112181` provides 15 *Camellia nitidissima* flower RNA-seq runs spanning five developmental stages and three biological replicates. It supports developmental pigment-pathway analysis; it does not by itself identify genus-scale transition direction.

## Next execution gate

Paper 1 remains at its public-data stop rule. The next direct test requires population-resolved wild pigment states and an independently reconstructed set of accepted-species transition branches, followed by a preregistered enrichment comparison against the frozen micro-only recurrence score.
