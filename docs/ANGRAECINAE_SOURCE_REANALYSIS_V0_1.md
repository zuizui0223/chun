# Angraecinae source-to-history reanalysis v0.1

## Executed result

Angraecinae is the third external flower-colour radiation reanalysed from source terminal traits and public sequences under the same binary Mk framework used after Hydrangea and Linoideae. The source layer contains 194 sample rows, including 189 source-defined Angraecinae ingroup rows; 186 ingroup sample rows have exact unique trait joins.

The result is split into ancestry, direction and state-space structure, with an additional tree-reconstruction sensitivity retained rather than hidden.

1. **Robust WHITE ancestry passes the pre-frozen gate in two independently executed ML reconstruction sets.** The minimum root P(WHITE) across sepal/petal, all three tree variants, ER/ARD and equal/stationary root treatments is **0.875** in the fresh full rerun and **0.938** in the checkpoint-resume reconstruction.
2. **A common directional GREEN/WHITE rate asymmetry fails the pre-frozen gate in both reconstruction sets.** Point estimates are consistently in the WHITE->GREEN direction for both primary organs, but the required profile/AIC support does not occur on >=2/3 trees for both organs.
3. **Fine organ-state structure remains after conditioning on coarse GREEN/WHITE status in every tested tree.** Exact fully binary trait joins provide 169 tips. Across the six tests from the two reconstruction sets, all 9,999-permutation conditional tests have p=0.0001 and observed/null minimum-change ratios of **0.513-0.549**.

Thus this radiation directly separates ancestral state from directional determinism: a strongly supported WHITE root does not imply a reproducibly supported common transition-rate direction.

## Source and observation grain

Primary source: Andriananjamanantsoa et al. (2016), DOI `10.1371/journal.pone.0163194`.

The source morphology matrix provides separate colour characters for sepal (20), petal (23), labellum (31) and spur (37). GREEN corresponds to source state 1 and WHITE to source state 2. Ocher/other source states remain outside the binary comparison and are never silently recoded.

At source-table level, 170 ingroup rows are GREEN/WHITE in all four organs. **46/170 (27.1%)** are organ-discordant. The dominant discordant pattern is WHITE/WHITE/WHITE/GREEN (34 rows). A one-organ representation discards about 47-50% of the equal-row entropy of the four-organ joint-state distribution. This is a descriptive information result, not an evolutionary effect size.

## Sequence and tree reconstruction

The source sample table yielded 577 unique requested GenBank accessions and 578 admitted sequence assignments after fail-closed source/metadata checks. Admitted sequences per locus were matK 189, rps16 144, trnL 169 and ITS 76. Alignment variants were:

- `plastid_full`: matK+rps16+trnL, 5,255 columns;
- `plastid50`: the same plastid loci after >=50% base-occupancy filtering, 3,304 columns;
- `all4_full`: plastid loci plus ITS, 6,176 columns.

The same source inputs were used in two executed ML reconstruction sets:

- **checkpoint_resume** — run `34141115622`, artifact `10026168219`, SHA256 `1688f6f87d556de5daea54f747628ecb00a620962c388ddb170042f46b3a381c`; it retains the completed original plastid trees and resumes the interrupted all4 IQ-TREE checkpoint;
- **fresh_repeat** — run `34138289110`, artifact `10025946443`, SHA256 `d256dd9f7d393956673afcffb4c4dee3fcd7405c6df7e859f234fe5b0116ab82`; it reruns all three ML searches from the same inputs.

The resulting Newick files are not byte-identical. This reconstruction variation changes some point estimates, especially for the all4 tree, but does not change the pre-frozen scientific gates. The two reconstruction sets are sensitivity analyses within one biological radiation, not two independent clades.

## Primary Mk results

The reported ratio is `q(GREEN->WHITE) / q(WHITE->GREEN)`. Ratio <1 points toward faster WHITE->GREEN evolution. Branch lengths are sequence substitutions/site, not years.

### Checkpoint-resume reconstruction

| Tree | Sepal ratio | Sepal ARD-ER dAIC | Sepal profile high | Petal ratio | Petal ARD-ER dAIC | Petal profile high |
|---|---:|---:|---:|---:|---:|---:|
| plastid_full | 0.540 | +1.071 | 2.260 | 0.177 | -1.131 | 1.151 |
| plastid50 | 0.486 | +0.763 | 1.739 | 0.179 | -1.719 | 1.020 |
| all4_full | 0.419 | +0.454 | 1.781 | 0.115 | -2.019 | 0.959 |

### Fresh-repeat reconstruction

| Tree | Sepal ratio | Sepal ARD-ER dAIC | Sepal profile high | Petal ratio | Petal ARD-ER dAIC | Petal profile high |
|---|---:|---:|---:|---:|---:|---:|
| plastid_full | 0.486 | +0.697 | 2.542 | 0.175 | -1.598 | 1.046 |
| plastid50 | 0.489 | +0.780 | 1.753 | 0.181 | -1.685 | 1.026 |
| all4_full | 0.110 | -2.219 | 0.919 | 0.116 | -2.801 | 0.847 |

A negative dAIC means ARD has lower AIC. A favorable all4 result in one reconstruction is not promoted because the predeclared directional gate required >=2/3 qualifying trees for **both** primary organs. The directional gate is therefore **FAIL in both reconstruction sets**.

## Robust WHITE root

The pre-result gate required root P(WHITE)>=0.8 across ER/ARD, equal/stationary treatments and all three trees for each primary organ. This criterion passes in both ML reconstruction sets. The lowest value across all primary fits and both reconstruction sets is **0.875**.

This is the key falsification of a simple ancestry-to-direction law: robust WHITE ancestry coexists with unresolved directional asymmetry.

## Conditional hierarchical state-space test

The conditional test uses exact fully binary joins only (169 tips; the source table has 170 before fail-closed trait joining). It fixes every tip's primary sepal GREEN/WHITE class and permutes the complete sepal/petal/labellum/spur state vector only within those classes. It asks whether organ configuration carries phylogenetic organization beyond the coarse primary binary state.

Across the two reconstruction sets:

| Reconstruction | Tree | Observed changes | Null mean | Observed/null | p |
|---|---|---:|---:|---:|---:|
| checkpoint_resume | plastid_full | 29 | 54.062 | 0.536 | 0.0001 |
| checkpoint_resume | plastid50 | 28 | 54.580 | 0.513 | 0.0001 |
| checkpoint_resume | all4_full | 29 | 53.260 | 0.544 | 0.0001 |
| fresh_repeat | plastid_full | 29 | 54.680 | 0.530 | 0.0001 |
| fresh_repeat | plastid50 | 28 | 54.580 | 0.513 | 0.0001 |
| fresh_repeat | all4_full | 30 | 54.688 | 0.549 | 0.0001 |

These scores are organization statistics, not counts of independent historical origins. No ecological or molecular cause is inferred.

## Cross-clade implication

Hydrangea, Linoideae and Angraecinae now have source-to-tree trait-history reanalyses. They do not recover a universally supported WHITE transition direction. Angraecinae is especially informative because its WHITE root passes a stringent robustness gate while the directional-rate gate fails.

A different positive pattern is replicated across two independent external radiations: Linoideae retains hue-specific phylogenetic organization after conditioning on WHITE/nonwhite status, and Angraecinae retains four-organ configuration structure after conditioning on primary GREEN/WHITE status. This supports a **hierarchical state-space constraint hypothesis**: biologically informative flower-colour organization can persist at finer hue or organ levels than coarse colour classes, while ancestral state does not uniquely determine transition direction.

This remains a replicated candidate rule, not a universal law. Camellia's analogous exploratory fine-state test is topology-sensitive/underpowered and is not counted as a third positive replication. Epimedium independently supports organ-specific rather than whole-flower ancestral-state coding, but its historical event identity remains unresolved.

## Reproducibility and boundary

The repository freezes both three-tree reconstruction sets, the exact source-derived terminal-state table, the sample-to-trait join manifest, provenance/hash contracts and the authoritative summary. Offline replay recomputes each reconstruction set's 72 Mk fits, 12 regular profiles and three 9,999-permutation conditional tests, then fails on numerical drift or input-hash mismatch.

Paper 1 science and manuscript files are unchanged. This reanalysis does not establish ecological causation, molecular module reuse, dated transition rates or a universal flower-colour law.
