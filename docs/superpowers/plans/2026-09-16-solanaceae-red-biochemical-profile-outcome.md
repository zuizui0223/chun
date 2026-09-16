# Solanaceae Red Biochemical Profile Outcome Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Execute the already-preregistered Solanaceae red-flower biochemical coarse/intermediate/fine resolution profile only after the S16617 source/tree crosswalk has been frozen on main.

**Architecture:** Reacquire the exact PMC Table S1 DOCX, parse only source-defined pelargonidin/cyanidin/delphinidin proportions and carotenoid presence, and join them to the frozen exact source-to-tree crosswalk. Build fine states first, drop fine states with fewer than five retained taxa, use that identical tip frame at all resolutions, then apply the same rank-AUC and joint-permutation estimator used for Petunieae.

**Tech Stack:** Python 3.12, standard-library DOCX XML parsing, Biopython 1.85, NumPy, SciPy.

**Spec:** `data/solanaceae_red_biochemical_resolution_profile_prereg_v0_1.json`

## Global Constraints

- Frozen crosswalk receipt must be `PASS_ARCHIVED_TREEBASE_S16617_OBJECT_CROSSWALK_FROZEN`.
- Use only `tree_85881.phy` from archived TreeBASE S16617; substitute trees are forbidden.
- Exact normalized source-binomial to exact normalized tree-tip joins only; no fuzzy/synonym repair.
- Anthocyanidin presence is numeric proportion `> 0`; exact zero is absence; missing/non-numeric is ineligible.
- Carotenoid status uses source-reported presence/absence only; unresolved is ineligible.
- Fine states represented by fewer than 5 taxa are excluded before all three resolutions.
- Retained common frame must have at least 20 taxa and at least 2 states at each resolution.
- Use patristic branch-length distance, rank ROC AUC, 9,999 joint label permutations, seed `20260915`.
- Do not alter Camellia Paper 1.

---

### Task 1: Outcome parsing and state construction

**Files:**
- Create: `scripts/run_solanaceae_red_biochemical_resolution_profile_v0_1.py`
- Create: `tests/test_solanaceae_red_biochemical_resolution_profile_v0_1.py`

**Interfaces:**
- Produces `parse_numeric_proportion`, `parse_carotenoid_presence`, `state_codes`, `auc`, `classify_terminal`.

- [ ] Write failing tests covering numeric/percent proportions, strict unresolved-value rejection, deterministic nested state mapping, rare-state gate, and terminal classification.
- [ ] Run tests and verify failure because the production runner does not yet exist.
- [ ] Implement only the tested pure functions.
- [ ] Run tests and verify they pass.

### Task 2: Frozen source/tree integration

**Files:**
- Modify: `scripts/run_solanaceae_red_biochemical_resolution_profile_v0_1.py`

**Interfaces:**
- Consumes `data/solanaceae_red_archived_treebase_crosswalk_v0_2.json` and the preregistration.
- Produces one deterministic outcome JSON.

- [ ] Reacquire the exact DOCX and verify SHA256 `be5b7c75d52fef4714080938d638e31645ef5909c6b7a40ca1e8f2cadacebc2a`.
- [ ] Reacquire the pinned archived `tree_85881.phy` and verify its frozen SHA256 from the crosswalk receipt.
- [ ] Parse the identifier table selected by the frozen preflight and identify source columns by normalized source labels, failing closed if required variables are ambiguous.
- [ ] Restrict to the 25 frozen exact source/tree matches before eligibility and rare-state filtering.
- [ ] Compute one common retained frame, patristic pair distances, AUCs, 9,999 joint permutations, signal p-values, winner-vs-runner joint p-value and terminal class.

### Task 3: Reproducible CI execution

**Files:**
- Create: `.github/workflows/solanaceae-red-biochemical-resolution-profile-outcome-v0-1.yml`

- [ ] Install pinned Biopython/NumPy/SciPy.
- [ ] Run the unit tests.
- [ ] Run the outcome script and upload the result artifact.
- [ ] Assert that prereg and frozen crosswalk inputs are unchanged and Paper 1 files are untouched.

### Task 4: Freeze the observed result

**Files:**
- Create after CI outcome: `data/solanaceae_red_biochemical_resolution_profile_result_v0_1.json`
- Create after CI outcome: `docs/SOLANACEAE_RED_BIOCHEMICAL_RESOLUTION_PROFILE_RESULT_V0_1.md`

- [ ] Download the CI artifact and inspect the terminal class, frame size, state counts, AUCs and permutation p-values.
- [ ] Commit the exact outcome JSON without changing preregistered thresholds or hierarchy.
- [ ] Update CI to byte-compare regenerated output against the committed result.
- [ ] Re-run CI and require unit tests, outcome recomputation and byte-identical comparison to pass.
