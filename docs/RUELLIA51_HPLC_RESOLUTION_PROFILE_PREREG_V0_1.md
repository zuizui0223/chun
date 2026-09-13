# Ruellia 51-species HPLC resolution-profile preregistration v0.1

## Goal

Run a new exact resolution-profile replication in the 51-species neotropical *Ruellia* dataset of Watts et al. 2026 (`10.1002/ajb2.70149`) without using visible hue and without inspecting CHUN-derived row-level HPLC state frequencies before the representation is frozen.

Status: `FROZEN_BEFORE_RUELLIA51_ROW_LEVEL_HPLC_STATE_INGESTION`.

This is analysis-prospective, not literature-blinded. The paper and author analysis code are public, and CHUN previously used a different 10-species *Ruellia* source for a pathway-region stress test. That earlier result is a different estimand and cannot count as this profile outcome.

## Why this source is admissible

The source reports 51 species with floral reflectance, six anthocyanidin HPLC measurements, and evolutionary history from ddRAD data. The author code defines three biochemical branches directly from the six compounds:

- PEL: Pelargonidin;
- CYA: Cyanidin + Peonidin;
- DEL: Delphinidin + Petunidin + Malvidin.

That source-defined architecture permits one genuinely nested biochemical ladder without mixing chemistry and visible hue.

## Frozen hierarchy

1. **Coarse:** any of the six anthocyanidins present vs none.
2. **Intermediate:** the three-bit PEL/CYA/DEL branch-presence pattern.
3. **Fine:** the six-bit individual-anthocyanidin presence pattern.

Presence is defined mechanically as HPLC concentration `> 0`; zero is absent and missing stays missing. Continuous concentration magnitude is outside the primary analysis.

Fine deterministically maps to intermediate, and intermediate deterministically maps to coarse. No realized frequency, phylogenetic AUC, or colour category may alter that mapping.

## Pre-outcome acquisition gate

Before any row-level six-compound values are used, freeze from source metadata/identifiers only:

- exact HPLC source file and digest;
- exact phylogeny source file and digest;
- tree tip labels and branch-length availability;
- sample-to-species mapping;
- species-to-tree crosswalk;
- duplicate/sample aggregation rule.

If more than one HPLC sample maps to one species, compound presence is OR-ed across nonmissing corolla samples. There is no sample selection based on phenotype frequency or profile performance.

## Common frame and statistic

Use one common retained-tip frame for all three resolutions. Remove species missing any required compound-presence state. Fine states with fewer than five matched tips are removed, after which the same species set is used for coarse/intermediate/fine. Require at least 20 species and at least two states at every resolution.

The statistic is the same profile estimator used in the programme: negative patristic distance predicts same-state pairs, scored by ROC AUC. Jointly permute complete three-level state triplets 9,999 times with seed `20260913`.

Terminal classes are fixed as `PROFILE_SIGNALLED_COARSE`, `PROFILE_SIGNALLED_INTERMEDIATE`, `PROFILE_SIGNALLED_FINE`, `PROFILE_SIGNALLED_TIED`, `PROFILE_NO_PHYLOGENETIC_SIGNAL`, or a preregistered `HOLD_*` state. Sensitivities cannot upgrade the primary terminal class.

## Relation to the cross-radiation programme

Iris remains the only completed exact-estimand prospective outcome and falsified a universal intermediate winner. Gesnerioideae remains a pre-outcome schema HOLD because its chemistry and visible-colour axes do not form one nested ladder. This *Ruellia* test instead stays entirely within anthocyanidin composition and therefore directly tests whether the strongest phylogenetic signal localizes at coarse, branch-pattern, or compound-pattern resolution.

No radiation-level moderator is fitted here. The frozen minimum remains five completed same-estimand radiations.

Camellia Paper 1 remains unchanged and closed.
