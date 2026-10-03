# Repository integrity gate policy

## Stable required-check target

The repository-level merge gate is the job named **integrity** in
`.github/workflows/repository-integrity-gate.yml` (workflow display name:
**Repository integrity gate**).

The workflow runs on every pull request without a path filter. It validates:

- workflow YAML syntax;
- incremental dependency pinning (changed workflows may not add unpinned installs);
- frozen Merianieae numeric-state support;
- Flowerclades51 relative-time contract chronology and half-depth result;
- frozen cross-radiation Evolution Letters v0.3 science;
- Paper 1 DOCX reproducibility;
- two independent Paper 1 bundle builds with byte-identical SHA256 inventories.

## Negative-canary evidence

Draft PR #373 intentionally added an `assert False` to
`tests/test_gate_merianieae_state_support_v0_1.py`.

Observed result:

- `Merianieae prospective hidden-memory pipeline v0.1`: **failure**
- `Repository integrity gate / integrity`: **failure**
- PR #373 was closed unmerged.

This demonstrates that the always-present repository gate detects a broken frozen
contract.

## Branch-protection requirement

Repository settings should require the **integrity** status check for merges to
`main`. Path-filtered scientific workflows should not individually be made the
sole required checks because a skipped workflow does not provide an always-present
status.

Administrator bypass, if retained, should be reserved for GitHub/service outages
or security recovery. A bypass must not be used to merge a scientifically red
integrity gate; any such bypass should be documented in the PR conversation with
the reason and a follow-up validation run.

## Current external-setting boundary

The in-repository gate and negative-canary verification are complete. The
branch-protection/ruleset toggle is a GitHub repository administration setting,
not a file in the repository. Its configured state must be checked in repository
Settings before Issue #364 is closed.
