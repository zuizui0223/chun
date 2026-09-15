# Rhododendron30 biochemical exact-profile source access recheck — v0.2

## Goal

Recheck the two exact source objects already frozen for the preregistered 30-species *Rhododendron* biochemical resolution profile, without changing the representation hierarchy and without opening chemistry outcomes.

## Frozen source objects

Trait identifiers:
- article DOI `10.1111/plb.12649`;
- supplement `plb12649-sup-0002-TableS3.docx`;
- species identifiers are projected from the first table column only.

Primary tree:
- Dryad DOI `10.5061/dryad.8cz8w9grq`;
- file `1_WP_RAxML.tre`;
- file id `1853438`;
- size `13,100` bytes;
- SHA-256 `784011d0e2e17df9ea21eb22d31197bad29219a37ac213fda013766e29b51362`.

## Recheck rule

The existing v0.1 source preflight is executed unchanged against the current network state. PASS requires the same preregistered source gate:
- exactly 30 Table S3 species identifiers;
- exact primary-tree bytes with frozen digest;
- tree branch lengths and no duplicate normalized tips;
- at least 20 exact normalized species/tree matches;
- no automatic synonym substitution.

## Outcome firewall

Before PASS and a separately frozen crosswalk:
- Table S1 chemistry is not downloaded;
- row-level anthocyanin values are not accessed;
- flower-colour and CIELAB values are not accessed;
- compound states, frequencies, AUCs and winner are not computed.

## Consequence

If source access now passes, freeze the exact source hashes and crosswalk in a separate gate before opening Table S1 chemistry. If access remains blocked, retain source HOLD and move to the next pre-admitted non-visible candidate rather than weakening the tree or trait-source contract.

Camellia Paper 1 remains unchanged.
