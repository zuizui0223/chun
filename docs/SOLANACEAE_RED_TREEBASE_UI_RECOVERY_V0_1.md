# Solanaceae red biochemical profile — TreeBASE S16617 UI recovery v0.1

## Purpose

The preregistered 27-species red-flowered Solanaceae biochemical exact-profile candidate passed supplement/schema identification but stopped at `HOLD_TREE_OBJECT_AMBIGUOUS_OR_UNAVAILABLE` because the study-level TreeBASE PhyloWS payload for S16617 was unavailable in the preflight environment.

This recovery gate asks only whether the exact published TreeBASE study can be recovered through another TreeBASE-native route. It does **not** open biochemical outcomes.

## Allowed recovery route

1. Query the TreeBASE Web UI study summary for study 16617.
2. Query the TreeBASE Web UI tree inventory for the same study.
3. Extract only TreeBASE tree-object identifiers (`Tr...`).
4. Retrieve those individual tree objects through TreeBASE/PhyloWS.
5. Evaluate only branch-length completeness and exact normalized species-name overlap with the already admitted 27 identifier rows.

The publication independently identifies its Solanaceae topology as TreeBASE study **S16617**. The recovery route must remain inside that study.

## Frozen pass rule

PASS only if exactly one recovered S16617 tree object:
- contains branch lengths on all edges; and
- exactly matches at least 20 of the 27 preregistered study species after the frozen normalized species-name transform.

If zero or multiple eligible TreeBASE objects remain, stop HOLD.

## Forbidden substitutions

Do not substitute:
- a later Solanaceae phylogeny;
- a tree digitized from Figure S1;
- a topology reconstructed from GenBank accessions;
- a manually chosen tree outside S16617;
- a tree selected after pigment/profile outcomes are inspected.

## Outcome firewall

This gate must not emit or compute:
- pelargonidin/cyanidin/delphinidin values;
- carotenoid state;
- coarse/intermediate/fine profile states;
- state frequencies;
- patristic profile distances;
- profile AUCs;
- permutations;
- winner class.

## Consequence

A PASS authorizes a later, separate outcome-opening PR under the already frozen estimator. A HOLD leaves this candidate inactive and the representation-level biochemical-vs-visible moderator unidentified. Camellia Paper 1 is unchanged.
