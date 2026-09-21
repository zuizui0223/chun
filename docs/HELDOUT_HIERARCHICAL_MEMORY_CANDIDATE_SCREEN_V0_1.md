# Held-out hierarchical-memory candidate screen — v0.1

## Purpose

Find one additional independent radiation for a **prospective within-coarse hidden-memory test** without choosing the system based on the target outcome.

## Hard admission

A candidate is admitted only if, before any target phenotype-state opening:

- at least 20 species can be placed on one joint trait/tree frame;
- exact public trait source exists;
- exact public branch-length phylogeny exists;
- coarse and fine states form a source-defined or deterministic pre-outcome nesting;
- the identifier crosswalk can be frozen without target outcomes;
- the frozen common frame can in principle support at least two coarse and two fine states with the existing minimum fine-state support of five;
- CHUN has not opened the within-coarse hidden-memory outcome.

## Metadata-only screen

Allowed: source metadata, counts, filenames, column names, tree identity, DOI/repository metadata, and source-defined state definitions.

Forbidden: row-level target states, state frequencies, fine-vs-coarse AUCs, or any result that reveals the target CHUN estimand.

## Prospective test if admitted

Opportunity gate:

`fine_state_count > coarse_state_count`

Then:

- retain same-coarse pairs;
- score by negative patristic distance;
- label same-fine state;
- compute conditional AUC;
- permute fine labels within coarse groups;
- 9,999 permutations;
- PASS only if observed conditional AUC exceeds the null mean and one-sided P <= 0.05.

Candidate selection is based on source completeness and schema only, not the target outcome.

Frozen EL v0.3, current v0.7 promotion HOLD, and Camellia Paper 1 remain unchanged.
